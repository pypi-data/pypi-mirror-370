# Copyright (C) 2025  CEA, EDF
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# See http://www.salome-platform.org/ or email : webmaster.salome@opencascade.com
#
"""
This script manages the execution of a command.
It is meant to be run on the remote server side.
This script should avoid the utilisation of non standard python modules for
better compatibility, because pybatch is not necessary installed on the remote
server.
"""

# No typing for better compatibility with older python versions.
# (edf gaia - python 3.5)
# mypy: ignore-errors
import argparse
import subprocess
import signal
import functools
import os
from pathlib import Path
import sys
import logging
import socket

global interrupted
interrupted = False

try:
    import psutil

    def process_exists(pid):
        return psutil.pid_exists(pid)

    def process_kill(pid):
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for p in children:
            try:
                p.terminate()
            except psutil.NoSuchProcess:
                pass
        parent.terminate()

except ModuleNotFoundError:
    # Implementation if psutil is not available on the server side.
    def process_exists(pid):
        proc_exists = True
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            proc_exists = False
        return proc_exists

    def process_kill(pid):
        os.kill(pid, signal.SIGTERM)


def handler(proc, signum, frame):
    proc.terminate()
    global interrupted
    interrupted = True


def run_one_job(workdir, command, wall_time, log_path, stdout_log, stderr_log):
    # file descriptors are automaticaly closed by default
    # (see close_fds argument of Popen).
    stdout_file = open(stdout_log, "w")  # python 3.5
    stderr_file = open(stderr_log, "w")  # python 3.5
    message = "Launch command: " + str(command)
    logging.info(message)
    proc = subprocess.Popen(
        command,
        stdout=stdout_file,
        stderr=stderr_file,
        cwd=workdir,
        creationflags=0,
    )
    signal.signal(signal.SIGTERM, functools.partial(handler, proc))
    try:
        exit_code = proc.wait(wall_time)
    except subprocess.TimeoutExpired:
        proc.terminate()
        logging.info("Timeout expired! Terminate child.")
        exit_code = proc.wait()
    exit_log = str(log_path / "exit_code.log")  # python 3.5
    with open(exit_log, "w") as exit_file:
        exit_file.write(str(exit_code))


def run_many_jobs(
    workdir,
    command,
    wall_time,
    log_path,
    stdout_log,
    stderr_log,
    total_jobs,
    max_simul_jobs,
):
    # TODO deal with max_simul_jobs
    global_exit_code = 0
    for idx in range(total_jobs):
        # file descriptors are automaticaly closed by default
        # (see close_fds argument of Popen).
        stdout_file = open(stdout_log, "a")  # python 3.5
        stderr_file = open(stderr_log, "a")  # python 3.5
        current_command = command + [str(idx)]
        message = "Launch command[{}]: {}"
        message = message.format(idx, current_command)
        logging.info(message)
        proc = subprocess.Popen(
            current_command, stdout=stdout_file, stderr=stderr_file, cwd=workdir
        )
        signal.signal(signal.SIGTERM, functools.partial(handler, proc))
        try:
            exit_code = proc.wait(wall_time)
        except subprocess.TimeoutExpired:
            proc.terminate()
            message = "Timeout expired! Terminate child[{}].".format(idx)
            logging.info(message)
            exit_code = proc.wait()
        if exit_code != 0:
            global_exit_code = exit_code
        global interrupted
        if interrupted:
            break
    exit_log = str(log_path / "exit_code.log")  # python 3.5
    with open(exit_log, "w") as exit_file:
        exit_file.write(str(global_exit_code))


def run(
    workdir,
    wall_time,
    total_jobs,
    max_simul_jobs,
    command,
):
    log_path = Path(workdir) / "logs"
    stdout_log = str(log_path / "output.log")
    stderr_log = str(log_path / "error.log")
    manager_log = str(log_path / "manager.log")
    if not wall_time:
        wall_time = None

    log = open(manager_log, "w")  # python 3.5
    # std redirection
    os.dup2(log.fileno(), sys.stdout.fileno())
    os.dup2(log.fileno(), sys.stderr.fileno())
    os.dup2(os.open(os.devnull, os.O_RDWR), sys.stdin.fileno())

    if total_jobs > 1:
        run_many_jobs(
            workdir,
            command,
            wall_time,
            log_path,
            stdout_log,
            stderr_log,
            total_jobs,
            max_simul_jobs,
        )
    else:
        run_one_job(
            workdir, command, wall_time, log_path, stdout_log, stderr_log
        )


def posix_submit(
    workdir,
    wall_time,
    total_jobs,
    max_simul_jobs,
    command,
):
    pid = os.fork()
    if pid > 0:
        # father side
        logging.info("Jobid " + str(pid))
        print(pid)
        return
    # child side
    os.setsid()
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    run(workdir, wall_time, total_jobs, max_simul_jobs, command)


def windows_submit(
    workdir,
    wall_time,
    total_jobs,
    max_simul_jobs,
    command,
):
    "Used for windows, when fork is not available."
    current_script = __file__
    py_exe = sys.executable
    if wall_time is None:
        wall_time = 0
    run_command = [
        py_exe,
        current_script,
        "run",
        workdir,
        str(wall_time),
        str(total_jobs),
        str(max_simul_jobs),
    ]
    run_command.extend(command)
    logging.info(str(run_command))
    stdout_file = open(
        str(Path(workdir) / "logs" / "submit_std.log"), "w"
    )  # python 3.5
    stderr_file = open(
        str(Path(workdir) / "logs" / "submit_err.log"), "w"
    )  # python 3.5
    proc = subprocess.Popen(
        run_command,
        cwd=workdir,
        stdout=stdout_file,
        stderr=stderr_file,
        # Windows specific flags.
        creationflags=subprocess.DETACHED_PROCESS
        | subprocess.CREATE_NEW_PROCESS_GROUP,
    )
    print(proc.pid)


