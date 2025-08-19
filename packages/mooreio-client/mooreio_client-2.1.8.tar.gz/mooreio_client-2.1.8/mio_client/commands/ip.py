# Copyright 2020-2025 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################

import warnings
from enum import Enum
from pathlib import Path
from typing import Dict

from semantic_version import SimpleSpec

from ..core.phase import Phase
from ..core.scheduler import JobScheduler
from ..core.service import ServiceType
from ..services.simulation import LogicSimulator, LogicSimulatorEncryptionRequest, \
    LogicSimulatorLibraryDeletionRequest, LogicSimulatorLibraryDeletionReport
from ..core.command import Command
from ..core.ip import Ip, IpDefinition, IpLocationType, IpPublishingCertificate, \
    MAX_DEPTH_DEPENDENCY_INSTALLATION



#######################################################################################################################
# API Entry Point
#######################################################################################################################
def get_commands():
    return [List, PackageCommand, PublishCommand, InstallCommand, UninstallCommand, CleanCommand]



#######################################################################################################################
# List Command
#######################################################################################################################
LIST_HELP_TEXT = """Moore.io IP List Command
   Lists IPs available to the current project.

Usage:
   mio list

Examples:
   mio list

Reference documentation: https://mooreio-client.rtfd.io/en/latest/commands.html#list"""

class List(Command):
    @staticmethod
    def name() -> str:
        return "list"

    @staticmethod
    def add_to_subparsers(subparsers):
        parser_list = subparsers.add_parser('list', help=LIST_HELP_TEXT, add_help=False)

    @property
    def executes_main_phase(self) -> bool:
        return False

    def needs_authentication(self) -> bool:
        return False

    def phase_post_ip_discovery(self, phase):
        all_ip_unsorted = self.rmh.ip_database.get_all_ip()
        self.rmh.info(f"Found {len(all_ip_unsorted)} IP(s):")
        sorted_ip = sorted(all_ip_unsorted, key=lambda current_ip: (current_ip.has_owner, current_ip.ip.vendor if current_ip.has_owner else '', current_ip.ip.name))
        for ip in sorted_ip:
            if ip.has_owner:
                ip_qualified_name = f"{ip.ip.vendor}/{ip.ip.name}"
            else:
                ip_qualified_name = f"<no owner>/{ip.ip.name}"
            ip_text = f"  {ip_qualified_name} v{ip.ip.version} - {ip.ip.pkg_type.value}: {ip.ip.full_name}"
            print(ip_text)
        phase.end_process = True



#######################################################################################################################
# Package Command
#######################################################################################################################
PACKAGE_HELP_TEXT = """Moore.io IP Package Command
   Command for encrypting/compressing entire IP on local disk.  To enable IP encryption, add an 'encrypted' entry to the
   'hdl_src' section of your descriptor (ip.yml).  Moore.io will only attempt to encrypt using the simulators listed
   under 'encrypted' of the 'ip' section.
   
Usage:
   mio package IP DEST
   
Examples:
   mio package uvma_my_ip ~  # Create compressed archive of IP 'uvma_my_ip' under user's home directory.

Reference documentation: https://mooreio-client.rtfd.io/en/latest/commands.html#package"""

class PackageCommand(Command):
    def __init__(self):
        super().__init__()
        self._ip_definition: 'IpDefinition'
        self._ip: 'Ip'
        self._destination: Path

    @property
    def ip_definition(self) -> 'IpDefinition':
        return self._ip_definition

    @property
    def ip(self) -> 'Ip':
        return self._ip

    @property
    def destination(self) -> Path:
        return self._destination

    @staticmethod
    def name() -> str:
        return "package"

    @staticmethod
    def add_to_subparsers(subparsers):
        parser_package = subparsers.add_parser('package', help=PACKAGE_HELP_TEXT, add_help=False)
        parser_package.add_argument('ip'            , help='Target IP'                          )
        parser_package.add_argument('dest'          , help='Destination path'                   )

    @property
    def executes_main_phase(self) -> bool:
        return True

    def needs_authentication(self) -> bool:
        return False

    def phase_init(self, phase):
        try:
            self._destination = Path(self.parsed_cli_arguments.dest)
            self._ip_definition = Ip.parse_ip_definition(self.parsed_cli_arguments.ip)
        except Exception as e:
            phase.error = e

    def phase_post_ip_discovery(self, phase):
        try:
            if self.ip_definition.vendor_name_is_specified:
                self._ip = self.rmh.ip_database.find_ip(self.ip_definition.ip_name, self.ip_definition.vendor_name)
            else:
                self._ip = self.rmh.ip_database.find_ip(self.ip_definition.ip_name)
        except Exception as e:
            phase.error = e
        else:
            if self.ip.location_type != IpLocationType.PROJECT_USER:
                phase.error = Exception(f"Can only package IP local to the project")

    def phase_main(self, phase):
        try:
            if (len(self.ip.ip.encrypted) > 0) or self.ip.ip.mlicensed:
                encryption_config = LogicSimulatorEncryptionRequest()
                tgz_path = self.ip.create_encrypted_compressed_tarball(encryption_config)
            else:
                tgz_path = self.ip.create_unencrypted_compressed_tarball()
            self.rmh.move_file(tgz_path, self.destination)
        except Exception as e:
            phase.error = Exception(f"Failed to package IP '{self.ip}': {e}")

    def phase_report(self, phase):
        self.rmh.info(f"Packaged IP '{self.ip}' successfully.")



