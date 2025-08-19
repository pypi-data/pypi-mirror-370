# Copyright 2020-2025 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
from enum import Enum
from pathlib import Path
from typing import Dict, List

from ..services.siarx import SiArxService, SiArxMode, SiArxRequest, SiArxReport
from ..services.init import InitServiceModes, InitServiceReport, InitService, InitProjectRequest, \
    InitIpRequest
from ..core.service import ServiceType
from ..core.phase import Phase
from ..core.command import Command
from ..core.ip import Ip, IpPkgType, DutType, IpLocationType


#######################################################################################################################
# API Entry Point
#######################################################################################################################
def get_commands():
    return [InitCommand, SiArxCommand]



#######################################################################################################################
# Init Command
#######################################################################################################################
INIT_HELP_TEXT = """Moore.io Initialization Command
   Creates a new Project skeleton if not already within a Project.  If not, a new IP skeleton is created.
   This is the recommended method for importing code to the Moore.io ecosystem.

Usage:
   mio init [OPTIONS]

Options:
   -i FILE, --input-file=FILE  # Specifies YAML input file path (instead of prompting user)

Examples:
   mio init                   # Create a new empty Project/IP in this location.
   mio init -i ~/answers.yml  # Create a new empty Project/IP in this location with pre-filled data.
   mio -C ~/my_proj init      # Create a new empty Project at a specific location.

Reference documentation: https://mooreio-client.rtfd.io/en/latest/commands.html#init"""


