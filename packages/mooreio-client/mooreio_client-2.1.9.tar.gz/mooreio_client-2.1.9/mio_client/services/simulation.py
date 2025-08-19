# Copyright 2020-2025 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
import datetime
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from pathlib import Path
from random import random, randint
from typing import List, Optional, Dict, Union

import yaml
from jinja2 import Template
from semantic_version import Version

from ..core.configuration import DSimCloudComputeSizes
from ..core.scheduler import JobScheduler, Job, JobSchedulerConfiguration, JobResults
from ..core.service import Service, ServiceType
from ..core.ip import Ip, IpLocationType, DutType
from abc import ABC, abstractmethod

from ..core.model import Model, UNDEFINED_CONST
import atexit
import signal


#######################################################################################################################
# API Entry Point
#######################################################################################################################
def get_services():
    return [SimulatorMetricsDSim, SimulatorXilinxVivado]


#######################################################################################################################
# Support Types
#######################################################################################################################
class UvmVerbosity(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    FULL = "full"
    DEBUG = "debug"



#######################################################################################################################
# Models
#######################################################################################################################
class LogicSimulatorReport(Model, ABC):
    name: str
    success: Optional[bool] = False
    num_errors: Optional[int] = 0
    num_warnings: Optional[int] = 0
    num_fatals: Optional[int] = 0
    errors: Optional[List[str]] = []
    warnings: Optional[List[str]] = []
    fatals: Optional[List[str]] = []
    work_directory: Optional[Path] = Path()
    jobs: Optional[List[Job]] = []
    scheduler_config: Optional[JobSchedulerConfiguration] = None
    timestamp_start: Optional[datetime.datetime] = datetime.datetime.now()
    timestamp_end: Optional[datetime.datetime] = datetime.datetime.now()
    duration: Optional[datetime.timedelta] = datetime.timedelta()

class LogicSimulatorLibraryCreationReport(LogicSimulatorReport):
    pass

class LogicSimulatorLibraryDeletionReport(LogicSimulatorReport):
    pass

class LogicSimulatorCompilationReport(LogicSimulatorReport):
    ordered_dependencies: Optional[list[Ip]] = []
    has_sv_files_to_compile: Optional[bool] = False
    has_vhdl_files_to_compile: Optional[bool] = False
    sv_compilation_success: Optional[bool] = False
    sv_cmd_log_file_path: Optional[Path] = Path()
    vhdl_compilation_success: Optional[bool] = False
    vhdl_cmd_log_file_path: Optional[Path] = Path()
    sv_file_list_path: Optional[Path] = Path()
    vhdl_file_list_path: Optional[Path] = Path()
    sv_log_path: Optional[Path] = Path()
    vhdl_log_path: Optional[Path] = Path()
    user_defines_boolean: Optional[list[str]] = []
    user_defines_value: Optional[dict[str, str]] = {}
    target_defines_boolean: Optional[dict[str, str]] = {}
    target_defines_value: Optional[dict[str, str]] = {}
    shared_objects: Optional[list[Path]] = []

class LogicSimulatorElaborationReport(LogicSimulatorReport):
    log_path: Optional[Path] = Path()
    elaboration_success: Optional[bool] = False
    cmd_log_file_path: Optional[Path] = Path()
    shared_objects: Optional[list[Path]] = []

class LogicSimulatorCompilationAndElaborationReport(LogicSimulatorReport):
    ordered_dependencies: Optional[list[Ip]] = []
    has_files_to_compile: Optional[bool] = False
    file_list_path: Optional[Path] = Path()
    log_path: Optional[Path] = Path()
    compilation_and_elaboration_success: Optional[bool] = False
    cmd_log_file_path: Optional[Path] = Path()
    user_defines_boolean: Optional[list[str]] = []
    user_defines_value: Optional[dict[str, str]] = {}
    target_defines_boolean: Optional[dict[str, str]] = {}
    target_defines_value: Optional[dict[str, str]] = {}
    shared_objects: Optional[list[Path]] = []

class LogicSimulatorSimulationReport(LogicSimulatorReport):
    test_name: Optional[str] = UNDEFINED_CONST
    uvm_test_class_name: Optional[str] = UNDEFINED_CONST
    seed: Optional[int] = -1
    verbosity: Optional[UvmVerbosity] = UvmVerbosity.DEBUG
    coverage: Optional[bool] = False
    waveform_capture: Optional[bool] = False
    waveform_file_path: Optional[Path] = Path()
    user_args_boolean: Optional[list[str]] = []
    user_args_value: Optional[dict[str, str] ]= {}
    args_boolean: Optional[list[str]] = []
    args_value: Optional[dict[str, str] ]= {}
    test_results_path: Optional[Path] = Path()
    log_path: Optional[Path] = Path()
    coverage_directory: Optional[Path] = Path()
    simulation_success: Optional[bool] = False
    cmd_log_file_path: Optional[Path] = Path()
    shared_objects: Optional[list[Path]] = []
    def __hash__(self):
        return hash(self.seed)
    

class LogicSimulatorEncryptionReport(LogicSimulatorReport):
    mlicense_key: Optional[str] = UNDEFINED_CONST
    path_to_encrypted_files: Optional[Path] = Path()
    sv_encryption_success: Optional[bool] = False
    vhdl_encryption_success: Optional[bool] = False
    has_sv_files_to_encrypt: Optional[bool] = False
    has_vhdl_files_to_encrypt: Optional[bool] = False
    sv_files_to_encrypt: Optional[list[Path]] = []
    vhdl_files_to_encrypt: Optional[list[Path]] = []


class LogicSimulatorCoverageMergeReport(LogicSimulatorReport):
    output_path: Optional[Path] = Path()
    has_html_report: Optional[bool] = True
    html_report_path: Optional[Path] = Path()
    html_report_index_path: Optional[Path] = Path()
    has_merge_log: Optional[bool] = False
    merge_log_file_path: Optional[Path] = Path()


class LogicSimulatorRequest(ABC):
    def __init__(self):
        self.dry_mode: bool = False
        self.use_relative_paths: bool = False
        self.start_path: Path = Path()
        self.use_custom_logs_path: bool = False
        self.custom_logs_path: Path = Path()

class LogicSimulatorLibraryCreationRequest(LogicSimulatorRequest):
    pass

class LogicSimulatorLibraryDeletionRequest(LogicSimulatorRequest):
    pass

class LogicSimulatorCompilationRequest(LogicSimulatorRequest):
    def __init__(self):
        super().__init__()
        self.enable_coverage: bool = False
        self.enable_waveform_capture: bool = False
        self.max_errors: int = 10
        self.defines_boolean: List[str] = []
        self.defines_value: Dict[str, str] = {}
        self.target: str = ""
        self.log_sv_cmd: bool = True
        self.log_vhdl_cmd: bool = True
        self.has_custom_dut: bool = False
        self.custom_dut_type: str = "N/A"
        self.custom_dut_name: str = ""
        self.custom_dut_directories: List[Path] = []
        self.custom_dut_sv_files: List[Path] = []
        self.custom_dut_vhdl_files: List[Path] = []
        self.custom_dut_defines_values: Dict[str, str] = {}
        self.custom_dut_defines_boolean: List[str] = []

class LogicSimulatorElaborationRequest(LogicSimulatorRequest):
    def __init__(self):
        super().__init__()
        self.log_cmd: bool = True

class LogicSimulatorCompilationAndElaborationRequest(LogicSimulatorCompilationRequest):
    def __init__(self):
        super().__init__()
        self.log_cmd: bool = True

class LogicSimulatorSimulationRequest(LogicSimulatorRequest):
    def __init__(self):
        super().__init__()
        self.target: str = ""
        self.enable_coverage: bool = False
        self.enable_waveform_capture: bool = False
        self.gui_mode: bool = False
        self.max_errors: int = 10
        self.user_args_boolean: List[str]= []
        self.user_args_value: Dict[str, str]= {}
        self.args_boolean: List[str] = []
        self.args_value: Dict[str, str] = {}
        self.test_name: str = "__UNDEFINED__"
        self.seed: int = randint(1, ((1 << 31)-1))
        self.verbosity: UvmVerbosity = UvmVerbosity.DEBUG
        self.log_cmd: bool = True
        self.print_to_terminal = True

    def summary_str(self) -> str:
        args_str = ""
        for arg in self.user_args_boolean:
            args_str += f" +{arg}"
        for arg in self.user_args_value:
            args_str += f" +{arg}={self.user_args_value[arg]}"
        return f"{self.test_name} seed={self.seed}{args_str}"

class LogicSimulatorEncryptionRequest(LogicSimulatorRequest):
    def __init__(self):
        super().__init__()
        self.add_license_key_checks: bool = False
        self.mlicense_key: str = UNDEFINED_CONST
        self.mlicense_id: int = -1

class LogicSimulatorCoverageMergeRequest(LogicSimulatorRequest):
    def __init__(self):
        super().__init__()
        self.target_name: str = ""
        self.input_simulation_reports: List[LogicSimulatorSimulationReport] = []
        self.output_path: Path = Path()
        self.create_html_report: bool = True
        self.html_report_path: Path = Path()
        self.merge_log_file_path: Path = Path()


class LogicSimulatorFileList(Model):
    name: str
    directories: Optional[list[str]] = []
    files: Optional[list[str]] = []

class LogicSimulatorMasterFileList(LogicSimulatorFileList):
    sub_file_lists: Optional[List[LogicSimulatorFileList]] = []
    needs_licensing: Optional[bool] = False
    licensing_sv_path: Optional[str] = ""
    licensing_vhdl_path: Optional[str] = ""
    defines_boolean: Optional[Dict[str, bool]] = {}
    defines_values: Optional[Dict[str, str]] = {}
    has_custom_dut: Optional[bool] = False
    custom_dut_type: Optional[str] = "N/A"
    custom_dut_name: Optional[str] = ""
    custom_dut_directories: Optional[List[str]] = []
    custom_dut_files: Optional[List[str]] = []
    custom_dut_defines_values: Optional[Dict[str, str]] = {}
    custom_dut_defines_boolean: Optional[List[str]] = []



#######################################################################################################################
# Logic Simulator Abstract Base Class
#######################################################################################################################
class LogicSimulator(Service, ABC):
    def __init__(self, rmh: 'RootManager', vendor_name: str, name: str, full_name: str):
        super().__init__(rmh, vendor_name, name, full_name)
        self._type = ServiceType.LOGIC_SIMULATION
        self._work_root_path = self.rmh.md / "logic_simulation"
        self._work_path = self.work_root_path / self.name
        self._work_temp_path = self.work_path / "temp"
        self._simulation_root_path = self.rmh.wd / self.rmh.configuration.logic_simulation.root_path
        self._simulation_results_path = self.simulation_root_path / self.rmh.configuration.logic_simulation.results_directory_name
        self._regression_root_path = self.simulation_root_path / self.rmh.configuration.logic_simulation.regression_directory_name
        self._simulation_logs_path = self.simulation_root_path / self.rmh.configuration.logic_simulation.logs_directory

    def __str__(self):
        #return f"{self.vendor_name} {self.name} {self.version}"
        return f"{self.vendor_name} {self.full_name}"

    @property
    @abstractmethod
    def installation_path(self) -> Path:
        pass

    @property
    @abstractmethod
    def supports_vhdl(self) -> bool:
        pass

    @property
    @abstractmethod
    def supports_verilog(self) -> bool:
        pass

    @property
    @abstractmethod
    def supports_system_verilog(self) -> bool:
        pass

    @property
    @abstractmethod
    def supports_one_step_simulation(self) -> bool:
        pass

    @property
    @abstractmethod
    def supports_two_step_simulation(self) -> bool:
        pass

    @property
    @abstractmethod
    def supports_uvm(self) -> bool:
        pass

    @property
    @abstractmethod
    def latest_uvm_version_supported(self) -> Version:
        pass

    @property
    @abstractmethod
    def oldest_uvm_version_supported(self) -> Version:
        pass

    @property
    def is_available(self) -> bool:
        return self.rmh.directory_exists(self.installation_path)

    @property
    def work_root_path(self) -> Path:
        return self._work_root_path

    @property
    def work_path(self) -> Path:
        return self._work_path

    @property
    def work_temp_path(self) -> Path:
        return self._work_temp_path

    @property
    def simulation_root_path(self) -> Path:
        return self._simulation_root_path

    @property
    def simulation_results_path(self) -> Path:
        return self._simulation_results_path

    @property
    def regression_root_path(self) -> Path:
        return self._regression_root_path

    @property
    def simulation_logs_path(self) -> Path:
        return self._simulation_logs_path

    def create_directory_structure(self):
        self.rmh.create_directory(self.work_root_path)
        self.rmh.create_directory(self.work_path)
        self.rmh.create_directory(self.work_temp_path)
        self.rmh.create_directory(self.simulation_root_path)
        self.rmh.create_directory(self.simulation_results_path)
        self.rmh.create_directory(self.regression_root_path)
        self.rmh.create_directory(self.simulation_logs_path)

    def create_files(self):
        pass

    def create_library(self, ip: Ip, request: LogicSimulatorLibraryCreationRequest, scheduler: JobScheduler) -> LogicSimulatorLibraryCreationReport:
        report = LogicSimulatorLibraryCreationReport(name=f"Library Creation for '{ip}' using '{self.full_name}'")
        scheduler_config = JobSchedulerConfiguration(self.rmh)
        scheduler_config.dry_run = request.dry_mode
        scheduler_config.output_to_terminal = self.rmh.print_trace
        self.do_create_library(ip, request, report, scheduler, scheduler_config)
        self.parse_library_creation_logs(ip, request, report)
        report.scheduler_config = scheduler_config
        return report

    def delete_library(self, ip: Ip, request: LogicSimulatorLibraryDeletionRequest, scheduler: JobScheduler) -> LogicSimulatorLibraryDeletionReport:
        report = LogicSimulatorLibraryDeletionReport(name=f"Library Deletion for '{ip}' using '{self.full_name}'")
        scheduler_config = JobSchedulerConfiguration(self.rmh)
        scheduler_config.dry_run = request.dry_mode
        scheduler_config.output_to_terminal = self.rmh.print_trace
        self.do_delete_library(ip, request, report, scheduler, scheduler_config)
        report.scheduler_config = scheduler_config
        return report

    def compile(self, ip: Ip, request: LogicSimulatorCompilationRequest, scheduler: JobScheduler) -> LogicSimulatorCompilationReport:
        report = LogicSimulatorCompilationReport(name=f"Compilation for '{ip}' using '{self.full_name}'")
        scheduler_config = JobSchedulerConfiguration(self.rmh)
        scheduler_config.dry_run = request.dry_mode
        scheduler_config.output_to_terminal = self.rmh.print_trace
        scheduler_config.timeout = self.rmh.configuration.logic_simulation.compilation_timeout
        report.ordered_dependencies = ip.get_dependencies_in_order()
        self.build_sv_flist(ip, request, report)
        self.build_vhdl_flist(ip, request, report)
        if (not report.has_sv_files_to_compile) and (not report.has_vhdl_files_to_compile):
            raise Exception(f"No files to compile for IP '{ip}'")
        report.user_defines_boolean = request.defines_boolean
        report.user_defines_value = request.defines_value
        report.work_directory = self.work_path / f"{ip.work_directory_name}"
        if request.use_custom_logs_path:
            logs_path = request.custom_logs_path
            self.rmh.create_directory(logs_path)
        else:
            logs_path =  self.simulation_logs_path
        report.sv_log_path = logs_path / f"{ip.result_file_name}.cmp.sv.{self.name}.log"
        report.vhdl_log_path = logs_path / f"{ip.result_file_name}.cmp.vhdl.{self.name}.log"
        report.sv_cmd_log_file_path = logs_path / f"{ip.result_file_name}.cmp.sv.{self.name}.cmd.log"
        report.vhdl_cmd_log_file_path = logs_path / f"{ip.result_file_name}.cmp.vhdl.{self.name}.cmd.log"
        self.rmh.create_directory(report.work_directory)
        report.shared_objects = self.get_all_shared_objects(ip, request, report.ordered_dependencies)
        self.do_compile(ip, request, report, scheduler, scheduler_config)
        report.success = (report.sv_compilation_success and report.vhdl_compilation_success)
        report.duration = report.timestamp_end - report.timestamp_start
        if not request.dry_mode:
            self.parse_compilation_logs(ip, request, report)
        report.scheduler_config = scheduler_config
        return report

    def elaborate(self, ip: Ip, request: LogicSimulatorElaborationRequest, scheduler: JobScheduler) -> LogicSimulatorElaborationReport:
        report = LogicSimulatorElaborationReport(name=f"Elaboration for '{ip}' using '{self.full_name}'")
        scheduler_config = JobSchedulerConfiguration(self.rmh)
        scheduler_config.dry_run = request.dry_mode
        scheduler_config.output_to_terminal = self.rmh.print_trace
        scheduler_config.timeout = self.rmh.configuration.logic_simulation.elaboration_timeout
        report.work_directory = self.work_path / f"{ip.work_directory_name}"
        if request.use_custom_logs_path:
            logs_path = request.custom_logs_path
            self.rmh.create_directory(logs_path)
        else:
            logs_path =  self.simulation_logs_path
        report.log_path = logs_path / f"{ip.result_file_name}.elab.{self.name}.log"
        report.cmd_log_file_path = logs_path / f"{ip.result_file_name}.elab.{self.name}.cmd.log"
        report.shared_objects = self.get_all_shared_objects(ip, request)
        self.do_elaborate(ip, request, report, scheduler, scheduler_config)
        report.success = report.elaboration_success
        report.duration = report.timestamp_end - report.timestamp_start
        if not request.dry_mode:
            self.parse_elaboration_logs(ip, request, report)
        report.scheduler_config = scheduler_config
        return report

    def compile_and_elaborate(self, ip: Ip, request: LogicSimulatorCompilationAndElaborationRequest, scheduler: JobScheduler) -> LogicSimulatorCompilationAndElaborationReport:
        report = LogicSimulatorCompilationAndElaborationReport(name=f"Compilation+Elaboration for '{ip}' using '{self.full_name}'")
        scheduler_config = JobSchedulerConfiguration(self.rmh)
        scheduler_config.dry_run = request.dry_mode
        scheduler_config.output_to_terminal = self.rmh.print_trace
        scheduler_config.timeout = self.rmh.configuration.logic_simulation.compilation_and_elaboration_timeout
        report.ordered_dependencies = ip.get_dependencies_in_order()
        self.build_sv_flist(ip, request, report)
        if not report.has_files_to_compile:
            raise Exception(f"No files to compile for IP '{ip}'")
        report.user_defines_boolean = request.defines_boolean
        report.user_defines_value = request.defines_value
        report.work_directory = self.work_path / f"{ip.work_directory_name}"
        if request.use_custom_logs_path:
            logs_path = request.custom_logs_path
            self.rmh.create_directory(logs_path)
        else:
            logs_path =  self.simulation_logs_path
        report.log_path = logs_path / f"{ip.result_file_name}.cmpelab.{self.name}.log"
        report.cmd_log_file_path = logs_path / f"{ip.result_file_name}.cmpelab.{self.name}.cmd.log"
        self.rmh.create_directory(report.work_directory)
        report.shared_objects = self.get_all_shared_objects(ip, request, report.ordered_dependencies)
        self.do_compile_and_elaborate(ip, request, report, scheduler, scheduler_config)
        report.success = report.compilation_and_elaboration_success
        report.duration = report.timestamp_end - report.timestamp_start
        if not request.dry_mode:
            self.parse_compilation_and_elaboration_logs(ip, request, report)
        report.scheduler_config = scheduler_config
        return report

    def simulate(self, ip: Ip, request: LogicSimulatorSimulationRequest, scheduler: JobScheduler) -> LogicSimulatorSimulationReport:
        # Init report
        report = LogicSimulatorSimulationReport(name=f"Simulation for '{ip}' using '{self.full_name}'")
        # Init scheduler
        scheduler_config = JobSchedulerConfiguration(self.rmh)
        scheduler_config.dry_run = request.dry_mode
        scheduler_config.timeout = self.rmh.configuration.logic_simulation.simulation_timeout
        scheduler_config.output_to_terminal = request.print_to_terminal
        # Create work dir
        report.work_directory = self.work_path / f"{ip.work_directory_name}"
        # Generate test result dir name from jinja template
        test_template = Template(ip.hdl_src.tests_name_template)
        test_result_dir_template = Template(self.rmh.configuration.logic_simulation.test_result_path_template)
        report.user_args_boolean = request.args_boolean
        report.user_args_value = request.args_value
        user_args = []
        for arg in report.user_args_boolean:
            if arg:
                user_args.append(arg)
        for arg in report.user_args_value:
            user_args.append(f"{arg}={report.user_args_value[arg]}")
        report.uvm_test_class_name = test_template.render(name=request.test_name)
        report.test_name = request.test_name
        if request.target != "default":
            target_text = f"#{request.target}"
        else:
            target_text = ""
        test_result_directory_name = test_result_dir_template.render(vendor=ip.ip.vendor, ip=ip.ip.name, test=request.test_name,
                                                                     seed=request.seed, target=target_text, args=user_args)
        if request.use_custom_logs_path:
            report.test_results_path = request.custom_logs_path / test_result_directory_name
        else:
            report.test_results_path = self.simulation_results_path / test_result_directory_name
        report.cmd_log_file_path = report.test_results_path / f"cmd.{self.name}.log"
        # Add UVM Args
        final_args_boolean_set = set(request.args_boolean)
        final_args_value = request.args_value
        final_args_boolean_set.add("UVM_NO_RELNOTES")
        final_args_value["UVM_TESTNAME"] = report.uvm_test_class_name
        final_args_value["UVM_VERBOSITY"] = f"UVM_{request.verbosity.value.upper()}"
        final_args_value["UVM_MAX_QUIT_COUNT"] = str(request.max_errors)
        # Add MIO Args
        self.rmh.create_directory(report.test_results_path / "uvmx")
        if request.use_relative_paths:
            final_args_value["__MIO_TEST_RESULTS_PATH__"] = str(os.path.relpath(report.test_results_path, request.start_path))
            final_args_value["__MIO_SIM_PATH__"] = str(os.path.relpath(self.simulation_root_path, request.start_path))
            final_args_value["__MIO_SIM_RESULTS_PATH__"] = str(os.path.relpath(self.simulation_results_path, request.start_path))
            final_args_value["__MIO_SIM_TB_PATH__"] = str(os.path.relpath(ip.resolved_src_path, request.start_path))
            final_args_value["__MIO_SIM_TESTS_PATH__"] = str(os.path.relpath(ip.resolved_tests_path, request.start_path))
        else:
            final_args_value["__MIO_TEST_RESULTS_PATH__"] = str(report.test_results_path)
            final_args_value["__MIO_SIM_PATH__"] = str(self.simulation_root_path)
            final_args_value["__MIO_SIM_RESULTS_PATH__"] = str(self.simulation_results_path)
            final_args_value["__MIO_SIM_TB_PATH__"] = str(ip.resolved_src_path)
            final_args_value["__MIO_SIM_TESTS_PATH__"] = str(ip.resolved_tests_path)
        if self.rmh.user.authenticated:
            pass
            #final_args_value["__MIO_USER_TOKEN__"] = self.rmh.user.access_token
        # Add TB/DUT Args
        if ip.has_dut:
            if ip.dut.type == DutType.MIO_IP:
                dut_target_name = ip.get_target_dut_target(request.target)
                dut_args_bool = ip.resolved_dut.get_target_cmp_bool_defines(dut_target_name)
                for arg in dut_args_bool:
                    if dut_args_bool[arg]:
                        final_args_boolean_set.add(arg)
                final_args_value.update(ip.resolved_dut.get_target_sim_val_args(dut_target_name))
        args_bool = ip.get_target_cmp_bool_defines(request.target)
        for arg in args_bool:
            if args_bool[arg]:
                final_args_boolean_set.add(arg)
        final_args_boolean = list(final_args_boolean_set)
        final_args_value.update(ip.get_target_sim_val_args(request.target))
        # Add to report
        report.log_path = report.test_results_path / f"sim.log"
        report.waveform_file_path = report.test_results_path / f"waves.{self.name}"
        report.coverage_directory = report.test_results_path / f"cov.{self.name}"
        report.args_boolean = final_args_boolean
        report.args_value = final_args_value
        # Create results directories
        self.rmh.create_directory(report.test_results_path)
        if request.enable_coverage:
            self.rmh.create_directory(report.coverage_directory)
        report.shared_objects = self.get_all_shared_objects(ip, request)
        # Perform simulation
        self.do_simulate(ip, request, report, scheduler, scheduler_config)
        # Complete report
        report.success = report.simulation_success
        report.waveform_capture = request.enable_waveform_capture
        report.coverage = request.enable_coverage
        report.seed = request.seed
        report.verbosity = request.verbosity
        report.duration = report.timestamp_end - report.timestamp_start
        if not request.dry_mode:
            self.parse_simulation_logs(ip, request, report)
        report.scheduler_config = scheduler_config
        return report

    def encrypt(self, ip: Ip, request: LogicSimulatorEncryptionRequest, scheduler: JobScheduler) -> LogicSimulatorEncryptionReport:
        report = LogicSimulatorEncryptionReport(name=f"Encryption for '{ip}' using '{self.full_name}'")
        report.path_to_encrypted_files = self.work_temp_path / f'encrypt_{ip.lib_name}'
        if self.rmh.directory_exists(report.path_to_encrypted_files):
            self.rmh.remove_directory(report.path_to_encrypted_files)
        self.rmh.copy_directory(ip.resolved_src_path, report.path_to_encrypted_files)
        # Find all SystemVerilog files within `ip.resolved_src_path` (recursively)
        sv_file_extensions = ["v", "vh", "sv", "svh"]
        for ext in sv_file_extensions:
            report.sv_files_to_encrypt += list(report.path_to_encrypted_files.rglob(f"*.{ext}"))
        report.has_sv_files_to_encrypt = len(report.sv_files_to_encrypt) > 0
        # Find all VHDL files within `ip.resolved_src_path` (recursively)
        vhdl_file_extensions = ["vhd", "vhdl"]
        for ext in vhdl_file_extensions:
            report.vhdl_files_to_encrypt += list(report.path_to_encrypted_files.rglob(f"*.{ext}"))
        report.has_vhdl_files_to_encrypt = len(report.vhdl_files_to_encrypt) > 0
        if (not report.has_sv_files_to_encrypt) and (not report.has_vhdl_files_to_encrypt):
            raise Exception(f"No SystemVerilog or VHDL files found to encrypt for IP '{ip}'")
        for file_path in report.sv_files_to_encrypt:
            with file_path.open("r") as file:
                file_content = file.read()
                file_content = f"`pragma protect begin\n{file_content}\n`pragma protect end\n"
                with file_path.open("w") as file:
                    file.write(file_content)
        for file_path in report.vhdl_files_to_encrypt:
            with file_path.open("r") as file:
                file_content = file.read()
                file_content = f"`protect begin\n{file_content}\n`protect end\n"
                with file_path.open("w") as file:
                    file.write(file_content)
        if ip.ip.mlicensed and request.add_license_key_checks:
            found_key_check = False
            # Search and replace in all SystemVerilog
            search_string = "`__MIO_LICENSE_KEY_CHECK_PHONY__"
            replace_string = f'`__MIO_LICENSE_KEY_CHECK__("{ip}", "{request.mlicense_key}", "{request.mlicense_id}")'
            for file_path in report.sv_files_to_encrypt:
                with file_path.open("r") as file:
                    file_content = file.read()
                if search_string in file_content:
                    file_content = file_content.replace(search_string, replace_string)
                    with file_path.open("w") as file:
                        file.write(file_content)
                    found_key_check = True
            # Search and replace in all VHDL files
            search_string = "-- __MIO_LICENSE_KEY_CHECK_PHONY__"
            replace_string = f'__MIO_LICENSE_KEY_CHECK__("{ip}", "{request.mlicense_key}", "{request.mlicense_id}");'  # TODO This is just theory
            for file_path in report.vhdl_files_to_encrypt:
                with file_path.open("r") as file:
                    file_content = file.read()
                if search_string in file_content:
                    file_content = file_content.replace(search_string, replace_string)
                    with file_path.open("w") as file:
                        file.write(file_content)
                    found_key_check = True
            #if not found_key_check:
            #    raise Exception(f"Did not find Moore.io License Key Check insertion points in HDL source code")
        scheduler_config = JobSchedulerConfiguration(self.rmh)
        scheduler_config.dry_run = request.dry_mode
        scheduler_config.output_to_terminal = False
        self.do_encrypt(ip, request, report, scheduler, scheduler_config)
        if not request.dry_mode:
            self.parse_encryption_logs(ip, request, report)
        report.scheduler_config = scheduler_config
        return report

    def coverage_merge(self, ip: Ip, request: LogicSimulatorCoverageMergeRequest, scheduler: JobScheduler) -> LogicSimulatorCoverageMergeReport:
        report = LogicSimulatorCoverageMergeReport(name=f"Coverage Merge for '{ip}' using '{self.full_name}'")
        scheduler_config = JobSchedulerConfiguration(self.rmh)
        scheduler_config.dry_run = request.dry_mode
        scheduler_config.output_to_terminal = False
        self.rmh.create_directory(request.output_path)
        self.do_coverage_merge(ip, request, report, scheduler, scheduler_config)
        if not request.dry_mode and report.has_merge_log:
            self.parse_merge_coverage_logs(ip, request, report)
        report.scheduler_config = scheduler_config
        return report

    def parse_library_creation_logs(self, ip: Ip, request: LogicSimulatorLibraryCreationRequest, report: LogicSimulatorLibraryCreationReport) -> None:
        pass

    def parse_compilation_logs(self, ip: Ip, request: LogicSimulatorCompilationRequest, report: LogicSimulatorCompilationReport) -> None:
        if report.has_sv_files_to_compile:
            report.errors   += self.rmh.search_file_for_patterns(report.sv_log_path, self.compilation_error_patterns)
            report.warnings += self.rmh.search_file_for_patterns(report.sv_log_path, self.compilation_warning_patterns)
            report.fatals   += self.rmh.search_file_for_patterns(report.sv_log_path, self.compilation_fatal_patterns)
        if report.has_vhdl_files_to_compile:
            report.errors   += self.rmh.search_file_for_patterns(report.vhdl_log_path, self.compilation_error_patterns)
            report.warnings += self.rmh.search_file_for_patterns(report.vhdl_log_path, self.compilation_warning_patterns)
            report.fatals   += self.rmh.search_file_for_patterns(report.vhdl_log_path, self.compilation_fatal_patterns)
        report.num_errors = len(report.errors)
        report.num_warnings = len(report.warnings)
        report.num_fatals = len(report.fatals)
        report.success &= (report.num_errors == 0) and (report.num_fatals == 0)

    def parse_elaboration_logs(self, ip: Ip, request: LogicSimulatorElaborationRequest, report: LogicSimulatorElaborationReport) -> None:
        report.errors   += self.rmh.search_file_for_patterns(report.log_path, self.elaboration_error_patterns)
        report.warnings += self.rmh.search_file_for_patterns(report.log_path, self.elaboration_warning_patterns)
        report.fatals   += self.rmh.search_file_for_patterns(report.log_path, self.elaboration_fatal_patterns)
        report.num_errors = len(report.errors)
        report.num_warnings = len(report.warnings)
        report.num_fatals = len(report.fatals)
        report.success &= (report.num_errors == 0) and (report.num_fatals == 0)

    def parse_compilation_and_elaboration_logs(self, ip: Ip, request: LogicSimulatorCompilationAndElaborationRequest, report: LogicSimulatorCompilationAndElaborationReport) -> None:
        report.errors   += self.rmh.search_file_for_patterns(report.log_path, self.compilation_and_elaboration_error_patterns)
        report.warnings += self.rmh.search_file_for_patterns(report.log_path, self.compilation_and_elaboration_warning_patterns)
        report.fatals   += self.rmh.search_file_for_patterns(report.log_path, self.compilation_and_elaboration_fatal_patterns)
        report.num_errors = len(report.errors)
        report.num_warnings = len(report.warnings)
        report.num_fatals = len(report.fatals)
        report.success &= (report.num_errors == 0) and (report.num_fatals == 0)

    def parse_simulation_logs(self, ip: Ip, request: LogicSimulatorSimulationRequest, report: LogicSimulatorSimulationReport) -> None:
        report.errors   += self.rmh.search_file_for_patterns(report.log_path, self.simulation_error_patterns)
        report.warnings += self.rmh.search_file_for_patterns(report.log_path, self.simulation_warning_patterns)
        report.fatals   += self.rmh.search_file_for_patterns(report.log_path, self.simulation_fatal_patterns)
        report.num_errors = len(report.errors)
        report.num_warnings = len(report.warnings)
        report.num_fatals = len(report.fatals)
        report.success &= (report.num_errors == 0) and (report.num_fatals == 0)

    def parse_encryption_logs(self, ip: Ip, request: LogicSimulatorEncryptionRequest, report: LogicSimulatorEncryptionReport) -> None:
        if report.sv_encryption_success and report.vhdl_encryption_success:
            report.success = True
        else:
            report.success = False

    def parse_merge_coverage_logs(self, ip: Ip, request: LogicSimulatorCoverageMergeRequest, report: LogicSimulatorCoverageMergeReport) -> None:
        report.errors   += self.rmh.search_file_for_patterns(report.merge_log_file_path, self.coverage_merge_error_patterns)
        report.warnings += self.rmh.search_file_for_patterns(report.merge_log_file_path, self.coverage_merge_warning_patterns)
        report.fatals   += self.rmh.search_file_for_patterns(report.merge_log_file_path, self.coverage_merge_fatal_patterns)
        report.num_errors = len(report.errors)
        report.num_warnings = len(report.warnings)
        report.num_fatals = len(report.fatals)
        report.success &= (report.num_errors == 0) and (report.num_fatals == 0)

    def build_sv_flist(self, ip:Ip,
                       request:Union[LogicSimulatorCompilationRequest, LogicSimulatorCompilationAndElaborationRequest],
                       report:Union[LogicSimulatorCompilationReport, LogicSimulatorCompilationAndElaborationReport]):
        has_files_to_compile:bool = False
        file_list = LogicSimulatorMasterFileList(name=ip.as_ip_definition)
        if request.has_custom_dut:
            file_list.has_custom_dut = True
            file_list.custom_dut_type = request.custom_dut_type
            file_list.custom_dut_name = request.custom_dut_name
            if request.use_relative_paths:
                for directory in request.custom_dut_directories:
                    file_list.custom_dut_directories.append(os.path.relpath(directory, request.start_path))
                for file in request.custom_dut_sv_files:
                    file_list.custom_dut_files.append(os.path.relpath(file, request.start_path))
            else:
                for directory in request.custom_dut_directories:
                    file_list.custom_dut_directories.append(str(directory))
                for file in request.custom_dut_sv_files:
                    file_list.custom_dut_files.append(str(file))
            file_list.custom_dut_defines_values = request.custom_dut_defines_values
            file_list.custom_dut_defines_boolean = request.custom_dut_defines_boolean
        for dep in report.ordered_dependencies:
            sub_file_list = LogicSimulatorFileList(name=dep.as_ip_definition)
            if dep.ip.mlicensed and dep.location_type == IpLocationType.PROJECT_INSTALLED:
                if self.name not in dep.resolved_encrypted_hdl_directories:
                    raise Exception(f"IP '{dep}' is licensed but has no encrypted SystemVerilog content defined for '{self.name}'")
                else:
                    file_list.needs_licensing = True
                    directories = dep.resolved_encrypted_hdl_directories[self.name]
                    files = dep.resolved_encrypted_top_sv_files[self.name]
            else:
                directories = dep.resolved_hdl_directories
                files = dep.resolved_top_sv_files
            for directory in directories:
                if request.use_relative_paths:
                    sub_file_list.directories.append(os.path.relpath(directory, request.start_path))
                else:
                    sub_file_list.directories.append(str(directory))
            for file in files:
                if request.use_relative_paths:
                    sub_file_list.files.append(os.path.relpath(file, request.start_path))
                else:
                    sub_file_list.files.append(str(file))
                has_files_to_compile = True
            file_list.sub_file_lists.append(sub_file_list)
        if ip.has_dut and ip.dut.type == DutType.MIO_IP:
            dut_target_name = ip.get_target_dut_target(request.target)
            file_list.defines_boolean.update(ip.resolved_dut.get_target_cmp_bool_defines(dut_target_name))
            file_list.defines_values.update(ip.resolved_dut.get_target_cmp_val_defines(dut_target_name))
        file_list.defines_boolean.update(ip.get_target_cmp_bool_defines(request.target))
        file_list.defines_values.update(ip.get_target_cmp_val_defines(request.target))
        if isinstance(request, LogicSimulatorCompilationRequest):
            for define in request.defines_boolean:
                file_list.defines_boolean[define] = True
            file_list.defines_values.update(request.defines_value)
        else:
            for define in request.defines_boolean:
                file_list.defines_boolean[define] = True
            file_list.defines_values.update(request.defines_value)
        if ip.ip.mlicensed and dep.location_type == IpLocationType.PROJECT_INSTALLED:
            if self.name not in ip.resolved_encrypted_hdl_directories:
                raise Exception(f"IP '{ip}' is licensed but has no encrypted SystemVerilog content defined for '{self.name}'")
            else:
                file_list.needs_licensing = True
                directories = ip.resolved_encrypted_hdl_directories[self.name]
                files = ip.resolved_encrypted_top_sv_files[self.name]
        else:
            directories = ip.resolved_hdl_directories
            files = ip.resolved_top_sv_files
        for directory in directories:
            if request.use_relative_paths:
                file_list.directories.append(os.path.relpath(directory, request.start_path))
            else:
                file_list.directories.append(str(directory))
        for file in files:
            if request.use_relative_paths:
                file_list.files.append(os.path.relpath(file, request.start_path))
            else:
                file_list.files.append(str(file))
            has_files_to_compile = True
        if isinstance(report, LogicSimulatorCompilationReport):
            report.has_sv_files_to_compile = has_files_to_compile
        else:
            report.has_files_to_compile = has_files_to_compile
        report.target_defines_boolean = file_list.defines_boolean
        report.target_defines_value = file_list.defines_values
        if has_files_to_compile:
            # Load the Jinja2 templates from disk
            template = self.rmh.j2_env.get_template(f"flist.sv.{self.name}.j2")
            # Render the templates with the master file lists
            if file_list.needs_licensing:
                licensing_sv_path = Path(os.path.join(self.rmh.data_files_path, f'mio_hdl_lic.{self.name}.sv'))
                if not self.rmh.file_exists(licensing_sv_path):
                    raise Exception(f"Cannot find License SystemVerilog file for {self.name}")
                if request.use_relative_paths:
                    file_list.licensing_sv_path = os.path.relpath(licensing_sv_path, request.start_path)
                else:
                    file_list.licensing_sv_path = str(licensing_sv_path)
            filelist_rendered = template.render(file_list.model_dump())
            # Save the rendered templates to disk
            flist_path = self.work_temp_path / f"{ip.result_file_name}.sv.{self.name}.flist"
            with open(flist_path, "w") as flist:
                flist.write(filelist_rendered)
            if isinstance(report, LogicSimulatorCompilationReport):
                report.sv_file_list_path = flist_path
            else:
                report.file_list_path = flist_path

    def build_vhdl_flist(self, ip:Ip, request:LogicSimulatorCompilationRequest, report:LogicSimulatorCompilationReport):
        file_list = LogicSimulatorMasterFileList(name=ip.as_ip_definition)
        if request.has_custom_dut:
            file_list.has_custom_dut = True
            file_list.custom_dut_type = request.custom_dut_type
            if request.use_relative_paths:
                for directory in request.custom_dut_directories:
                    file_list.custom_dut_directories.append(os.path.relpath(directory, request.start_path))
                for file in request.custom_dut_vhdl_files:
                    file_list.custom_dut_files.append(os.path.relpath(file, request.start_path))
            else:
                for directory in request.custom_dut_directories:
                    file_list.custom_dut_directories.append(str(directory))
                for file in request.custom_dut_vhdl_files:
                    file_list.custom_dut_files.append(str(file))
            file_list.custom_dut_defines_values = request.custom_dut_defines_values
            file_list.custom_dut_defines_boolean = request.custom_dut_defines_boolean
        target_name = request.target
        for dep in report.ordered_dependencies:
            sub_file_list = LogicSimulatorFileList(name=dep.as_ip_definition)
            if dep.ip.mlicensed and dep.location_type == IpLocationType.PROJECT_INSTALLED:
                if self.name not in dep.resolved_encrypted_hdl_directories:
                    raise Exception(f"IP '{dep}' is licensed but has no encrypted VHDL content defined for '{self.name}'")
                else:
                    file_list.needs_licensing = True
                    directories = dep.resolved_encrypted_hdl_directories[self.name]
                    files = dep.resolved_encrypted_top_vhdl_files[self.name]
            else:
                directories = dep.resolved_hdl_directories
                files = dep.resolved_top_vhdl_files
            for directory in directories:
                if request.use_relative_paths:
                    file_list.directories.append(os.path.relpath(directory, request.start_path))
                else:
                    file_list.directories.append(str(directory))
            for file in files:
                if request.use_relative_paths:
                    sub_file_list.files.append(os.path.relpath(file, request.start_path))
                else:
                    sub_file_list.files.append(str(file))
                report.has_vhdl_files_to_compile = True
            file_list.sub_file_lists.append(sub_file_list)
        if ip.has_dut and ip.dut.type == DutType.MIO_IP:
            dut_target_name = ip.get_target_dut_target(request.target)
            file_list.defines_boolean.update(ip.resolved_dut.get_target_cmp_bool_defines(dut_target_name))
            file_list.defines_values.update(ip.resolved_dut.get_target_cmp_val_defines(dut_target_name))
        file_list.defines_boolean.update(ip.get_target_cmp_bool_defines(request.target))
        file_list.defines_values.update(ip.get_target_cmp_val_defines(request.target))
        for define in request.defines_boolean:
            file_list.defines_boolean[define] = True
        file_list.defines_values.update(request.defines_value)
        if ip.ip.mlicensed and dep.location_type == IpLocationType.PROJECT_INSTALLED:
            if self.name not in ip.resolved_encrypted_hdl_directories:
                raise Exception(f"IP '{ip}' is licensed but has no encrypted VHDL content defined for '{self.name}'")
            else:
                file_list.needs_licensing = True
                directories = ip.resolved_encrypted_hdl_directories[self.name]
                files = ip.resolved_encrypted_top_vhdl_files[self.name]
        else:
            directories = ip.resolved_hdl_directories
            files = ip.resolved_top_vhdl_files
        for directory in directories:
            if request.use_relative_paths:
                file_list.directories.append(os.path.relpath(directory, request.start_path))
            else:
                file_list.directories.append(str(directory))
        for file in files:
            if request.use_relative_paths:
                file_list.files.append(os.path.relpath(file, request.start_path))
            else:
                file_list.files.append(str(file))
            report.has_vhdl_files_to_compile = True
        report.target_defines_boolean = file_list.defines_boolean
        report.target_defines_value = file_list.defines_values
        if report.has_vhdl_files_to_compile:
            # Load the Jinja2 templates from disk
            template = self.rmh.j2_env.get_template(f"flist.vhdl.{self.name}.j2")
            # Render the templates with the master file lists
            if file_list.needs_licensing:
                licensing_vhdl_path = Path(os.path.join(self.rmh.data_files_path, f'mio_hdl_lic.{self.name}.vhdl'))
                if not self.rmh.file_exists(licensing_vhdl_path):
                    raise Exception(f"Cannot find License VHDL file for {self.name}")
                if request.use_relative_paths:
                    file_list.licensing_vhdl_path = os.path.relpath(licensing_vhdl_path, request.start_path)
                else:
                    file_list.licensing_vhdl_path = str(licensing_vhdl_path)
            filelist_rendered = template.render(file_list.model_dump())
            # Save the rendered templates to disk
            flist_path = self.work_temp_path / f"{ip.result_file_name}.{self.name}.vhdl.flist"
            with open(flist_path, "w") as flist:
                flist.write(filelist_rendered)
            report.vhdl_file_list_path = flist_path

    def get_all_shared_objects(self, ip:Ip, request: LogicSimulatorRequest, ordered_dependencies:List[Ip]=None) -> List[Path]:
        needs_license_so = False
        shared_objects: List[Path] = []
        try:
            ip.resolve_shared_objects(self.name)
        except Exception as e:
            raise Exception(f"Failed to resolve shared objects for IP '{ip}': {e}")
        else:
            shared_objects = ip.resolved_shared_objects
        if not ordered_dependencies:
            dependencies = ip.get_dependencies_in_order()
        else:
            dependencies = ordered_dependencies
        for dep in dependencies:
            try:
                dep.resolve_shared_objects(self.name)
            except Exception as e:
                raise Exception(f"Failed to resolve shared objects for IP '{dep}': {e}")
            else:
                shared_objects += dep.resolved_shared_objects
        shared_objects = list(set(shared_objects))
        if request.use_relative_paths:
            relative_shared_objects: List[Path] = []
            for so in shared_objects:
                relative_so_path: Path = Path(os.path.relpath(so, request.start_path))
                relative_shared_objects.append(relative_so_path)
            shared_objects = relative_shared_objects
        if needs_license_so:
            lic_so_path = Path(os.path.join(self.rmh.data_files_path, f'mio_hdl_lic_dpi.{self.name}.so'))
            if not self.rmh.file_exists(lic_so_path):
                raise Exception(f"Cannot find License DPI for {self.name}")
            else:
                if request.use_relative_paths:
                    relative_lic_so_path: Path = Path(os.path.relpath(lic_so_path, request.start_path))
                    shared_objects.append(relative_lic_so_path)
                else:
                    shared_objects.append(lic_so_path)
                shared_objects.append(f"libcurl.so")
        return shared_objects

    @property
    @abstractmethod
    def library_creation_error_patterns(self) -> List[str]:
        pass
    
    @property
    @abstractmethod
    def library_creation_warning_patterns(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def library_creation_fatal_patterns(self) -> List[str]:
        pass
    
    @property
    @abstractmethod
    def compilation_error_patterns(self) -> List[str]:
        pass
    
    @property
    @abstractmethod
    def compilation_warning_patterns(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def compilation_fatal_patterns(self) -> List[str]:
        pass
    
    @property
    @abstractmethod
    def elaboration_error_patterns(self) -> List[str]:
        pass
    
    @property
    @abstractmethod
    def elaboration_warning_patterns(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def elaboration_fatal_patterns(self) -> List[str]:
        pass
    
    @property
    @abstractmethod
    def compilation_and_elaboration_error_patterns(self) -> List[str]:
        pass
    
    @property
    @abstractmethod
    def compilation_and_elaboration_warning_patterns(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def compilation_and_elaboration_fatal_patterns(self) -> List[str]:
        pass
    
    @property
    @abstractmethod
    def simulation_error_patterns(self) -> List[str]:
        pass
    
    @property
    @abstractmethod
    def simulation_warning_patterns(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def simulation_fatal_patterns(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def encryption_error_patterns(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def encryption_warning_patterns(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def encryption_fatal_patterns(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def coverage_merge_error_patterns(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def coverage_merge_warning_patterns(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def coverage_merge_fatal_patterns(self) -> List[str]:
        pass
    
    @abstractmethod
    def do_create_library(self, ip: Ip, request: LogicSimulatorLibraryCreationRequest, report: LogicSimulatorLibraryCreationReport, scheduler: JobScheduler, scheduler_config: JobSchedulerConfiguration):
        pass

    @abstractmethod
    def do_delete_library(self, ip: Ip, request: LogicSimulatorLibraryDeletionRequest, report: LogicSimulatorLibraryDeletionReport, scheduler: JobScheduler, scheduler_config: JobSchedulerConfiguration):
        pass

    @abstractmethod
    def do_compile(self, ip: Ip, request: LogicSimulatorCompilationRequest, report: LogicSimulatorCompilationReport, scheduler: JobScheduler, scheduler_config: JobSchedulerConfiguration):
        pass

    @abstractmethod
    def do_elaborate(self, ip: Ip, request: LogicSimulatorElaborationRequest, report: LogicSimulatorElaborationReport, scheduler: JobScheduler, scheduler_config: JobSchedulerConfiguration):
        pass

    @abstractmethod
    def do_compile_and_elaborate(self, ip: Ip, request: LogicSimulatorCompilationAndElaborationRequest, report: LogicSimulatorCompilationAndElaborationReport, scheduler: JobScheduler, scheduler_config: JobSchedulerConfiguration):
        pass

    @abstractmethod
    def do_simulate(self, ip: Ip, request: LogicSimulatorSimulationRequest, report: LogicSimulatorSimulationReport, scheduler: JobScheduler, scheduler_config: JobSchedulerConfiguration):
        pass

    @abstractmethod
    def get_view_waves_command(self, request: LogicSimulatorSimulationRequest, report: LogicSimulatorSimulationReport):
        pass

    @abstractmethod
    def do_encrypt(self, ip: Ip, request: LogicSimulatorEncryptionRequest, report: LogicSimulatorEncryptionReport, scheduler: JobScheduler, scheduler_config: JobSchedulerConfiguration):
        pass

    @abstractmethod
    def do_coverage_merge(self, ip: Ip, request: LogicSimulatorCoverageMergeRequest, report: LogicSimulatorCoverageMergeReport, scheduler: JobScheduler, scheduler_config: JobSchedulerConfiguration):
        pass



#######################################################################################################################
# Logic Simulator Implementation: Altair DSim
#######################################################################################################################
class DSimCloudSimulationState(Enum):
    BUILDING_JOB = "1/5 Building Job File"
    INIT_WORKSPACE = "2/5 Initializing workspace"
    SIMULATING = "3/5 Simulating Job File"
    DOWNLOADING_ARTIFACTS = "4/5 Downloading artifacts"
    PARSING_RESULTS = "5/5 Parsing simulation results"
    FINISHED = "Finished"

class DSimCloudWorkspaceStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DESTROYED = "destroyed"

class DSimConfigurationPackage(Model):
    name: str
    version: str

class DSimConfigurationToolchain(Model):
    environment_variables: Optional[Dict[str, str]] = {}
    packages: Optional[List[DSimConfigurationPackage]] = []
    dsim: Optional[Dict[str,str]] = {}

class DSimConfiguration(Model):
    toolchain: Optional[DSimConfigurationToolchain] = None
    @classmethod
    def load_from_yaml(cls, file_path: Path) -> 'DSimConfiguration':
        with open(file_path, 'r') as file:
            return cls.model_validate(yaml.safe_load(file))
    def save_to_yaml(self, file_path: Path):
        with open(file_path, 'w') as file:
            yaml.safe_dump(self.model_dump(), file)

class DSimCloudTaskResource(Model):
    name: str
    path: str

class DSimCloudTaskInputs(Model):
    working: List[DSimCloudTaskResource]

class DSimCloudTaskOutputs(Model):
    working: Optional[List[DSimCloudTaskResource]] = []
    artifacts: Optional[List[DSimCloudTaskResource]] = []

class DSimCloudTask(Model):
    name: str
    compute_size: Optional[str] = DSimCloudComputeSizes.S4.value
    depends: Optional[List[str]] = []
    commands: List[str]
    inputs: Optional[DSimCloudTaskInputs] = None
    outputs: DSimCloudTaskOutputs
    mdc_work: Optional[str] = "./"

class DSimCloudJob(Model):
    name: str
    keep_for_support: Optional[bool] = False
    tasks: List[DSimCloudTask]
    @classmethod
    def load_from_yaml(cls, file_path: Path) -> 'DSimCloudJob':
        with open(file_path, 'r') as file:
            return cls.model_validate(yaml.safe_load(file))
    def save_to_yaml(self, file_path: Path):
        with open(file_path, 'w') as file:
            model_data: Dict = self.model_dump(exclude_defaults=True)
            yaml.safe_dump(model_data, file)

class DSimCloudSimulationRequest:
    def __init__(self):
        self.name: str = ""
        self.dry_mode: bool = False
        self.timeout: float = 0
        self.max_parallel_tasks: int = 1
        self.results_path: Path = Path()
        self.compute_size: Optional[DSimCloudComputeSizes] = DSimCloudComputeSizes.S4
        self.compilation_config: LogicSimulatorCompilationRequest = None
        self.elaboration_config: LogicSimulatorElaborationRequest = None
        self.compilation_and_elaboration_config: LogicSimulatorCompilationAndElaborationRequest = None
        self.simulation_configs: List[LogicSimulatorSimulationRequest] = []

class DSimCloudSimulationReport(Model):
    success: Optional[bool] = False
    compilation_report: Optional[LogicSimulatorCompilationReport] = None
    elaboration_report: Optional[LogicSimulatorElaborationReport] = None
    compilation_and_elaboration_report: Optional[LogicSimulatorCompilationAndElaborationReport] = None
    simulation_reports: Optional[List[LogicSimulatorSimulationReport]] = []
    jobs: Optional[List[Job]] = []
    cloud_job: Optional[DSimCloudJob] = None
    cloud_job_file_path: Optional[Path] = Path()
    timestamp_start: Optional[datetime.datetime] = datetime.datetime.now()
    timestamp_end: Optional[datetime.datetime] = datetime.datetime.now()
    duration: Optional[datetime.timedelta] = datetime.timedelta()


class SimulatorMetricsDSim(LogicSimulator):
    def __init__(self, rmh: 'RootManager'):
        super().__init__(rmh, "Altair", "dsim", "DSim")
        self._cloud_mode: bool = False
        self._cloud_job: DSimCloudJob = None
        self._cloud_sim_task_cmp_elab: DSimCloudTask = None
        self._cloud_sim_tasks_simulate: List[DSimCloudTask] = []
        self._cloud_sim_state: DSimCloudSimulationState = DSimCloudSimulationState.BUILDING_JOB
        self._cloud_sim_installation_path: Path = Path()
        self._cloud_job_id: str = ""
        self._cloud_job_finished: bool = False
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        atexit.register(self.cleanup)
    
    @property
    def cloud_mode(self) -> bool:
        return self._cloud_mode
    @cloud_mode.setter
    def cloud_mode(self, value: bool):
        self._cloud_mode = value
        
    @property
    def cloud_sim_state(self) -> DSimCloudSimulationState:
        return self._cloud_sim_state
    @cloud_sim_state.setter
    def cloud_sim_state(self, value: DSimCloudSimulationState):
        self.rmh.debug(f"DSim Cloud Simulation State Change: '{self._cloud_sim_state}' -> '{value}'")
        self._cloud_sim_state = value
    
    @property
    def installation_path(self) -> Path:
        return self.rmh.configuration.logic_simulation.altair_dsim_installation_path
    @property
    def supports_vhdl(self) -> bool:
        return True
    @property
    def supports_verilog(self) -> bool:
        return True
    @property
    def supports_system_verilog(self) -> bool:
        return True
    @property
    def supports_one_step_simulation(self) -> bool:
        return True
    @property
    def supports_two_step_simulation(self) -> bool:
        return True
    @property
    def supports_uvm(self) -> bool:
        return True
    @property
    def latest_uvm_version_supported(self) -> Version:
        return Version("1.2")
    @property
    def oldest_uvm_version_supported(self) -> Version:
        return Version("1.1b")

    @property
    def library_creation_error_patterns(self) -> List[str]:
        return [r'^.*=E:.*$']
    @property
    def library_creation_warning_patterns(self) -> List[str]:
        return [r'^.*=W:.*$']
    @property
    def library_creation_fatal_patterns(self) -> List[str]:
        return [r'^.*=F:.*$']
    @property
    def compilation_error_patterns(self) -> List[str]:
        return [r'^.*=E:.*$']
    @property
    def compilation_warning_patterns(self) -> List[str]:
        return [r'^.*=W:.*$']
    @property
    def compilation_fatal_patterns(self) -> List[str]:
        return [r'^.*=F:.*$']
    @property
    def elaboration_error_patterns(self) -> List[str]:
        return [r'^.*=E:.*$']
    @property
    def elaboration_warning_patterns(self) -> List[str]:
        return [r'^.*=W:.*$']
    @property
    def elaboration_fatal_patterns(self) -> List[str]:
        return [r'^.*=F:.*$']
    @property
    def compilation_and_elaboration_error_patterns(self) -> List[str]:
        return [r'^.*=E:.*$']
    @property
    def compilation_and_elaboration_warning_patterns(self) -> List[str]:
        return [r'^.*=W:.*$']
    @property
    def compilation_and_elaboration_fatal_patterns(self) -> List[str]:
        return [r'^.*=F:.*$']
    @property
    def simulation_error_patterns(self) -> List[str]:
        return [r'^.*=E:.*$', r'^UVM_ERROR @.*$']
    @property
    def simulation_warning_patterns(self) -> List[str]:
        return [r'^.*=W:.*$', r'^UVM_WARNING @.*$']
    @property
    def simulation_fatal_patterns(self) -> List[str]:
        return [r'^.*=F:.*$', r'^UVM_FATAL @.*$']
    @property
    def encryption_error_patterns(self) -> List[str]:
        return [r'^.*=E:.*$']
    @property
    def encryption_warning_patterns(self) -> List[str]:
        return [r'^.*=W:.*$']
    @property
    def encryption_fatal_patterns(self) -> List[str]:
        return [r'^.*=F:.*$']
    @property
    def coverage_merge_error_patterns(self) -> List[str]:
        return [r'^.*=E:.*$']
    @property
    def coverage_merge_warning_patterns(self) -> List[str]:
        return [r'^.*=W:.*$']
    @property
    def coverage_merge_fatal_patterns(self) -> List[str]:
        return [r'^.*=F:.*$']

    def get_version(self) -> Version:
        # TODO Get version string from dsim
        return Version('1.0.0')

    def set_job_env(self, job:Job):
        dsim_home: str = f"{self.rmh.configuration.logic_simulation.altair_dsim_installation_path}"
        job.env_vars["DSIM_HOME"] = dsim_home
        job.env_vars["STD_LIBS"] = f"{dsim_home}/std_pkgs/lib"
        job.env_vars["RADFLEX_PATH"] = f"{dsim_home}/radflex"
        job.env_vars["LLVM_HOME"] = f"{dsim_home}/llvm_small"
        job.pre_path = f"{dsim_home}/bin:{dsim_home}/{self.rmh.configuration.logic_simulation.uvm_version.value}/bin:{dsim_home}/llvm_small/bin"
        job.env_vars["LD_LIBRARY_PATH"] = f"{dsim_home}/lib:" +"${LD_LIBRARY_PATH}:" + f"{dsim_home}/llvm_small/lib"
        job.env_vars["UVM_HOME"] = f"{dsim_home}/uvm/" + self.rmh.configuration.logic_simulation.uvm_version.value
        job.env_vars["DSIM_LICENSE"] = self.rmh.configuration.logic_simulation.altair_dsim_license_path

    def do_create_library(self, ip: Ip, request: LogicSimulatorLibraryCreationRequest, report: LogicSimulatorLibraryCreationReport, scheduler: JobScheduler, scheduler_config: JobSchedulerConfiguration):
        pass

    def do_delete_library(self, ip: Ip, request: LogicSimulatorLibraryDeletionRequest, report: LogicSimulatorLibraryDeletionReport, scheduler: JobScheduler, scheduler_config: JobSchedulerConfiguration):
        report.work_directory = self.work_path / f"{ip.work_directory_name}"
        if self.rmh.directory_exists(report.work_directory):
            self.rmh.remove_directory(report.work_directory)
        report.success = True

    def do_compile(self, ip: Ip, request: LogicSimulatorCompilationRequest, report: LogicSimulatorCompilationReport, scheduler: JobScheduler, scheduler_config: JobSchedulerConfiguration):
        defines_str = ""
        for define in report.user_defines_boolean:
            defines_str += f" +define+{define}"
        for define in report.user_defines_value:
            defines_str += f" +define+{define}={report.user_defines_value[define]}"
        so_str = ""
        if os.name == 'nt':  # DSim for Windows requires SOs at compile time
            for so in report.shared_objects:
                so_str += f" -sv_lib {so}"
        if report.has_vhdl_files_to_compile:
            if request.use_relative_paths:
                vhdl_file_list_path: str = str(os.path.relpath(report.vhdl_file_list_path, request.start_path))
                vhdl_log_path: str = str(os.path.relpath(report.vhdl_log_path, request.start_path))
            else:
                vhdl_file_list_path: str = str(report.vhdl_file_list_path)
                vhdl_log_path: str = str(report.vhdl_log_path)
            args = self.rmh.configuration.logic_simulation.altair_dsim_default_compilation_vhdl_arguments + [
                defines_str,
                f"-f {vhdl_file_list_path}",
                f"-uvm {self.rmh.configuration.logic_simulation.uvm_version.value}",
                so_str,
                f"-lib {ip.lib_name}",
                f"-l {vhdl_log_path}"
            ]
            job_cmp_vhdl = Job(self.rmh, report.work_directory, f"dsim_vhdl_compilation_{ip.lib_name}",
                               Path(os.path.join(self.installation_path, "bin", "dvhcom")), args)
            self.set_job_env(job_cmp_vhdl)
            if self.cloud_mode:
                self._cloud_sim_task_cmp_elab.commands.append(str(job_cmp_vhdl))
                self._cloud_sim_task_cmp_elab.outputs.artifacts.append(
                    DSimCloudTaskResource(name=f"cmp-vhdl-log", path=vhdl_log_path))
            else:
                report.jobs.append(job_cmp_vhdl)
                if request.log_vhdl_cmd:
                    job_cmp_vhdl.write_to_file(report.vhdl_cmd_log_file_path)
                results_cmp_vhdl = scheduler.dispatch_job(job_cmp_vhdl, scheduler_config)
                report.vhdl_compilation_success = (results_cmp_vhdl.return_code == 0)
                report.timestamp_start = results_cmp_vhdl.timestamp_start
                if not report.has_sv_files_to_compile:
                    report.timestamp_end = results_cmp_vhdl.timestamp_end
        else:
            report.vhdl_compilation_success = True
        if report.has_sv_files_to_compile:
            if request.use_relative_paths:
                sv_file_list_path: str = str(os.path.relpath(report.sv_file_list_path, request.start_path))
                sv_log_path: str = str(os.path.relpath(report.sv_log_path, request.start_path))
            else:
                sv_file_list_path: str = str(report.sv_file_list_path)
                sv_log_path: str = str(report.sv_log_path)
            args = self.rmh.configuration.logic_simulation.altair_dsim_default_compilation_sv_arguments + [
                defines_str,
                f"-f {sv_file_list_path}",
                f"-uvm {self.rmh.configuration.logic_simulation.uvm_version.value}",
                so_str,
                f"-lib {ip.lib_name}",
                f"-l {sv_log_path}"
            ]
            job_cmp_sv = Job(self.rmh, report.work_directory, f"dsim_sv_compilation_{ip.lib_name}",
                             Path(os.path.join(self.installation_path, "bin", "dvlcom")), args)
            self.set_job_env(job_cmp_sv)
            if self.cloud_mode:
                self._cloud_sim_task_cmp_elab.commands.append(str(job_cmp_sv))
                self._cloud_sim_task_cmp_elab.outputs.artifacts.append(
                    DSimCloudTaskResource(name=f"cmp-sv-log", path=sv_log_path))
            else:
                report.jobs.append(job_cmp_sv)
                if request.log_sv_cmd:
                    job_cmp_sv.write_to_file(report.sv_cmd_log_file_path)
                results_cmp_sv = scheduler.dispatch_job(job_cmp_sv, scheduler_config)
                report.sv_compilation_success = (results_cmp_sv.return_code == 0)
                if not report.has_vhdl_files_to_compile:
                    report.timestamp_start = results_cmp_sv.timestamp_start
                report.timestamp_end = results_cmp_sv.timestamp_end
        else:
            report.sv_compilation_success = True

    def do_elaborate(self, ip: Ip, request: LogicSimulatorElaborationRequest, report: LogicSimulatorElaborationReport, scheduler: JobScheduler, scheduler_config: JobSchedulerConfiguration):
        top_str = ""
        for top in ip.hdl_src.top:
            top_str = f"{top_str} -top {top}"
        if request.use_relative_paths:
            log_path = os.path.relpath(report.log_path, request.start_path)
        else:
            log_path = report.log_path
        args = self.rmh.configuration.logic_simulation.altair_dsim_default_elaboration_arguments + [
            f"-genimage {ip.lib_name}",
            f"-uvm {self.rmh.configuration.logic_simulation.uvm_version.value}",
            top_str,
            f"-lib {ip.lib_name}",
            f"-l {log_path}",
        ]
        job_elaborate = Job(self.rmh, report.work_directory, f"dsim_elaboration_{ip.lib_name}",
                            Path(os.path.join(self.installation_path, "bin", "dsim")), args)
        self.set_job_env(job_elaborate)
        if self.cloud_mode:
            self._cloud_sim_task_cmp_elab.commands.append(str(job_elaborate))
            self._cloud_sim_task_cmp_elab.outputs.artifacts.append(
                DSimCloudTaskResource(name=f"elab-log", path=log_path))
        else:
            report.jobs.append(job_elaborate)
            if request.log_cmd:
                job_elaborate.write_to_file(report.cmd_log_file_path)
            results_elaborate = scheduler.dispatch_job(job_elaborate, scheduler_config)
            report.elaboration_success = (results_elaborate.return_code == 0)
            report.timestamp_start = results_elaborate.timestamp_start
            report.timestamp_end = results_elaborate.timestamp_end

    def do_compile_and_elaborate(self, ip: Ip, request: LogicSimulatorCompilationAndElaborationRequest, report: LogicSimulatorCompilationAndElaborationReport, scheduler: JobScheduler, scheduler_config: JobSchedulerConfiguration):
        if not ip.has_vhdl_content:
            defines_str = ""
            for define in report.user_defines_boolean:
                defines_str += f" +define+{define}"
            for define in report.user_defines_value:
                defines_str += f" +define+{define}={report.user_defines_value[define]}"
            top_str = ""
            for top in ip.hdl_src.top:
                top_str = f"{top_str} -top {top}"
            so_str = ""
            if os.name == 'nt':  # DSim for Windows requires SOs at compile time
                for so in report.shared_objects:
                    so_str += f" -sv_lib {so}"
            if request.use_relative_paths:
                log_path = str(os.path.relpath(report.log_path, request.start_path))
            else:
                log_path = str(report.log_path)
            if request.use_relative_paths:
                file_list_path = str(os.path.relpath(report.file_list_path, request.start_path))
            else:
                file_list_path = str(report.file_list_path)
            args = self.rmh.configuration.logic_simulation.altair_dsim_default_compilation_and_elaboration_arguments + [
                f"-genimage {ip.lib_name}",
                defines_str,
                so_str,
                f"-f {file_list_path}",
                f"-uvm {self.rmh.configuration.logic_simulation.uvm_version.value}",
                top_str,
                f"-lib {ip.lib_name}",
                f"-l {log_path}"
            ]
            job_compile_and_elaborate = Job(self.rmh, report.work_directory,
                                      f"dsim_compilation_and_elaboration_{ip.lib_name}",
                                            Path(os.path.join(self.installation_path, "bin", "dsim")), args)
            self.set_job_env(job_compile_and_elaborate)
            if self.cloud_mode:
                self._cloud_sim_task_cmp_elab.commands.append(str(job_compile_and_elaborate))
                self._cloud_sim_task_cmp_elab.outputs.artifacts.append(
                    DSimCloudTaskResource(name=f"cmp-elab-log", path=log_path))
            else:
                report.jobs.append(job_compile_and_elaborate)
                if request.log_cmd:
                    job_compile_and_elaborate.write_to_file(report.cmd_log_file_path)
                results_compile_and_elaborate = scheduler.dispatch_job(job_compile_and_elaborate, scheduler_config)
                report.compilation_and_elaboration_success = (results_compile_and_elaborate.return_code == 0)
                report.timestamp_start = results_compile_and_elaborate.timestamp_start
                report.timestamp_end = results_compile_and_elaborate.timestamp_end
        else:
            raise Exception(f"Cannot perform Compilation+Elaboration with DSim for IPs containing VHDL content: IP '{ip}'")

    def do_simulate(self, ip: Ip, request: LogicSimulatorSimulationRequest, report: LogicSimulatorSimulationReport, scheduler: JobScheduler, scheduler_config: JobSchedulerConfiguration):
        args_str = ""
        for arg in report.args_boolean:
            args_str += f" +{arg}"
        for arg in report.args_value:
            args_str += f" +{arg}={report.args_value[arg]}"
        so_str = ""
        if self.cloud_mode or (os.name != 'nt'):  # DSim for Linux requires SOs at runtime
            for so in report.shared_objects:
                so_str += f" -sv_lib {so}"
        if request.use_relative_paths:
            log_path = os.path.relpath(report.log_path, request.start_path)
        else:
            log_path = report.log_path
        args = self.rmh.configuration.logic_simulation.altair_dsim_default_simulation_arguments + [
            f"-image {ip.lib_name}",
            args_str,
            so_str,
            f"-sv_seed {request.seed}",
            f"-uvm {self.rmh.configuration.logic_simulation.uvm_version.value}",
            #f"-sv_lib libcurl.so",
            f"-timescale {self.rmh.configuration.logic_simulation.timescale}",
            f"-l {log_path}"
        ]
        if request.enable_waveform_capture:
            if request.use_relative_paths:
                waveform_file_path = os.path.relpath(report.waveform_file_path, request.start_path)
            else:
                waveform_file_path = report.waveform_file_path
            args.append(f"-waves {waveform_file_path}.mxd")
        if request.enable_coverage:
            coverage_directory: Path = report.coverage_directory / "dsim.db"
            if request.use_relative_paths:
                coverage_directory = os.path.relpath(coverage_directory, request.start_path)
            else:
                coverage_directory = coverage_directory
            args.append(f"-code-cov a")
            args.append(f"-cov-db {coverage_directory}")
        else:
            args.append(f"-no-fcov")
        job_simulate: Job = Job(self.rmh, report.work_directory, f"dsim_simulation_{ip.lib_name}",
                                Path(os.path.join(self.installation_path, "bin", "dsim")), args)
        self.set_job_env(job_simulate)
        if self.cloud_mode:
            sim_task = min(self._cloud_sim_tasks_simulate, key=lambda task: len(task.commands), default=None)
            test_results_path_str: str = str(os.path.relpath(report.test_results_path, request.start_path))
            sim_task.outputs.artifacts.append(DSimCloudTaskResource(name=f"results-{request.seed}", path=test_results_path_str))
            sim_task.commands.append(str(job_simulate))
        else:
            report.jobs.append(job_simulate)
            if request.log_cmd:
                job_simulate.write_to_file(report.cmd_log_file_path)
            results_simulate = scheduler.dispatch_job(job_simulate, scheduler_config)
            report.simulation_success = (results_simulate.return_code == 0)
            report.timestamp_start = results_simulate.timestamp_start
            report.timestamp_end = results_simulate.timestamp_end

    def get_view_waves_command(self, request: LogicSimulatorSimulationRequest, report: LogicSimulatorSimulationReport):
        viewer_bin_path: Path = Path(os.path.join(self.rmh.configuration.logic_simulation.vscode_installation_path, "code"))
        return f"{viewer_bin_path} {report.waveform_file_path}"

    def do_encrypt(self, ip: Ip, request: LogicSimulatorEncryptionRequest, report: LogicSimulatorEncryptionReport, scheduler: JobScheduler, scheduler_config: JobSchedulerConfiguration):
        # TODO Add support for config.relative_paths=True
        if report.has_sv_files_to_encrypt:
            report.sv_encryption_success = True
            for file in report.sv_files_to_encrypt:
                file_encrypted = Path(f"{file}.encrypted")
                sv_args = []
                sv_args.append(str(file))
                sv_args.append(f"-i {self.rmh.configuration.encryption.altair_dsim_sv_key_path}")
                sv_args.append(f"-o {file_encrypted}")
                job_encrypt_sv = Job(self.rmh, report.work_directory, f"dsim_encryption_sv_{ip.lib_name}_{file.name}",
                                     Path(os.path.join(self.installation_path, "bin", "dvlencrypt")), sv_args)
                self.set_job_env(job_encrypt_sv)
                results_encrypt_sv = scheduler.dispatch_job(job_encrypt_sv, scheduler_config)
                report.sv_encryption_success &= (results_encrypt_sv.return_code == 0)
                if report.sv_encryption_success and os.path.isfile(file_encrypted) and os.path.getsize(file_encrypted) > 0:
                    with open(file, 'rb') as original_file, open(file_encrypted, 'rb') as encrypted_file:
                        if original_file.read() != encrypted_file.read():
                            self.rmh.move_file(file_encrypted, file)
                        else:
                            report.sv_encryption_success = False
                            raise Exception(f"Failed to encrypt file {file}")
                else:
                    report.sv_encryption_success = False
                    raise Exception(f"Failed to encrypt file {file}")
        else:
            report.sv_encryption_success = True
        if report.has_vhdl_files_to_encrypt:
            report.vhdl_encryption_success = True
            for file in report.vhdl_files_to_encrypt:
                file_encrypted = Path(f"{file}.encrypted")
                vhdl_args = []
                vhdl_args.append(str(file))
                vhdl_args.append(f"-i {self.rmh.configuration.encryption.altair_dsim_vhdl_key_path}")
                vhdl_args.append(f"-o {file_encrypted}")
                job_encrypt_vhdl = Job(self.rmh, report.work_directory, f"dsim_encryption_vhdl_{ip.lib_name}_{file.name}",
                                       Path(os.path.join(self.installation_path, "bin", "dvhencrypt")), vhdl_args)
                self.set_job_env(job_encrypt_vhdl)
                results_encrypt_vhdl = scheduler.dispatch_job(job_encrypt_vhdl, scheduler_config)
                report.vhdl_encryption_success &= (results_encrypt_vhdl.return_code == 0)
                if report.vhdl_encryption_success and os.path.isfile(file_encrypted) and os.path.getsize(file_encrypted) > 0:
                    with open(file, 'rb') as original_file, open(file_encrypted, 'rb') as encrypted_file:
                        if original_file.read() != encrypted_file.read():
                            self.rmh.move_file(file_encrypted, file)
                        else:
                            report.vhdl_encryption_success = False
                            raise Exception(f"Failed to encrypt file {file}")
                else:
                    report.vhdl_encryption_success = False
                    raise Exception(f"Failed to encrypt file {file}")
        else:
            report.vhdl_encryption_success = True
        report.timestamp_end = datetime.datetime.now()

    def do_coverage_merge(self, ip: Ip, request: LogicSimulatorCoverageMergeRequest, report: LogicSimulatorCoverageMergeReport, scheduler: JobScheduler, scheduler_config: JobSchedulerConfiguration):
        if len(request.input_simulation_reports) > 1:
            merged_db_path: Path = request.output_path / "coverage.db"
            if request.use_relative_paths:
                merged_db_path_str: str = str(os.path.relpath(merged_db_path, request.start_path))
            else:
                merged_db_path_str: str = str(merged_db_path)
            merge_args: List[str] = [
                f"-out_db {merged_db_path_str}"
            ]
            for simulation_report in request.input_simulation_reports:
                coverage_db_path: Path = simulation_report.coverage_directory / "dsim.db"
                if request.use_relative_paths:
                    coverage_db_path_str: str = str(os.path.relpath(coverage_db_path, request.start_path))
                else:
                    coverage_db_path_str: str = str(coverage_db_path)
                merge_args.append(coverage_db_path_str)
            job_merge: Job = Job(self.rmh, report.work_directory, f"dsim_coverage_merge_{ip.lib_name}",
                                 Path(os.path.join(self.installation_path, "bin", "dcmerge")), merge_args)
            self.set_job_env(job_merge)
            report.jobs.append(job_merge)
            results_merge = scheduler.dispatch_job(job_merge, scheduler_config)
            report.success = (results_merge.return_code == 0)
            input_db_path: Path = merged_db_path
        else:
            report.success = True
            input_db_path: Path = request.input_simulation_reports[0].coverage_directory / "dsim.db"
        if report.success:
            if request.use_relative_paths:
                input_db_path_str: str = str(os.path.relpath(input_db_path, request.start_path))
                html_report_path_str: str = str(os.path.relpath(request.html_report_path, request.start_path))
            else:
                input_db_path_str: str = str(input_db_path)
                html_report_path_str: str = str(request.html_report_path)
            report_args: List[str] = [
                f"-out_dir {html_report_path_str}",
                str(input_db_path_str)
            ]
            job_report: Job = Job(self.rmh, report.work_directory, f"dsim_coverage_report_{ip.lib_name}",
                                  Path(os.path.join(self.installation_path, "bin", "dcreport")), report_args)
            self.set_job_env(job_report)
            report.jobs.append(job_report)
            report.html_report_path = request.html_report_path
            report.html_report_index_path = report.html_report_path / "index.html"
            results_report = scheduler.dispatch_job(job_report, scheduler_config)
            report.success &= (results_report.return_code == 0)
            report.timestamp_end = results_report.timestamp_end

    def dsim_cloud_simulate(self, ip: Ip, cloud_simulation_request: DSimCloudSimulationRequest, scheduler: JobScheduler) -> DSimCloudSimulationReport:
        self._cloud_sim_installation_path = self.rmh.configuration.logic_simulation.altair_dsim_cloud_installation_path
        # 1. Initialize report
        report: DSimCloudSimulationReport = DSimCloudSimulationReport()
        config_report_map: Dict[LogicSimulatorSimulationReport, LogicSimulatorSimulationRequest] = {}
        # 2. Create top-level Job object
        job_data: Dict = {
            'name': cloud_simulation_request.name,
            'tasks': []
        }
        self._cloud_job = DSimCloudJob(**job_data)
        # 3. Build compilation/elaboration tasks
        task_cmp_elab_data: Dict = {
            'name': 'cmp-elab',
            'commands': [],
            'outputs': {}
        }
        self._cloud_sim_task_cmp_elab: DSimCloudTask = DSimCloudTask(**task_cmp_elab_data)
        self._cloud_job.tasks.append(self._cloud_sim_task_cmp_elab)
        self._cloud_sim_task_cmp_elab.compute_size = cloud_simulation_request.compute_size.value
        self._cloud_sim_task_cmp_elab.inputs = DSimCloudTaskInputs(working=[])
        self._cloud_sim_task_cmp_elab.outputs = DSimCloudTaskOutputs()
        self._cloud_sim_task_cmp_elab.outputs.working.append(
            DSimCloudTaskResource(name="image", path=f"./dsim_work/{ip.lib_name}.so"))
        self._cloud_sim_task_cmp_elab.outputs.working.append(
            DSimCloudTaskResource(name="source", path="./"))
        # 4. Build simulation tasks
        data_files_path_str: str = str(os.path.relpath(self.rmh.data_files_path, self.rmh.project_root_path))
        sim_results_path_str: str = str(os.path.relpath(cloud_simulation_request.results_path, self.rmh.project_root_path))
        for ii in range(cloud_simulation_request.max_parallel_tasks):
            sim_task_name: str = f"sim-{ii}"
            task_sim_data: Dict = {
                'name': sim_task_name,
                'depends': ['cmp-elab'],
                'commands': [],
                'outputs': {}
            }
            sim_task: DSimCloudTask = DSimCloudTask(**task_sim_data)
            self._cloud_sim_tasks_simulate.append(sim_task)
            sim_task.compute_size = cloud_simulation_request.compute_size.value
            sim_task.inputs = DSimCloudTaskInputs(working=[])
            sim_task.inputs.working.append(
                DSimCloudTaskResource(name="cmp-elab.image", path=f"./dsim_work/{ip.lib_name}.so"))
            sim_task.inputs.working.append(
                DSimCloudTaskResource(name="cmp-elab.source", path="./"))
            sim_task.outputs = DSimCloudTaskOutputs()
        for simulation_config in cloud_simulation_request.simulation_configs:
            simulation_config.use_relative_paths = True
            simulation_config.start_path = self.rmh.project_root_path
            simulation_config.use_custom_logs_path = True
            simulation_config.custom_logs_path = cloud_simulation_request.results_path
            simulation_report = self.simulate(ip, simulation_config, scheduler)
            report.simulation_reports.append(simulation_report)
            config_report_map[simulation_report] = simulation_config
        for sim_task in self._cloud_sim_tasks_simulate:
            if len(sim_task.commands) > 0:
                self._cloud_job.tasks.append(sim_task)
        # 5. Accumulate compilation/elaboration commands
        if ip.has_vhdl_content:
            cloud_simulation_request.compilation_config.use_relative_paths = True
            cloud_simulation_request.compilation_config.start_path = self.rmh.project_root_path
            cloud_simulation_request.compilation_config.use_custom_logs_path = True
            cloud_simulation_request.compilation_config.custom_logs_path = cloud_simulation_request.results_path
            report.compilation_report = self.compile(ip, cloud_simulation_request.compilation_config, scheduler)
            cloud_simulation_request.elaboration_config.use_relative_paths = True
            cloud_simulation_request.elaboration_config.start_path = self.rmh.project_root_path
            cloud_simulation_request.elaboration_config.use_custom_logs_path = True
            cloud_simulation_request.elaboration_config.custom_logs_path = cloud_simulation_request.results_path
            report.elaboration_report = self.elaborate(ip, cloud_simulation_request.elaboration_config, scheduler)
        else:
            cloud_simulation_request.compilation_and_elaboration_config.use_relative_paths = True
            cloud_simulation_request.compilation_and_elaboration_config.start_path = self.rmh.project_root_path
            cloud_simulation_request.compilation_and_elaboration_config.use_custom_logs_path = True
            cloud_simulation_request.compilation_and_elaboration_config.custom_logs_path = cloud_simulation_request.results_path
            report.compilation_and_elaboration_report = self.compile_and_elaborate(ip, cloud_simulation_request.compilation_and_elaboration_config, scheduler)
        # 6. Initialize workspace
        self.cloud_sim_state = DSimCloudSimulationState.INIT_WORKSPACE
        workspace_status: DSimCloudWorkspaceStatus = self.dsim_cloud_workspace_status(ip, cloud_simulation_request, report, scheduler)
        if workspace_status != DSimCloudWorkspaceStatus.ACTIVE:
            self.dsim_cloud_init_workspace(ip, cloud_simulation_request, report, scheduler)
        # 7. Submit job to cloud
        report.cloud_job_file_path = self.work_temp_path / f"{cloud_simulation_request.name}.yaml"
        self._cloud_job.save_to_yaml(report.cloud_job_file_path)
        if cloud_simulation_request.dry_mode:
            report.success = True
        else:
            self.cloud_sim_state = DSimCloudSimulationState.SIMULATING
            report.timestamp_start = datetime.datetime.now()
            self._cloud_job_id = self.dsim_cloud_submit_job(ip, cloud_simulation_request, report, scheduler)
            # 8. Timeout
            with ThreadPoolExecutor() as executor:
                future = executor.submit(self.dsim_cloud_job_status_wait, self._cloud_job_id, ip, cloud_simulation_request, report, scheduler)
                try:
                    future.result(timeout=cloud_simulation_request.timeout * 3600)
                except TimeoutError:
                    self.dsim_cloud_job_kill(self._cloud_job_id, ip, cloud_simulation_request, report, scheduler)
                    raise TimeoutError(
                        f"DSim Cloud Simulation '{cloud_simulation_request.name}' exceeded {cloud_simulation_request.timeout} hour(s).")
            report.timestamp_end = datetime.datetime.now()
            report.duration = report.timestamp_end - report.timestamp_start
            # 9. Download artifacts
            self.cloud_sim_state = DSimCloudSimulationState.DOWNLOADING_ARTIFACTS
            self.dsim_cloud_job_download(self._cloud_job_id, ip, cloud_simulation_request, report, scheduler)
            # 10. Parse logs
            self.cloud_sim_state = DSimCloudSimulationState.PARSING_RESULTS
            report.success = True
            if ip.has_vhdl_content:
                self.parse_compilation_logs(ip, cloud_simulation_request.compilation_config, report.compilation_report)
                self.parse_elaboration_logs(ip, cloud_simulation_request.elaboration_config, report.elaboration_report)
                report.success &= report.compilation_report.success
                report.success &= report.elaboration_report.success
            else:
                self.parse_compilation_and_elaboration_logs(ip, cloud_simulation_request.compilation_and_elaboration_config, report.compilation_and_elaboration_report)
            for simulation_report in report.simulation_reports:
                simulation_report.timestamp_start = report.timestamp_start
                simulation_report.timestamp_end = report.timestamp_end
                simulation_report.duration = (simulation_report.timestamp_end - simulation_report.timestamp_start) / len(report.simulation_reports)
                simulation_config = config_report_map[simulation_report]
                self.parse_simulation_logs(ip, simulation_config, simulation_report)
                report.success &= simulation_report.success
            self.cloud_sim_state = DSimCloudSimulationState.FINISHED
        return report

    def dsim_cloud_init_workspace(self, ip: Ip, request: DSimCloudSimulationRequest, report: DSimCloudSimulationReport, scheduler: JobScheduler):
        scheduler_config: JobSchedulerConfiguration = JobSchedulerConfiguration(self.rmh)
        scheduler_config.output_to_terminal = self.rmh.print_trace
        args: List[str] = [
            "init",
            "--local-only"
        ]
        job: Job = Job(self.rmh, self.rmh.project_root_path, f"dsim_workspace_init",
                       Path(os.path.join(self._cloud_sim_installation_path, "mdc")), args)
        report.jobs.append(job)
        results: JobResults = scheduler.dispatch_job(job, scheduler_config)
        if results.return_code != 0:
            raise Exception(f"Failed to initialize DSim Workspace:\n{results.stderr}\n{results.stdout}")
        else:
            stdout: str = results.stdout.lower()
            if "initialized local workspace in" not in stdout:
                raise Exception(f"Failed to initialize DSim Workspace:\n{results.stdout}")

    def dsim_cloud_workspace_status(self, ip: Ip, request: DSimCloudSimulationRequest, report: DSimCloudSimulationReport, scheduler: JobScheduler) -> DSimCloudWorkspaceStatus:
        scheduler_config: JobSchedulerConfiguration = JobSchedulerConfiguration(self.rmh)
        scheduler_config.output_to_terminal = self.rmh.print_trace
        args: List[str] = [
            "status"
        ]
        job: Job = Job(self.rmh, self.rmh.project_root_path, f"dsim_workspace_status",
                       Path(os.path.join(self._cloud_sim_installation_path, "mdc")), args)
        report.jobs.append(job)
        results: JobResults = scheduler.dispatch_job(job, scheduler_config)
        if results.return_code != 0:
            stderr: str = results.stderr.lower()
            if "you must be authenticated to dsim cloud in order to execute this command" in stderr:
                raise Exception(f"Not authenticated with DSim Cloud: run `mdc auth login`")
            elif "this is not a dsim cloud workspace" in stderr:
                return DSimCloudWorkspaceStatus.DESTROYED
            else:
                raise Exception(f"Failed to check status for DSim Workspace:\n{results.stderr}\n{results.stdout}")
        else:
            stdout: str = results.stdout.lower()
            if ('local workspace:' in stdout) and ('dsim cloud jobs:' in stdout):
                return DSimCloudWorkspaceStatus.ACTIVE
            else:
                if 'this is not a dsim cloud workspace.' in stdout:
                    return DSimCloudWorkspaceStatus.DESTROYED
                else:
                    return DSimCloudWorkspaceStatus.PAUSED

    def dsim_cloud_submit_job(self, ip: Ip, request: DSimCloudSimulationRequest, report: DSimCloudSimulationReport, scheduler: JobScheduler) -> str:
        scheduler_config: JobSchedulerConfiguration = JobSchedulerConfiguration(self.rmh)
        scheduler_config.output_to_terminal = self.rmh.print_trace
        scheduler_config.kill_job_on_termination = False
        verbosity_str: str = ""
        if self.rmh.print_trace:
            verbosity_str = f"--verbose"
        cloud_job_file_path_str: str = str(os.path.relpath(report.cloud_job_file_path, self.rmh.project_root_path))
        args: List[str] = [
            "job",
            "submit",
            cloud_job_file_path_str,
            #verbosity_str
        ]
        job: Job = Job(self.rmh, self.rmh.project_root_path, f"dsim_cloud_job_submit",
                       Path(os.path.join(self._cloud_sim_installation_path, "mdc")), args)
        report.jobs.append(job)
        results: JobResults = scheduler.dispatch_job(job, scheduler_config)
        if results.return_code != 0:
            raise Exception(f"Failed to submit DSim cloud job:\n{results.stderr}\n{results.stdout}")
        else:
            stdout: str = results.stdout.lower()
            if "job submitted." in stdout:
                job_id_match: re.Match[str] = re.search(r'job id:\s*(\S+)$', stdout)
                if job_id_match:
                    job_id: str = job_id_match.group(1).replace("\\n", "").strip()
                    return job_id
                else:
                    raise Exception(f"Job ID not found in the DSim Cloud submission response: {results.stdout}")
            else:
                raise Exception(f"Failure in DSim Cloud submission response: {results.stdout}")

    def dsim_cloud_job_status_wait(self, job_id: str, ip: Ip, request: DSimCloudSimulationRequest, report: DSimCloudSimulationReport, scheduler: JobScheduler):
        scheduler_config: JobSchedulerConfiguration = JobSchedulerConfiguration(self.rmh)
        scheduler_config.output_to_terminal = self.rmh.print_trace
        args: List[str] = [
            "job",
            "status",
            job_id,
            "--watch",
            "--exit-code"
        ]
        job: Job = Job(self.rmh, self.rmh.project_root_path, f"dsim_job_status_wait_{job_id}",
                       Path(os.path.join(self._cloud_sim_installation_path, "mdc")), args)
        report.jobs.append(job)
        results: JobResults = scheduler.dispatch_job(job, scheduler_config)
        if results.return_code != 0:
            raise Exception(
                f"Failed DSim Cloud job - ID '{job_id}':\n{results.stderr}\n{results.stdout}")
        self._cloud_job_finished = True
        report.timestamp_start = results.timestamp_start
        report.timestamp_end = results.timestamp_end
        report.duration = report.timestamp_end - report.timestamp_start

    def dsim_cloud_job_download(self, job_id: str, ip: Ip, request: DSimCloudSimulationRequest, report: DSimCloudSimulationReport, scheduler: JobScheduler):
        scheduler_config: JobSchedulerConfiguration = JobSchedulerConfiguration(self.rmh)
        scheduler_config.output_to_terminal = self.rmh.print_trace
        destination_path: Path = self.work_temp_path / request.name
        self.rmh.create_directory(destination_path)
        args: List[str] = [
            "job",
            "download",
            job_id,
            '--accept-prompts',
            '--extract',
            f'--destination {destination_path}'
        ]
        job: Job = Job(self.rmh, self.rmh.project_root_path, f"dsim_job_download_{job_id}",
                       Path(os.path.join(self._cloud_sim_installation_path, "mdc")), args)
        report.jobs.append(job)
        results: JobResults = scheduler.dispatch_job(job, scheduler_config)
        if results.return_code != 0:
            raise Exception(
                f"Failed to download artifacts for DSim cloud job id '{job_id}':\n{results.stderr}\n{results.stdout}")
        else:
            cmp_elab_task_downloaded_artifacts_path: Path = destination_path / "cmp-elab-log"
            if ip.has_vhdl_content:
                cmp_vhdl_log_path: Path = cmp_elab_task_downloaded_artifacts_path / report.compilation_report.vhdl_log_path.name
                self.rmh.move_file(cmp_vhdl_log_path, report.compilation_report.vhdl_log_path)
                if ip.has_sv_content:
                    cmp_sv_log_path: Path = cmp_elab_task_downloaded_artifacts_path / report.compilation_report.sv_log_path.name
                    self.rmh.move_file(cmp_sv_log_path, report.compilation_report.sv_log_path)
            else:
                cmp_elab_log_path: Path = cmp_elab_task_downloaded_artifacts_path / report.compilation_and_elaboration_report.log_path.name
                self.rmh.move_file(cmp_elab_log_path, report.compilation_and_elaboration_report.log_path)
            for sim_config in request.simulation_configs:
                sim_task_downloaded_artifacts_path: Path = destination_path / f"results-{sim_config.seed}"
                if self.rmh.directory_exists(sim_task_downloaded_artifacts_path):
                    for item in sim_task_downloaded_artifacts_path.iterdir():
                        if item.is_dir():
                            sim_results_destination = request.results_path / item.name
                            self.rmh.move_directory(item, sim_results_destination, True)
        self.rmh.remove_directory(destination_path)

    def dsim_cloud_job_kill(self, job_id: str, ip: Ip, request: DSimCloudSimulationRequest, report: DSimCloudSimulationReport, scheduler: JobScheduler):
        scheduler_config: JobSchedulerConfiguration = JobSchedulerConfiguration(self.rmh)
        scheduler_config.output_to_terminal = self.rmh.print_trace
        args: List[str] = [
            "job",
            "kill",
            job_id
        ]
        job: Job = Job(self.rmh, self.rmh.project_root_path, f"dsim_job_kill_{job_id}",
                       Path(os.path.join(self._cloud_sim_installation_path, "mdc")), args)
        report.jobs.append(job)
        results: JobResults = scheduler.dispatch_job(job, scheduler_config)
        if results.return_code != 0:
            raise Exception(f"Failed to kill DSim cloud job id '{job_id}':\n{results.stderr}\n{results.stdout}")

    def parse_compilation_logs(self, ip: Ip, request: LogicSimulatorCompilationRequest, report: LogicSimulatorCompilationReport) -> None:
        if self.cloud_mode:
            if self.cloud_sim_state == DSimCloudSimulationState.PARSING_RESULTS:
                report.success = True
                super().parse_compilation_logs(ip, request, report)
        else:
            super().parse_compilation_logs(ip, request, report)
    
    def parse_elaboration_logs(self, ip: Ip, request: LogicSimulatorElaborationRequest, report: LogicSimulatorElaborationReport) -> None:
        if self.cloud_mode:
            if self.cloud_sim_state == DSimCloudSimulationState.PARSING_RESULTS:
                report.success = True
                super().parse_elaboration_logs(ip, request, report)
        else:
            super().parse_elaboration_logs(ip, request, report)

    def parse_compilation_and_elaboration_logs(self, ip: Ip, request: LogicSimulatorCompilationAndElaborationRequest, report: LogicSimulatorCompilationAndElaborationReport) -> None:
        if self.cloud_mode:
            if self.cloud_sim_state == DSimCloudSimulationState.PARSING_RESULTS:
                report.success = True
                super().parse_compilation_and_elaboration_logs(ip, request, report)
        else:
            super().parse_compilation_and_elaboration_logs(ip, request, report)

    def parse_simulation_logs(self, ip: Ip, request: LogicSimulatorSimulationRequest, report: LogicSimulatorSimulationReport) -> None:
        if self.cloud_mode:
            if self.cloud_sim_state == DSimCloudSimulationState.PARSING_RESULTS:
                report.success = True
                super().parse_simulation_logs(ip, request, report)
        else:
            super().parse_simulation_logs(ip, request, report)

    def _handle_signal(self, signum, frame):
        self.cleanup()
        #raise SystemExit(0)

    def cleanup(self):
        if self.cloud_mode and (not self._cloud_job_finished) and (self._cloud_job_id != ""):
            scheduler = self.rmh.scheduler_database.get_default_scheduler()
            scheduler_config: JobSchedulerConfiguration = JobSchedulerConfiguration(self.rmh)
            scheduler_config.output_to_terminal = self.rmh.print_trace
            scheduler_config.kill_job_on_termination = False
            args: List[str] = [
                "job",
                "kill",
                self._cloud_job_id
            ]
            job: Job = Job(self.rmh, self.rmh.project_root_path, f"dsim_job_kill_{self._cloud_job_id}",
                           Path(os.path.join(self._cloud_sim_installation_path, "mdc")), args)
            results: JobResults = scheduler.dispatch_job(job, scheduler_config)
            if results.return_code != 0:
                self.rmh.error(f"Failed to kill DSim cloud job id '{self._cloud_job_id}':\n{results.stderr}\n{results.stdout}")


#######################################################################################################################
# Logic Simulator Implementation: Xilinx Vivado (TM)
#######################################################################################################################
class SimulatorXilinxVivado(LogicSimulator):
    def __init__(self, rmh: 'RootManager'):
        super().__init__(rmh, "Xilinx", "vivado", "Vivado")

    @property
    def installation_path(self) -> Path:
        return self.rmh.configuration.logic_simulation.xilinx_vivado_installation_path
    @property
    def supports_vhdl(self) -> bool:
        return True
    @property
    def supports_verilog(self) -> bool:
        return True
    @property
    def supports_system_verilog(self) -> bool:
        return True
    @property
    def supports_one_step_simulation(self) -> bool:
        return False
    @property
    def supports_two_step_simulation(self) -> bool:
        return False
    @property
    def supports_uvm(self) -> bool:
        return True
    @property
    def latest_uvm_version_supported(self) -> Version:
        return Version("1.2")
    @property
    def oldest_uvm_version_supported(self) -> Version:
        return Version("1.2")

    @property
    def library_creation_error_patterns(self) -> List[str]:
        return [r'^.*ERROR:.*$']

    @property
    def library_creation_warning_patterns(self) -> List[str]:
        return [r'^.*WARNING:.*$']

    @property
    def library_creation_fatal_patterns(self) -> List[str]:
        return [r'^.*FATAL:.*$']

    @property
    def compilation_error_patterns(self) -> List[str]:
        return [r'^.*ERROR:.*$', r'^.*CRITICAL WARNING:.*$']

    @property
    def compilation_warning_patterns(self) -> List[str]:
        return [r'^.*WARNING:.*$']

    @property
    def compilation_fatal_patterns(self) -> List[str]:
        return [r'^.*FATAL:.*$']

    @property
    def elaboration_error_patterns(self) -> List[str]:
        return [r'^.*ERROR:.*$', r'^.*Invalid path for DPI library:.*$']

    @property
    def elaboration_warning_patterns(self) -> List[str]:
        return [r'^.*WARNING:.*$']

    @property
    def elaboration_fatal_patterns(self) -> List[str]:
        return [r'^.*FATAL:.*$']

    @property
    def compilation_and_elaboration_error_patterns(self) -> List[str]:
        return [r'^.*ERROR:.*$', r'^.*CRITICAL WARNING:.*$', r'^.*Invalid path for DPI library:.*$']

    @property
    def compilation_and_elaboration_warning_patterns(self) -> List[str]:
        return [r'^.*WARNING:.*$']

    @property
    def compilation_and_elaboration_fatal_patterns(self) -> List[str]:
        return [r'^.*FATAL:.*$']

    @property
    def simulation_error_patterns(self) -> List[str]:
        return [r'^.ERROR:.*$', r'^UVM_ERROR @.*$']

    @property
    def simulation_warning_patterns(self) -> List[str]:
        return [r'^.WARNING:.*$', r'^UVM_WARNING @.*$']

    @property
    def simulation_fatal_patterns(self) -> List[str]:
        return [r'^.*FATAL:.*$', r'^UVM_FATAL @.*$']

    @property
    def encryption_error_patterns(self) -> List[str]:
        return [r'^.*ERROR:.*$']

    @property
    def encryption_warning_patterns(self) -> List[str]:
        return [r'^.*WARNING:.*$']

    @property
    def encryption_fatal_patterns(self) -> List[str]:
        return [r'^.*FATAL:.*$']

    @property
    def coverage_merge_error_patterns(self) -> List[str]:
        return [r'^.*ERROR:.*$']

    @property
    def coverage_merge_warning_patterns(self) -> List[str]:
        return [r'^.*WARNING:.*$']

    @property
    def coverage_merge_fatal_patterns(self) -> List[str]:
        return [r'^.*FATAL:.*$']

    def get_version(self) -> Version:
        # TODO Get version string from vivado
        return Version('1.0.0')

    def do_create_library(self, ip: Ip, request: LogicSimulatorLibraryCreationRequest,
                          report: LogicSimulatorLibraryCreationReport, scheduler: JobScheduler,
                          scheduler_config: JobSchedulerConfiguration):
        pass

    def do_delete_library(self, ip: Ip, request: LogicSimulatorLibraryDeletionRequest,
                          report: LogicSimulatorLibraryDeletionReport, scheduler: JobScheduler,
                          scheduler_config: JobSchedulerConfiguration):
        report.work_directory = self.work_path / f"{ip.work_directory_name}"
        if self.rmh.directory_exists(report.work_directory):
            self.rmh.remove_directory(report.work_directory)
        report.success = True

    def do_compile(self, ip: Ip, request: LogicSimulatorCompilationRequest,
                   report: LogicSimulatorCompilationReport, scheduler: JobScheduler,
                   scheduler_config: JobSchedulerConfiguration):
        defines_str: str = ""
        # Getting around Vivado bug where it ignores defines within filelists
        target_defines_boolean: List[str] = []
        for define_boolean in report.target_defines_boolean:
            if report.target_defines_boolean[define_boolean]:
                target_defines_boolean.append(define_boolean)
        all_defines_boolean = target_defines_boolean + report.user_defines_boolean
        for define in all_defines_boolean:
            defines_str += f" -d {define}"
        all_defines_value: Dict[str, str] = {}
        all_defines_value.update(report.target_defines_value)
        all_defines_value.update(report.user_defines_value)
        for define in all_defines_value:
            defines_str += f" -d {define}={all_defines_value[define]}"
        if report.has_vhdl_files_to_compile:
            if request.use_relative_paths:
                vhdl_file_list_path: str = str(os.path.relpath(report.vhdl_file_list_path, request.start_path))
                vhdl_log_path: str = str(os.path.relpath(report.vhdl_log_path, request.start_path))
            else:
                vhdl_file_list_path: str = str(report.vhdl_file_list_path)
                vhdl_log_path: str = str(report.vhdl_log_path)
            args = self.rmh.configuration.logic_simulation.xilinx_vivado_default_compilation_vhdl_arguments + [
                defines_str,
                f"-f {vhdl_file_list_path}",
                f"-L uvm",
                f"--uvm_version {self.rmh.configuration.logic_simulation.uvm_version.value}",
                f"--work {ip.lib_name}",
                f"--log {vhdl_log_path}"
            ]
            # Adding verbosity to Vivado for compilation causes it to hang! (Code below)
            #if self.rmh.print_trace:
            #    args.append(f"--verbose 2")
            job_cmp_vhdl = Job(self.rmh, report.work_directory, f"vivado_vhdl_compilation_{ip.lib_name}",
                               Path(os.path.join(self.installation_path, "bin", "xvhdl")), args)
            report.jobs.append(job_cmp_vhdl)
            if request.log_vhdl_cmd:
                job_cmp_vhdl.write_to_file(report.vhdl_cmd_log_file_path)
            results_cmp_vhdl = scheduler.dispatch_job(job_cmp_vhdl, scheduler_config)
            report.vhdl_compilation_success = (results_cmp_vhdl.return_code == 0)
            report.timestamp_start = results_cmp_vhdl.timestamp_start
            if not report.has_sv_files_to_compile:
                report.timestamp_end = results_cmp_vhdl.timestamp_end
        else:
            report.vhdl_compilation_success = True
        if report.has_sv_files_to_compile:
            if request.use_relative_paths:
                sv_file_list_path: str = str(os.path.relpath(report.sv_file_list_path, request.start_path))
                sv_log_path: str = str(os.path.relpath(report.sv_log_path, request.start_path))
            else:
                sv_file_list_path: str = str(report.sv_file_list_path)
                sv_log_path: str = str(report.sv_log_path)
            args = self.rmh.configuration.logic_simulation.xilinx_vivado_default_compilation_sv_arguments + [
                defines_str,
                f"-sv",
                f"-f {sv_file_list_path}",
                f"-L uvm",
                f"--uvm_version {self.rmh.configuration.logic_simulation.uvm_version.value}",
                f"--work {ip.lib_name}",
                f"--log {sv_log_path}"
            ]
            # Adding verbosity to Vivado for compilation causes it to hang! (Code below)
            #if self.rmh.print_trace:
            #    args.append(f"--verbose 2")
            job_cmp_sv = Job(self.rmh, report.work_directory, f"vivado_sv_compilation_{ip.lib_name}",
                             Path(os.path.join(self.installation_path, "bin", "xvlog")), args)
            report.jobs.append(job_cmp_sv)
            if request.log_sv_cmd:
                job_cmp_sv.write_to_file(report.sv_cmd_log_file_path)
            results_cmp_sv = scheduler.dispatch_job(job_cmp_sv, scheduler_config)
            report.sv_compilation_success = (results_cmp_sv.return_code == 0)
            if not report.has_vhdl_files_to_compile:
                report.timestamp_start = results_cmp_sv.timestamp_start
            report.timestamp_end = results_cmp_sv.timestamp_end
        else:
            report.sv_compilation_success = True

    def do_elaborate(self, ip: Ip, request: LogicSimulatorElaborationRequest,
                     report: LogicSimulatorElaborationReport, scheduler: JobScheduler,
                     scheduler_config: JobSchedulerConfiguration):
        so_str = ""
        for so in report.shared_objects:
            so_local_copy_path: Path = self.work_path / so.name
            self.rmh.copy_file(so, so_local_copy_path)
            so_str += f" -sv_lib {so_local_copy_path.name}"
        top_str = ""
        for top in ip.hdl_src.top:
            top_str = f"{top_str} {ip.lib_name}.{top}"
        if request.use_relative_paths:
            log_path = os.path.relpath(report.log_path, request.start_path)
        else:
            log_path = report.log_path
        args = self.rmh.configuration.logic_simulation.xilinx_vivado_default_elaboration_arguments + [
            f"-timescale {self.rmh.configuration.logic_simulation.timescale}",
            f"--log {log_path}",
            f"-s {ip.lib_name}",
            f"-L {ip.lib_name}",
            top_str,
            f"-sv_root {self.work_path}",
            so_str,
        ]
        job_elaborate = Job(self.rmh, report.work_directory, f"vivado_elaboration_{ip.lib_name}",
                            Path(os.path.join(self.installation_path, "bin", "xelab")), args)
        report.jobs.append(job_elaborate)
        if request.log_cmd:
            job_elaborate.write_to_file(report.cmd_log_file_path)
        results_elaborate = scheduler.dispatch_job(job_elaborate, scheduler_config)
        report.elaboration_success = (results_elaborate.return_code == 0)
        report.timestamp_start = results_elaborate.timestamp_start
        report.timestamp_end = results_elaborate.timestamp_end

    def do_compile_and_elaborate(self, ip: Ip, request: LogicSimulatorCompilationAndElaborationRequest,
                                 report: LogicSimulatorCompilationAndElaborationReport, scheduler: JobScheduler,
                                 scheduler_config: JobSchedulerConfiguration):
        raise Exception(
            f"Cannot perform Compilation+Elaboration with Vivado: IP '{ip}'")

    def do_simulate(self, ip: Ip, request: LogicSimulatorSimulationRequest,
                    report: LogicSimulatorSimulationReport, scheduler: JobScheduler,
                    scheduler_config: JobSchedulerConfiguration):
        args_str = ""
        for arg in report.args_boolean:
            args_str += f" -testplusarg {arg}"
        for arg in report.args_value:
            args_str += f" -testplusarg {arg}={report.args_value[arg]}"
        if request.use_relative_paths:
            log_path = os.path.relpath(report.log_path, request.start_path)
        else:
            log_path = report.log_path
        args = self.rmh.configuration.logic_simulation.xilinx_vivado_default_simulation_arguments + [
            args_str,
            f"--log {log_path}"
        ]
        if request.gui_mode:
            args.append(f"--gui")
        if (not request.gui_mode) and request.enable_waveform_capture:
            waves_tcl_script_path: Path = report.test_results_path / "waves.vivado.tcl"
            with open(waves_tcl_script_path, 'w') as file:
                file.write("log_wave -recursive *\nrun -all\nquit\n")
            if request.use_relative_paths:
                waveform_file_path = os.path.relpath(report.waveform_file_path, request.start_path)
                waves_tcl_script_path_str: str = os.path.relpath(waves_tcl_script_path, request.start_path)
            else:
                waveform_file_path = report.waveform_file_path
                waves_tcl_script_path_str: str = str(waves_tcl_script_path)
            args.append(f"-wdb {waveform_file_path}.wdb")
            args.append(f"--tclbatch {waves_tcl_script_path_str}")
        else:
            args.append("--runall")
            args.append("--onerror quit")
        if request.enable_coverage:
            if request.use_relative_paths:
                coverage_directory = os.path.relpath(report.coverage_directory, request.start_path)
            else:
                coverage_directory = report.coverage_directory
            args.append(f"-cov_db_name {ip.lib_name}")
            args.append(f"-cov_db_dir {coverage_directory}")
        else:
            args.append("-ignore_coverage")
        args.append(f"{ip.lib_name}")
        args.append(f"-sv_seed {request.seed}")
        job_simulate: Job = Job(self.rmh, report.work_directory, f"vivado_simulation_{ip.lib_name}",
                                Path(os.path.join(self.installation_path, "bin", "xsim")), args)
        report.jobs.append(job_simulate)
        if request.log_cmd:
            job_simulate.write_to_file(report.cmd_log_file_path)
        results_simulate = scheduler.dispatch_job(job_simulate, scheduler_config)
        report.simulation_success = (results_simulate.return_code == 0)
        report.timestamp_start = results_simulate.timestamp_start
        report.timestamp_end = results_simulate.timestamp_end

    def get_view_waves_command(self, request: LogicSimulatorSimulationRequest, report: LogicSimulatorSimulationReport):
        viewer_bin_path: Path = Path(os.path.join(self.installation_path, "bin", "xsim"))
        return f"{viewer_bin_path} -gui {report.waveform_file_path}"

    def do_encrypt(self, ip: Ip, request: LogicSimulatorEncryptionRequest,
                   report: LogicSimulatorEncryptionReport, scheduler: JobScheduler,
                   scheduler_config: JobSchedulerConfiguration):
        if report.has_vhdl_files_to_encrypt:
            tcl_script_vhdl_path: Path = self.work_temp_path / f"{ip.lib_name}_encrypt_vhdl.vivado.tcl"
            if request.use_relative_paths:
                tcl_script_vhdl_path_str: str = os.path.relpath(tcl_script_vhdl_path, request.start_path)
            else:
                tcl_script_vhdl_path_str: str = str(tcl_script_vhdl_path)
            tcl_script_vhdl_str: str = f"encrypt -key {self.rmh.configuration.encryption.xilinx_vivado_key_path} -lang vhdl"
            report.vhdl_encryption_success = True
            vhdl_encrypted_file_map: Dict[Path, Path] = {}
            for file in report.vhdl_files_to_encrypt:
                file_encrypted: Path = Path(f"{file}.encrypted")
                self.rmh.copy_file(file, file_encrypted)
                vhdl_encrypted_file_map[file] = file_encrypted
                if request.use_relative_paths:
                    file_path_str: str = os.path.relpath(file_encrypted, request.start_path)
                else:
                    file_path_str: str = str(file_encrypted)
                tcl_script_vhdl_str += f" {file_path_str}"
            with open(tcl_script_vhdl_path, 'w') as tcl_vhdl_file:
                tcl_vhdl_file.write(tcl_script_vhdl_str)
            vhdl_args: List[str] = [
                "-mode batch",
                f"-source {tcl_script_vhdl_path_str}"
            ]
            job_encrypt_vhdl = Job(self.rmh, report.work_directory,
                                   f"vivado_encryption_vhdl_{ip.lib_name}",
                                   Path(os.path.join(self.installation_path, "bin", "vivado")), vhdl_args)
            results_encrypt_vhdl = scheduler.dispatch_job(job_encrypt_vhdl, scheduler_config)
            report.vhdl_encryption_success &= (results_encrypt_vhdl.return_code == 0)
            if report.vhdl_encryption_success:
                for file in vhdl_encrypted_file_map:
                    file_encrypted = vhdl_encrypted_file_map[file]
                    if os.path.isfile(file_encrypted) and os.path.getsize(file_encrypted) > 0:
                        with open(file, 'rb') as original_file, open(file_encrypted, 'rb') as encrypted_file:
                            if original_file.read() != encrypted_file.read():
                                self.rmh.move_file(file_encrypted, file)
                            else:
                                report.vhdl_encryption_success = False
                                raise Exception(f"Failed to encrypt file {file}")
            else:
                raise Exception(f"Failed to encrypt VHDL files")
        else:
            report.vhdl_encryption_success = True
        if report.has_sv_files_to_encrypt:
            tcl_script_sv_path: Path = self.work_temp_path / f"{ip.lib_name}_encrypt_sv.vivado.tcl"
            if request.use_relative_paths:
                tcl_script_sv_path_str: str = os.path.relpath(tcl_script_sv_path, request.start_path)
            else:
                tcl_script_sv_path_str: str = str(tcl_script_sv_path)
            tcl_script_sv_str: str = f"encrypt -key {self.rmh.configuration.encryption.xilinx_vivado_key_path} -lang ver"
            report.sv_encryption_success = True
            sv_encrypted_file_map: Dict[Path, Path] = {}
            for file in report.sv_files_to_encrypt:
                file_encrypted: Path = Path(f"{file}.encrypted")
                self.rmh.copy_file(file, file_encrypted)
                sv_encrypted_file_map[file] = file_encrypted
                if request.use_relative_paths:
                    file_path_str: str = os.path.relpath(file_encrypted, request.start_path)
                else:
                    file_path_str: str = str(file_encrypted)
                tcl_script_sv_str += f" {file_path_str}"
            with open(tcl_script_sv_path, 'w') as tcl_sv_file:
                tcl_sv_file.write(tcl_script_sv_str)
            sv_args: List[str] = [
                "-mode batch",
                f"-source {tcl_script_sv_path_str}"
            ]
            job_encrypt_sv = Job(self.rmh, report.work_directory,
                                 f"vivado_encryption_sv_{ip.lib_name}",
                                 Path(os.path.join(self.installation_path, "bin", "vivado")), sv_args)
            results_encrypt_sv = scheduler.dispatch_job(job_encrypt_sv, scheduler_config)
            report.sv_encryption_success &= (results_encrypt_sv.return_code == 0)
            if report.sv_encryption_success:
                for file in sv_encrypted_file_map:
                    file_encrypted = sv_encrypted_file_map[file]
                    if os.path.isfile(file_encrypted) and os.path.getsize(file_encrypted) > 0:
                        with open(file, 'rb') as original_file, open(file_encrypted, 'rb') as encrypted_file:
                            if original_file.read() != encrypted_file.read():
                                self.rmh.move_file(file_encrypted, file)
                            else:
                                report.vhdl_encryption_success = False
                                raise Exception(f"Failed to encrypt file {file}")
            else:
                raise Exception(f"Failed to encrypt SystemVerilog files")
        else:
            report.sv_encryption_success = True
        report.timestamp_end = datetime.datetime.now()

    def do_coverage_merge(self, ip: Ip, request: LogicSimulatorCoverageMergeRequest,
                          report: LogicSimulatorCoverageMergeReport, scheduler: JobScheduler,
                          scheduler_config: JobSchedulerConfiguration):
        merged_db_path: Path = request.output_path
        if request.use_relative_paths:
            merged_db_path_str: str = os.path.relpath(merged_db_path, request.start_path)
            merge_log_path_str: str = os.path.relpath(request.merge_log_file_path, request.start_path)
            html_report_path_str: str = os.path.relpath(request.html_report_path, request.start_path)
        else:
            merged_db_path_str: str = str(merged_db_path)
            merge_log_path_str: str = str(request.merge_log_file_path)
            html_report_path_str: str = str(request.html_report_path)
        merge_args: List[str] = [
            f"-log {merge_log_path_str}"
        ]
        if len(request.input_simulation_reports) > 1:
            merge_args.append(f"-merge_dir {merged_db_path_str}")
            merge_args.append(f"-merge_db_name {ip.lib_name}")
        for simulation_report in request.input_simulation_reports:
            if request.use_relative_paths:
                sim_cov_path_str: str = os.path.relpath(simulation_report.coverage_directory, request.start_path)
            else:
                sim_cov_path_str: str = str(simulation_report.coverage_directory)
            merge_args.append(f" -dir {sim_cov_path_str}")
        if request.create_html_report:
            merge_args.append(f"-report_format html")
            merge_args.append(f"-report_dir {html_report_path_str}")
        job_merge_report: Job = Job(self.rmh, report.work_directory, f"vivado_coverage_merge_{ip.lib_name}",
                                    Path(os.path.join(self.installation_path, "bin", "xcrg")), merge_args)
        report.jobs.append(job_merge_report)
        results_merge_report = scheduler.dispatch_job(job_merge_report, scheduler_config)
        report.success = (results_merge_report.return_code == 0)
        report.html_report_path = request.html_report_path
        report.html_report_index_path = Path(os.path.join(report.html_report_path, "functionalCoverageReport", "dashboard.html"))
        report.has_merge_log = True
        report.merge_log_file_path = request.merge_log_file_path
        report.timestamp_start = results_merge_report.timestamp_start
        report.timestamp_end = results_merge_report.timestamp_end

