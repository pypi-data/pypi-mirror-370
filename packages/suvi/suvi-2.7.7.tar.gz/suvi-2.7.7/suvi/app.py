import logging
import os
import platform
import signal
import subprocess
import sys
import tempfile
import threading
import time
import warnings
from collections import Counter, deque
from datetime import datetime, timedelta
from importlib.metadata import version
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional, Union
from uuid import uuid4
from zipfile import ZipFile

import psutil
import typer
from flask import Flask, Response, jsonify, redirect, render_template, request
from markdown import markdown
from uptime import uptime
from waitress import serve

from suvi.app_state import AppState
from suvi.config_cache import ConfigCache
from suvi.multiuser_basic_auth import MultiuserBasicAuth
from suvi.task import ParseError, ParseWarning, Task, TaskExec, TaskType

__version__ = version("suvi")
__about__ = "© 2025 ECMind GmbH (Switzerland)"

logger = logging.getLogger("suvi")

base_dir = os.path.abspath(os.path.dirname(__file__))

cmd = typer.Typer()
app = Flask(
    __name__,
    static_folder=os.path.join(base_dir, "static"),
    template_folder=os.path.join(base_dir, "templates"),
)
auth = MultiuserBasicAuth(app)

config = ConfigCache()
state = AppState()


@app.route("/")
@auth.user_required
def app_root():
    return redirect("/log")


@app.route("/ps")
@auth.user_required
def app_ps():
    return render_template("ps.html", current="ps", processes=state.processes.copy())


@app.route("/ps_inner")
@auth.user_required
def app_ps_inner():
    text_filter = str(request.args.get("filter", "")).lower()

    if text_filter == "":
        filtered_processes = state.processes.copy()
    else:
        filtered_processes = {}
        for task_name, proc in state.processes.copy().items():
            if text_filter in str(task_name).lower() or text_filter in "\n".join(proc.args).lower():
                filtered_processes[task_name] = proc

    return render_template("ps_inner.html", processes=filtered_processes, filter=text_filter)


@app.route("/ps.json")
@auth.user_required
def app_ps_json():
    ps_list = []
    for task_name, proc in state.processes.items():
        ps_list.append((task_name, proc.pid, proc.args))
    return jsonify(ps_list)


@app.route("/tasks")
@auth.user_required
def app_tasks():
    return render_template("tasks.html", current="tasks", **create_task_lists(), cycle_wait=state.cycle_wait)


@app.route("/tasks_inner")
@auth.user_required
def app_tasks_inner():
    text_filter = str(request.args.get("filter", "")).lower()
    lists = create_task_lists()
    filtered_lists = {}
    if text_filter == "":
        filtered_lists = lists
    else:
        filtered_lists = {list_name: {} for list_name in lists}
        for list_name, task_dict in lists.items():
            for task_name, task in task_dict.items():
                if text_filter in str(task_name).lower() or text_filter in "\n".join(flatten(task.args)).lower():
                    filtered_lists[list_name][task_name] = task

    return render_template("tasks_inner.html", **filtered_lists, cycle_wait=state.cycle_wait)


@app.route("/tasks.json")
@auth.user_required
def app_tasks_json():
    return jsonify(create_task_lists())


def fetch_infos() -> dict:
    infos = {}
    try:
        infos["os / system / release"] = f"{os.name} / {platform.system()} / {platform.release()}"
    except Exception as ex:
        log(f"Manage: {type(ex).__name__} ({ex.args})", is_error=True)

    try:
        infos["whoami"] = os.getlogin()
    except Exception as ex:
        log(f"Manage: {type(ex).__name__} ({ex.args})", is_error=True)

    try:
        infos["cpu count"] = os.cpu_count()
    except Exception as ex:
        log(f"Manage: {type(ex).__name__} ({ex.args})", is_error=True)

    try:
        infos["uptime"] = str(timedelta(seconds=uptime()))  # type: ignore
    except Exception as ex:
        log(f"Manage: {type(ex).__name__} ({ex.args})", is_error=True)

    infos["cwd"] = os.getcwd()
    infos["suvi.toml"] = os.path.exists("suvi.toml") and os.path.isfile("suvi.toml")

    return infos