class InitCommand(Command):
    def __init__(self):
        super().__init__()
        self._prompt_user: bool = False
        self._user_input_file: Path = Path()
        self._mode: InitServiceModes = InitServiceModes.UNDEFINED
        self._init_project_configuration: InitProjectRequest
        self._init_ip_configuration: InitIpRequest
        self._init_service: InitService
        self._report: InitServiceReport
        self._success: bool = False

    @staticmethod
    def name() -> str:
        return "init"

    @property
    def executes_main_phase(self) -> bool:
        return False

    @property
    def perform_ip_discovery(self) -> bool:
        return False

    @property
    def prompt_user(self) -> bool:
        return self._prompt_user

    @property
    def user_input_file(self) -> Path:
        return self._user_input_file

    @property
    def mode(self) -> InitServiceModes:
        return self._mode

    @property
    def init_project_configuration(self) -> InitProjectRequest:
        return self._init_project_configuration

    @property
    def init_ip_configuration(self) -> InitIpRequest:
        return self._init_ip_configuration

    @property
    def init_service(self) -> InitService:
        return self._init_service

    @property
    def report(self) -> InitServiceReport:
        return self._report

    @property
    def success(self) -> bool:
        return self._success

    @staticmethod
    def add_to_subparsers(subparsers):
        parser_init = subparsers.add_parser('init', help=INIT_HELP_TEXT, add_help=False)
        parser_init.add_argument('-i', "--input-file",
                                 help='Specifies YAML input file path (instead of prompting user)', type=str,
                                 required=False)

    def needs_authentication(self) -> bool:
        return False

    def phase_init(self, phase: Phase):
        if self.parsed_cli_arguments.input_file:
            self._user_input_file = Path(self.parsed_cli_arguments.input_file.strip())
            if not self.rmh.file_exists(self.user_input_file):
                phase.error = Exception(f"File '{self.user_input_file}' does not exist.")
            else:
                self._prompt_user = False

    def do_phase_post_validate_configuration_space(self, phase: Phase):
        if self.rmh.project_configuration_path is None:
            self._mode = InitServiceModes.NEW_PROJECT
        else:
            self._mode = InitServiceModes.NEW_IP

    def phase_post_service_discovery(self, phase: Phase):
        try:
            self._init_service = self.rmh.service_database.find_service(ServiceType.CODE_GENERATION, "init")
        except Exception as e:
            phase.error = e
        else:
            if self.mode == InitServiceModes.NEW_PROJECT:
                self.new_project(phase)
            elif self.mode == InitServiceModes.NEW_IP:
                self.new_ip(phase)
            self.print_report(phase)
            phase.end_process = True

    def new_project(self, phase: Phase):
        try:
            self.fill_project_configuration_from_user_input()
            self.init_project_configuration.input_path = self.rmh.wd
        except Exception as e:
            self._success = False
            phase.error = Exception(f"Failed to obtain valid Project data from user: {e}")
        else:
            try:
                self._report = self.init_service.init_project(self.init_project_configuration)
            except Exception as e:
                phase.error = Exception(f"Failed to initialize Project: {e}")
                self._success = False
            else:
                self._success = self.report.success

    def new_ip(self, phase: Phase):
        try:
            self.fill_ip_configuration_from_user_input()
            self.init_ip_configuration.input_path = self.rmh.wd
        except Exception as e:
            self._success = False
            phase.error = Exception(f"Failed to obtain valid IP data from user: {e}")
        else:
            try:
                self._report = self.init_service.init_ip(self.init_ip_configuration)
            except Exception as e:
                phase.error = Exception(f"Failed to initialize IP: {e}")
                self._success = False
            else:
                self._success = self.report.success

    def phase_report(self, phase: Phase):
        self.print_report(phase)

    def print_report(self, phase: Phase):
        if self.success:
            banner = f"{'*' * 53}\033[32m SUCCESS \033[0m{'*' * 54}"
        else:
            banner = f"{'*' * 53}\033[31m\033[4m FAILURE \033[0m{'*' * 54}"
        print(banner)
        if self.mode == InitServiceModes.NEW_PROJECT:
            self.rmh.info(f"New Project '{self.report.name}' initialized at '{self.rmh.wd}'")
        else:
            self.rmh.info(f"New IP '{self.report.name}' initialized at '{self.rmh.wd}'")
        print(banner)

    def fill_project_configuration_from_user_input(self):
        if self.prompt_user:
            name: str = input("Enter the project name: ").strip()
            full_name: str = input("Enter the project full name: ").strip()
            ip_directories_raw: List[str] = input(
                "Enter the name of directories where Project IP are located (separated by commas): ").split(",")
            ip_directories: List[str] = []
            for ip_directory in ip_directories_raw:
                ip_directories.append(ip_directory.strip())
            sim_directory: str = input("Enter the logic simulation directory: ").strip()
            docs_directory: str = input("Enter the documentation directory: ").strip()
            self._project_configuration: InitProjectRequest = InitProjectRequest(
                input_path=str(self.rmh.wd),
                name=name.strip().lower(),
                full_name=full_name.strip(),
                ip_directories=ip_directories,
                sim_directory=sim_directory,
                docs_directory=docs_directory
            )
        else:
            self._init_project_configuration = InitProjectRequest.load_from_yaml(self.user_input_file)

    def fill_ip_configuration_from_user_input(self):
        if self.prompt_user:
            ip_types_options = [member.name for member in IpPkgType]
            ip_types_str: str = ', '.join(ip_types_options).lower()
            ip_dut_types_options = [member.name for member in DutType]
            ip_dut_types_str: str = ', '.join(ip_dut_types_options).lower()
            vendor: str = input("Enter the IP vendor: ").strip().lower()
            name: str = input("Enter the IP name: ").strip().lower()
            full_name: str = input("Enter the full IP name: ").strip()
            version: str = input("Enter the IP version (e.g., 1.0.0): ").strip()
            ip_type: Ip.IpType = Ip.IpType[input(f"Enter the IP type [{ip_types_str}]: ").strip().upper()]
            has_docs_directory: bool = bool(input("Does the IP have a documentation directory? (True/False): "))
            docs_directory: str = ""
            if has_docs_directory:
                docs_directory = input("Enter the documentation directory (path): ").strip()
            has_scripts_directory: bool = bool(input("Does the IP have a scripts directory? (True/False): "))
            scripts_directory: str = ""
            if has_scripts_directory:
                scripts_directory = input("Enter the scripts directory (path): ").strip()
            has_examples_directory: bool = bool(input("Does the IP have examples directory? (True/False): "))
            examples_directory: str = ""
            if has_examples_directory:
                examples_directory = input("Enter the examples directory (path): ").strip()
            hdl_src_directory = input("Enter the HDL source directory path: ").strip()
            hdl_src_sub_directories: List[str] = []
            if hdl_src_directory != ".":
                hdl_src_sub_directories_raw: List[str] = input(
                    "Enter source sub-directories, separated by commas: ").split(",")
                for hdl_src_sub_directory in hdl_src_sub_directories_raw:
                    hdl_src_sub_directories.append(hdl_src_sub_directory.strip())
            hdl_top_sv_files_raw: List[str] = input("Enter the top SystemVerilog file(s), separated by commas: ").split(
                ",")
            hdl_top_sv_files: List[str] = []
            for hdl_top_sv_file in hdl_top_sv_files_raw:
                hdl_top_sv_files.append(hdl_top_sv_file.strip())
            hdl_top_vhdl_files_raw: List[str] = input("Enter the top VHDL file(s), separated by commas: ").split(",")
            hdl_top_vhdl_files: List[str] = []
            for hdl_top_vhdl_file in hdl_top_vhdl_files_raw:
                hdl_top_vhdl_files.append(hdl_top_vhdl_file.strip())
            dut_type: DutType = DutType.MIO_IP
            dut_name: str = ""
            dut_version: str = ""
            hdl_top: List[str] = []
            hdl_tests_path: str = ""
            hdl_tests_name_template: str = ""
            if ip_type == IpPkgType.DV_TB:
                dut_type = DutType[input(f"Enter the DUT type [{ip_dut_types_str}]: ").strip().upper()]
                dut_name = input("Enter the DUT name: ").strip().lower()
                dut_version = input("Enter the DUT version (e.g., 1.0.0): ").strip()
                hdl_top_raw: List[str] = input("Enter the top design construct(s), separated by commas: ").split(",")
                for top in hdl_top_raw:
                    hdl_top.append(top.strip())
                hdl_tests_path = input("Enter the tests directory (path): ").strip()
                hdl_tests_name_template = input(
                    f"Enter the template for test class names (e.g., '{name}_{{{{ name }}}}_test_c' ): ").strip()
            self._init_ip_configuration = InitIpRequest(
                input_path=str(self.rmh.wd),
                vendor=vendor,
                name=name,
                full_name=full_name,
                version=version,
                ip_type=ip_type,
                has_docs_directory=has_docs_directory,
                docs_directory=docs_directory,
                has_scripts_directory=has_scripts_directory,
                scripts_directory=scripts_directory,
                has_examples_directory=has_examples_directory,
                examples_directory=examples_directory,
                dut_type=dut_type,
                dut_name=dut_name,
                dut_version=dut_version,
                hdl_src_directory=hdl_src_directory,
                hdl_src_sub_directories=hdl_src_sub_directories,
                hdl_top_sv_files=hdl_top_sv_files,
                hdl_top_vhdl_files=hdl_top_vhdl_files,
                hdl_top=hdl_top,
                hdl_tests_path=hdl_tests_path,
                hdl_tests_name_template=hdl_tests_name_template
            )
        else:
            self._init_ip_configuration = InitIpRequest.load_from_yaml(self.user_input_file)