#######################################################################################################################
# Publish Command
#######################################################################################################################
PUBLISH_HELP_TEXT = """Moore.io IP Publish Command
   Packages and publishes an IP to the Moore.io IP Marketplace (https://mooreio.com).
   Currently only available to administrator accounts.

Usage:
   mio publish IP [OPTIONS]

Options:
   -c ORG, --customer ORG  # Specifies Customer Organization name.  Commercial IPs only.

Examples:
   mio publish uvma_my_ip          # Publish Public IP 'uvma_my_ip'.
   mio publish uvma_my_ip -c acme  # Publish Commercial IP 'uvma_my_ip' for customer 'acme'.

Reference documentation: https://mooreio-client.rtfd.io/en/latest/commands.html#publish"""

class PublishCommand(Command):
    def __init__(self):
        super().__init__()
        self._ip_definition: 'IpDefinition'
        self._ip: 'Ip'
        self._publishing_certificate: IpPublishingCertificate
        self._customer: str

    @property
    def ip_definition(self) -> 'IpDefinition':
        return self._ip_definition

    @property
    def ip(self) -> 'Ip':
        return self._ip

    @property
    def customer(self) -> str:
        return self._customer

    @property
    def publishing_certificate(self) -> IpPublishingCertificate:
        return self._publishing_certificate

    @staticmethod
    def name() -> str:
        return "publish"

    @staticmethod
    def add_to_subparsers(subparsers):
        parser_publish = subparsers.add_parser('publish', help=PUBLISH_HELP_TEXT, add_help=False)
        parser_publish.add_argument('ip', help='Target IP')
        parser_publish.add_argument(
            '-c', "--customer",
            help='Customer (Moore.io Organization) name.  Commercial IPs only.',
            required=False
        )

    @property
    def executes_main_phase(self) -> bool:
        return True

    def needs_authentication(self) -> bool:
        return True

    def phase_init(self, phase):
        if not self.parsed_cli_arguments.ip:
            phase.error = Exception(f"No IP specified")
        else:
            self._ip_definition = Ip.parse_ip_definition(self.parsed_cli_arguments.ip)

    def phase_post_ip_discovery(self, phase):
        try:
            if self.ip_definition.vendor_name_is_specified:
                self._ip = self.rmh.ip_database.find_ip(self.ip_definition.ip_name, self.ip_definition.vendor_name)
            else:
                self._ip = self.rmh.ip_database.find_ip(self.ip_definition.ip_name)
        except Exception as e:
            phase.error = e
        else:
            if self.ip.location_type != IpLocationType.PROJECT_USER:
                phase.error = Exception(f"Can only publish IP local to the project")
            if self.ip.ip.mlicensed:
                if not self.parsed_cli_arguments.customer:
                    phase.error = Exception(f"Must specify customer (`-c`) when publishing commercial IP")
                else:
                    self._customer = self.parsed_cli_arguments.customer.strip().lower()
            else:
                self._customer = "public"

    def phase_main(self, phase):
        try:
            encryption_config = LogicSimulatorEncryptionRequest()
            self._publishing_certificate = self.rmh.ip_database.publish_new_version_to_server(self.ip, encryption_config, self.customer)
        except Exception as e:
            phase.error = Exception(f"Failed to publish IP '{self.ip}': {e}")

    def phase_report(self, phase):
        print(f"Published IP '{self.ip}' successfully.")

    def phase_cleanup(self, phase):
        try:
            # TODO Turn into configuration parameter to store these somewhere for safekeeping
            #self.rmh.remove_file(self.self._publishing_certificate._tgz_path)
            pass
        except Exception as e:
            self.rmh.warning(f"Failed to delete compressed tarball for IP '{self.ip}': {e}")



