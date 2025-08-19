# Copyright 2020-2025 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
import base64
import os
import tarfile
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from http import HTTPMethod
from io import BytesIO
from pathlib import Path
from typing import Optional, List, Union, Any, Dict, Literal

import yaml
from pydantic import constr, PositiveInt, ValidationError
from semantic_version import SimpleSpec

from .model import Model, VALID_NAME_REGEX, VALID_IP_OWNER_NAME_REGEX, VALID_FSOC_NAMESPACE_REGEX, \
    VALID_POSIX_PATH_REGEX, UNDEFINED_CONST, PosixPath, PosixPathList, HdlNameList, HdlName, OrgName

from enum import Enum

from .version import SemanticVersion, SemanticVersionSpec
from .configuration import Ip, LogicSimulators
from .service import ServiceType


#######################################################################################################################
# Support Types
#######################################################################################################################
MAX_DEPTH_DEPENDENCY_INSTALLATION = 50

class IpPkgType(Enum):
    DV_LIBRARY = "dv_lib"
    DV_AGENT = "dv_agent"
    DV_ENV = "dv_env"
    DV_TB = "dv_tb"
    LIBRARY = "lib"
    BLOCK = "block"
    SS = "ss"
    FPGA = "fpga"
    CHIP = "chip"
    SYSTEM = "system"
    CUSTOM = "custom"

class DutType(Enum):
    MIO_IP = "ip"
    FUSE_SOC = "fsoc"
    VIVADO = "vivado"

class ParameterType(Enum):
    INT = "int"
    BOOL = "bool"

class IpLocationType(Enum):
    PROJECT_USER = "local"
    PROJECT_INSTALLED = "installed"
    GLOBAL = "global"

class IpLicenseType(Enum):
    PUBLIC_OPEN_SOURCE = "public_open_source"
    COMMERCIAL = "commercial"
    PRIVATE = "private"


#######################################################################################################################
# Server communication models
#######################################################################################################################
class IpPublishingConfirmation(Model):
    success: bool
    certificator: str
    timestamp: datetime
    license_type: IpLicenseType


class IpPublishingCertificate(Model):
    granted: bool
    certificator: str
    timestamp: datetime
    license_type: IpLicenseType
    version_id: int
    license_id: Optional[int] = -1
    license_key: Optional[str] = UNDEFINED_CONST
    customer_id: Optional[int] = -1

    def __init__(self, **data: Any):
        super().__init__(**data)
        self._tgz_file_path: Path

    @property
    def tgz_file_path(self) -> Path:
        return self._tgz_file_path
    @tgz_file_path.setter
    def tgz_file_path(self, value: Path):
        self._tgz_file_path = Path(value)


class IpFindResults(Model):
    found: bool
    ip_id: Optional[int] = -1
    timestamp: Optional[datetime] = None
    license_type: Optional[IpLicenseType] = IpLicenseType.PUBLIC_OPEN_SOURCE
    license_id: Optional[int] = -1
    version: Optional[SemanticVersion] = SemanticVersion()
    version_id: Optional[int] = -1


class IpGetResults(Model):
    success: bool
    payload: Optional[str] = ""


#######################################################################################################################
# IP Classes
#######################################################################################################################
class IpDefinition:
    vendor_name_is_specified: bool = False
    vendor_name: str = ""
    ip_name: str = ""
    version_spec: SimpleSpec = SimpleSpec("*")
    online_id: int
    target: str = ""
    is_dut: bool = False
    find_results: IpFindResults

    def __str__(self):
        if self.target != "":
            target = f"#{self.target}"
        else:
            target = ""
        if self.vendor_name_is_specified:
            return f"{self.vendor_name}/{self.ip_name}{target}"
        else:
            return f"{self.ip_name}{target}"

    @property
    def installation_directory_name(self) -> str:
        if not self.find_results:
            raise Exception(f"This IP Definition '{self}' has not been checked against the Server")
        else:
            version_str = str(self.find_results.version).replace(".", "p")
            if self.vendor_name_is_specified:
                return f"{self.vendor_name}__{self.ip_name}__{version_str}"
            else:
                return f"{self.ip_name}__{version_str}"


class Structure(Model):
    scripts_path: Optional[PosixPath] = UNDEFINED_CONST
    docs_path: Optional[PosixPath] = UNDEFINED_CONST
    examples_path: Optional[PosixPath] = UNDEFINED_CONST
    hdl_src_path: PosixPath

    def model_dump(self, **kwargs):
        return_dict = {
            'hdl_src_path': self.hdl_src_path,
        }
        if self.scripts_path != UNDEFINED_CONST:
            return_dict['scripts_path'] = self.scripts_path
        if self.docs_path != UNDEFINED_CONST:
            return_dict['docs_path'] = self.docs_path
        if self.examples_path != UNDEFINED_CONST:
            return_dict['examples_path'] = self.examples_path
        return return_dict


class HdlSource(Model):
    directories: PosixPathList
    top_sv_files: Optional[PosixPathList] = []
    top_vhdl_files: Optional[PosixPathList] = []
    top: Optional[HdlNameList] = []
    tests_path: Optional[PosixPath] = UNDEFINED_CONST
    tests_name_template: Optional[str] = UNDEFINED_CONST
    so_libs: Optional[PosixPathList] = []

    def model_dump(self, **kwargs):
        return_dict = {
            'directories': self.directories,
        }
        if len(self.top_sv_files) > 0:
            return_dict['top_sv_files'] = self.top_sv_files
        if len(self.top_vhdl_files) > 0:
            return_dict['top_vhdl_files'] = self.top_vhdl_files
        if len(self.top) > 0:
            return_dict['top'] = self.top
        if self.tests_path != UNDEFINED_CONST:
            return_dict['tests_path'] = self.tests_path
        if self.tests_name_template != UNDEFINED_CONST:
            return_dict['tests_name_template'] = self.tests_name_template
        if len(self.so_libs) > 0:
            return_dict['so_libs'] = self.so_libs
        return return_dict