@app.route("/manage")
@auth.admin_required
def app_manage():
    return render_template("manage.html", current="manage", message=None, infos=fetch_infos())


@app.route("/about")
@auth.user_required
def app_about():
    return render_template("about.html", current="about", about=__about__, version=__version__)


@app.route("/remove/<task_name>")
@auth.user_required
def app_remove(task_name):
    remove(task_name)
    return f"<del>{task_name}</del>", 200


def remove(task_name):
    log(f"Killing & removing {task_name}")
    kill(task_name)
    state.schedules.pop(task_name, None)


def stop_task(task_name) -> bool:
    log(f"Stopping {task_name}")
    try:
        kill(task_name)
        state.task_files.pop(task_name)
        state.schedules.pop(task_name, None)
        return True
    except KeyError:
        log(f"Task {task_name} is unknown.", True)
        return False


@app.route("/stop/<task_name>")
@auth.user_required
def app_stop_task(task_name):
    if stop_task(task_name):
        return f"<del>{task_name}</del>", 200
    else:
        return f"{task_name}", 500


@app.route("/run/<task_name>")
@auth.user_required
def app_run(task_name):
    task: Task = state.task_files[task_name]
    if not task_name in state.processes:
        log(f"Running task {task_name}")
        exec_task(task_name, task)
    else:
        log(f"Will not start task {task_name}: already running.")
    return redirect(f"/tasklog/{task_name}")


@app.route("/run/hook/<token>", methods=["GET", "POST"])
def app_run_hook(token):
    log(f"Executing tasks for hook {token}, method {request.method}")
    time.sleep(1)
    tasks = {task_name: task for task_name, task in state.task_files.items() if task is not None and token in task.tokens}
    result = 0
    for task_name, task in tasks.items():
        if not task_name in state.processes:
            log(f"Running task {task_name} for hook {token}")
            stdin_data = request.get_data() if request.method == "POST" else None
            exec_task(task_name, task, stdin_data)
            result += 1
        else:
            log(f"Will not start task {task_name} for hook {token}: already running.")

    log(f"Executing {result} tasks for hook {token}")
    if len(tasks) > 0:
        return jsonify(result)
    else:
        return jsonify(result)


@app.route("/log")
@auth.user_required
def app_log():
    return render_template("log.html", current="log", log=state.loq_queue.copy())


@app.route("/log_inner")
@auth.user_required
def app_log_inner():
    return render_template("log_inner.html", log=state.loq_queue.copy())


@app.route("/log.json")
@auth.user_required
def app_log_json():
    return jsonify(list(state.loq_queue))


@app.route("/log.txt")
@auth.user_required
def app_log_txt():
    result = "\n".join(["\t".join(line) for line in list(state.loq_queue)])
    return Response(result, mimetype="text/plain")


@app.route("/tasklog")
@auth.user_required
def app_task_logs():
    return render_template(
        "tasklogs.html",
        current="task_logs",
    )


@app.route("/tasklog_inner")
@auth.user_required
def app_task_logs_inner():
    text_filter = str(request.args.get("filter", "")).lower()

    if text_filter == "":
        logs = state.task_log_queues

    else:
        logs = {}
        for log_name, queue in state.task_log_queues.items():
            if text_filter in str(log_name).lower():
                logs[log_name] = queue

    return render_template("tasklogs_inner.html", logs=logs, filter=text_filter)


@app.route("/tasklog.json")
@auth.user_required
def app_task_logs_json():
    return jsonify(list(state.task_log_queues))


@app.route("/tasklog/<task_name>")
@auth.user_required
def app_task_log(task_name):
    return render_template(
        "tasklog.html",
        current="task_logs",
        log=state.task_log_queues.get(task_name, deque([], 1)).copy(),
        task_name=task_name,
        proc=state.processes.get(task_name, None),
    )


