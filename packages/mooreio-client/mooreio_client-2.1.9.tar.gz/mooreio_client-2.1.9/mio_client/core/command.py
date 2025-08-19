# Copyright 2020-2025 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
from abc import abstractmethod

from .phase import Phase
from .model import Model


class CommandHistory(Model):
    pass


#######################################################################################################################
# Abtract
#######################################################################################################################
class Command:
    def __init__(self):
        """
        Constructor for initializing command object.
        :param name: The name of the command.
        """
        self._rmh = None
        self._parsed_cli_arguments = None
        self._current_phase = None

    @staticmethod
    @abstractmethod
    def name() -> str:
        """
        :return: The name of the command.
        """
        pass

    @property
    def rmh(self) -> 'RootManager':
        """
        :return: The current root object.
        """
        return self._rmh

    @rmh.setter
    def rmh(self, value: 'RootManager'):
        """
        :param value: The new root object
        :return: None
        """
        if not isinstance(value, 'RootManager'):
            raise TypeError("root must be an instance of Root")
        self._rmh = value

    @property
    def parsed_cli_arguments(self):
        """
        :return: The parsed command-line arguments.
        """
        return self._parsed_cli_arguments

    @parsed_cli_arguments.setter
    def parsed_cli_arguments(self, value):
        """
        Setter method for the `parsed_cli_arguments` property.
        :param value: The value to set for the `parsed_cli_arguments` property.
        :return: None
        """
        self._parsed_cli_arguments = value

    @property
    def current_phase(self):
        """
        Read-only property to get the current phase.
        :return: The current phase.
        """
        return self._current_phase

    @staticmethod
    @abstractmethod
    def add_to_subparsers(subparsers):
        """
        Add parser(s) to the CLI argument subparsers.
        This method is a placeholder and must be implemented by subclasses.
        :param subparsers: The subparsers object to add the current command to.
        :return: None
        """
        pass

    @property
    @abstractmethod
    def executes_main_phase(self) -> bool:
        """
        Check if command executes job(s).
        This method is a placeholder and must be implemented by subclasses.
        :return: bool
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @property
    def perform_ip_discovery(self) -> bool:
        """
        Check if command performs IP discovery.
        :return: bool
        """
        return True

    def needs_authentication(self) -> bool:
        """
        Check if user needs authentication to perform this command.
        This method is a placeholder and must be implemented by subclasses.
        :return: bool
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def check_phase(self, phase: Phase):
        """
        Check if the given phase is a valid instance of Phase.
        :param phase: The phase to be checked.
        :return: None
        :raises TypeError: If phase is not an instance of Phase.
        """
        #if not isinstance(phase, Phase):
        #    raise TypeError("phase must be an instance of Phase")
        self._current_phase = phase

    def do_phase_init(self, phase: Phase):
        """
        Dispatcher for Init Phase; called by Root.
        :param phase: handle to phase object
        :return: 
        """
        self.check_phase(phase)
        self.phase_init(phase)

    def do_phase_pre_load_default_configuration(self, phase: Phase):
        """
        Dispatcher for Pre-load Default Configuration Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_pre_load_default_configuration(phase)

    def do_phase_post_load_default_configuration(self, phase: Phase):
        """
        Dispatcher for Post-load Default Configuration Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_post_load_default_configuration(phase)

    def do_phase_pre_locate_project_file(self, phase: Phase):
        """
        Dispatcher for Pre-locate Project File Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_pre_locate_project_file(phase)

    def do_phase_post_locate_project_file(self, phase: Phase):
        """
        Dispatcher for Post-locate Project File Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_post_locate_project_file(phase)

    def do_phase_pre_create_common_files_and_directories(self, phase: Phase):
        """
        Dispatcher for Pre-create Common Files and Directories Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_pre_create_common_files_and_directories(phase)

    def do_phase_create_common_files_and_directories(self, phase: Phase):
        """
        Dispatcher for Create Common Files and Directories Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_create_common_files_and_directories(phase)

    def do_phase_post_create_common_files_and_directories(self, phase: Phase):
        """
        Dispatcher for Post-create Common Files and Directories Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_post_create_common_files_and_directories(phase)

    def do_phase_pre_load_project_configuration(self, phase: Phase):
        """
        Dispatcher for Pre-load Project Configuration Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_pre_load_project_configuration(phase)

    def do_phase_post_load_project_configuration(self, phase: Phase):
        """
        Dispatcher for Post-load Project Configuration Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_post_load_project_configuration(phase)

    def do_phase_pre_load_user_configuration(self, phase: Phase):
        """
        Dispatcher for Pre-load User Configuration Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_pre_load_user_configuration(phase)

    def do_phase_post_load_user_configuration(self, phase: Phase):
        """
        Dispatcher for Post-load User Configuration Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_post_load_user_configuration(phase)

    def do_phase_pre_validate_configuration_space(self, phase: Phase):
        """
        Dispatcher for Pre-validate Configuration Space Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_pre_validate_configuration_space(phase)

    def do_phase_post_validate_configuration_space(self, phase: Phase):
        """
        Dispatcher for Post-validate Configuration Space Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_post_validate_configuration_space(phase)

    def do_phase_pre_load_user_data(self, phase: Phase):
        """
        Dispatcher for Pre-load User Data Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_pre_load_user_data(phase)

    def do_phase_post_load_user_data(self, phase: Phase):
        """
        Dispatcher for Post-load User Data Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_post_load_user_data(phase)

    def do_phase_pre_authenticate(self, phase: Phase):
        """
        Dispatcher for Pre-authenticate Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_pre_authenticate(phase)

    def do_phase_post_authenticate(self, phase: Phase):
        """
        Dispatcher for Post-authenticate Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_post_authenticate(phase)

    def do_phase_pre_save_user_data(self, phase: Phase):
        """
        Dispatcher for Pre-save User Data Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_pre_save_user_data(phase)

    def do_phase_post_save_user_data(self, phase: Phase):
        """
        Dispatcher for Post-save User Data Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_post_save_user_data(phase)

    def do_phase_pre_scheduler_discovery(self, phase: Phase):
        """
        Dispatcher for Pre-scheduler Discovery Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_pre_scheduler_discovery(phase)

    def do_phase_post_scheduler_discovery(self, phase: Phase):
        """
        Dispatcher for Post-scheduler Discovery Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_post_scheduler_discovery(phase)

    def do_phase_pre_service_discovery(self, phase: Phase):
        """
        Dispatcher for Pre-service Discovery Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_pre_service_discovery(phase)

    def do_phase_post_service_discovery(self, phase: Phase):
        """
        Dispatcher for Post-service Discovery Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_post_service_discovery(phase)

    def do_phase_pre_ip_discovery(self, phase: Phase):
        """
        Dispatcher for Pre-IP Discovery Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_pre_ip_discovery(phase)

    def do_phase_post_ip_discovery(self, phase: Phase):
        """
        Dispatcher for Post-IP Discovery Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_post_ip_discovery(phase)

    def do_phase_pre_main(self, phase: Phase):
        """
        Dispatcher for Pre-main Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_pre_main(phase)

    def do_phase_main(self, phase: Phase):
        """
        Dispatcher for Main Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_main(phase)

    def do_phase_post_main(self, phase: Phase):
        """
        Dispatcher for Post-main Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_post_main(phase)

    def do_phase_pre_check(self, phase: Phase):
        """
        Dispatcher for Pre-check Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_pre_check(phase)

    def do_phase_check(self, phase: Phase):
        """
        Dispatcher for Check Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_check(phase)

    def do_phase_post_check(self, phase: Phase):
        """
        Dispatcher for Post-check Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_post_check(phase)

    def do_phase_pre_report(self, phase: Phase):
        """
        Dispatcher for Pre-report Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_pre_report(phase)

    def do_phase_report(self, phase: Phase):
        """
        Dispatcher for Report Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_report(phase)

    def do_phase_post_report(self, phase: Phase):
        """
        Dispatcher for Post-report Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_post_report(phase)

    def do_phase_pre_cleanup(self, phase: Phase):
        """
        Dispatcher for Pre-cleanup Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_pre_cleanup(phase)

    def do_phase_cleanup(self, phase: Phase):
        """
        Dispatcher for Cleanup Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_cleanup(phase)

    def do_phase_post_cleanup(self, phase: Phase):
        """
        Dispatcher for Post-cleanup Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_post_cleanup(phase)

    def do_phase_pre_shutdown(self, phase: Phase):
        """
        Dispatcher for Pre-shutdown Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_pre_shutdown(phase)

    def do_phase_shutdown(self, phase: Phase):
        """
        Dispatcher for Shutdown Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_shutdown(phase)

    def do_phase_post_shutdown(self, phase: Phase):
        """
        Dispatcher for Post-shutdown Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_post_shutdown(phase)

    def do_phase_pre_final(self, phase: Phase):
        """
        Dispatcher for Pre-final Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_pre_final(phase)

    def do_phase_final(self, phase: Phase):
        """
        Dispatcher for Final Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_final(phase)

    def do_phase_post_final(self, phase: Phase):
        """
        Dispatcher for Post-final Phase; called by Root.
        :param phase: handle to phase object
        :return:
        """
        self.check_phase(phase)
        self.phase_post_final(phase)
    
    def phase_init(self, phase: Phase):
        """
        Init phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_pre_load_default_configuration(self, phase: Phase):
        """
        Pre-load default configuration phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_post_load_default_configuration(self, phase: Phase):
        """
        Post-load default configuration phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_pre_load_user_data(self, phase: Phase):
        """
        Pre-load user data phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_post_load_user_data(self, phase: Phase):
        """
        Post-load user data phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_pre_authenticate(self, phase: Phase):
        """
        Pre-authenticate phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_post_authenticate(self, phase: Phase):
        """
        Post-authenticate phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_pre_save_user_data(self, phase: Phase):
        """
        Pre-save user data phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_post_save_user_data(self, phase: Phase):
        """
        Post-save user data phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_pre_locate_project_file(self, phase: Phase):
        """
        Pre-locate project file phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_post_locate_project_file(self, phase: Phase):
        """
        Post-locate project file phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_pre_create_common_files_and_directories(self, phase: Phase):
        """
        Pre-create common files and directories phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_create_common_files_and_directories(self, phase: Phase):
        """
        Create common files and directories phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_post_create_common_files_and_directories(self, phase: Phase):
        """
        Post-create common files and directories phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_pre_validate_project_file(self, phase: Phase):
        """
        Pre-validate project file phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_post_validate_project_file(self, phase: Phase):
        """
        Post-validate project file phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_pre_load_user_configuration(self, phase: Phase):
        """
        Pre-load user configuration phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_post_load_user_configuration(self, phase: Phase):
        """
        Post-load user configuration phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_pre_load_project_configuration(self, phase: Phase):
        """
        Pre-load project configuration phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_post_load_project_configuration(self, phase: Phase):
        """
        Post-load project configuration phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_pre_validate_configuration_space(self, phase: Phase):
        """
        Pre-validate configuration space phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_post_validate_configuration_space(self, phase: Phase):
        """
        Post-validate configuration space phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_pre_scheduler_discovery(self, phase: Phase):
        """
        Pre-scheduler discovery phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_post_scheduler_discovery(self, phase: Phase):
        """
        Post-scheduler discovery phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_pre_service_discovery(self, phase: Phase):
        """
        Pre-service discovery phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_post_service_discovery(self, phase: Phase):
        """
        Post-service discovery phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_pre_ip_discovery(self, phase: Phase):
        """
        Pre-IP Discovery phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_post_ip_discovery(self, phase: Phase):
        """
        Post-IP Discovery phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_pre_main(self, phase: Phase):
        """
        Pre-main phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_main(self, phase: Phase):
        """
        Main phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_post_main(self, phase: Phase):
        """
        Post-main phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_pre_check(self, phase: Phase):
        """
        Pre-check phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_check(self, phase: Phase):
        """
        Check phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_post_check(self, phase: Phase):
        """
        Post-check phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_pre_report(self, phase: Phase):
        """
        Pre-report phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_report(self, phase: Phase):
        """
        Report phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_post_report(self, phase: Phase):
        """
        Post-report phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_pre_cleanup(self, phase: Phase):
        """
        Pre-cleanup phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_cleanup(self, phase: Phase):
        """
        Cleanup phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_post_cleanup(self, phase: Phase):
        """
        Post-cleanup phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_pre_shutdown(self, phase: Phase):
        """
        Pre-shutdown phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_shutdown(self, phase: Phase):
        """
        Shutdown phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_post_shutdown(self, phase: Phase):
        """
        Post-shutdown phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_pre_final(self, phase: Phase):
        """
        Pre-final phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_final(self, phase: Phase):
        """
        Final phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass

    def phase_post_final(self, phase: Phase):
        """
        Post-final phase. To be overridden by subclasses.
        :param phase: handle to phase object
        :return: None
        """
        pass
