# Copyright 2020-2025 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
import re
import sys
from http import HTTPMethod
from pathlib import Path
from typing import List, Dict

import shutil
import jinja2
import requests
import toml
import yaml
from pydantic import ValidationError
import os
import getpass

from .command import Command
from .configuration import Configuration
from .ip import IpDataBase, IpLocationType
from .phase import Phase
from .scheduler import JobSchedulerDatabase
from .service import ServiceDataBase
from .user import User


#######################################################################################################################
# Support Types
#######################################################################################################################
class PhaseEndProcessException(Exception):
    def __init__(self, message: str = ""):
        self.message = message
    def __str__(self):
        return self.message
    @property
    def message(self) -> str:
        return self._message
    @message.setter
    def message(self, message: str):
        self._message = message


#######################################################################################################################
# Root Manager implementation
#######################################################################################################################
class RootManager:
    """
    Component which performs all vital tasks and executes phases.
    """
    def __init__(self, name: str, wd: Path, test_mode: bool = False, user_home_path:Path=os.path.expanduser("~/.mio")):
        """
        Initialize an instance of the Root Manager.

        :param name: The name of the instance.
        :param wd: The working directory for the instance.
        :param test_mode: Pytest mode
        :param user_home_path: Path to user home directory
        """
        self._name: str = name
        self._test_mode: bool = test_mode
        self._wd: Path = wd
        self._md: Path = self.wd / ".mio"
        self._temp_dir: Path = self.md / "temp"
        self._locally_installed_ip_dir: Path = self.md / "installed_ip"
        self._global_ip_local_copy_dir: Path = self.md / "global_ip"
        self._url_base: str = ""
        self._url_api: str = ""
        self._print_trace: bool = False
        self._command: Command = None
        self._install_path: Path = None
        self._data_files_path: Path = None
        self._user_home_path: Path = Path(user_home_path)
        self._user_data_file_path: Path = self.user_home_path / "user.yml"
        self._user: User = None
        self._project_root_path: Path = None
        self._default_configuration_path: Path = None
        self._user_configuration_path: Path = None
        self._project_configuration_path: Path = None
        self._default_configuration: Dict = {}
        self._user_configuration:Dict = {}
        self._project_configuration: Dict = {}
        self._cli_configuration: Dict = {}
        self._configuration: Configuration = None
        self._scheduler_database: JobSchedulerDatabase = None
        self._service_database: ServiceDataBase = None
        self._ip_database: IpDataBase = None
        self._j2_env: jinja2.Environment = None
        self._current_phase: Phase = None

    def __str__(self):
        """
        Returns a string representation of the object.
        :return: The name of the object as a string.
        """
        return self.name

    @property
    def name(self) -> str:
        """
        :return: The name of the Root. Read-only.
        :rtype: str
        """
        return self._name

    @property
    def test_mode(self) -> bool:
        return self._test_mode

    @property
    def wd(self) -> Path:
        """
        :return: Working directory.
        """
        return self._wd

    @property
    def md(self) -> Path:
        """
        :return: Moore.io work (hidden) directory.
        """
        return self._md

    @property
    def temp_dir(self) -> Path:
        return self._temp_dir

    @property
    def locally_installed_ip_dir(self) -> Path:
        return self._locally_installed_ip_dir

    @property
    def global_ip_local_copy_dir(self) -> Path:
        return self._global_ip_local_copy_dir

    @property
    def url_base(self) -> str:
        """
        :return: Moore.io Web Server URL.
        """
        return self._url_base

    @property
    def url_api(self) -> str:
        """
        :return: Moore.io Web Server API URL.
        """
        return self._url_api

    @property
    def user_home_path(self) -> Path:
        """
        :return: Path to user .mio directory
        """
        return self._user_home_path

    @property
    def print_trace(self) -> bool:
        """
        :return: Whether to print debug information
        """
        return self._print_trace
    @print_trace.setter
    def print_trace(self, value: bool):
        self._print_trace = value

    @property
    def command(self) -> Command:
        """
        :return: The command being executed.
        """
        return self._command

    @property
    def user(self) -> User:
        """
        :return: The User model.
        """
        return self._user

    @property
    def install_path(self) -> Path:
        return self._install_path

    @property
    def data_files_path(self) -> Path:
        return self._data_files_path

    @property
    def project_root_path(self) -> Path:
        """
        :return: The Project root path.
        """
        return self._project_root_path

    @property
    def default_configuration_path(self) -> Path:
        """
        :return: Path to default configuration file.
        """
        return self._default_configuration_path

    @property
    def user_configuration_path(self) -> Path:
        """
        :return: Path to User configuration file.
        """
        return self._user_configuration_path

    @property
    def project_configuration_path(self) -> Path:
        """
        :return: Path to Project configuration file.
        """
        return self._project_configuration_path

    @property
    def default_configuration(self) -> dict:
        """
        :return: The raw default configuration space.
        """
        return self._default_configuration

    @property
    def configuration(self) -> Configuration:
        """
        :return: The configuration space.
        """
        return self._configuration

    @property
    def scheduler_database(self) -> JobSchedulerDatabase:
        """
        :return: The task scheduler database.
        """
        return self._scheduler_database

    @property
    def service_database(self) -> ServiceDataBase:
        """
        :return: The Service database.
        """
        return self._service_database

    @property
    def ip_database(self) -> IpDataBase:
        """
        :return: The IP database.
        """
        return self._ip_database

    @property
    def j2_env(self) -> jinja2.Environment:
        return self._j2_env

    def info(self, message: str):
        print(f"\033[35m[MIO]\033[0m {message}")

    def debug(self, message: str):
        if self.print_trace:
            print(f"\033[32m[MIO-DBG] {message} \033[0m")

    def warning(self, message: str):
        print(f"\033[33m\033[1m[MIO-WARNING] {message} \033[0m")

    def error(self, message: str):
        print(f"\033[31m\033[4m[MIO-ERROR] {message} \033[0m")

    def fatal(self, message: str):
        print(f"\033[31m\033[4m[MIO-FATAL] {message} \033[0m")

    @property
    def current_phase(self) -> 'Phase':
        """
        :return: The current phase.
        """
        return self._current_phase
    
    def run(self, command: Command) -> int:
        if self.test_mode:
            try:
                self.run_sequence(command)
            except PhaseEndProcessException as e:
                if e.message != "":
                    self.fatal(e.message)
                return 0
            else:
                return 0
        else:
            try:
                self.run_sequence(command)
            except PhaseEndProcessException as e:
                if e.message != "":
                    self.fatal(e.message)
                return 0
            except Exception as e:
                self.fatal(str(e))
                return 1
            else:
                return 0

    def run_sequence(self, command: Command):
        """
        The `run` method is responsible for executing a series of phases to complete a command.

        :param command: The command to be executed.
        :return: None

        The `run` method starts by setting the provided command as the current command.
        Then it goes through the following steps in order:
        - phase_init
        - phase_load_default_configuration
        - phase_locate_project_file
        - phase_create_common_files_and_directories
        - phase_load_user_configuration
        - phase_load_project_configuration
        - phase_validate_configuration_space
        - phase_load_user_data
        - phase_authenticate
        - phase_save_user_data
        - phase_scheduler_discovery
        - phase_service_discovery
        - phase_ip_discovery
        - phase_main
        - phase_check
        - phase_report
        - phase_cleanup
        - phase_shutdown
        - phase_final
        """
        self.set_command(command)
        # 1. INIT
        init_phase:Phase = self.do_phase_init()
        if init_phase.end_process:
            return
        # 2. LOAD DEFAULT CONFIGURATION
        load_default_configuration_phase:Phase = self.do_phase_load_default_configuration()
        if load_default_configuration_phase.end_process:
            return
        # 3. LOCATE PROJECT FILE
        locate_project_file_phase:Phase = self.do_phase_locate_project_file()
        if locate_project_file_phase.end_process:
            return
        # 4. CREATE COMMON FILES AND DIRECTORIES
        create_common_files_and_directories_phase:Phase = self.do_phase_create_common_files_and_directories()
        if create_common_files_and_directories_phase.end_process:
            return
        # 5. LOAD PROJECT CONFIGURATION
        load_project_configuration_phase:Phase = self.do_phase_load_project_configuration()
        if load_project_configuration_phase.end_process:
            return
        # 6. LOAD USER CONFIGURATION
        load_user_configuration_phase:Phase = self.do_phase_load_user_configuration()
        if load_user_configuration_phase.end_process:
            return
        # 7. VALIDATE CONFIGURATION SPACE
        validate_configuration_space_phase:Phase = self.do_phase_validate_configuration_space()
        if validate_configuration_space_phase.end_process:
            return
        # 8. LOAD USER DATA
        load_user_data_phase:Phase = self.do_phase_load_user_data()
        if load_user_data_phase.end_process:
            return
        # 9. AUTHENTICATE
        authenticate_phase:Phase = self.do_phase_authenticate()
        if authenticate_phase.end_process:
            return
        # 10. SAVE USER DATA
        save_user_data_phase:Phase = self.do_phase_save_user_data()
        if save_user_data_phase.end_process:
            return
        # 11. SCHEDULER DISCOVERY
        scheduler_discovery_phase:Phase = self.do_phase_scheduler_discovery()
        if scheduler_discovery_phase.end_process:
            return
        # 12. SERVICE DISCOVERY
        service_discovery_phase:Phase = self.do_phase_service_discovery()
        if service_discovery_phase.end_process:
            return
        # 13. IP DISCOVERY
        if self.command.perform_ip_discovery:
            ip_discovery_phase:Phase = self.do_phase_ip_discovery()
            if ip_discovery_phase.end_process:
                return
        # 14. MAIN
        if self.command.executes_main_phase:
            main_phase:Phase = self.do_phase_main()
            if main_phase.end_process:
                return
        # 15. CHECK
        check_phase:Phase = self.do_phase_check()
        if check_phase.end_process:
            return
        # 16. REPORT
        report_phase:Phase = self.do_phase_report()
        if report_phase.end_process:
            return
        # 17. CLEANUP
        cleanup_phase:Phase = self.do_phase_cleanup()
        if cleanup_phase.end_process:
            return
        # 18. SHUTDOWN
        shutdown_phase:Phase = self.do_phase_shutdown()
        if shutdown_phase.end_process:
            return
        # 19. FINAL
        final_phase:Phase = self.do_phase_final()
        if final_phase.end_process:
            return
    
    def set_command(self, command: Command):
        """
        Sets the command for the root.
        :param command: the command to be set as the root command
        :return: None
        """
        #if not issubclass(type(command), Command):
        #    raise TypeError("command must extend from class 'Command'")
        self._command = command()
        command.rmh = self
    
    def create_phase(self, name: str):
        """
        Creates a new phase with the given name.
        :param name: A string representing the name of the phase.
        :return: A `Phase` object representing the newly created phase.
        """
        self._current_phase = Phase(self, name)
        self.debug(f"Starting phase '{name}': {self._current_phase.init_timestamp}")
        return self._current_phase
    
    def check_phase_finished(self, phase: Phase):
        """
        Check if a phase has finished properly.
        :param phase: The phase to be checked.
        :return: None.
        """
        if not phase.has_finished():
            if phase.error:
                raise RuntimeError(f"Phase '{phase}' has encountered an error: {phase.error}")
            else:
                raise RuntimeError(f"Phase '{phase}' has not finished properly")
        else:
            self.debug(f"Finished phase '{phase}': {phase.duration.total_seconds()} seconds")
        if phase.end_process and phase.error:
            raise PhaseEndProcessException(phase.end_process_message)
        elif phase.end_process and not phase.error:
            self.info(phase.end_process_message)
    
    def file_exists(self, path: Path) -> bool:
        """
        Check if a file exists at the specified path.
        :param path: Path to the file.
        :return: True if the file exists, False otherwise.
        :raises ValueError: if the path is None or empty.
        """
        if not path:
            raise ValueError("Path must not be None or empty")
        return os.path.isfile(path)
    
    def create_file(self, path: Path):
        """
        Create a file at the specified path.
        :param path: The path where the file should be created.
        :return: None
        """
        self.debug(f"Creating file at '{path}'")
        try:
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            with open(path, 'w') as file_handle:
                pass
        except OSError as e:
            print(f"An error occurred while creating file '{path}': {e}")

    def move_file(self, src: Path, dst: Path):
        """
        Move a file from src to dst.
        :param src: Path to the source file.
        :param dst: Path to the destination.
        """
        self.debug(f"Moving file from '{src}' to '{dst}'")
        try:
            if not os.path.exists(src):
                raise FileNotFoundError(f"Source file '{src}' does not exist")
            os.rename(src, dst)
        except OSError as e:
            print(f"An error occurred while moving file from '{src}' to '{dst}': {e}")

    def copy_file(self, src: Path, dst: Path):
        """
        Copy a file from src to dst.
        :param src: Path to the source file.
        :param dst: Path to the destination.
        """
        self.debug(f"Copying file from '{src}' to '{dst}'")
        try:
            if not os.path.exists(src):
                raise FileNotFoundError(f"Source file '{src}' does not exist")
            directory = os.path.dirname(dst)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            shutil.copy2(src, dst)
        except OSError as e:
            print(f"An error occurred while copying file from '{src}' to '{dst}': {e}")

    def remove_file(self, path: Path):
        """
        Remove a file at the specified path.
        :param path: Path to the file.
        """
        self.debug(f"Removing file at '{path}'")
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"File '{path}' does not exist")
            os.remove(path)
        except OSError as e:
            error = f"An error occurred while removing file '{path}': {e}"
            raise Exception(error)

    def directory_exists(self, path: Path):
        """
        Check if a directory exists at the specified path.
        :param path: Path to the directory.
        :return: True if the directory exists, False otherwise.
        :raises ValueError: if the path is None or empty.
        """
        if not path:
            raise ValueError("Path must not be None or empty")
        return os.path.isdir(path)

    def create_directory(self, path: Path):
        """
        Create a directory at the specified path.
        :param path: Path to the directory.
        """
        self.debug(f"Creating directory at '{path}'")
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError as e:
            print(f"An error occurred while creating directory '{path}': {e}")

    def move_directory(self, src: Path, dst: Path, force: bool = False):
        """
        Move a directory from src to dst.
        :param src: Path to the source directory.
        :param dst: Path to the destination.
        """
        self.debug(f"Moving directory from '{src}' to '{dst}'")
        try:
            if not os.path.exists(src):
                raise FileNotFoundError(f"Source directory '{src}' does not exist")
            if os.path.exists(dst):
                if force:
                    self.remove_directory(dst)
                else:
                    raise FileExistsError(f"Destination directory '{dst}' already exists")
            shutil.move(src, dst)
        except OSError as e:
            print(f"An error occurred while moving directory from '{src}' to '{dst}': {e}")

    def copy_directory(self, src: Path, dst: Path):
        """
        Copy a directory from src to dst.
        :param src: Path to the source directory.
        :param dst: Path to the destination.
        """
        self.debug(f"Copying directory from '{src}' to '{dst}'")
        try:
            if not os.path.exists(src):
                raise FileNotFoundError(f"Source directory '{src}' does not exist")
            directory = os.path.dirname(dst)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            shutil.copytree(src, dst)
        except OSError as e:
            print(f"An error occurred while copying directory from '{src}' to '{dst}': {e}")

    def remove_directory(self, path: Path):
        """
        Remove a directory at the specified path.
        :param path: Path to the directory.
        """
        self.debug(f"Removing directory at '{path}'")
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Directory '{path}' does not exist")
            shutil.rmtree(path)
        except OSError as e:
            print(f"An error occurred while removing directory '{path}': {e}")

    def search_file_for_patterns(self, file_path: Path, patterns: List[str]) -> List[str]:
        """
        Searches a file at file_path for regular expressions in patterns.
        :param file_path: Path to file being searched
        :param patterns: List of patterns to be found
        :return: List of found strings
        """
        try:
            with open(file_path, 'r') as file_searched:
                file_content = file_searched.read()
            matches = []
            for pattern_str in patterns:
                pattern = re.compile(pattern_str, re.MULTILINE)
                matches.extend(pattern.findall(file_content))
            return matches
        except OSError as e:
            print(f"An error occurred while searching file '{file_path}': {e}")
            return []

    def merge_dictionaries(self,d1: Dict, d2: Dict) -> Dict:
        """
        Merge two dictionaries, d2 will overwrite d1 where keys overlap
        """
        for key, value in d2.items():
            if key in d1 and isinstance(d1[key], Dict) and isinstance(value, Dict):
                d1[key] = self.merge_dictionaries(d1[key], value)
            else:
                d1[key] = value
        return d1

    def do_phase_init(self) -> Phase:
        """
        Perform any steps necessary before real work begins.
        :return: None
        """
        current_phase = self.create_phase('init')
        current_phase.next()
        self.phase_init(current_phase)
        self.command.do_phase_init(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        return current_phase

    def do_phase_load_default_configuration(self) -> Phase:
        """
        Load default configuration file from the package.
        :return: None
        """
        current_phase = self.create_phase('pre_load_default_configuration')
        current_phase.next()
        self.command.do_phase_pre_load_default_configuration(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('load_default_configuration')
        current_phase.next()
        self.phase_load_default_configuration(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('post_load_default_configuration')
        current_phase.next()
        self.command.do_phase_post_load_default_configuration(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        return current_phase

    def do_phase_locate_project_file(self) -> Phase:
        """
        Locate the project file (`mio.toml`).
        :return: None
        """
        current_phase = self.create_phase('pre_locate_project_file')
        current_phase.next()
        self.command.do_phase_pre_locate_project_file(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('locate_project_file')
        current_phase.next()
        self.phase_locate_project_file(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('post_locate_project_file')
        current_phase.next()
        self.command.do_phase_post_locate_project_file(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        return current_phase

    def do_phase_create_common_files_and_directories(self) -> Phase:
        """
        Create files and directories needed for proper Moore.io Client and command operation.
        :return: None
        """
        current_phase = self.create_phase('pre_create_common_files_and_directories')
        current_phase.next()
        self.command.do_phase_pre_create_common_files_and_directories(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('create_common_files_and_directories')
        current_phase.next()
        self.phase_create_common_files_and_directories(current_phase)
        self.command.do_phase_create_common_files_and_directories(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('post_create_common_files_and_directories')
        current_phase.next()
        self.command.do_phase_post_create_common_files_and_directories(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        return current_phase

    def do_phase_load_project_configuration(self) -> Phase:
        """
        Load project configuration space from disk.
        :return: None
        """
        current_phase = self.create_phase('pre_load_project_configuration')
        current_phase.next()
        self.command.do_phase_pre_load_project_configuration(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('load_project_configuration')
        current_phase.next()
        self.phase_load_project_configuration(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('post_load_project_configuration')
        current_phase.next()
        self.command.do_phase_post_load_project_configuration(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        return current_phase

    def do_phase_load_user_configuration(self) -> Phase:
        """
        Load user configuration space from disk.
        :return: None
        """
        current_phase = self.create_phase('pre_load_user_configuration')
        current_phase.next()
        self.command.do_phase_pre_load_user_configuration(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('load_user_configuration')
        current_phase.next()
        self.phase_load_user_configuration(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('post_load_user_configuration')
        current_phase.next()
        self.command.do_phase_post_load_user_configuration(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        return current_phase

    def do_phase_validate_configuration_space(self) -> Phase:
        """
        Merge & validate the configuration space.
        :return: None
        """
        current_phase = self.create_phase('pre_validate_configuration_space')
        current_phase.next()
        self.command.do_phase_pre_validate_configuration_space(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('validate_configuration_space')
        current_phase.next()
        self.phase_validate_configuration_space(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('post_validate_configuration_space')
        current_phase.next()
        self.command.do_phase_post_validate_configuration_space(current_phase)
        self.relocate_data_files(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        return current_phase

    def do_phase_load_user_data(self) -> Phase:
        """
        Load user data from disk.
        :return: None
        """
        current_phase = self.create_phase('pre_load_user_data')
        current_phase.next()
        self.command.do_phase_pre_load_user_data(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('load_user_data')
        current_phase.next()
        self.phase_load_user_data(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('post_load_user_data')
        current_phase.next()
        self.command.do_phase_post_load_user_data(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        return current_phase

    def do_phase_authenticate(self) -> Phase:
        """
        Authenticate the user with mio_web if necessary.
        :return: None
        """
        current_phase = self.create_phase('pre_authenticate')
        current_phase.next()
        self.command.do_phase_pre_authenticate(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('authenticate')
        current_phase.next()
        if self._command.needs_authentication():
            self.authenticate(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('post_authenticate')
        current_phase.next()
        self.command.do_phase_post_authenticate(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        return current_phase

    def do_phase_save_user_data(self) -> Phase:
        """
        Write user data to disk.
        :return: None
        """
        current_phase = self.create_phase('pre_save_user_data')
        current_phase.next()
        self.command.do_phase_pre_save_user_data(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('save_user_data')
        current_phase.next()
        self.phase_save_user_data(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('post_save_user_data')
        current_phase.next()
        self.command.do_phase_post_save_user_data(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        return current_phase

    def do_phase_scheduler_discovery(self) -> Phase:
        """
        Creates and registers task schedulers as described in configuration space.
        :return: None.
        """
        current_phase = self.create_phase('pre_scheduler_discovery')
        current_phase.next()
        self.command.do_phase_pre_scheduler_discovery(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('scheduler_discovery')
        current_phase.next()
        self.phase_scheduler_discovery(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('post_scheduler_discovery')
        current_phase.next()
        self.command.do_phase_post_scheduler_discovery(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        return current_phase

    def do_phase_service_discovery(self) -> Phase:
        """
        Creates and registers services as described in configuration space.
        :return: None.
        """
        current_phase = self.create_phase('pre_service_discovery')
        current_phase.next()
        self.command.do_phase_pre_service_discovery(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('service_discovery')
        current_phase.next()
        self.phase_service_discovery(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('post_service_discovery')
        current_phase.next()
        self.command.do_phase_post_service_discovery(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        return current_phase

    def do_phase_ip_discovery(self) -> Phase:
        """
        Finds and loads IP models in both local and global locations.
        :return: None
        """
        current_phase = self.create_phase('pre_ip_discovery')
        current_phase.next()
        self.command.do_phase_pre_ip_discovery(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('ip_discovery')
        current_phase.next()
        self.phase_ip_discovery(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('post_ip_discovery')
        current_phase.next()
        self.command.do_phase_post_ip_discovery(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        return current_phase

    def do_phase_main(self) -> Phase:
        """
        Execute the main task(s) of the command.
        :return: None
        """
        current_phase = self.create_phase('pre_main')
        current_phase.next()
        self.command.do_phase_pre_main(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('main')
        current_phase.next()
        self.command.do_phase_main(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('post_main')
        current_phase.next()
        self.command.do_phase_post_main(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        return current_phase

    def do_phase_check(self) -> Phase:
        """
        Check task(s) outputs for errors/warnings.
        :return: None
        """
        current_phase = self.create_phase('pre_check')
        current_phase.next()
        self.command.do_phase_pre_check(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('check')
        current_phase.next()
        self.phase_check(current_phase)
        self.command.do_phase_check(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('post_check')
        current_phase.next()
        self.command.do_phase_post_check(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        return current_phase

    def do_phase_report(self) -> Phase:
        """
        Create report(s) on task(s) executed.
        :return: None
        """
        current_phase = self.create_phase('pre_report')
        current_phase.next()
        self.command.do_phase_pre_report(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('report')
        current_phase.next()
        self.phase_report(current_phase)
        self.command.do_phase_report(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('post_report')
        current_phase.next()
        self.command.do_phase_post_report(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        return current_phase

    def do_phase_cleanup(self) -> Phase:
        """
        Delete any temporary files, close handles and connections.
        :return: None
        """
        current_phase = self.create_phase('pre_cleanup')
        current_phase.next()
        self.command.do_phase_pre_cleanup(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('cleanup')
        current_phase.next()
        self.phase_cleanup(current_phase)
        self.command.do_phase_cleanup(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('post_cleanup')
        current_phase.next()
        self.command.do_phase_post_cleanup(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        return current_phase

    def do_phase_shutdown(self) -> Phase:
        """
        Perform any step(s) necessary before Moore.io Client ends its operation.
        :return: None
        """
        current_phase = self.create_phase('pre_shutdown')
        current_phase.next()
        self.command.do_phase_pre_shutdown(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('shutdown')
        current_phase.next()
        self.phase_shutdown(current_phase)
        self.command.do_phase_shutdown(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('post_shutdown')
        current_phase.next()
        self.command.do_phase_post_shutdown(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        return current_phase

    def do_phase_final(self) -> Phase:
        """
        Last call.
        :return: None
        """
        current_phase = self.create_phase('pre_final')
        current_phase.next()
        self.command.do_phase_pre_final(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('final')
        current_phase.next()
        self.phase_final(current_phase)
        self.command.do_phase_final(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        current_phase = self.create_phase('post_final')
        current_phase.next()
        self.command.do_phase_post_final(current_phase)
        current_phase.next()
        self.check_phase_finished(current_phase)
        return current_phase

    def phase_init(self, phase: Phase):
        file_path = os.path.realpath(__file__)
        directory_path = os.path.dirname(file_path)
        install_path = Path(Path(directory_path) / '..').resolve()
        self._install_path = install_path
        self._data_files_path = install_path / "data"
        template_loader = jinja2.FileSystemLoader(searchpath=self._install_path / "data")
        self._j2_env = jinja2.Environment(loader=template_loader)

    def phase_load_default_configuration(self, phase: Phase):
        self._default_configuration_path = self._install_path / 'data' / 'defaults.toml'
        try:
            with open(self.default_configuration_path, 'r') as f:
                self._default_configuration = toml.load(f)
        except ValidationError as e:
            phase.error = Exception(
                f"Failed to load default configuration file at '{self.default_configuration_path}': {e}")
        else:
            self.debug(f"Loaded default configuration from '{self.default_configuration_path}':\n{self._default_configuration}")

    def phase_load_user_data(self, phase: Phase):
        if self.file_exists(self._user_data_file_path):
            try:
                self._user = User.load(self._user_data_file_path)
            except ValidationError as e:
                phase.error = Exception(f"Failed to load User Data at '{self._user_data_file_path}': {e}")
        else:
            self._user = User.new()
            self.debug(f"Loaded user data from '{self._user_data_file_path}':\n{self.user}")

    def authenticate(self, phase: Phase):
        if not self.user.authenticated:
            if self.user.use_pre_set_username:
                self.user.username = self.user.pre_set_username
            else:
                if self.user.username == "__ANONYMOUS__":
                    self.user.username = input("Enter your username: ")
            password = ""
            try:
                if self.user.use_pre_set_password:
                    password = self.user.pre_set_password
                else:
                    password = getpass.getpass("Enter your password: ")
            except Exception as e:
                phase.error = Exception(f"An error occurred during authentication: {e}")
            else:
                credentials = {
                    'username': self.user.username,
                    'password': password,
                }
                final_url: str = f"{self.url_api}/auth/login/"
                try:
                    session = requests.Session()
                    response = session.post(final_url, data=credentials)
                    response.raise_for_status()  # Raise an error for bad status codes
                    self.user.session_cookies = requests.utils.dict_from_cookiejar(session.cookies)
                    self.user.session_headers = dict(session.headers)
                except Exception as e:
                    phase.error = Exception(f"An error occurred during authentication with '{final_url}': {e}")
                else:
                    self.user.authenticated = True

    def deauthenticate(self, phase: Phase):
        final_url: str = f"{self.url_api}/auth/logout/"
        try:
            session = requests.Session()
            session.cookies = requests.utils.cookiejar_from_dict(self.user.session_cookies)
            session.headers.update(self.user.session_headers)
            session.headers['X-CSRFToken'] = session.cookies.get('csrftoken')
            response = session.post(final_url)
            response.raise_for_status()  # Raise an error for bad status codes
            session.cookies.clear()
        except requests.RequestException as e:
            Exception(f"Error during de-authentication with '{final_url}': {e}")

    def web_api_call(self, method: HTTPMethod, path: str, data: dict) -> dict:
        response = {}
        if not self.user.authenticated:
            raise Exception(f"Error during Web API call: user not authenticated")
        else:
            final_url: str = f"{self.url_api}/{path}"
            try:
                session = requests.Session()
                session.cookies = requests.utils.cookiejar_from_dict(self.user.session_cookies)
                session.headers.update(self.user.session_headers)
                session.headers['X-CSRFToken'] = session.cookies.get('csrftoken')
                if method == HTTPMethod.POST:
                    response = session.post(final_url, data=data)
                    response.raise_for_status()  # Raise an error for bad status codes
                else:
                    raise Exception(f"Method {method} is not supported")
            except requests.RequestException as e:
                raise Exception(f"Error during Web API {method} to '{final_url}': {e}")
        return response

    def phase_save_user_data(self, phase: Phase):
        try:
            self._user.save(self._user_data_file_path)
            self.debug(f"Saved user data to '{self._user_data_file_path}'")
        except Exception as e:
            phase.error = Exception(f"Failed to save User Data at '{self._user_data_file_path}': {e}")

    def locate_project_file(self) -> Path:
        current_path = self.wd
        while current_path != os.path.dirname(current_path):  # Stop if we're at the root directory
            candidate_path = Path(os.path.join(current_path, 'mio.toml'))
            if self.file_exists(candidate_path):
                return Path(candidate_path)
            # Move up one directory
            current_path = os.path.dirname(current_path)

    def phase_locate_project_file(self, phase: Phase):
        try:
            self._project_configuration_path = self.locate_project_file()
        except Exception as e:
            if self.command.executes_main_phase:
                phase.error = Exception(f"Could not locate Project 'mio.toml': {e}")
        else:
            self.debug(f"Found Project root at '{self.project_configuration_path}'")

    def phase_create_common_files_and_directories(self, phase: Phase):
        self.create_directory(self.md)
        self.create_directory(self.locally_installed_ip_dir)
        self.create_directory(self.global_ip_local_copy_dir)
        self.create_directory(self.temp_dir)

    def phase_load_project_configuration(self, phase: Phase):
        if not self.project_configuration_path:
            if self.command.executes_main_phase:
                phase.error = Exception("Could not find project root path")
            return
        try:
            with open(self.project_configuration_path, 'r') as f:
                self._project_configuration = toml.load(f)
        except ValidationError as e:
            phase.error = Exception(
                f"Failed to load Project configuration file at '{self.project_configuration_path}': {e}")
        else:
            self._project_root_path = self.project_configuration_path.parent
            self.debug(f"Loaded project configuration from '{self.project_configuration_path}':\n{self._project_configuration}")

    def phase_load_user_configuration(self, phase: Phase):
        self._user_configuration_path = self.user_home_path / "mio.toml"
        if self.file_exists(self.user_configuration_path):
            try:
                with open(self.user_configuration_path, 'r') as f:
                    self._user_configuration = toml.load(f)
            except ValidationError as e:
                phase.error = Exception(f"Failed to load User configuration at '{self.user_configuration_path}': {e}")
        else:
            self.create_file(self.user_configuration_path)
            self.debug(f"Loaded user configuration from '{self.user_configuration_path}':\n{self._user_configuration}")

    def phase_validate_configuration_space(self, phase):
        merged_configuration = self.merge_dictionaries(self._default_configuration, self._user_configuration)
        merged_configuration = self.merge_dictionaries(merged_configuration, self._project_configuration)
        try:
            self._configuration = Configuration.model_validate(merged_configuration)
        except ValidationError as e:
            errors = e.errors()
            error_messages = "\n  ".join([f"{error['msg']}: {error['loc']}" for error in errors])
            phase.error = Exception(f"Failed to validate Configuration Space: {error_messages}")
        else:
            self.configuration.check()
            if self._test_mode:
                self._url_base = "http://localhost:8000"
                self._url_api = f"{self._url_base}/api"
            else:
                self._url_base = self.configuration.authentication.server_url
                self._url_api = self.configuration.authentication.server_api_url
            self.debug(f"Final configuration tree:\n{merged_configuration}")

    def relocate_data_files(self, phase: Phase):
        if self.configuration.project.local_mode:
            self.debug(f"Relocating MIO data files to project")
            new_data_files_path = self.temp_dir / "mio_data_files"
            if self.directory_exists(new_data_files_path):
                self.remove_directory(new_data_files_path)
            self.copy_directory(self._data_files_path, new_data_files_path)
            self._data_files_path = new_data_files_path

    def phase_scheduler_discovery(self, phase: Phase):
        self._scheduler_database = JobSchedulerDatabase(self)
        self.scheduler_database.discover_schedulers()

    def phase_service_discovery(self, phase: Phase):
        self._service_database = ServiceDataBase(self)
        self.service_database.discover_services()

    def phase_ip_discovery(self, phase: Phase):
        """
        Discover and load all 'ip.yml' files in the directory specified by self.project_root_path.
        :param phase: handle to phase object
        :return: None
        """
        self._ip_database = IpDataBase(self)
        local_paths = [os.path.join(self.project_root_path, path) for path in self.configuration.ip.local_paths]
        global_paths = [os.path.expanduser(path) for path in self.configuration.ip.global_paths]
        for path in local_paths:
            self.ip_database.discover_ip(Path(path), IpLocationType.PROJECT_USER)
        if not self.ip_database.has_ip:
            phase.warning = Exception("No IP definitions found in the project")
        else:
            for path in global_paths:
                self.ip_database.discover_ip(Path(path), IpLocationType.GLOBAL)
            if not self.configuration.authentication.offline:
                self.ip_database.discover_ip(self.locally_installed_ip_dir, IpLocationType.PROJECT_INSTALLED)
                self.ip_database.resolve_local_dependencies()

    def phase_check(self, phase: Phase):
        pass

    def phase_report(self, phase: Phase):
        pass

    def phase_cleanup(self, phase: Phase):
        pass

    def phase_shutdown(self, phase: Phase):
        pass

    def phase_final(self, phase: Phase):
        pass