class DesignUnderTest(Model):
    type: DutType
    name: str = UNDEFINED_CONST
    full_name: Optional[str] = UNDEFINED_CONST
    version: Optional[SemanticVersionSpec] = SemanticVersionSpec()
    target: Optional[HdlName] = UNDEFINED_CONST

    def model_dump(self, **kwargs):
        if self.type.value == DutType.FUSE_SOC.value:
            return_dict = {
                'type': self.type.value,
                'name': self.name,
                'full_name': self.full_name,
                'version': str(self.version),
                'target': self.target,
            }
        else:
            return_dict = {
                'type': self.type.value,
                'name': self.name,
                'version': str(self.version),
                'target': self.target,
            }
        return return_dict


class Parameter(Model):
    type: ParameterType
    min: Optional[int] = 0
    max: Optional[int] = 0
    default: Union[int, bool]


class Target(Model):
    dut: Optional[str] = UNDEFINED_CONST
    cmp: Optional[dict[HdlName, Union[PositiveInt, bool]]] = {}
    elab: Optional[dict[HdlName, Union[PositiveInt, bool]]] = {}
    sim: Optional[dict[HdlName, Union[PositiveInt, bool]]] = {}

    def model_dump(self, **kwargs):
        return_dict = {
        }
        if self.dut != UNDEFINED_CONST:
            return_dict['dut'] = self.dut
        if len(self.cmp) > 0:
            return_dict['cmp'] = self.cmp
        if len(self.elab) > 0:
            return_dict['elab'] = self.elab
        if len(self.sim) > 0:
            return_dict['sim'] = self.sim
        return return_dict


class About(Model):
    sync: bool
    vendor: HdlName
    name: HdlName
    full_name: str
    version: SemanticVersion
    pkg_type: IpPkgType
    sync_id: Optional[PositiveInt] = 0
    sync_revision: Optional[str] = UNDEFINED_CONST
    encrypted: Optional[HdlNameList] = []
    mlicensed: Optional[bool] = False

    def model_dump(self, **kwargs):
        return_dict = {
            'sync': self.sync,
            'vendor': self.vendor,
            'name': self.name,
            'full_name': self.full_name,
            'version': str(self.version),
            'pkg_type': self.pkg_type.value,
        }
        if self.sync:
            return_dict['sync_id'] = self.sync_id
            return_dict['sync_revision'] = self.sync_revision
        if len(self.encrypted) > 0:
            return_dict['encrypted'] = self.encrypted
        if self.mlicensed:
            return_dict['mlicensed'] = self.mlicensed
        return return_dict