#######################################################################################################################
# SiArx Command
#######################################################################################################################
SIARX_HELP_TEXT = """Moore.io SiArx Command
   Generates IP HDL code using Datum SiArx (requires license).  If not within an initialized Project, the ID must be
   specified via `-p/--project-id`.
   
Usage:
   mio x [OPTIONS]

Options:
   -p ID, --project-id=ID   # Specifies Project ID when initializing a new project
   -f   , --force           # Overwrites user changes
   
Examples:
   mio x         # Sync (generate) project with SiArx definition on server
   mio x -p 123  # Initialize and generate Project from empty directory

Reference documentation: https://mooreio-client.rtfd.io/en/latest/commands.html#x"""

class SiArxCommand(Command):
    def __init__(self):
        super().__init__()
        self._mode: SiArxMode
        self._project_id: str = ""
        self._force_update: bool = False
        self._input_path: Path = Path
        self._siarx_service: SiArxService
        self._request: SiArxRequest
        self._report: SiArxReport
        self._success: bool = False

    @staticmethod
    def name() -> str:
        return "x"

    @property
    def perform_ip_discovery(self) -> bool:
        return False

    @property
    def executes_main_phase(self) -> bool:
        return False
    
    @property
    def mode(self) -> SiArxMode:
        return self._mode
        
    @property
    def project_id(self) -> str:
        return self._project_id
    
    @property
    def force_generation(self) -> bool:
        return self._force_update
    
    @property
    def dry_run(self) -> bool:
        return self._dry_run

    @property
    def input_path(self) -> Path:
        return self._input_path

    @property
    def siarx_service(self) -> SiArxService:
        return self._siarx_service
    
    @property
    def request(self) -> SiArxRequest:
        return self._request

    @property
    def report(self) -> SiArxReport:
        return self._report

    @property
    def success(self) -> bool:
        return self._success

    @staticmethod
    def add_to_subparsers(subparsers):
        parser_x = subparsers.add_parser('x', help=SIARX_HELP_TEXT, add_help=False)
        parser_x.add_argument('-p', "--project-id",
                              help='Specifies Project ID when initializing a new project',
                              type=str, required=False)
        parser_x.add_argument('-f', "--force", help="Overwrites user changes",
                              action="store_true", required=False)

    def needs_authentication(self) -> bool:
        return True

    def phase_init(self, phase: Phase):
        self._force_update = self.parsed_cli_arguments.force

    def phase_post_service_discovery(self, phase: Phase):
        try:
            self._siarx_service = self.rmh.service_database.find_service(ServiceType.CODE_GENERATION, "siarx")
        except Exception as e:
            phase.error = e
            self._success = False
        else:
            if self.parsed_cli_arguments.project_id:
                self._mode = SiArxMode.NEW_PROJECT
                self._project_id = self.parsed_cli_arguments.project_id
                self._input_path = self.rmh.wd
                self.perform_siarx_gen(phase)
            else:
                self._mode = SiArxMode.UPDATE_PROJECT
                self._project_id = str(self.rmh.configuration.project.sync_id)
                self._input_path = self.rmh.project_root_path
                self.perform_siarx_gen(phase)
    
    def phase_report(self, phase: Phase):
        if self._success:
            banner = f"{'*' * 53}\033[32m SUCCESS \033[0m{'*' * 54}"
            print(banner)
            if self.rmh.print_trace:
                self.print_infos()
            self.print_warnings()
            if self.mode == SiArxMode.NEW_PROJECT:
                self.rmh.info(f"Initialized Project ID '{self._project_id}' with SiArx successfully.")
            elif self.mode == SiArxMode.UPDATE_PROJECT:
                self.rmh.info(f"Updated Project with Datum SiArx successfully.")
            print(banner)
        else:
            banner = f"{'*' * 53}\033[31m\033[4m FAILURE \033[0m{'*' * 54}"
            print(banner)
            self.print_infos()
            self.print_warnings()
            self.print_errors()
            if self.mode == SiArxMode.NEW_PROJECT:
                self.rmh.error(f"Failed to initialize Project '{self.project_id}' with SiArx.")
            elif self.mode == SiArxMode.UPDATE_PROJECT:
                self.rmh.error(f"Failed to update project with Datum SiArx.")
            print(banner)
            phase.error = Exception(f"Failed to generate code with SiArx.")

    def perform_siarx_gen(self, phase: Phase):
        self.rmh.info(f"Generating code with SiArx ...")
        self._request = SiArxRequest(
            input_path=self.input_path,
            mode=self.mode,
            project_id=self._project_id,
            force_update=self._force_update,
            quiet=False
        )
        self._report = self.siarx_service.gen_project(self._request)
        self._success = self._report.success
        if not self._success:
            phase.error = Exception(f"Failed to generate SiArx Project: {len(self._report.errors)}E {len(self._report.warnings)}W")
            if self.rmh.print_trace:
                self.print_infos()
            self.print_warnings()
            self.print_errors()

    def print_infos(self):
        for info in self._report.infos:
            self.rmh.info(info)

    def print_warnings(self):
        for warning in self._report.warnings:
            self.rmh.warning(warning)

    def print_errors(self):
        for error in self._report.errors:
            self.rmh.error(error)