#######################################################################################################################
# Install Command
#######################################################################################################################
INSTALL_HELP_TEXT = """Moore.io IP Install Command
   Downloads IP(s) from Moore.io Server.  Can be used in 3 ways:
     1) Without specifying an IP: install all missing dependencies for all IPs in the current Project
     2) Specifying the name a local IP: install all missing dependencies for a specific IP in the current project
     3) Specifying the name of an IP on the Moore.io Server: install remote IP and all its dependencies into the current Project
   
Usage:
   mio install [IP] [OPTIONS]

Options:
   -v SPEC, --version SPEC  # Specifies IP version (only for remote IPs). Must specify IP when using this option.
   
Examples:
   mio install                     # Install all dependencies for all IPs in the current Project
   mio install my_ip               # Install all dependencies for a specific IP in the current Project
   mio install acme/abc            # Install latest version of IP from Moore.io Server and its dependencies into current Project
   mio install acme/abc -v "1.2.3" # Install specific version of IP from Moore.io Server and its dependencies into current Project

Reference documentation: https://mooreio-client.rtfd.io/en/latest/commands.html#install"""

class InstallMode(Enum):
    UNKNOWN = 0
    ALL = 1
    LOCAL = 2
    REMOTE = 3

class InstallCommand(Command):
    def __init__(self):
        super().__init__()
        self._ip_definition: 'IpDefinition' = None
        self._ip: 'Ip' = None
        self._mode: InstallMode = InstallMode.UNKNOWN

    @staticmethod
    def name() -> str:
        return "install"

    @property
    def ip_definition(self) -> 'IpDefinition':
        return self._ip_definition

    @property
    def ip(self) -> 'Ip':
        return self._ip

    @property
    def mode(self) -> InstallMode:
        return self._mode

    @staticmethod
    def add_to_subparsers(subparsers):
        parser_install = subparsers.add_parser('install', help=INSTALL_HELP_TEXT, add_help=False)
        parser_install.add_argument('ip', help='Target IP', nargs='?', default="*")
        parser_install.add_argument(
            '-v', "--version",
            help='IP version spec (remote IPs only)',
            required=False
        )

    @property
    def executes_main_phase(self) -> bool:
        return True

    def needs_authentication(self) -> bool:
        return True

    def phase_init(self, phase: Phase):
        if self.parsed_cli_arguments.ip == "*":
            self._mode = InstallMode.ALL
        else:
            self._ip_definition = Ip.parse_ip_definition(self.parsed_cli_arguments.ip)
        if self.parsed_cli_arguments.version and (self.mode == InstallMode.ALL):
            phase.error = Exception(f"Cannot specify a version when requesting to install all IPs")
        elif self.parsed_cli_arguments.version and (self.mode != InstallMode.ALL):
            try:
                self.ip_definition.version_spec = SimpleSpec(self.parsed_cli_arguments.version)
            except Exception as e:
                phase.error = Exception(f"Invalid version specifier: {e}")

    def phase_post_ip_discovery(self, phase: Phase):
        if self.mode != InstallMode.ALL:
            self._ip = self.rmh.ip_database.find_ip_definition(self.ip_definition, raise_exception_if_not_found=False)
            if self.ip:
                self._mode = InstallMode.LOCAL
            else:
                self._mode = InstallMode.REMOTE

    def phase_main(self, phase: Phase):
        if self.mode == InstallMode.REMOTE:
            self.ip_definition.find_results = self.rmh.ip_database.ip_definition_is_available_on_server(self.ip_definition)
            if self.ip_definition.find_results.found:
                try:
                    self.rmh.ip_database.install_ip_from_server(self.ip_definition)
                except Exception as e:
                    phase.error = e
                    return
            else:
                phase.error = Exception(f"IP {self.ip_definition} does not exist on Server")
                return
        elif self.mode == InstallMode.LOCAL:
            pass
        depth = 0
        while depth < MAX_DEPTH_DEPENDENCY_INSTALLATION:
            try:
                self.rmh.ip_database.discover_ip(self.rmh.locally_installed_ip_dir, IpLocationType.PROJECT_INSTALLED, error_on_malformed=True)
                if self.mode == InstallMode.ALL:
                    self.rmh.ip_database.resolve_local_dependencies()
                elif self.mode == InstallMode.REMOTE:
                    if depth == 0:
                        self._ip = self.rmh.ip_database.find_ip_definition(self.ip_definition)
                    self.rmh.ip_database.resolve_dependencies(self.ip, recursive=True)
                elif self.mode == InstallMode.LOCAL:
                    self.rmh.ip_database.resolve_dependencies(self.ip, recursive=True)
                if not self.rmh.ip_database.need_to_find_dependencies_on_remote:
                    break
                else:
                    if not self.rmh.user.authenticated:
                        self.rmh.authenticate(phase)
                    self.rmh.ip_database.find_all_missing_dependencies_on_server()
                    self.rmh.ip_database.install_all_missing_dependencies_from_server()
                depth += 1
            except Exception as e:
                phase.error = Exception(f"Failed to install remote IP dependencies: {e}")
                break
        if self.rmh.ip_database.need_to_find_dependencies_on_remote:
            phase.error = Exception(f"Failed to resolve all IP dependencies after {depth} attempts")

    def phase_report(self, phase: Phase):
        if self.mode == InstallMode.ALL:
            self.rmh.info(f"Installed all IPs successfully.")
        else:
            self.rmh.info(f"Installed IP '{self.ip}' successfully.")