class Ip(Model):
    ip: About
    structure: Structure
    hdl_src: HdlSource
    dependencies: Optional[dict[OrgName, SemanticVersionSpec]] = {}
    dut: Optional[DesignUnderTest] = None
    targets: Optional[dict[HdlName, Target]] = {}

    def __init__(self, **data: Any):
        super().__init__(**data)
        self._uid: int
        self._rmh: 'RootManager' = None
        self._ip_database: 'IpDatabase' = None
        self._file_path: Path = None
        self._location_type: IpLocationType
        self._file_path_set: bool = False
        self._root_path: Path = None
        self._resolved_src_path: Path = None
        self._resolved_docs_path: Path = None
        self._resolved_scripts_path: Path = None
        self._resolved_examples_path: Path = None
        self._has_docs: bool = False
        self._has_scripts: bool = False
        self._has_examples: bool = False
        self._resolved_hdl_directories: List[Path] = []
        self._resolved_shared_objects: List[Path] = []
        self._resolved_top_sv_files: List[Path] = []
        self._resolved_top_vhdl_files: List[Path] = []
        self._resolved_encrypted_hdl_directories: dict[str, List[Path]] = {}
        self._resolved_encrypted_top_sv_files: dict[str, List[Path]] = {}
        self._resolved_encrypted_top_vhdl_files: dict[str, List[Path]] = {}
        self._resolved_top: List[str] = []
        self._resolved_dut: Ip
        self._resolved_dependencies: dict[IpDefinition, Ip] = {}
        self._dependencies_to_find_online: List[IpDefinition] = []
        self._dependencies_resolved: bool = False
        self._uninstalled = False

    def model_dump(self, **kwargs):
        return_dict = {
            'ip': self.ip.model_dump(**kwargs),
            'structure': self.structure.model_dump(**kwargs),
            'hdl_src': self.hdl_src.model_dump(**kwargs),
        }
        if len(self.dependencies) > 0:
            return_dict['dependencies'] = {}
            for key, value in self.dependencies.items():
                return_dict['dependencies'][key] = str(value)
        if len(self.targets) > 0:
            return_dict['targets'] = {}
            for name, target in self.targets.items():
                return_dict['targets'][name] = target.model_dump(**kwargs)
        if self.ip.pkg_type == IpPkgType.DV_TB:
            return_dict['dut'] = self.dut.model_dump(**kwargs)
        return return_dict


    def __str__(self):
        if self.ip.vendor != UNDEFINED_CONST:
            return f"{self.ip.vendor} {self.ip.name} v{self.ip.version}"
        else:
            return f"{self.ip.name} v{self.ip.version}"

    @property
    def ip_database(self) -> 'IpDatabase':
        return self._ip_database
    @ip_database.setter
    def ip_database(self, value: 'IpDatabase'):
        self._ip_database = value
    
    @property
    def archive_name(self) -> str:
        version_no_dots = str(self.ip.version).replace(".", "p")
        if self.ip.vendor != UNDEFINED_CONST:
            return f"{self.ip.vendor}__{self.ip.name}__v{version_no_dots}"
        else:
            return f"{self.ip.name}__v{self.ip.version}"

    @property
    def installation_directory_name(self) -> str:
        version_no_dots = str(self.ip.version).replace(".", "p")
        if self.ip.vendor != UNDEFINED_CONST:
            return f"{self.ip.vendor}__{self.ip.name}__v{version_no_dots}"
        else:
            return f"{self.ip.name}__v{self.ip.version}"

    @property
    def lib_name(self) -> str:
        version_no_dots = str(self.ip.version).replace(".", "p")
        if self.ip.vendor != UNDEFINED_CONST:
            return f"{self.ip.vendor}__{self.ip.name}__v{version_no_dots}"
        else:
            return f"{self.ip.name}__v{self.ip.version}"

    @property
    def image_name(self) -> str:
        version_no_dots = str(self.ip.version).replace(".", "p")
        if self.ip.vendor != UNDEFINED_CONST:
            return f"img__{self.ip.vendor}__{self.ip.name}__v{version_no_dots}"
        else:
            return f"img__{self.ip.name}__v{self.ip.version}"

    @property
    def work_directory_name(self) -> str:
        if self.ip.vendor != UNDEFINED_CONST:
            return f"{self.ip.vendor}__{self.ip.name}"
        else:
            return f"{self.ip.name}"

    @property
    def result_file_name(self) -> str:
        if self.ip.vendor != UNDEFINED_CONST:
            return f"{self.ip.vendor}_{self.ip.name}"
        else:
            return f"{self.ip.name}"

    @property
    def as_ip_definition(self) -> str:
        version_str = str(self.ip.version)
        if self.ip.vendor != UNDEFINED_CONST:
            return f"{self.ip.vendor}/{self.ip.name}@{version_str}"
        else:
            return f"{self.ip.name}@{self.ip.version}"

    @property
    def has_vhdl_content(self) -> bool:
        return_bool:bool = False
        if len(self.resolved_top_vhdl_files) > 0:
            return_bool = True
        return return_bool

    @staticmethod
    def parse_ip_definition(definition: str) -> IpDefinition:
        ip_definition = IpDefinition()
        slash_split = definition.split("/")
        if len(slash_split) == 1:
            ip_definition.vendor_name_is_specified = False
            ip_definition.ip_name = slash_split[0].strip().lower()
        elif len(slash_split) == 2:
            ip_definition.vendor_name_is_specified = True
            ip_definition.vendor_name = slash_split[0].strip().lower()
            ip_definition.ip_name = slash_split[1].strip().lower()
        else:
            raise Exception(f"Invalid IP definition: {definition}")
        return ip_definition

    @classmethod
    def load_from_yaml(cls, file_path: Path):
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
            if data is None:
                data = {}
            instance = cls(**data)
            instance.file_path = file_path
            return instance
    def save_to_yaml(self, file_path: Path):
        with open(file_path, 'w') as file:
            model_data: Dict = self.model_dump(exclude_defaults=True)
            yaml.safe_dump(model_data, file)

    @property
    def uid(self) -> int:
        return self._uid
    @uid.setter
    def uid(self, value: int):
        self._uid = value

    @property
    def has_owner(self) -> bool:
        return self.ip.vendor != UNDEFINED_CONST
    
    @property
    def rmh(self) -> 'RootManager':
        return self._rmh
    @rmh.setter
    def rmh(self, value: 'RootManager'):
        self._rmh = value
    
    @property
    def file_path(self) -> Path:
        return self._file_path
    @file_path.setter
    def file_path(self, value: str):
        self._file_path_set = True
        self._file_path = Path(value)
        self._root_path = self._file_path.parent

    @property
    def location_type(self) -> IpLocationType:
        return self._location_type
    @location_type.setter
    def location_type(self, value: IpLocationType):
        self._location_type = value

    @property
    def root_path(self) -> Path:
        return self._root_path
    
    @property
    def resolved_src_path(self) -> Path:
        return self._resolved_src_path
    
    @property
    def resolved_docs_path(self) -> Path:
        return self._resolved_docs_path
    
    @property
    def resolved_scripts_path(self) -> Path:
        return self._resolved_scripts_path
    
    @property
    def resolved_examples_path(self) -> Path:
        return self._resolved_examples_path

    @property
    def resolved_hdl_directories(self) -> List[Path]:
        return self._resolved_hdl_directories

    @property
    def resolved_shared_objects(self) -> List[Path]:
        return self._resolved_shared_objects

    @property
    def resolved_top_sv_files(self) -> List[Path]:
        return self._resolved_top_sv_files

    @property
    def resolved_top_vhdl_files(self) -> List[Path]:
        return self._resolved_top_vhdl_files

    @property
    def resolved_tests_path(self) -> Path:
        return self._root_path / self.hdl_src.tests_path

    @property
    def resolved_encrypted_hdl_directories(self) -> dict[str, List[Path]]:
        return self._resolved_encrypted_hdl_directories

    @property
    def resolved_encrypted_top_sv_files(self) -> dict[str, List[Path]]:
        return self._resolved_encrypted_top_sv_files

    @property
    def resolved_encrypted_top_vhdl_files(self) -> dict[str, List[Path]]:
        return self._resolved_encrypted_top_vhdl_files
    
    @property
    def has_docs(self) -> bool:
        return self._has_docs
    
    @property
    def has_scripts(self) -> bool:
        return self._has_scripts
    
    @property
    def has_examples(self) -> bool:
        return self._has_examples

    @property
    def resolved_dependencies(self) -> dict[IpDefinition, Ip]:
        return self._resolved_dependencies

    @property
    def dependencies_resolved(self) -> bool:
        return self._dependencies_resolved
    @dependencies_resolved.setter
    def dependencies_resolved(self, value: bool):
        self._dependencies_resolved = value

    @property
    def has_dut(self) -> bool:
        if self.dut:
            return self.dut.name != UNDEFINED_CONST
        else:
            return False

    @property
    def resolved_dut(self) -> Ip:
        return self._resolved_dut

    @property
    def dut_needs_prep(self) -> bool:
        if self.has_dut:
            return self.dut.type != DutType.MIO_IP.value
        return False

    @property
    def uninstalled(self) -> bool:
        return self._uninstalled

    def resolve_shared_objects(self, simulator:str):
        for so in self.hdl_src.so_libs:
            so_path: Path = self.resolved_scripts_path / f"{so}.{simulator}.so"
            if self.rmh.file_exists(so_path):
                self._resolved_shared_objects.append(so_path)
            else:
                raise Exception(f"Shared object '{so}' for simulator '{simulator}' cannot be found at '{so_path}'")

    def check(self):
        # If configured to local_mode, global IPs must 'relocate' to the project's mio work directory
        if (self.location_type == IpLocationType.GLOBAL) and self.rmh.configuration.project.local_mode:
            current_ip_root_path = self.file_path.parent
            new_ip_root_path = self.rmh.global_ip_local_copy_dir / self.installation_directory_name
            self.rmh.debug(f"Relocating GLOBAL IP '{self}' from '{current_ip_root_path}' to '{new_ip_root_path}' ...")
            if self.rmh.directory_exists(new_ip_root_path):
                self.rmh.remove_directory(new_ip_root_path)
            self.rmh.copy_directory(current_ip_root_path, new_ip_root_path)
            self.file_path = new_ip_root_path / self.file_path.name
        # Check hdl-src directories & files
        self._resolved_src_path = self.root_path / self.structure.hdl_src_path
        if self.ip.mlicensed and (self.location_type == IpLocationType.PROJECT_INSTALLED):
            if len(self.ip.encrypted) == 0:
                raise Exception(f"IP '{self}' is licensed but has no simulators specified in 'encrypted'")
            else:
                for simulator in self.ip.encrypted:
                    self.check_hdl_src(Path(f"{self._resolved_src_path}.{simulator}"), simulator)
        else:
            self.check_hdl_src(self._resolved_src_path)
        # Check non-src directories
        if self.structure.scripts_path != UNDEFINED_CONST:
            self._has_scripts = True
            self._resolved_scripts_path = self.root_path / self.structure.scripts_path
            if not self.rmh.directory_exists(self.resolved_scripts_path):
                self.rmh.warning(f"IP '{self}' scripts path '{self.resolved_scripts_path}' does not exist")
        if self.structure.docs_path != UNDEFINED_CONST:
            self._has_docs = True
            self._resolved_docs_path = self.root_path / self.structure.docs_path
            if not self.rmh.directory_exists(self.resolved_docs_path):
                self.rmh.warning(f"IP '{self}' docs path '{self.resolved_docs_path}' does not exist")
        if self.structure.examples_path != UNDEFINED_CONST:
            self._has_examples = True
            self._resolved_examples_path = self.root_path / self.structure.examples_path
            if not self.rmh.directory_exists(self.resolved_examples_path):
                self.rmh.warning(f"IP '{self}' examples path '{self.resolved_examples_path}' does not exist")
        # Check targets
        if 'default' not in self.targets:
            default_target = Target()
            default_target.dut = "default"
            self.targets['default'] = default_target

    def check_hdl_src(self, path: Path, simulator: str=""):
        if not self.rmh.directory_exists(path):
            self.rmh.warning(f"IP '{self}' src path '{path}' does not exist")
        for directory in self.hdl_src.directories:
            directory_path = path / directory
            if not self.rmh.directory_exists(directory_path):
                self.rmh.warning(f"IP '{self}' HDL src path '{directory_path}' does not exist")
            else:
                if simulator == "":
                    self.resolved_hdl_directories.append(directory_path)
                else:
                    if simulator not in self.resolved_encrypted_hdl_directories:
                        self._resolved_encrypted_hdl_directories[simulator] = []
                    self.resolved_encrypted_hdl_directories[simulator].append(directory_path)
        if self.hdl_src.tests_path != UNDEFINED_CONST:
            tests_directory_path = path / self.hdl_src.tests_path
            if not self.rmh.directory_exists(tests_directory_path):
                self.rmh.warning(f"IP '{self}' HDL Tests src path '{tests_directory_path}' does not exist")
            else:
                if simulator == "":
                    self.resolved_hdl_directories.append(tests_directory_path)
                else:
                    if simulator not in self.resolved_encrypted_hdl_directories:
                        self._resolved_encrypted_hdl_directories[simulator] = []
                    self.resolved_encrypted_hdl_directories[simulator].append(tests_directory_path)
        for file in self.hdl_src.top_sv_files:
            full_path = path / file
            if not self.rmh.file_exists(full_path):
                raise Exception(f"IP '{self}' src SystemVerilog file path '{full_path}' does not exist")
            else:
                if simulator == "":
                    self._resolved_top_sv_files.append(full_path)
                else:
                    if simulator not in self.resolved_encrypted_top_sv_files:
                        self._resolved_encrypted_top_sv_files[simulator] = []
                    self.resolved_encrypted_top_sv_files[simulator].append(full_path)
        for file in self.hdl_src.top_vhdl_files:
            full_path = path / file
            if not self.rmh.file_exists(full_path):
                raise Exception(f"IP '{self}' src VHDL file path '{full_path}' does not exist")
            else:
                if simulator == "":
                    self.resolved_top_vhdl_files.append(full_path)
                else:
                    if simulator not in self.resolved_encrypted_top_vhdl_files:
                        self._resolved_encrypted_top_vhdl_files[simulator] = []
                    self.resolved_encrypted_top_vhdl_files[simulator].append(full_path)

    def add_resolved_dependency(self, ip_definition: IpDefinition, ip: Ip):
        num_dependencies = len(self.dependencies)
        if self.has_dut:
            num_dependencies += 1
            if ip_definition.is_dut:
                if self.dut.type == DutType.MIO_IP:
                    self._resolved_dut = ip
            else:
                self._resolved_dependencies[ip_definition] = ip
        else:
            self._resolved_dependencies[ip_definition] = ip
        if len(self._resolved_dependencies) == len(self.dependencies):
            self.dependencies_resolved = True
        else:
            self.dependencies_resolved = False
    
    def add_dependency_to_find_on_remote(self, ip_definition: IpDefinition):
        self._dependencies_to_find_online.append(ip_definition)
    
    def get_dependencies_to_find_on_remote(self) -> List[IpDefinition]:
        return self._dependencies_to_find_online

    def create_encrypted_compressed_tarball(self, encryption_config: 'LogicSimulatorEncryptionConfiguration', certificate: IpPublishingCertificate=None) -> Path:
        try:
            if self.resolved_src_path == self.root_path:
                raise Exception(f"Cannot encrypt IPs where the source root is also the IP root: {self}")
            tgz_file_path = self.rmh.md / f"temp/{self.archive_name}.tgz"
            with tarfile.open(tgz_file_path, "w:gz") as tar:
                for sim_spec in self.ip.encrypted:
                    try:
                        simulator = self.ip_database.rmh.service_database.find_service(ServiceType.LOGIC_SIMULATION, sim_spec)
                        if certificate:
                            if self.ip.mlicensed and (certificate.license_key==""):
                                raise Exception(f"Cannot package Moore.io Licensed IP without a valid key")
                            else:
                                encryption_config.add_license_key_checks = True
                                encryption_config.mlicense_key = certificate.license_key
                                encryption_config.mlicense_id  = certificate.license_id
                        scheduler = self.ip_database.rmh.scheduler_database.get_default_scheduler()
                        encryption_report = simulator.encrypt(self, encryption_config, scheduler)
                        if not encryption_report.success:
                            raise Exception(f"Failed to encrypt")
                        else:
                            tar.add(encryption_report.path_to_encrypted_files, arcname=f"{self.structure.hdl_src_path}.{simulator.name}")
                            self.ip_database.rmh.remove_directory(encryption_report.path_to_encrypted_files)
                    except Exception as e:
                        raise Exception(f"Could not encrypt IP {self} for simulator '{sim_spec}': {e}")
                tar.add(self.file_path, arcname=self.file_path.name)
                if self.has_docs:
                    tar.add(self.resolved_docs_path, arcname=self.resolved_docs_path.name)
                if self.has_examples:
                    tar.add(self.resolved_examples_path, arcname=self.resolved_examples_path.name)
                if self.has_scripts:
                    tar.add(self.resolved_scripts_path, arcname=self.resolved_scripts_path.name)
        except Exception as e:
            raise Exception(f"Failed to create encrypted compressed tarball for {self}: {e}")
        return tgz_file_path
    
    def create_unencrypted_compressed_tarball(self) -> Path:
        try:
            tgz_file_path: Path = self.rmh.md / f"temp/{self.archive_name}.tgz"
            with tarfile.open(tgz_file_path, "w:gz") as tar:
                if self.resolved_src_path == self.root_path:
                    tar.add(self.root_path, arcname=".", recursive=True)
                else:
                    tar.add(self.file_path, arcname=self.file_path.name)
                    tar.add(self.resolved_src_path, arcname=self.resolved_src_path.name)
                    if self.has_docs:
                        tar.add(self.resolved_docs_path, arcname=self.resolved_docs_path.name)
                    if self.has_examples:
                        tar.add(self.resolved_examples_path, arcname=self.resolved_examples_path.name)
                    if self.has_scripts:
                        tar.add(self.resolved_scripts_path, arcname=self.resolved_scripts_path.name)
        except Exception as e:
            raise Exception(f"Failed to create unencrypted compressed tarball for {self}: {e}")
        return tgz_file_path
    
    def uninstall(self):
        if self.location_type == IpLocationType.PROJECT_INSTALLED:
            if not self._uninstalled:
                self.rmh.remove_directory(self.root_path)
                self._uninstalled = True

    def __eq__(self, other):
        if isinstance(other, Ip):
            return self.archive_name == other.archive_name
        return False

    def __hash__(self):
        return hash(self.archive_name)
    
    def get_dependencies(self, src_dest_map: Dict[Ip, List[Ip]]):
        src_dest_map[self] = []
        for dep in self.resolved_dependencies:
            dependency = self.resolved_dependencies[dep]
            src_dest_map[self].append(dependency)
            dependency.get_dependencies(src_dest_map)
        if self.has_dut and self.dut.type == DutType.MIO_IP:
            src_dest_map[self].append(self.resolved_dut)
            self.resolved_dut.get_dependencies(src_dest_map)

    def get_dependencies_in_order(self) -> List[Ip]:
        """
        Apply a topological sorting algorithm to determine the order of compilation (Khan's algorithm)
        :return: List of IPs in order of compilation
        """
        dependencies = {}
        self.get_dependencies(dependencies)
        all_ip = list(dependencies.keys())
        # Create a graph and a dictionary to keep track of in-degrees of nodes
        graph = defaultdict(list)
        in_degree = {package: 0 for package in all_ip}
        # Populate the graph and in-degrees based on dependencies
        for dep_ip in dependencies:
            for dep in dependencies[dep_ip]:
                graph[dep_ip].append(dep)
                in_degree[dep] += 1
        # Find all nodes with in-degree 0
        queue = deque([ip for ip in all_ip if in_degree[ip] == 0])
        topo_order = []
        while queue:
            node = queue.popleft()
            topo_order.append(node)
            # Decrease the in-degree of adjacent nodes
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                # If in-degree becomes 0, add it to the queue
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        # If topological sort includes all nodes, return the order
        if len(topo_order) == len(all_ip):
            # Remove self from the topological order if it exists
            if self in topo_order:
                topo_order.remove(self)
            return topo_order[::-1] # Flip the order
        else:
            # There is a cycle and topological sorting is not possible
            raise Exception(f"A cycle was detected in {self} dependencies")

    def check_target(self, name: str="default"):
        if self.targets:
            if name not in self.targets:
                raise Exception(f"Target '{name}' does not exist for IP '{self}'")

    def get_target_dut_target(self, target_name: str="default") -> str:
        dut_target_name = "default"
        if not self.has_dut:
            raise Exception(f"IP '{self}' does not have DUT")
        if self.targets and target_name!="default":
            if target_name not in self.targets:
                raise Exception(f"Target '{target_name}' does not exist for IP '{self}'")
            if target_name != "default":
                dut_target_name = self.targets["default"].dut
            if self.targets[target_name].dut != UNDEFINED_CONST:
                dut_target_name = self.targets[target_name].dut
        return dut_target_name

    def get_target_cmp_bool_defines(self, target_name: str="default") -> Dict[str, bool]:
        if target_name != "default":
            defines = self.get_target_cmp_bool_defines()
        else:
            defines = {}
        if self.targets:
            for define, value in self.targets[target_name].cmp.items():
                if isinstance(value, bool):
                    defines[define] = value
        return defines
    
    def get_target_cmp_val_defines(self, target_name: str="default") -> Dict[str, str]:
        if target_name != "default":
            defines = self.get_target_cmp_val_defines()
        else:
            defines = {}
        if self.targets:
            for define, value in self.targets[target_name].cmp.items():
                if not isinstance(value, bool):
                    defines[define] = str(value)
        return defines
    
    def get_target_sim_bool_args(self, target_name: str="default") -> Dict[str, bool]:
        if target_name != "default":
            defines = self.get_target_sim_bool_args()
        else:
            defines = {}
        if self.targets:
            for define, value in self.targets[target_name].sim.items():
                if isinstance(value, bool):
                    defines[define] = value
        return defines
    
    def get_target_sim_val_args(self, target_name: str="default") -> Dict[str, str]:
        if target_name != "default":
            defines = self.get_target_sim_val_args()
        else:
            defines = {}
        if self.targets:
            for define, value in self.targets[target_name].sim.items():
                if not isinstance(value, bool):
                    defines[define] = str(value)
        return defines


