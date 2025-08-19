# Copyright 2020-2025 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional

import fusesoc.main
import yaml

from mio_client.core.configuration import LogicSimulators
from mio_client.core.scheduler import JobScheduler, Job, JobSchedulerConfiguration
from mio_client.core.service import Service, ServiceType
from mio_client.core.ip import Ip
from mio_client.core.model import Model
from semantic_version import Version


#######################################################################################################################
# API Entry Point
#######################################################################################################################
def get_services():
    return [FuseSocService]


#######################################################################################################################
# Support Classes
#######################################################################################################################
class FuseSocSetupCoreRequest(Model):
    core_name: str
    system_name: str
    target: str
    simulator: LogicSimulators

class FuseSocSetupCoreReport(Model):
    success: bool
    tool_name: str
    build_path: Path
    eda_file_path: Optional[Path] = Path()
    directories: List[Path]
    sv_files: List[Path]
    vhdl_files: List[Path]
    defines_values: Dict[str, str]
    defines_boolean: List[str]
    errors: List[str]
    warnings: List[str]
    infos: List[str]

class FuseSocFindCoreRequest(Model):
    core_name: str
    system_name: str

class FuseSocFindCoreReport(Model):
    found: bool
    location: Path


#######################################################################################################################
# Service
#######################################################################################################################
class FuseSocService(Service):
    def __init__(self, rmh: 'RootManager'):
        super().__init__(rmh, 'Olof Kindgren', 'fsoc', 'FuseSoC')
        self._type = ServiceType.PACKAGE_MANAGEMENT
        self._work_path = self.rmh.md / "fsoc"
        self._build_root = self._work_path / "build"
        self._cores_paths = []

    def is_available(self) -> bool:
        try:
            import fusesoc.main
            return True
        except Exception as e:
            self.rmh.warning(f"FuseSoC could not be imported. Please install it using 'pip install fusesoc': {e}")
            return False

    def create_directory_structure(self):
        self.rmh.create_directory(self._work_path)
        self.rmh.create_directory(self._build_root)

    def create_files(self):
        pass

    def get_version(self) -> Version:
        # TODO
        return Version('0.0.0')

    @property
    def work_path(self) -> Path:
        return self._work_path
    @property
    def build_root(self) -> Path:
        return self._build_root

    def map_simulator_to_tool_name(self, simulator: LogicSimulators) -> str:
        if simulator == LogicSimulators.DSIM:
            return "xsim"
        elif simulator == LogicSimulators.VIVADO:
            return "xsim"
        elif simulator == LogicSimulators.XCELIUM:
            return "xcelium"
        elif simulator == LogicSimulators.QUESTA:
            return "modelsim"
        elif simulator == LogicSimulators.VCS:
            return "vcs"
        else:
            return "xsim"

    def map_simulator_to_tool_binaries(self, simulator: LogicSimulators) -> List[str]:
        if simulator == LogicSimulators.DSIM:
            return ["xelab"]
        elif simulator == LogicSimulators.VIVADO:
            return ["xelab"]
        elif simulator == LogicSimulators.XCELIUM:
            return []
        elif simulator == LogicSimulators.QUESTA:
            return []
        elif simulator == LogicSimulators.VCS:
            return []
        else:
            return []

    def core_setup_eda_yaml_file_path(self, request: FuseSocSetupCoreRequest, suffix: str= "") -> Path:
        tool_name:str = self.map_simulator_to_tool_name(request.simulator)
        eda_file_name: str = f"{request.system_name.replace(':','_')}{suffix}"
        eda_file_directory_path: Path = self._build_root / eda_file_name / f"{request.target}-{tool_name}"
        eda_final_file_name: str = f"{eda_file_name}.eda.yml"
        eda_file_path: Path = eda_file_directory_path / eda_final_file_name
        return eda_file_path

    def load_core_setup_eda_yaml(self, eda_file_path: Path) -> dict:
        """Parse the FuseSoC generated .eda.yml file"""
        import yaml
        if not eda_file_path.exists():
            raise FileNotFoundError(f"EDA file not found at {eda_file_path}")
        with open(eda_file_path, 'r') as f:
            return yaml.safe_load(f)

    def parse_core_setup_eda_yaml_define(self, request:FuseSocSetupCoreRequest, option:str, results:FuseSocSetupCoreReport):
        define_boolean_regex = ""
        define_value_regex = ""
        if request.simulator in [LogicSimulators.DSIM, LogicSimulators.VIVADO]:
            define_boolean_regex = re.compile(r'^--define\s+(\S+)$')
            define_value_regex = re.compile(r'^--define\s+(\S+)\s*=\s*(\S+)$')
        else:
            define_boolean_regex = re.compile(r'^\+define\+(\S+)$')
            define_value_regex = re.compile(r'^\+define\+(\S+)=(\S+)$')
        match = re.match(define_value_regex, option)
        if match:
            key = match.group(1)
            value = match.group(2)
            results.defines_values[key] = value
        else:
            match = re.match(define_boolean_regex, option)
            if match:
                boolean_name = match.group(1)
                results.defines_boolean.append(boolean_name)


    def parse_eda_data(self, request: FuseSocSetupCoreRequest, results: FuseSocSetupCoreReport):
        # Prep
        results.eda_file_path = self.core_setup_eda_yaml_file_path(request)
        results_dir:Path = results.eda_file_path.parent
        if not results.eda_file_path.exists():
            # HACK Don't know why this is needed
            results.eda_file_path = self.core_setup_eda_yaml_file_path(request, "_0")
            if not results.eda_file_path.exists():
                raise FileNotFoundError(f"EDA file not found at {results.eda_file_path}")
        eda_data: Dict = self.load_core_setup_eda_yaml(results.eda_file_path)
        # Extract files
        directories:Dict[str] = {}
        for file_entry in eda_data.get('files', []):
            file_type = file_entry.get('file_type', '').lower()
            file_name = file_entry.get('name', '')
            file_path:Path = results_dir / file_name
            if file_type == 'systemVerilogSource'.lower():
                results.sv_files.append(file_path.absolute())
                directories[str(file_path.parent.absolute())] = True
            elif file_type == 'vhdlSource'.lower():
                results.vhdl_files.append(file_path.absolute())
                directories[str(file_path.parent.absolute())] = True
            if 'include_path' in file_entry:
                include_path: Path = results_dir / file_entry['include_path']
                directories[str(include_path.absolute())] = True
        # Extract directories
        for directory in directories:
            results.directories.append(directory)
        # Extract defines
        tool_options = eda_data.get('tool_options', {})
        if results.tool_name in tool_options:
            tool_binaries: List[str] = self.map_simulator_to_tool_binaries(request.simulator)
            for binary in tool_binaries:
                binary_full_name: str = f"{binary}_options"
                if binary_full_name in tool_options[results.tool_name]:
                    for option in tool_options[results.tool_name][binary_full_name]:
                        self.parse_core_setup_eda_yaml_define(request, option.strip(), results)
        parameters = eda_data.get('parameters', {})
        for param in parameters:
            parameter = parameters[param]
            if parameter['paramtype'] in ['vlogdefine', 'vhdldefine']:
                if (parameter['datatype'] == 'bool') and (parameter['default']):
                    results.defines_boolean.append(param)
                # TODO Support other FuseSoC core parameter types

    def setup_core(self, request: FuseSocSetupCoreRequest) -> FuseSocSetupCoreReport:
        tool_name:str = self.map_simulator_to_tool_name(request.simulator)
        report: FuseSocSetupCoreReport = FuseSocSetupCoreReport(
            success=False, infos=[], warnings=[], errors=[], build_path=self._build_root.absolute(), tool_name=tool_name,
            directories=[], sv_files=[], vhdl_files=[], defines_values={}, defines_boolean=[]
        )
        core_paths = []
        for path in self.rmh.configuration.package_management.fsoc_cores_global_paths:
            core_paths.append(str(path.absolute()))
        for path in self.rmh.configuration.package_management.fsoc_cores_local_paths:
            core_paths.append(str((self.rmh.project_root_path / path).absolute()))
        try:
            # Invoke FuseSoC
            raw_args = []
            for path in core_paths:
                raw_args.append("--cores-root")
                raw_args.append(f"{path}")
            raw_args.append("run")
            raw_args.append(f"--tool={tool_name}")
            raw_args.append(f"--target={request.target}")
            raw_args.append(f"--system={request.system_name}")
            raw_args.append(f"--build-root={self._build_root.absolute()}")
            raw_args.append("--no-export")
            raw_args.append("--setup")
            raw_args.append(request.core_name)
            if not self.rmh.print_trace:
                sys.stdout = open(os.devnull, 'w')
            args = fusesoc.main.parse_args(raw_args)
            fusesoc.main.fusesoc(args)
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            report.errors.append(str(e))
        else:
            # FuseSoC .eda.yml file parsing
            try:
                self.parse_eda_data(request, report)
            except Exception as e:
                report.errors.append(str(e))
            else:
                report.success = True
        return report

    def find_core(self, request: FuseSocFindCoreRequest) -> FuseSocFindCoreReport:
        results: FuseSocFindCoreReport = FuseSocFindCoreReport(
            found=True, location=self.work_path.absolute()
        )
        # TODO
        return results