#######################################################################################################################
# Uninstall Command
#######################################################################################################################
UNINSTALL_HELP_TEXT = """Moore.io IP Uninstall Command
   Removes IP(s) installed in current Project.  Can be used in 3 ways:
     1) Without specifying an IP: delete all installed dependencies for all IPs in the current Project
     2) Specifying the name a local IP: delete all installed dependencies for a specific local IP in the current project
     3) Specifying the name of an installed IP: delete installed IP and all its installed dependencies from the current Project
   
Usage:
   mio uninstall [IP]

Examples:
   mio uninstall           # Delete all installed IPs in current project
   mio uninstall my_ip     # Delete all installed dependencies for a specific local IP in the current project
   mio uninstall acme/abc  # Delete specific installed IP and all its installed dependencies from current project

Reference documentation: https://mooreio-client.rtfd.io/en/latest/commands.html#uninstall"""

class UninstallCommand(Command):
    def __init__(self):
        super().__init__()
        self._ip_definition: 'IpDefinition'
        self._ip: 'Ip'
        self._uninstall_all: bool

    @staticmethod
    def name() -> str:
        return "uninstall"

    @property
    def ip_definition(self) -> 'IpDefinition':
        return self._ip_definition

    @property
    def ip(self) -> 'Ip':
        return self._ip

    @property
    def uninstall_all(self) -> bool:
        return self._uninstall_all

    @staticmethod
    def add_to_subparsers(subparsers):
        parser_uninstall = subparsers.add_parser('uninstall', help=UNINSTALL_HELP_TEXT, add_help=False)
        parser_uninstall.add_argument('ip', help='Target IP', nargs='?', default="*")

    @property
    def executes_main_phase(self) -> bool:
        return True

    def needs_authentication(self) -> bool:
        return False

    def phase_init(self, phase: Phase):
        if self.parsed_cli_arguments.ip != "*":
            self._uninstall_all = False
            self._ip_definition = Ip.parse_ip_definition(self.parsed_cli_arguments.ip)
        else:
            self._uninstall_all = True

    def phase_post_ip_discovery(self, phase: Phase):
        if not self.uninstall_all:
            try:
                if self.ip_definition.vendor_name_is_specified:
                    self._ip = self.rmh.ip_database.find_ip(self.ip_definition.ip_name, self.ip_definition.vendor_name)
                else:
                    self._ip = self.rmh.ip_database.find_ip(self.ip_definition.ip_name)
            except Exception as e:
                phase.error = e

    def phase_main(self, phase: Phase):
        if self.uninstall_all:
            self.rmh.ip_database.uninstall_all()
        else:
            self.rmh.ip_database.uninstall(self.ip)

    def phase_report(self, phase: Phase):
        if self.uninstall_all:
            self.rmh.info(f"Uninstalled all IPs successfully.")
        else:
            self.rmh.info(f"Uninstalled IP '{self.ip}' successfully.")


