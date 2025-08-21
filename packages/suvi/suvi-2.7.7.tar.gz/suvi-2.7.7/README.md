- Distributed under [GNU General Public License Version 3](https://gitlab.ecmind.ch/open/suvi/-/raw/main/LICENSE).
- [Change log](https://gitlab.ecmind.ch/open/suvi/-/raw/main/CHANGELOG).
- This README.md is just boilerplate for the [wiki](https://gitlab.ecmind.ch/open/suvi/-/wikis/home).

## Parameters

`--bind`: The ip/interface where suvi listens at. [default: 0.0.0.0]
`--port`: The listening port. [default: 8080]
`--enforce` / `--no-enforce`: Require a basic auth login [default: no-enforce]
`--admin-login`: Username for the admin user [default: admin]
`--admin-password`: Password for the admin user
`--user-login`: Username for the standard user [default: user]
`--user-password`: Password for the standard user
`--tasks`: Where to look for task config files (`.json` files) [default: ./tasks]
`--cycle`: Update interval in seconds to look for new/deleted task config files [default: 10]
`--logs`: Directory where to store suvi and task log files. [default: ./log]
`--log-rotate-when`: When to rotate log files (`H` for hours, `D` for days or `midnight`) [default: midnight]
`--log-rotate-interval`: How many instances fo `when` have to pass before rotating the log file [default: 1]
`--log-backup-count`: How many file rollovers should be stored [default: 5]
`--help`: Show help message and exit.

### Using environment vars to configure suvi

Parameters can be set via environment vars, example:

```bash
#/bin/bash

PW1=$(pwmake 80)
PW2=$(pwmake 80)

echo Setting admin password to "$PW1" and user password to "$PW2".

SUVI_ENFORCE=True \
SUVI_ADMIN_LOGIN=admin \
SUVI_ADMIN_PASSWORD="$PW1" \
SUVI_USER_LOGIN=user \
SUVI_USER_PASSWORD="$PW2" \
suvi
```

### Using `suvi.toml` to configure suvi

Parameters can also be set by a `suvi.toml` file:

```toml
bind = "0.0.0.0"
port = 8080
enforce = true
admin_login = "admin"
admin_password = "RamesesII"
user_login = "user"
user_password = "TrustNo1"
tasks = "./tasks"
cycle = 5
logs = "./log"
log_rotate_when = "midnight"
log_rotate_interval = 1
log_backup_count = 5
```

The values of the configuration file are overwritten by console values. For windows service deployments, `suvi.toml` is expected at `%WINDIR%\system32`.

## Task config files (`.json`)

- `type`: Defines the startup strategy
  - `"type": "ondemand"`: Run the task on user interaction/get call.
  - `"type": "keepalive"`: Automatically start the task with suvi and restart if necessary.
  - `"type": "schedule"`: Automatically start the task with suvi and restart if necessary.
- `exec`: Defines how to start the task
  - `"exec": "system"`: Starts an external executable via `popen`
  - `"exec": "shell"`: Starts an external executable via `popen` in the current system shell.
    - The "`args`" list should be joined and instead just separated by spaces for the shell to interpret the command.
  - `"exec": "stop"`: Stops (= kill & reload) tasks by config file name i. e. on a schedule
    - Example: `{ "type": "schedule", "schedule": "* 0 * * *", "exec": "stop", "args": [ "has-to-restart-sometimes" ], "cwd": "/tmp" }`
    - `"args"` may contain one or more config files names without the json extension
  - `"exec": "talend"`: Deflates & starts a talend job build to a zip package
    - When using `"talend"` for `"exec"`, this additional config parameters exist:
      - `"package"`: Path to the talend build zip file.
      - `"java"`: Optional path to the java binary. When this path to the `java` binary is omitted, the system default will be used.
    - The `cwd` parameter is used as base path for deflated jobs. When `cmd` is omitted, the system default temp path is used instead.
    - Example: `{ "type": "keepalive", "exec": "talend", "package": "/jobs/talend-demo-job-with-subtask.zip", "args": ["--context=Test", "-Xms256M", "-Xmx1024M"], "cwd": "/tmp", "info": "deflate and keepalive talend demo job" }`
- `args`: Array of startup params or an array of arrays it multiple programs should be started if the previous job succeeded
  - `"args": ["notepad.exe", "test.txt"]`
  - `"args": [ ["notepad.exe", "test.txt"], ["calc.exe"] ]`
- `cwd`: Optional startup path for the task
  - `"cwd": "C:/temp"`
- `env`: Optional dictionary that extends/overwrites suvis environment variables
  - `"env": {"TAIL_FILE": "/tmp/test"}, "args": ["bash", "-c", "tail -f $TAIL_FILE"]`
- `schedule`: Read when `"type": "schedule"` is set to launch an instance of the task if not already running.
  - minutes, hours, days, month, weekdays
  - `"schedule": "0 */4 * * 1-3,5"`: Start every four hours Monday to Wednesday and Friday.
  - Minutes range from `0` to `59`
  - Hours range from `0` to `23`
  - Days range from `1` to `31`
  - Month range from `1` (Jan) to `12` (Dec)
  - Weekdays range from `1` (Mon) to `7` (Sun) including `0` (also Sun)
- `tokens`: Optional list of secret tokens to start a tasks without a password via HTTP GET or POST at `/run/hook/<token>`
  - Example: `"tokens": ["30d827f9-e22f-4b6a-85f1-bcb9977c6155", "69f541f8-614a-45f4-950b-67998c819ee0"]`
  - When POSTing to a webhook of `"exec": "system"`, the raw body gets redirected to STDIN of the (first) `"args"` command.
- `info`: Optional markdown text to provide task info.
  - Line breaks have to be encoded as `\n` in JSON.

## Environment variables of tasks

The environment variables for the runtime of a task consist of:

- `SUVI_TASK_NAME` set to the task name.
- `SUVI_EXEC_UUID` set to a unique uuid for each task execution. This uuid is unchanged between executions of subtasks (when `args` is a list is lists).
- Variables set by the OS
- Variables set by `env` task configuration.