@app.route("/tasklog_inner/<task_name>")
@auth.user_required
def app_task_log_inner(task_name):
    return render_template(
        "tasklog_inner.html",
        log=state.task_log_queues.get(task_name, deque([], 1)).copy(),
        task_name=task_name,
        proc=state.processes.get(task_name, None),
        known=task_name in state.task_files,
    )


@app.route("/tasklog/<task_name>.json")
@auth.user_required
def app_task_log_json(task_name):
    task_log = list(state.task_log_queues.get(task_name, deque([], 1)))
    return jsonify(task_log)


@app.route("/tasklog/<task_name>.txt")
@auth.user_required
def app_task_log_txt(task_name):
    result = "\n".join(["\t".join(line) for line in list(state.task_log_queues.get(task_name, deque([], 1)))])
    return Response(result, mimetype="text/plain")


@app.route("/taskinfo/<task_name>")
@auth.user_required
def app_task_info(task_name):
    task = state.task_files.get(task_name, None)
    if task is not None:
        task_info = task.info if task.info else "*No info provided.*"
    else:
        task_info = "*Task not found.*"
    task_info = markdown(task_info)
    return render_template("taskinfo.html", task_name=task_name, task_info=task_info)


@app.route("/reload/<task_name>")
@auth.user_required
def app_reload(task_name):
    log("Reload " + task_name)
    state.task_files.pop(task_name)
    state.schedules.pop(task_name, None)
    return redirect("/tasks")


@app.route("/clean/tasklogs")
@auth.admin_required
def app_clean_task_logs():
    state.task_log_queues = {}
    return render_template("manage.html", current="manage", message="All tasklogs cleared.", infos=fetch_infos())


@app.route("/shutdown")
@auth.admin_required
def app_shutdown():
    shutdown()
    return render_template("manage.html", current="manage", message="All tasks and schedules stopped.", infos={})


@app.after_request
def kill_self(response):
    if request.path == "/shutdown":
        log("Shutdown.")
        time.sleep(1)
        pid = os.getpid()
        if os.name == "nt":
            os.kill(pid, signal.CTRL_BREAK_EVENT)  # pylint: disable=no-member
        else:
            os.kill(pid, signal.SIGKILL)

    return response


def shutdown():
    log("Shutting down suvi tasks and schedules")
    state.cycle_wait = 1000000
    state.continue_threads = False
    if state.thread_main:
        state.thread_main.join(0.5)
    if state.thread_schedule:
        state.thread_schedule.join(0.5)
    for task_name in state.task_files:
        remove(task_name)
    state.task_files.clear()
    log("All tasks and schedules stopped.")


@app.route("/telemetry.json")
@auth.user_required
def telemetry_json():
    time_1 = datetime.now() - timedelta(minutes=1)
    time_5 = datetime.now() - timedelta(minutes=5)
    time_15 = datetime.now() - timedelta(minutes=15)

    telemetry_1 = Counter()
    telemetry_5 = Counter()
    telemetry_15 = Counter()

    for telemetry_item in state.telemetry_data.copy():
        item_time, item_value = telemetry_item

        if item_time > time_1:
            telemetry_1[item_value] += 1
            telemetry_5[item_value] += 1
            telemetry_15[item_value] += 1
        elif item_time > time_5:
            telemetry_5[item_value] += 1
            telemetry_15[item_value] += 1
        elif item_time > time_15:
            telemetry_15[item_value] += 1

    return jsonify(
        {
            "version": __version__,
            "startup": int(state.startup.timestamp()),
            "now": int(datetime.now().timestamp()),
            "continue": state.continue_threads,
            "processes": len(state.processes),
            "tasks": len(state.task_files),
            "schedules": len(state.schedules),
            "telemetry_1": telemetry_1,
            "telemetry_5": telemetry_5,
            "telemetry_15": telemetry_15,
        }
    )