#######################################################################################################################
# Clean Command
#######################################################################################################################
CLEAN_HELP_TEXT = """Moore.io Clean Command
   Deletes output artifacts from EDA tools and/or Moore.io Project directory contents (/.mio).
   Only logic simulation artifacts are currently supported.
   
Usage:
   mio clean [IP] [OPTIONS]
   
Options:
   -d, --deep  # Removes Project Moore.io directory (/.mio)
   
Examples:
   mio clean my_ip   # Delete compilation, elaboration and simulation artifacts for IP 'my_ip'
   mio clean --deep  # Removes contents of Project Moore.io directory (/.mio)

Reference documentation: https://mooreio-client.rtfd.io/en/latest/commands.html#clean"""

class CleanCommand(Command):
    def __init__(self):
        super().__init__()
        self._ip_definition: 'IpDefinition'
        self._ip: 'Ip'
        self._deep_clean: bool
        self._scheduler: JobScheduler
        self._simulators: list[LogicSimulator] = []
        self._request: LogicSimulatorLibraryDeletionRequest = LogicSimulatorLibraryDeletionRequest()
        self._reports: Dict[LogicSimulator, LogicSimulatorLibraryDeletionReport] = {}
        self._success: bool = False

    @staticmethod
    def name() -> str:
        return "clean"

    @property
    def ip_definition(self) -> 'IpDefinition':
        return self._ip_definition

    @property
    def ip(self) -> 'Ip':
        return self._ip

    @property
    def deep_clean(self) -> bool:
        return self._deep_clean
    
    @property
    def simulators(self) -> list[LogicSimulator]:
        return self._simulators

    @property
    def scheduler(self) -> JobScheduler:
        return self._scheduler

    @property
    def request(self) -> LogicSimulatorLibraryDeletionRequest:
        return self._request

    @property
    def reports(self) -> Dict[LogicSimulator, LogicSimulatorLibraryDeletionReport]:
        return self._reports

    @property
    def success(self) -> bool:
        return self._success

    @staticmethod
    def add_to_subparsers(subparsers):
        parser_clean = subparsers.add_parser('clean', help=CLEAN_HELP_TEXT, add_help=False)
        parser_clean.add_argument('ip', help='Target IP', nargs='?', default="*")
        parser_clean.add_argument('-d', "--deep", help='Removes Project Moore.io directory (/.mio)', action="store_true", default=False , required=False)

    @property
    def executes_main_phase(self) -> bool:
        return True

    def needs_authentication(self) -> bool:
        return False

    def phase_init(self, phase: Phase):
        if self.parsed_cli_arguments.ip != "*":
            self._deep_clean = False
            self._ip_definition = Ip.parse_ip_definition(self.parsed_cli_arguments.ip)
        else:
            if self.parsed_cli_arguments.deep:
                self._deep_clean = True
            else:
                phase.error = Exception(f"Must specify '-d/--deep' when not specifying an IP to clean")

    def phase_post_scheduler_discovery(self, phase: Phase):
        try:
            # TODO Add support for other schedulers
            self._scheduler = self.rmh.scheduler_database.get_default_scheduler()
        except Exception as e:
            phase.error = e

    def phase_post_service_discovery(self, phase: Phase):
        try:
            self._simulators = self.rmh.service_database.find_all_services_by_type(ServiceType.LOGIC_SIMULATION)
        except Exception as e:
            phase.error = e

    def phase_post_ip_discovery(self, phase: Phase):
        if not self.deep_clean:
            try:
                if self.ip_definition.vendor_name_is_specified:
                    self._ip = self.rmh.ip_database.find_ip(self.ip_definition.ip_name, self.ip_definition.vendor_name)
                else:
                    self._ip = self.rmh.ip_database.find_ip(self.ip_definition.ip_name)
            except Exception as e:
                phase.error = e

    def phase_main(self, phase: Phase):
        if self.deep_clean:
            self.rmh.remove_directory(self.rmh.md)
            self._success = True
        else:
            self._success = True
            for simulator in self._simulators:
                self._reports[simulator] = simulator.delete_library(self.ip, self.request, self.scheduler)
                self._success &= self._reports[simulator].success
            if not self._success:
                phase.error = Exception(f"Failed to clean IP '{self.ip}'")

    def phase_report(self, phase: Phase):
        if self.deep_clean:
            if self.success:
                self.rmh.info(f"Deleted '{self.rmh.md}' successfully.")
            else:
                self.rmh.error(f"Failed to delete '{self.rmh.md}'.")
        else:
            if self.success:
                self.rmh.info(f"Cleaned IP '{self.ip}' successfully.")
            else:
                self.rmh.error(f"Failed to clean IP '{self.ip}'.")