def submit(workdir, command, wall_time, ntasks, total_jobs, max_simul_jobs):
    """Launch a command and return immediatly.

    The command is launched in workdir.
    The pid of the created process is printed on stdout.
    """
    message = (
        "submit workdir={}, command={}, walltime={}, ntasks={}, total_jobs={}"
    )
    message = message.format(workdir, command, wall_time, ntasks, total_jobs)
    logging.info(message)
    # check access to workdir before fork.
    log_path = Path(workdir) / "logs"
    log_path.mkdir(parents=True, exist_ok=True)
    stdout_log = log_path / "output.log"
    stderr_log = log_path / "error.log"
    manager_log = log_path / "manager.log"
    stdout_log.touch()
    stderr_log.touch()
    manager_log.touch()
    # generate batch_nodefile.txt
    if ntasks > 0:
        nodelist = (socket.gethostname() + "\n") * ntasks
        nodefile = Path(workdir) / "batch_nodefile.txt"
        nodefile.write_text(nodelist)

    # execute in detached mode
    if hasattr(os, "fork"):
        posix_submit(workdir, wall_time, total_jobs, max_simul_jobs, command)
    else:
        windows_submit(workdir, wall_time, total_jobs, max_simul_jobs, command)


def wait(proc_id):
    "Wait for the process to finish."
    logging.info("Wait jobid " + str(proc_id))
    import time

    while process_exists(proc_id):
        time.sleep(0.1)
    logging.info("Wait finished.")


def state(proc_id, workdir):
    """Print the state of the process.

    The work directory of the job is supposed to be the same as the directory
    of this script.
    """
    logging.info("state jobid " + str(proc_id))
    proc_exists = process_exists(proc_id)
    if proc_exists:
        logging.info("state RUNNING")
        print("RUNNING")
    else:
        exit_log = Path(workdir) / "logs" / "exit_code.log"
        if exit_log.is_file():
            exit_value = exit_log.read_text().strip()
            if exit_value == "0":
                logging.info("state FINISHED")
                print("FINISHED")
            else:
                logging.info("state FAILED")
                print("FAILED")
        else:
            logging.info("state FAILED")
            print("FAILED")


def cancel(proc_id):
    "Kill the process."
    logging.info("cancel jobid " + str(proc_id))
    try:
        process_kill(proc_id)
    except Exception:
        # TODO
        logging.info("cancel kill failed!")


def main(args_list=None):
    parser = argparse.ArgumentParser(description="Job manager for pybatch.")
    subparsers = parser.add_subparsers(
        dest="mode",  # required=True,#python>=3.7
        help="Use mode.",
    )

    # SUBMIT
    parser_submit = subparsers.add_parser(
        "submit", help="Start a job and print the pid."
    )
    parser_submit.add_argument("work_dir", help="Work directory.")
    parser_submit.add_argument(
        "--wall_time",
        type=int,
        default=None,
        help="Maximum execution time in seconds.",
    )
    parser_submit.add_argument(
        "--ntasks",
        type=int,
        default=0,
        help="If positive, generate batch_nodefile.txt.",
    )
    parser_submit.add_argument(
        "--total_jobs",
        type=int,
        default=1,
        help="Number of jobs to launch, 1 by default.",
    )
    parser_submit.add_argument(
        "--max_simul_jobs",
        type=int,
        default=1,
        help="For future use. Parameter ignored.",
    )
    parser_submit.add_argument("command", nargs="+", help="Command to submit.")

    # RUN
    parser_run = subparsers.add_parser("run", help="Run in background.")
    parser_run.add_argument("work_dir", help="Work directory.")
    parser_run.add_argument(
        "wall_time",
        type=int,
        help="Maximum execution time in seconds.",
    )
    parser_run.add_argument(
        "total_jobs",
        type=int,
        help="Number of jobs to launch.",
    )
    parser_run.add_argument(
        "max_simul_jobs",
        type=int,
        help="For future use. Parameter ignored.",
    )
    parser_run.add_argument("command", nargs="+", help="Command to submit.")

    # WAIT
    parser_wait = subparsers.add_parser(
        "wait", help="Wait for the end of a job."
    )
    parser_wait.add_argument("proc", type=int, help="Process id.")

    # STATE
    parser_state = subparsers.add_parser(
        "state", help="Print the state of a job."
    )
    parser_state.add_argument("proc", type=int, help="Process id.")
    parser_state.add_argument("work_dir", help="Work directory.")

    # CANCEL
    parser_cancel = subparsers.add_parser("cancel", help="Cancel a job.")
    parser_cancel.add_argument("proc", type=int, help="Process id.")

    args = parser.parse_args(args_list)
    if args.mode == "submit":
        submit(
            args.work_dir,
            args.command,
            args.wall_time,
            args.ntasks,
            args.total_jobs,
            args.max_simul_jobs,
        )
    elif args.mode == "wait":
        wait(args.proc)
    elif args.mode == "state":
        state(args.proc, args.work_dir)
    elif args.mode == "cancel":
        cancel(args.proc)
    elif args.mode == "run":
        run(
            args.work_dir,
            args.wall_time,
            args.total_jobs,
            args.max_simul_jobs,
            args.command,
        )
    else:
        print("No command defined!")


def log_config():
    workdir = os.path.dirname(sys.argv[0])
    log_file = os.path.join(workdir, "pybatch.log")
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format="%(asctime)s - %(message)s",
    )


if __name__ == "__main__":
    log_config()
    main()