#######################################################################################################################
# IP Database Service
#######################################################################################################################
class IpDataBase():
    def __init__(self, rmh: 'RootManager'):
        self._ip_list: list[Ip] = []
        self._rmh: 'RootManager' = rmh
        self._need_to_find_dependencies_on_remote: bool = False
        self._ip_with_missing_dependencies: Dict[int, Ip] = {}
        self._ip_definitions_to_be_installed: List[IpDefinition] = []

    def add_ip(self, ip: Ip):
        self.rmh.debug(f"Discovered IP '{ip}'")
        self._ip_list.append(ip)
        ip.ip_database = self
    
    @property
    def rmh(self) -> 'RootManager':
        return self._rmh

    @property
    def has_ip(self) -> bool:
        return len(self._ip_list) > 0

    @property
    def num_ips(self) -> int:
        return len(self._ip_list)

    @property
    def need_to_find_dependencies_on_remote(self) -> bool:
        return self._need_to_find_dependencies_on_remote

    @property
    def ip_definitions_to_be_installed(self) -> List[IpDefinition]:
        return self._ip_definitions_to_be_installed

    def get_all_ip(self) -> List[Ip]:
        return self._ip_list

    def get_all_ip_by_location_type(self, location_type: IpLocationType) -> List[Ip]:
        ip_list = []
        for ip in self._ip_list:
            if ip.location_type == location_type:
                ip_list.append(ip)
        return ip_list

    def find_ip_definition(self, definition: IpDefinition, raise_exception_if_not_found: bool=True) -> Ip:
        ip:Ip
        if definition.vendor_name_is_specified:
            ip = self.find_ip(definition.ip_name, definition.vendor_name, definition.version_spec, raise_exception_if_not_found)
        else:
            ip = self.find_ip(definition.ip_name, "*", definition.version_spec, raise_exception_if_not_found)
        if ip and (definition.target != ""):
            ip.check_target(definition.target)
        return ip

    def find_ip(self, name: str, owner: str="*", version_spec: SimpleSpec=SimpleSpec("*"), raise_exception_if_not_found: bool=True) -> Ip:
        for ip in self._ip_list:
            if ip.ip.name == name and (owner == "*" or ip.ip.vendor == owner) and version_spec.match(ip.ip.version):
                return ip
        if raise_exception_if_not_found:
            raise ValueError(f"IP with name '{name}', owner '{owner}', version '{version_spec}' not found.")

    def find_ip_by_sync_id(self, sync_id: str, raise_exception_if_not_found: bool=True) -> Ip:
        for ip in self._ip_list:
            if ip.ip.sync and (ip.ip.sync_id == sync_id):
                return ip
        if raise_exception_if_not_found:
            raise ValueError(f"IP with sync_id '{sync_id}' not found.")

    def discover_ip(self, path: Path, ip_location_type: IpLocationType, error_on_malformed: bool=False, error_on_nothing_found: bool=False) -> List[Ip]:
        ip_list: List[Ip] = []
        ip_files: List[str] = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file == 'ip.yml':
                    ip_files.append(os.path.join(root, file))
        if len(ip_files) == 0:
            if error_on_nothing_found:
                raise Exception(f"No 'ip.yml' files found in the '{ip_location_type}' directory.")
        else:
            for file in ip_files:
                try:
                    ip_model = Ip.load_from_yaml(file)
                    if ip_model.ip.vendor == UNDEFINED_CONST:
                        if self.find_ip(ip_model.ip.name, "*", SimpleSpec(str(ip_model.ip.version)), raise_exception_if_not_found=False):
                            continue
                    else:
                        if self.find_ip(ip_model.ip.name, ip_model.ip.vendor, SimpleSpec(str(ip_model.ip.version)), raise_exception_if_not_found=False):
                            continue
                    ip_model.rmh = self.rmh
                    ip_model.file_path = file
                    ip_model.uid = self.num_ips
                    ip_model.location_type = ip_location_type
                    ip_model.check()
                except ValidationError as e:
                    errors = e.errors()
                    error_messages = "\n  ".join([f"{error['msg']}: {error['loc']}" for error in errors])
                    if error_on_malformed:
                        raise Exception(f"IP definition at '{file}' is malformed: {error_messages}")
                    else:
                        self.rmh.warning(f"Skipping IP definition at '{file}': {error_messages}")
                else:
                    self.add_ip(ip_model)
                    ip_list.append(ip_model)
        return ip_list

    def resolve_local_dependencies(self, reset_list_of_dependencies_to_find_online: bool=True):
        if reset_list_of_dependencies_to_find_online:
            self._dependencies_to_find_online = []
            self._need_to_find_dependencies_on_remote = False
        for ip in self._ip_list:
            self.resolve_dependencies(ip, reset_list_of_dependencies_to_find_online=False)

    def resolve_dependencies(self, ip: Ip, recursive: bool=False, reset_list_of_dependencies_to_find_online: bool=True, depth: int=0):
        if depth > MAX_DEPTH_DEPENDENCY_INSTALLATION:
            raise Exception(f"Loop detected in IP dependencies after depth of {depth}")
        if reset_list_of_dependencies_to_find_online:
            self._dependencies_to_find_online = []
            self._need_to_find_dependencies_on_remote = False
        if ip.has_dut:
            if ip.dut.type == DutType.MIO_IP and not ip.dependencies_resolved:
                dut_definition = Ip.parse_ip_definition(ip.dut.name)
                dut_definition.version_spec = ip.dut.version
                dut_definition.is_dut = True
                dut_dependency = self.find_ip_definition(dut_definition, raise_exception_if_not_found=False)
                if dut_dependency is None:
                    ip.add_dependency_to_find_on_remote(dut_definition)
                    self._need_to_find_dependencies_on_remote = True
                    self._ip_with_missing_dependencies[ip.uid] = ip
                    self._dependencies_to_find_online.append(dut_definition)
                else:
                    ip.add_resolved_dependency(dut_definition, dut_dependency)
                    if recursive:
                        self.resolve_dependencies(dut_dependency, recursive=True, reset_list_of_dependencies_to_find_online=False, depth=depth+1)
            else:
                # Custom DUT
                if ip.dut.type == DutType.FUSE_SOC:
                    # TODO Add checks for FuseSoC core spec
                    pass
        if ip.dependencies is not None:
            for ip_definition_str, ip_version_spec in ip.dependencies.items():
                if not ip.dependencies_resolved:
                    ip_definition = Ip.parse_ip_definition(ip_definition_str)
                    ip_definition.version_spec = ip_version_spec
                    ip_dependency = self.find_ip_definition(ip_definition, raise_exception_if_not_found=False)
                    if ip_dependency is None:
                        ip.add_dependency_to_find_on_remote(ip_definition)
                        self._need_to_find_dependencies_on_remote = True
                        self._ip_with_missing_dependencies[ip.uid] = ip
                        self._dependencies_to_find_online.append(ip_definition)
                    else:
                        ip.add_resolved_dependency(ip_definition, ip_dependency)
                        if recursive:
                            self.resolve_dependencies(ip_dependency, recursive=True, reset_list_of_dependencies_to_find_online=False, depth=depth+1)
    
    def find_all_missing_dependencies_on_server(self):
        ordered_deps = {}
        for dep in self._dependencies_to_find_online:
            if dep not in ordered_deps:
                ordered_deps[dep] = []
            ordered_deps[dep].append(dep.version_spec)
        # TODO Check all specs for same IP definition for contradictions using ordered_deps
        unique_dependencies = {dep.ip_name + dep.vendor_name: dep for dep in self._dependencies_to_find_online}
        self._dependencies_to_find_online = list(unique_dependencies.values())
        ip_definitions_not_found = []
        for ip_definition in self._dependencies_to_find_online:
            ip_definition.find_results = self.ip_definition_is_available_on_server(ip_definition)
            if ip_definition.find_results.found:
                self._ip_definitions_to_be_installed.append(ip_definition)
            else:
                print(f"Could not find IP dependency '{ip_definition}' on the Server")
                ip_definitions_not_found.append(ip_definition)
        if len(ip_definitions_not_found) > 0:
            raise Exception(f"Could not resolve all dependencies for the following IP: {ip_definitions_not_found}")

    def ip_definition_is_available_on_server(self, ip_definition: IpDefinition) -> IpFindResults:
        if ip_definition.vendor_name_is_specified:
            vendor = ip_definition.vendor_name
        else:
            vendor = "*"
        request = {
            "name": ip_definition.ip_name,
            "vendor": vendor,
            "version_spec": str(ip_definition.version_spec)
        }
        try:
            response = self.rmh.web_api_call(HTTPMethod.POST, "find-ip", request)
            results = IpFindResults.model_validate(response.json())
        except Exception as e:
            raise Exception(f"Error while getting IP '{ip_definition}' information from server")
        else:
            return results

    def install_all_missing_dependencies_from_server(self):
        ip_definitions_that_failed_to_install: list[IpDefinition] = []
        for ip_definition in self._ip_definitions_to_be_installed:
            if not self.install_ip_from_server(ip_definition):
                ip_definitions_that_failed_to_install.append(ip_definition)
        number_of_failed_installations = len(ip_definitions_that_failed_to_install)
        if number_of_failed_installations > 0:
            raise Exception(f"Failed to install {number_of_failed_installations} IPs from remote")
    
    def install_ip_from_server(self, ip_definition: IpDefinition) -> bool:
        request = {
            "version_id" : ip_definition.find_results.version_id,
            "license_id" : ip_definition.find_results.license_id
        }
        try:
            response = self.rmh.web_api_call(HTTPMethod.POST, "get-ip", request)
            results = IpGetResults.model_validate(response.json())
        except Exception as e:
            raise e
        else:
            if results.success:
                try:
                    b64encoded_data = results.payload
                    data = base64.b64decode(b64encoded_data)
                    path_installation = self.rmh.locally_installed_ip_dir / ip_definition.installation_directory_name
                    self.rmh.create_directory(path_installation)
                    with tarfile.open(fileobj=BytesIO(data), mode='r:gz') as tar:
                        tar.extractall(path=path_installation)
                except Exception as e:
                    raise Exception(f"Failed to decompress tgz data for IP version '{ip_definition.find_results.version_id}' from server: {e}")
                else:
                    return True
            else:
                raise Exception(f"Failed to get IP version '{ip_definition.find_results.version_id}' from server")
    
    def publish_new_version_to_server(self, ip: Ip, encryption_config: 'LogicSimulatorEncryptionConfiguration', customer: str) -> IpPublishingCertificate:
        certificate = self.get_publishing_certificate(ip, customer)
        if not certificate.granted:
            raise Exception(f"IP {ip} is not available for publishing")
        else:
            if certificate.license_type == IpLicenseType.COMMERCIAL:
                if not ip.ip.mlicensed:
                    raise Exception(f"Attempting to publish Open-Source/Private IP to a Commercial license.")
                else:
                    if (certificate.license_id == -1) or (certificate.license_key == UNDEFINED_CONST) or (certificate.customer_id == -1):
                        raise Exception(f"Invalid certificate received for Commercial IP")
                    tgz_path = ip.create_encrypted_compressed_tarball(encryption_config, certificate)
            else:
                tgz_path = ip.create_unencrypted_compressed_tarball()
            certificate.tgz_file_path = tgz_path
            try:
                with open(tgz_path,'rb') as f:
                    tgz_b64_encoded = str(base64.b64encode(f.read()))[2:-1]
            except Exception as e:
                raise Exception(f"Failed to encode IP {ip} compressed tarball: {e}")
            else:
                try:
                    if certificate.license_type == IpLicenseType.COMMERCIAL:
                        data = {
                            'version_id' : certificate.version_id,
                            'license_id' : certificate.license_id,
                            'license_key' : certificate.license_key,
                            'payload' : str(tgz_b64_encoded),
                        }
                        response = self.rmh.web_api_call(HTTPMethod.POST, 'publish-ip/commercial-payload', data)
                        confirmation = IpPublishingConfirmation.model_validate(response.json())
                        if not confirmation.success:
                            raise Exception(f"Failed to push IP commercial payload to server for '{ip}'")
                    else:
                        data = {
                            'id' : certificate.version_id,
                            'payload' : str(tgz_b64_encoded),
                        }
                        response = self.rmh.web_api_call(HTTPMethod.POST, 'publish-ip/payload', data)
                        confirmation = IpPublishingConfirmation.model_validate(response.json())
                        if not confirmation.success:
                            raise Exception(f"Failed to push IP public payload to server for '{ip}'")
                except Exception as e:
                    raise Exception(f"Failed to push IP payload to server for '{ip}': {e}")
        return certificate
    
    def get_publishing_certificate(self, ip: Ip, customer: str) -> IpPublishingCertificate:
        request = {
            'vendor': ip.ip.vendor,
            "package_name": ip.ip.name,
            "ip_id": ip.ip.sync_id,
            "ip_version": str(ip.ip.version),
            "customer": customer
        }
        try:
            response = self.rmh.web_api_call(HTTPMethod.POST, "publish-ip/certificate", request)
            certificate = IpPublishingCertificate.model_validate(response.json())
        except Exception as e:
            raise Exception(f"Failed to obtain certificate from server for publishing IP {ip}: {e}")
        else:
            return certificate
    
    def uninstall(self, ip: Ip, recursive: bool=True):
        if not ip.uninstalled:
            if recursive:
                for dep in ip.resolved_dependencies:
                    ip = ip.resolved_dependencies[dep]
                    self.uninstall(ip, recursive=True)
            ip.uninstall()
            if ip.location_type == IpLocationType.PROJECT_INSTALLED:
                try: # HACK!
                    self._ip_list.remove(ip)
                except:
                    pass

    def uninstall_all(self):
        list_copy = self._ip_list.copy()
        for ip in list_copy:
            self.uninstall(ip, recursive=False)
