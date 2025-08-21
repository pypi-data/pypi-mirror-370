import threading
from collections import deque
from datetime import datetime

from suvi.task import Task


class AppState:
    def __init__(self):
        self.continue_threads = True
        self.cycle_wait = 60
        self.logging_handler_backup_count = 5
        self.logging_handler_path = "./log"
        self.logging_handler_rotate_interval = 1
        self.logging_handler_rotate_when = "midnight"
        self.loq_queue = deque([], 1000)
        self.processes = {}
        self.schedules: dict[str, Task] = {}
        self.startup = datetime.now()
        self.task_files: dict[str, Task] = {}
        self.task_log_queues = {}
        self.tasks_path = ""
        self.telemetry_data = []
        self.thread_main: threading.Thread | None = None
        self.thread_schedule: threading.Thread | None = None