def add_file_log_handler(logger_to_add_handler: logging.Logger, format_string: str):
    logging_formatter = logging.Formatter(format_string)
    file_handler = TimedRotatingFileHandler(
        os.path.join(str(state.logging_handler_path), f"{logger_to_add_handler.name}.log"),
        when=str(state.logging_handler_rotate_when),
        interval=int(str(state.logging_handler_rotate_interval)),
        backupCount=int(str(state.logging_handler_backup_count)),
    )
    file_handler.setFormatter(logging_formatter)
    logger_to_add_handler.setLevel(logging.INFO)
    logger_to_add_handler.addHandler(file_handler)


# For routes /tasks...
def create_task_lists() -> Dict[str, Any]:
    keepalive = {task_name: task for task_name, task in state.task_files.items() if task.type == TaskType.KEEPALIVE}
    for task_name, task in keepalive.items():
        task.runtime["active"] = task_name in state.processes

    ondemand = {task_name: task for task_name, task in state.task_files.items() if task.type == TaskType.ONDEMAND}

    schedules_copy = state.schedules.copy()

    return {"keepalive": keepalive, "ondemand": ondemand, "schedules": schedules_copy}


def runner():
    def trunate_telemetry_data():

        while state.continue_threads:
            time.sleep(30)
            min_time = datetime.now() - timedelta(minutes=16)
            log(f"Truncating telemetry data before {min_time}.")
            new_data = state.telemetry_data.copy()
            try:
                for telemetry_item in state.telemetry_data:
                    item_time, _ = telemetry_item
                    if item_time < min_time:
                        new_data.remove(telemetry_item)
            except Exception as ex:
                log(f"Telemetry truncation: {type(ex).__name__} ({ex.args})", is_error=True)
            state.telemetry_data = new_data

    thread_trunate_telemetry_data = threading.Thread(name="trunate_telemetry_data", target=trunate_telemetry_data, args=())
    thread_trunate_telemetry_data.start()

    def run_keepalives():
        time.sleep(1)
        log(f"Watching {state.tasks_path} ({os.path.abspath(state.tasks_path)}) for changes every {state.cycle_wait} seconds.")
        iteration = 0
        while state.continue_threads:
            telemetry("cycle")
            log(f"Checking for task file updates, iteration {iteration}")
            new_listing = dict([(Path(f).stem, None) for f in os.listdir(state.tasks_path) if f.endswith(".json") and f != "suvi.json"])
            removed = [f for f in state.task_files if not f in new_listing]
            added = [f for f in new_listing if not f in state.task_files]
            for task_name in removed:
                task_name = Path(task_name).stem
                telemetry("task-removed")
                log(f"{task_name} removed.")
                state.task_files.pop(task_name)
                state.task_log_queues.pop(task_name, "")
                state.schedules.pop(task_name, None)
                kill(task_name)
            for task_name in added:
                task_name = Path(task_name).stem
                telemetry("task-added")
                log(f"{task_name} added.")
                load_task(task_name)
            iteration += 1
            time.sleep(state.cycle_wait)
        log("Discontinue job runner thread.")

    state.thread_main = threading.Thread(name="run_keepalives", target=run_keepalives, args=())
    state.thread_main.start()

    def run_schedules():
        last_schedule_cycle = datetime.now() - timedelta(minutes=2)
        while state.continue_threads:
            time.sleep(5)
            now = datetime.now()
            if now.minute != last_schedule_cycle.minute:
                last_schedule_cycle = now
                log("Checking for scheduled events.")
                schedules_copy = state.schedules.copy()
                for task_name, task in schedules_copy.items():
                    if task.schedule_matches(now):
                        if task_name in state.processes:
                            log(
                                f"Cannot run scheduled task {task_name} since it is already running.",
                                is_error=True,
                            )
                        else:
                            try:
                                task: Task = state.task_files[task_name]
                                exec_part = "start" if task.exec in [TaskExec.SYSTEM, TaskExec.SHELL] else task.exec.value
                                telemetry(f"task-scheduled-{exec_part}-{task_name}")
                                telemetry(f"scheduled-{exec_part}")
                                log(f"Running scheduled {task.exec.value} task {task_name}")
                                exec_task(task_name, task)

                            except KeyError:
                                log(f"Task {task_name} vanished.", is_error=True)
                            except Exception as ex:
                                log(
                                    f"{task_name}: {type(ex).__name__} ({ex.args})",
                                    is_error=True,
                                )
        log("Discontinue schedules thread.")

    thread_schedule = threading.Thread(name="run_schedules", target=run_schedules, args=())
    thread_schedule.start()


