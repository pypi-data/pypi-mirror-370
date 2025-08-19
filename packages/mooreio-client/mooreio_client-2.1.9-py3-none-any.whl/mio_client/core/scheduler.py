# Copyright 2020-2025 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
import importlib
import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from datetime import datetime
from semantic_version import Version
import atexit
import signal


class Job:
    def __init__(self, rmh: 'RootManager', wd: Path, name: str, binary: Path, arguments: List[str]):
        self._rmh: 'RootManager' = rmh
        self._wd: Path = wd
        self._name: str = name
        self._pre_arguments: List[str] = []
        self._binary: Path = binary
        self._arguments: List[str] = arguments
        self._env_vars:dict = {}
        self._pre_path:str = ""
        self._post_path:str = ""
        self._print_to_screen:bool = False
        self._hostname:str = ""
        self._dry_run:bool = False
        self._is_part_of_set:bool = False
        self._parent_set:'JobSet' = None

    def __str__(self):
        string: str = f"{self._binary.name}"
        for arg in self.arguments:
            string += f" {arg}"
        return string

    @property
    def wd(self) -> Path:
        return self._wd
    
    @property
    def name(self) -> str:
        return self._name

    @property
    def binary(self) -> Path:
        return self._binary

    @property
    def env_vars(self) -> dict:
        return self._env_vars
    @env_vars.setter
    def env_vars(self, value: dict):
        self._env_vars = value

    @property
    def pre_path(self) -> str:
        return self._pre_path
    @pre_path.setter
    def pre_path(self, value: str):
        self._pre_path = value

    @property
    def post_path(self) -> str:
        return self._post_path
    @post_path.setter
    def post_path(self, value: str):
        self._post_path = value

    @property
    def print_to_screen(self) -> bool:
        return self._print_to_screen
    @print_to_screen.setter
    def print_to_screen(self, value: bool):
        self._print_to_screen = value

    @property
    def pre_arguments(self) -> List[str]:
        return self._pre_arguments
    @pre_arguments.setter
    def pre_arguments(self, value: List[str]):
        self._pre_arguments = value
    
    @property
    def arguments(self) -> List[str]:
        return self._arguments
        
    @property
    def hostname(self) -> str:
        return self._hostname
    @hostname.setter
    def hostname(self, value:str):
        self._hostname = value

    @property
    def dry_run(self) -> bool:
        return self._dry_run
    @dry_run.setter
    def dry_run(self, value: bool):
        self._dry_run = value

    @property
    def is_part_of_set(self) -> bool:
        return self._is_part_of_set

    @property
    def parent_set(self) -> 'JobSet':
        return self._parent_set
    @parent_set.setter
    def parent_set(self, value:'JobSet'):
        if value is not None:
            self._is_part_of_set = True
        self._parent_set = value

    def write_to_file(self, file_path: Path):
        with file_path.open('w') as file:
            file.write(str(self))
    

class JobSet:
    def __init__(self, rmh: 'RootManager', name: str):
        self._rmh:'RootManager' = rmh
        self._name: str = name
        self._tasks: List[Job] = []

    @property
    def rmh(self) -> 'RootManager':
        return self._rmh

    @property
    def name(self) -> str:
        return self._name

    def add_task(self, task: Job):
        task.parent_set = self
        self._tasks.append(task)


class JobSchedulerConfiguration:
    def __init__(self, rmh: 'RootManager'):
        self._output_to_terminal: bool = True
        self._max_number_of_parallel_processes :int = 1
        self._dry_run: bool  = False
        self._has_job_set: bool = False
        self._job_set: JobSet
        self._timeout: float = 60
        self._kill_job_on_termination = True

    @property
    def output_to_terminal(self) -> bool:
        return self._output_to_terminal
    @output_to_terminal.setter
    def output_to_terminal(self, value: bool):
        self._output_to_terminal = value

    @property
    def max_number_of_parallel_processes(self) -> int:
        return self._max_number_of_parallel_processes
    @max_number_of_parallel_processes.setter
    def max_number_of_parallel_processes(self, value: int):
        self._max_number_of_parallel_processes = value

    @property
    def dry_run(self) -> bool:
        return self._dry_run
    @dry_run.setter
    def dry_run(self, value: bool):
        self._dry_run = value

    @property
    def timeout(self) -> float:
        return self._timeout
    @timeout.setter
    def timeout(self, value: float):
        self._timeout = value

    @property
    def has_job_set(self) -> bool:
        return self._has_job_set

    @property
    def job_set(self) -> 'JobSet':
        return self._job_set
    @job_set.setter
    def job_set(self, value:'JobSet'):
        if value is not None:
            self._has_job_set = True
        self._job_set = value

    @property
    def kill_job_on_termination(self) -> bool:
        return self._kill_job_on_termination
    @kill_job_on_termination.setter
    def kill_job_on_termination(self, value: bool):
        self._kill_job_on_termination = value



