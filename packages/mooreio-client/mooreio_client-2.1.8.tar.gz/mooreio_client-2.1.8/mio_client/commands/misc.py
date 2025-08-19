# Copyright 2020-2025 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
from typing import Dict, List

from ..services.doxygen import DoxygenServiceReport, DoxygenService, DoxygenServiceRequest
from ..core.ip import IpLocationType, Ip
from ..core.scheduler import JobScheduler
from ..core.service import ServiceType
from . import user, ip, sim, gen
from ..core.phase import Phase
from ..core.command import Command



#######################################################################################################################
# API Entry Point
#######################################################################################################################
def get_commands():
    return [HelpCommand, DoxygenCommand]


#######################################################################################################################
# Help Command
#######################################################################################################################
HELP_TEXT = """Moore.io Help Command
   Prints out documentation on a specific command.  This is meant for quick lookups and is only a subset of the
   documentation found in the User Manual (https://mooreio-client.rtfd.io/).
   
Usage:
   mio help CMD
   
Examples:
   mio help sim  # Prints out a summary on the Logic Simulation command and its options

Reference documentation: https://mooreio-client.rtfd.io//en/latest/commands.html#help"""

ALL_COMMANDS = [
    "help", "login", "logout", "list", "package", "publish", "install", "uninstall", "clean", "sim", "regr", "dox",
    "init", "x"
]

class HelpCommand(Command):
    @staticmethod
    def name() -> str:
        return "help"

    @staticmethod
    def add_to_subparsers(subparsers):
        parser_help = subparsers.add_parser('help', description="Provides documentation on specific command", add_help=False)
        parser_help.add_argument("cmd", help='Command whose documentation to print', choices=ALL_COMMANDS)

    def print_text_and_exit(self, phase: Phase, text: str):
        print(text)
        phase.end_process = True

    def phase_init(self, phase):
        if self.parsed_cli_arguments.cmd == "help":
            self.print_text_and_exit(phase, HELP_TEXT)
        if self.parsed_cli_arguments.cmd == "login":
            self.print_text_and_exit(phase, user.LOGIN_HELP_TEXT)
        if self.parsed_cli_arguments.cmd == "logout":
            self.print_text_and_exit(phase, user.LOGOUT_HELP_TEXT)
        if self.parsed_cli_arguments.cmd == "list":
            self.print_text_and_exit(phase, ip.LIST_HELP_TEXT)
        if self.parsed_cli_arguments.cmd == "package":
            self.print_text_and_exit(phase, ip.PACKAGE_HELP_TEXT)
        if self.parsed_cli_arguments.cmd == "publish":
            self.print_text_and_exit(phase, ip.PUBLISH_HELP_TEXT)
        if self.parsed_cli_arguments.cmd == "install":
            self.print_text_and_exit(phase, ip.INSTALL_HELP_TEXT)
        if self.parsed_cli_arguments.cmd == "uninstall":
            self.print_text_and_exit(phase, ip.UNINSTALL_HELP_TEXT)
        if self.parsed_cli_arguments.cmd == "clean":
            self.print_text_and_exit(phase, ip.CLEAN_HELP_TEXT)
        if self.parsed_cli_arguments.cmd == "sim":
            self.print_text_and_exit(phase, sim.SIM_HELP_TEXT)
        if self.parsed_cli_arguments.cmd == "regr":
            self.print_text_and_exit(phase, sim.REGR_HELP_TEXT)
        if self.parsed_cli_arguments.cmd == "dox":
            self.print_text_and_exit(phase, DOX_HELP_TEXT)
        if self.parsed_cli_arguments.cmd == "init":
            self.print_text_and_exit(phase, gen.INIT_HELP_TEXT)
        if self.parsed_cli_arguments.cmd == "x":
            self.print_text_and_exit(phase, gen.SIARX_HELP_TEXT)

    @property
    def executes_main_phase(self) -> bool:
        return False

    def needs_authentication(self) -> bool:
        return False