def kill(task_name: str):
    proc = state.processes.pop(task_name, None)
    if proc:
        log(f"Killing process {task_name} with pid " + str(proc.pid))
        try:
            parent = psutil.Process(proc.pid)
            children = parent.children(recursive=True)
            for child in children:
                log(f"Killing child process for {task_name} with pid " + str(child.pid))
                child.kill()
        except psutil.NoSuchProcess:
            ...
        proc.kill()


def load_task(task_name: str):
    if not os.path.exists(f"{state.tasks_path}/{task_name}.json"):
        log(f"{task_name} vanished. Ignoring.", is_error=True)
        return None

    new_task = None
    try:
        with warnings.catch_warnings(record=True) as caught_warnings:
            new_task = Task(f"{state.tasks_path}/{task_name}.json")
            for warning in caught_warnings:
                if warning.category == ParseWarning:
                    log(f"{task_name}: {warning.message}", is_error=True)
    except ParseError as pe:
        log(f"{task_name}: { type(pe).__name__} ({pe.args})", is_error=True)

    if not new_task:
        log(f"{task_name}: Loading impossible.", is_error=False)
        return

    state.task_files.update({task_name: new_task})

    log(f"Loaded process {task_name} with type {new_task.type.value}.")
    if new_task.type == TaskType.KEEPALIVE:
        telemetry(f"task-keepalive-start-{task_name}")
        telemetry("keepalive-start")
        exec_task(task_name, new_task)
    elif new_task.type == TaskType.SCHEDULE:
        state.schedules.update({task_name: new_task})


