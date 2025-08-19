# Copyright 2020-2024 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
import os
from pathlib import Path

import pytest

import mio_client.cli
from .common import OutputCapture, TestBase


class TestCliMisc(TestBase):
    @pytest.fixture(autouse=True)
    def setup(self):
        mio_client.cli.TEST_MODE = True

    @pytest.mark.core
    def test_cli_help(self, capsys):
        result = self.run_cmd(capsys, ['--help'])
        self.check_help(result)
        result = self.run_cmd(capsys, ['-h'])
        self.check_help(result)

    def check_help(self, result: OutputCapture):
        assert result.return_code == 0
        assert "Moore.io" in result.text
        assert "Client" in result.text
        assert "https://mooreio-client.rtfd.io" in result.text
        assert "Usage" in result.text
        assert "Options" in result.text
        assert "Full Command List" in result.text

    @pytest.mark.core
    def test_cli_version(self, capsys):
        result = self.run_cmd(capsys, ['--version'])
        self.check_version(result)
        result = self.run_cmd(capsys, ['-v'])
        self.check_version(result)

    def check_version(self, result: OutputCapture):
        assert result.return_code == 0
        assert "Moore.io Client" in result.text
        assert mio_client.cli.VERSION in result.text

    @pytest.mark.core
    def test_cli_help_command_help(self, capsys):
        result = self.run_cmd(capsys, ['help', 'help'])
        assert result.return_code == 0
        assert "Moore.io" in result.text
        assert "Help Command" in result.text
        assert "User Manual" in result.text
        assert "https://mooreio-client.rtfd.io" in result.text
        assert "Usage" in result.text
        assert "Examples" in result.text
        assert "Reference documentation" in result.text

    @pytest.mark.core
    def test_cli_help_command_login(self, capsys):
        result = self.run_cmd(capsys, ['help', 'login'])
        assert result.return_code == 0
        assert "Moore.io" in result.text
        assert "User Login Command" in result.text
        assert "Usage" in result.text
        assert "Options" in result.text
        assert "Examples" in result.text
        assert "Reference documentation" in result.text

    @pytest.mark.core
    def test_cli_help_command_logout(self, capsys):
        result = self.run_cmd(capsys, ['help', 'logout'])
        assert result.return_code == 0
        assert "Moore.io" in result.text
        assert "User Logout Command" in result.text
        assert "Usage" in result.text
        assert "Examples" in result.text
        assert "Reference documentation" in result.text

    @pytest.mark.core
    def test_cli_help_command_list(self, capsys):
        result = self.run_cmd(capsys, ['help', 'list'])
        assert result.return_code == 0
        assert "Moore.io" in result.text
        assert "IP List Command" in result.text
        assert "Usage" in result.text
        assert "Examples" in result.text
        assert "Reference documentation" in result.text

    @pytest.mark.core
    def test_cli_help_command_package(self, capsys):
        result = self.run_cmd(capsys, ['help', 'package'])
        assert result.return_code == 0
        assert "Moore.io" in result.text
        assert "IP Package Command" in result.text
        assert "Usage" in result.text
        assert "Examples" in result.text
        assert "Reference documentation" in result.text

    @pytest.mark.core
    def test_cli_help_command_publish(self, capsys):
        result = self.run_cmd(capsys, ['help', 'publish'])
        assert result.return_code == 0
        assert "Moore.io" in result.text
        assert "IP Publish Command" in result.text
        assert "Usage" in result.text
        assert "Options" in result.text
        assert "Examples" in result.text
        assert "Reference documentation" in result.text

    @pytest.mark.core
    def test_cli_help_command_install(self, capsys):
        result = self.run_cmd(capsys, ['help', 'install'])
        assert result.return_code == 0
        assert "Moore.io" in result.text
        assert "IP Install Command" in result.text
        assert "Usage" in result.text
        assert "Options" in result.text
        assert "Examples" in result.text

    @pytest.mark.core
    def test_cli_help_command_uninstall(self, capsys):
        result = self.run_cmd(capsys, ['help', 'uninstall'])
        assert result.return_code == 0
        assert "Moore.io" in result.text
        assert "IP Uninstall Command" in result.text
        assert "Usage" in result.text
        assert "Examples" in result.text
        assert "Reference documentation" in result.text

    @pytest.mark.core
    def test_cli_help_command_sim(self, capsys):
        result = self.run_cmd(capsys, ['help', 'sim'])
        assert result.return_code == 0
        assert "Moore.io" in result.text
        assert "Logic Simulation Command" in result.text
        assert "Usage" in result.text
        assert "Options" in result.text
        assert "Examples" in result.text
        assert "Reference documentation" in result.text

    @pytest.mark.core
    def test_cli_help_command_regr(self, capsys):
        result = self.run_cmd(capsys, ['help', 'regr'])
        assert result.return_code == 0
        assert "Moore.io" in result.text
        assert "Regression Command" in result.text
        assert "Usage" in result.text
        assert "Options" in result.text
        assert "Examples" in result.text
        assert "Reference documentation" in result.text

    @pytest.mark.core
    def test_cli_help_command_dox(self, capsys):
        result = self.run_cmd(capsys, ['help', 'dox'])
        assert result.return_code == 0
        assert "Moore.io" in result.text
        assert "Doxygen Command" in result.text
        assert "Usage" in result.text
        assert "Examples" in result.text
        assert "Reference documentation" in result.text

    @pytest.mark.core
    def test_cli_help_command_init(self, capsys):
        result = self.run_cmd(capsys, ['help', 'init'])
        assert result.return_code == 0
        assert "Moore.io" in result.text
        assert "Initialization Command" in result.text
        assert "Usage" in result.text
        assert "Options" in result.text
        assert "Examples" in result.text
        assert "Reference documentation" in result.text

    @pytest.mark.core
    def test_cli_help_command_siarx(self, capsys):
        result = self.run_cmd(capsys, ['help', 'x'])
        assert result.return_code == 0
        assert "Moore.io" in result.text
        assert "SiArx Command" in result.text
        assert "Usage" in result.text
        assert "Options" in result.text
        assert "Examples" in result.text
        assert "Reference documentation" in result.text


