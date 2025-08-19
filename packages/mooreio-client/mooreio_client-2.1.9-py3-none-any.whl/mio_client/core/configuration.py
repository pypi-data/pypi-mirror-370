# Copyright 2020-2025 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
from typing import List, Optional

from pydantic import BaseModel, constr, FilePath, PositiveInt, PositiveFloat, conlist, StrictInt
from .model import Model, VALID_NAME_REGEX, VALID_LOGIC_SIMULATION_TIMESCALE_REGEX, \
    VALID_POSIX_PATH_REGEX, VALID_POSIX_DIR_NAME_REGEX, UNDEFINED_CONST, PosixPathList, PosixPath, PosixDirName
from enum import Enum



class UvmVersions(Enum):
    V_1_2 = "1.2"
    V_1_1d = "1.1d"
    V_1_1c = "1.1c"
    V_1_1b = "1.1b"
    V_1_1a = "1.1a"
    V_1_0 = "1.0"


class LogicSimulators(Enum):
    UNDEFINED = UNDEFINED_CONST
    DSIM = "dsim"
    VIVADO = "vivado"
    VCS = "vcs"
    XCELIUM = "xcelium"
    QUESTA = "questa"
    RIVIERA = "riviera"
    #UNDEFINED = "!Undefined!"
    #DSIM = "Altair DSim"
    #VIVADO = "Xilinx Vivado"
    #VCS = "Synopsys VCS"
    #XCELIUM = "Cadence XCelium"
    #QUESTA = "Siemens QuestaSim"
    #RIVIERA = "Aldec Riviera-PRO"

class DSimCloudComputeSizes(Enum):
    S4 = "s4"
    S8 = "s8"


class Project(Model):
    sync: Optional[bool] = False
    sync_id: Optional[StrictInt] = -1
    local_mode: bool
    name: Optional[constr(pattern=VALID_NAME_REGEX)] = UNDEFINED_CONST
    full_name: Optional[str] = UNDEFINED_CONST
    description: Optional[str] = UNDEFINED_CONST


class Authentication(Model):
    offline: bool
    server_url: str
    server_api_url: str


class Applications(Model):
    editor: PosixPath
    web_browser: PosixPath


class LogicSimulation(Model):
    root_path: PosixPath
    regression_directory_name: PosixDirName
    results_directory_name: PosixDirName
    logs_directory: PosixDirName
    test_result_path_template: str
    uvm_version: UvmVersions
    timescale: constr(pattern=VALID_LOGIC_SIMULATION_TIMESCALE_REGEX)
    compilation_timeout: PositiveFloat
    elaboration_timeout: PositiveFloat
    compilation_and_elaboration_timeout: PositiveFloat
    simulation_timeout: PositiveFloat
    vscode_installation_path: Optional[PosixPath] = UNDEFINED_CONST
    altair_dsim_license_path: Optional[PosixPath] = UNDEFINED_CONST
    altair_dsim_cloud_max_compute_size: Optional[DSimCloudComputeSizes] = DSimCloudComputeSizes.S4
    altair_dsim_installation_path: Optional[PosixPath] = UNDEFINED_CONST
    altair_dsim_cloud_installation_path: Optional[PosixPath] = UNDEFINED_CONST
    xilinx_vivado_installation_path: Optional[PosixPath] = UNDEFINED_CONST
    altair_dsim_default_compilation_sv_arguments: List[str] = []
    xilinx_vivado_default_compilation_sv_arguments: List[str] = []
    altair_dsim_default_compilation_vhdl_arguments: List[str] = []
    xilinx_vivado_default_compilation_vhdl_arguments: List[str] = []
    altair_dsim_default_elaboration_arguments: List[str] = []
    xilinx_vivado_default_elaboration_arguments: List[str] = []
    altair_dsim_default_compilation_and_elaboration_arguments: List[str] = []
    altair_dsim_default_simulation_arguments: List[str] = []
    xilinx_vivado_default_simulation_arguments: List[str] = []
    default_simulator: Optional[LogicSimulators] = LogicSimulators.UNDEFINED


class LogicSynthesis(Model):
    root_path: PosixPath


class Linting(Model):
    root_path: PosixPath


class Ip(Model):
    global_paths: PosixPathList = []
    local_paths: PosixPathList


class PackageManagement(Model):
    fsoc_cores_global_paths: PosixPathList = []
    fsoc_cores_local_paths: PosixPathList = []


class Docs(Model):
    root_path: PosixPath
    doxygen_installation_path: Optional[PosixPath] = UNDEFINED_CONST


class Encryption(Model):
    altair_dsim_sv_key_path: Optional[PosixPath] = UNDEFINED_CONST
    altair_dsim_vhdl_key_path: Optional[PosixPath] = UNDEFINED_CONST
    xilinx_vivado_key_path: Optional[PosixPath] = UNDEFINED_CONST


class Configuration(Model):
    """
    Model for mio.toml configuration files.
    """
    project: Project
    package_management: PackageManagement
    logic_simulation: LogicSimulation
    logic_synthesis: LogicSynthesis
    lint: Linting
    ip: Ip
    docs: Docs
    encryption: Encryption
    authentication: Authentication
    applications: Applications

    def check(self):
        pass