def exec_task(task_name: str, task: Task, send_to_stdin: Optional[bytes] = None):
    def run_in_thread(task_name, args, env, cwd: str, shell: bool = False):
        task_logger = logging.getLogger(task_name)

        def task_log(pipe, level):
            queue_level = "error" if level == logging.ERROR else "info"
            try:
                for line in iter(pipe.readline, b""):
                    line_text = ""
                    try:
                        line_text = line.decode("UTF-8", errors="replace").strip()
                    except Exception as ex:
                        line_text = str(ex)
                    task_logger.log(level, line_text)
                    state.task_log_queues.setdefault(task_logger.name, deque([], 1000)).append(
                        (
                            task_logger.name,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            queue_level,
                            line_text,
                        )
                    )
            finally:
                ...

            return

        if not task_logger.handlers:
            add_file_log_handler(
                logger_to_add_handler=task_logger,
                format_string="%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s",
            )

        try:
            if not isinstance(args[0], list):
                args = [args]

            exec_uuid = uuid4().hex

            sub_proc_no = 0
            for sub_args in args:
                sub_proc_no += 1
                proc = subprocess.Popen(
                    args=sub_args,
                    env={
                        "SUVI_TASK_NAME": task_name,
                        "SUVI_EXEC_UUID": exec_uuid,
                        **env,
                    },
                    cwd=cwd,
                    shell=shell,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=(subprocess.PIPE if sub_proc_no == 1 and send_to_stdin else None),
                )
                state.processes.update({task_name: proc})
                log(
                    (
                        f"Started process #{sub_proc_no} of {len(args)} with PID {proc.pid}"
                        f"for {task_name} ({exec_uuid}){' in shell' if shell else ''}."
                    )
                )

                thread_task_stdout = threading.Thread(
                    name=f"task_{task_name}_stdout",
                    target=task_log,
                    args=[proc.stdout, logging.INFO],
                )
                thread_task_stderr = threading.Thread(
                    name=f"task_{task_name}_stderr",
                    target=task_log,
                    args=[proc.stderr, logging.ERROR],
                )
                thread_task_stdout.start()
                thread_task_stderr.start()

                if sub_proc_no == 1 and send_to_stdin:
                    log(
                        (
                            f"Sending stdin text with {len(send_to_stdin)} bytes to"
                            f"#{sub_proc_no} of {len(args)} with PID {proc.pid} for {task_name}."
                        )
                    )
                    proc.communicate(input=send_to_stdin)

                proc.wait()
                thread_task_stdout.join()
                thread_task_stderr.join()

                msg = f"-------------- Process {sub_proc_no} of {len(args)} closed with return code {proc.returncode} --------------"
                task_logger.log(
                    msg=msg,
                    level=logging.INFO if proc.returncode == 0 else logging.ERROR,
                )
                state.task_log_queues.setdefault(task_logger.name, deque([], 1000)).append(
                    (
                        task_logger.name,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "info" if proc.returncode == 0 else "error",
                        msg,
                    )
                )

                if (sub_proc_no < len(args)) and (proc.returncode != 0):
                    log(f"Breaking after {sub_proc_no} of {len(args)} for {task_name}.")
                    break

            proc = state.processes.pop(task_name, None)
            if proc:
                telemetry(f'task-{"end" if proc.returncode == 0 else "error"}-{task_name}')
                log(
                    f"The process {proc.pid} for {task_name} terminated with returncode {proc.returncode}",
                    (True if proc.returncode != 0 else False),
                )
                state.task_files.pop(task_name, None)
                state.schedules.pop(task_name, None)

        except FileNotFoundError as e:
            log(f"{task_name}: {e.strerror}: '{e.filename}'", is_error=True)
            proc = state.task_files.pop(task_name, None)
        except OSError as e:
            log(f"{task_name}: {e.strerror}", is_error=True)
            proc = state.task_files.pop(task_name, None)
        finally:
            if task_logger.handlers:
                for handler in task_logger.handlers:
                    task_logger.removeHandler(handler)

    if task.exec in [TaskExec.SYSTEM, TaskExec.SHELL]:
        thread = threading.Thread(
            name=f"task_{task_name}",
            target=run_in_thread,
            args=(
                task_name,
                task.args,
                {**os.environ.copy(), **task.env},
                task.cwd,
                task.exec == TaskExec.SHELL,
            ),
        )
        thread.start()
        return thread
    elif task.exec == TaskExec.TALEND:
        try:
            log(f"Using talend package location {task.package} for task {task_name}")

            path = os.path.join(
                task.cwd if task.cwd else tempfile.gettempdir(),
                task_name,
                task.package_md5,
            )
            if not task.package:
                raise ValueError("No talend package specified.")

            if not os.path.isdir(path):
                with ZipFile(task.package, "r") as zip_file:
                    log(f"Extracting package {task.package} for task {task_name} to {path}")
                    zip_file.extractall(path=path)

            task.runtime["talend"] = load_properties_file(os.path.join(path, "jobInfo.properties"))
            state.task_files.update({task_name: task})

            log(
                (
                    f"Talend task '{task_name}' contains package '{task.runtime['talend']['job']}', "
                    f"version '{task.runtime['talend']['jobVersion']}' build on "
                    f"'{task.runtime['talend']['date']}' with default context '{task.runtime['talend']['contextName']}'"
                )
            )

            java_platform_delimiter = ";" if os.name == "nt" else ":"

            args = [
                task.java_exec,
                "-cp",
                f"../lib/*{java_platform_delimiter}*{java_platform_delimiter}",
                (
                    f"{task.runtime['talend']['project'].lower()}.{task.runtime['talend']['job'].lower()}"
                    f"_{task.runtime['talend']['jobVersion'].replace('.', '_')}.{task.runtime['talend']['job']}"
                ),
            ] + task.args
            thread = threading.Thread(
                name=f"task_{task_name}",
                target=run_in_thread,
                args=(
                    task_name,
                    args,
                    {**os.environ.copy(), **task.env},
                    os.path.join(path, task.runtime["talend"]["job"].lower()),
                ),
            )
            thread.start()
            return thread
        except Exception as ex:
            log(
                f"{task_name}: {type(ex).__name__} ({ex.args})",
                is_error=True,
            )
            return None
    elif task.exec == TaskExec.STOP:
        for arg in task.args:
            stop_task(arg)