class JobResults:
    _return_code: int = 0
    _stdout: str = ""
    _stderr: str = ""
    _timestamp_start: datetime = None
    _timestamp_end: datetime = None

    @property
    def return_code(self) -> int:
        return self._return_code

    @return_code.setter
    def return_code(self, value: int):
        self._return_code = value

    @property
    def stdout(self) -> str:
        return self._stdout

    @stdout.setter
    def stdout(self, value: str):
        self._stdout = value

    @property
    def stderr(self) -> str:
        return self._stderr

    @stderr.setter
    def stderr(self, value: str):
        self._stderr = value

    @property
    def timestamp_start(self) -> datetime:
        return self._timestamp_start

    @timestamp_start.setter
    def timestamp_start(self, value: datetime):
        self._timestamp_start = value

    @property
    def timestamp_end(self) -> datetime:
        return self._timestamp_end

    @timestamp_end.setter
    def timestamp_end(self, value: datetime):
        self._timestamp_end = value


class JobScheduler(ABC):
    _is_scheduler:bool = True
    def __init__(self, rmh: 'RootManager', name: str=""):
        self._rmh = rmh
        self._name = name
        self._version = None
        self._db = None
        self._jobs_dispatched: List[Job] = []
        self._jobs_in_progress: List[Job] = []
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        atexit.register(self.cleanup)

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> Version:
        return self._version

    @property
    def db(self) -> 'JobSchedulerDatabase':
        return self._db
    @db.setter
    def db(self, value: 'JobSchedulerDatabase'):
        self._db = value

    @property
    def rmh(self) -> 'RootManager':
        return self._rmh
    @rmh.setter
    def rmh(self, value: 'RootManager'):
        self._rmh = value

    @property
    def jobs_dispatched(self) -> List[Job]:
        return self._jobs_dispatched

    @property
    def jobs_in_progress(self) -> List[Job]:
        return self._jobs_in_progress

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    def dispatch_job(self, job: Job, configuration: JobSchedulerConfiguration) -> JobResults:
        self.jobs_dispatched.append(job)
        if not configuration.dry_run:
            self.jobs_in_progress.append(job)
            self.rmh.debug(f"Dispatching job '{job}'")
        results: JobResults = self.do_dispatch_job(job, configuration)
        if not configuration.dry_run:
            self.jobs_in_progress.remove(job)
            self.rmh.debug(f"Finished job '{job}' with return code '{results.return_code}'")
        return results

    def dispatch_job_set(self, job_set: JobSet, configuration: JobSchedulerConfiguration):
        return self.do_dispatch_job_set(job_set, configuration)

    @abstractmethod
    def do_dispatch_job(self, job: Job, configuration: JobSchedulerConfiguration) -> JobResults:
        pass

    @abstractmethod
    def do_dispatch_job_set(self, job_set: JobSet, configuration: JobSchedulerConfiguration):
        pass

    def _handle_signal(self, signum, frame):
        print(f"Received signal {signum}. Terminating subprocess...")
        self.cleanup()
        #raise SystemExit(0)


class JobSchedulerDatabase:
    def __init__(self, rmh: 'RootManager'):
        self._rmh = rmh
        self._task_schedulers: list[JobScheduler] = []

    @property
    def rmh(self) -> 'RootManager':
        return self._rmh
    
    def discover_schedulers(self):
        scheduler_directory = os.path.join(os.path.dirname(__file__), '..', 'schedulers')
        for filename in os.listdir(scheduler_directory):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = f'.schedulers.{filename[:-3]}'
                try:
                    module = importlib.import_module(module_name, 'mio_client')
                    new_schedulers = module.get_schedulers()
                    for scheduler in new_schedulers:
                        try:
                            scheduler_instance = scheduler(self._rmh)
                            self.add_scheduler(scheduler_instance)
                        except Exception as e:
                            print(f"Scheduler '{scheduler}' has errors and is not being loaded: {e}", file=sys.stderr)
                except Exception as e:
                    print(f"Scheduler module '{module_name}' has errors and is not being loaded: {e}", file=sys.stderr)
                    continue

    def add_scheduler(self, job_scheduler: 'JobScheduler'):
        self.rmh.debug(f"Added scheduler '{job_scheduler}'")
        job_scheduler.db = self
        if job_scheduler.is_available():
            self._task_schedulers.append(job_scheduler)
            job_scheduler.init()

    def find_scheduler(self, name: str) -> 'JobScheduler':
        for task_scheduler in self._task_schedulers:
            if task_scheduler.name == name:
                return task_scheduler
        raise Exception(f"No Job Scheduler '{name}' exists in the Job Scheduler Database")

    def get_default_scheduler(self) -> 'JobScheduler':
        # TODO Add support for other schedulers
        return self.find_scheduler("sub_process")