# Copyright 2020-2025 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
import os
from ..core.command import Command
from ..core.phase import Phase



#######################################################################################################################
# API Entry Point
#######################################################################################################################
def get_commands():
    return [LoginCommand, LogoutCommand]


#######################################################################################################################
# Login Command
#######################################################################################################################
PASSWORD_ENV_VAR_NAME="MIO_AUTHENTICATION_PASSWORD"
LOGIN_HELP_TEXT = f"""Moore.io User Login Command
   Authenticates session with Moore.io Server.

Usage:
   mio login [OPTIONS]

Options:
   -u USERNAME, --username USERNAME  # Specifies Moore.io username
   -n         , --no-input           # Specify credentials without a keyboard. Must be combined with `-u` and by
                                       setting the environment variable `{PASSWORD_ENV_VAR_NAME}`

Examples:
   mio login                        # Log in with prompts for username and password 
   mio login -u user123             # Specify username inline and only get prompted for the password
   mio login -u user123 --no-input  # Authenticate without a keyboard (especially handy for CI)

Reference documentation: https://mooreio-client.rtfd.io/en/latest/commands.html#login"""

class LoginCommand(Command):
    @staticmethod
    def name() -> str:
        return "login"

    @staticmethod
    def add_to_subparsers(subparsers):
        parser_login = subparsers.add_parser('login', add_help=False)
        parser_login.add_argument(
            '-u', "--username",
            help='Moore.io Server username',
            required=False
        )
        parser_login.add_argument(
            '-n', "--no-input",
            help='Ignores standard input and uses credentials from `-u` and environment variable',
            action="store_true",
            required=False
        )

    def phase_init(self, phase: Phase):
        if self.parsed_cli_arguments.no_input and not self.parsed_cli_arguments.username:
            phase.error = Exception("`--no-input` must be combined with `--username`")

    @property
    def executes_main_phase(self) -> bool:
        return False

    def needs_authentication(self) -> bool:
        return True

    def phase_post_load_default_configuration(self, phase: Phase):
        try:
            # TODO This is a hack and will break if the configuration tree definition changes
            offline = self.rmh.default_configuration['authentication']['offline']
        except:
            offline = False
        if offline:
            phase.error = Exception("Cannot log in: configuration is set to offline mode")

    def phase_post_load_user_data(self, phase: Phase):
        if self.parsed_cli_arguments.no_input and self.parsed_cli_arguments.username:
            self.rmh.user.authenticated = False
            self.rmh.user.session_cookies = {}
            self.rmh.user.session_headers = {}
            self.rmh.user.pre_set_username = self.parsed_cli_arguments.username.strip().lower()
            password = os.getenv(f"{PASSWORD_ENV_VAR_NAME}")
            if not password:
                phase.error = Exception(f"Environment variable `{PASSWORD_ENV_VAR_NAME}` not set")
            else:
                self.rmh.user.pre_set_password = password
        elif self.parsed_cli_arguments.username:
            self.rmh.user.pre_set_username = self.parsed_cli_arguments.username.strip().lower()

    def phase_post_save_user_data(self, phase: Phase):
        phase.end_process = True
        phase.end_process_message = f"Logged in successfully as '{self.rmh.user.username}'."


#######################################################################################################################
# Logout Command
#######################################################################################################################
LOGOUT_HELP_TEXT = """Moore.io User Logout Command
   De-authenticates session with Moore.io Server.
   
Usage:
   mio logout
   
Examples:
   mio logout

Reference documentation: https://mooreio-client.rtfd.io/en/latest/commands.html#logout"""

class LogoutCommand(Command):
    @staticmethod
    def name() -> str:
        return "logout"

    @staticmethod
    def add_to_subparsers(subparsers):
        parser_logout = subparsers.add_parser('logout', add_help=False)

    @property
    def executes_main_phase(self) -> bool:
        return False

    def needs_authentication(self) -> bool:
        return False

    def phase_post_load_user_data(self, phase: Phase):
        if self.rmh.user.authenticated:
            try:
                self.rmh.deauthenticate(phase)
            except Exception as e:
                phase.error = e
            else:
                self.rmh.user.reset()
        else:
            phase.end_process = True
            phase.end_process_message = "Not authenticated: no action taken"

    def phase_post_save_user_data(self, phase: Phase):
        phase.end_process = True
        phase.end_process_message = "Logged out successfully."