def log(text: str, is_error: bool = False):
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    level = "error" if is_error else "info"
    user = auth.current_user()  # type: ignore
    if is_error:
        telemetry("error")
        logger.error(text, extra={"user": user})
    else:
        logger.info(text, extra={"user": user})

    state.loq_queue.append((dt, user, level, text))


def telemetry(event_name: str):
    state.telemetry_data.append((datetime.now(), event_name))


def load_properties_file(fname: str):
    result = {}
    with open(fname, "r", encoding="utf-8") as f:
        for line in f.readlines():
            if not (line.strip().startswith("#") or (line.strip().find("=") == -1)):
                k, v = line.split(sep="=", maxsplit=1)
                result[k.strip()] = v.strip()
    return result


@cmd.command()
def main(
    bind: str = typer.Option(config["bind"], envvar="SUVI_BIND"),
    port: int = typer.Option(config["port"], envvar="SUVI_PORT"),
    enforce: bool = typer.Option(config["enforce"], envvar="SUVI_ENFORCE"),
    admin_login: str = typer.Option(config["admin_login"], envvar="SUVI_ADMIN_LOGIN"),
    admin_password: Union[str, None] = typer.Option(config["admin_password"], envvar="SUVI_ADMIN_PASSWORD"),
    user_login: str = typer.Option(config["user_login"], envvar="SUVI_USER_LOGIN"),
    user_password: Union[str, None] = typer.Option(config["user_password"], envvar="SUVI_USER_PASSWORD"),
    tasks: str = typer.Option(config["tasks"], envvar="SUVI_TASKS"),
    cycle: int = typer.Option(config["cycle"], envvar="SUVI_CYCLE"),
    logs: str = typer.Option(config["logs"], envvar="SUVI_LOGS"),
    log_rotate_when: str = typer.Option(config["log_rotate_when"], envvar="SUVI_LOG_ROTATE_WHEN"),
    log_rotate_interval: int = typer.Option(config["log_rotate_interval"], envvar="SUVI_LOG_ROTATE_INTERVAL"),
    log_backup_count: int = typer.Option(config["log_backup_count"], envvar="SUVI_LOG_BACKUP_COUNT"),
):
    for d in [tasks, logs]:
        if not os.path.isdir(d):
            print(f'Directory "{d}" missing. Trying to create it.')
            os.makedirs(d, exist_ok=True)

    state.logging_handler_path = logs
    state.logging_handler_rotate_when = log_rotate_when
    state.logging_handler_rotate_interval = log_rotate_interval
    state.logging_handler_backup_count = log_backup_count
    state.tasks_path = tasks
    state.cycle_wait = cycle

    auth.enforce = enforce
    if enforce:
        if not (admin_login and admin_password and user_login and user_password):
            raise ValueError("Cannot have empty admin/user credentials with enforce on.")

        def login_callback(username, success):
            if not success:
                log(f"Login for user {username} failed", is_error=True)

        auth.admins = {admin_login: admin_password}
        auth.users = {user_login: user_password}
        auth.login_callback = login_callback

    logging_format_string = "%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s"
    logging.basicConfig(format=logging_format_string)
    add_file_log_handler(logger, logging_format_string)

    log(f"Starting suvi {__version__}; {__about__}")
    runner()
    log(f"Listen at http://{bind}:{port}")

    def frontend_thread_target():
        serve(app, host=bind, port=port)

    frontend_thread = threading.Thread(
        name="frontend",
        target=frontend_thread_target,
    )
    frontend_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("Console shutdown.")
        shutdown()
        time.sleep(5)
        pid = os.getpid()
        if os.name == "nt":
            os.kill(pid, signal.CTRL_BREAK_EVENT)  # pylint: disable=no-member
        else:
            os.kill(pid, signal.SIGKILL)

        sys.exit(0)


def flatten(coll):
    for i in coll:
        if isinstance(i, list):
            for subc in flatten(i):
                yield subc
        else:
            yield i


if __name__ == "__main__":
    cmd()