#######################################################################################################################
# Dox Command
#######################################################################################################################
DOX_HELP_TEXT = """Moore.io Doxygen Command
   Generates reference documentation from IP HDL source code using Doxygen.
   
Usage:
   mio dox [IP]
   
Examples:
   mio dox my_ip  # Generates HTML documentation for IP 'my_ip'
   mio dox        # Generates HTML all local Project IPs

Reference documentation: https://mooreio-client.rtfd.io/en/latest/commands.html#dox"""

class DoxygenCommand(Command):
    def __init__(self):
        super().__init__()
        self._ip_definition: 'IpDefinition'
        self._ip: List['Ip'] = []
        self._scheduler: JobScheduler
        self._doxygen: DoxygenService
        self._configuration: DoxygenServiceRequest = DoxygenServiceRequest()
        self._reports: Dict[Ip, DoxygenServiceReport] = {}
        self._all_ip: bool = False
        self._success: bool = False

    @staticmethod
    def name() -> str:
        return "dox"

    @property
    def ip_definition(self) -> 'IpDefinition':
        return self._ip_definition

    @property
    def ip(self) -> List['Ip']:
        return self._ip

    @property
    def scheduler(self) -> JobScheduler:
        return self._scheduler

    @property
    def doxygen(self) -> DoxygenService:
        return self._doxygen

    @property
    def configuration(self) -> DoxygenServiceRequest:
        return self._configuration

    @property
    def reports(self) -> Dict[Ip, DoxygenServiceReport]:
        return self._reports

    @property
    def all_ip(self) -> bool:
        return self._all_ip

    @property
    def success(self) -> bool:
        return self._success

    @staticmethod
    def add_to_subparsers(subparsers):
        parser_dox = subparsers.add_parser('dox', help=DOX_HELP_TEXT, add_help=False)
        parser_dox.add_argument('ip', help='Target IP', nargs='?', default="*")

    @property
    def executes_main_phase(self) -> bool:
        return True

    def needs_authentication(self) -> bool:
        return False

    def phase_init(self, phase: Phase):
        if self.parsed_cli_arguments.ip != "*":
            self._all_ip = False
            self._ip_definition = Ip.parse_ip_definition(self.parsed_cli_arguments.ip)
        else:
            self._all_ip = True

    def phase_post_scheduler_discovery(self, phase: Phase):
        try:
            # TODO Add support for other schedulers
            self._scheduler = self.rmh.scheduler_database.get_default_scheduler()
        except Exception as e:
            phase.error = e

    def phase_post_service_discovery(self, phase: Phase):
        try:
            self._doxygen = self.rmh.service_database.find_service(ServiceType.DOCUMENTATION_GENERATOR, "doxygen")
        except Exception as e:
            phase.error = e

    def phase_post_ip_discovery(self, phase: Phase):
        if not self.all_ip:
            try:
                if self.ip_definition.vendor_name_is_specified:
                    ip: Ip = self.rmh.ip_database.find_ip(self.ip_definition.ip_name, self.ip_definition.vendor_name)
                else:
                    ip: Ip = self.rmh.ip_database.find_ip(self.ip_definition.ip_name)
                self.ip.append(ip)
            except Exception as e:
                phase.error = e
        else:
            self._ip = self.rmh.ip_database.get_all_ip_by_location_type(IpLocationType.PROJECT_USER)

    def phase_main(self, phase: Phase):
        self._success = True
        for ip in self.ip:
            self.reports[ip] = self.doxygen.generate_documentation(ip, self.configuration, self.scheduler)
            self._success &= self.reports[ip].success

    def phase_report(self, phase: Phase):
        if self.success:
            banner = f"{'*' * 53}\033[32m SUCCESS \033[0m{'*' * 54}"
        else:
            banner = f"{'*' * 53}\033[31m\033[4m FAILURE \033[0m{'*' * 54}"
        print(banner)
        print(f" Generated Doxygen reference documentation successfully for:")
        for ip in self.reports:
            if self.reports[ip].success:
                print(f" * '{ip}': {self.rmh.configuration.applications.web_browser} {self.reports[ip].html_index_path} &")
        if not self.success:
            print(f" Failed to generate Doxygen reference documentation for:")
            for ip in self.reports:
                if not self.reports[ip].success:
                    self.rmh.error(f" * {ip}")
        print(banner)

