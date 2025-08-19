# Copyright 2020-2024 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
import os
from pathlib import Path
from unittest import SkipTest

import pytest
import shutil

import mio_client.cli
from .common import OutputCapture, TestBase


class TestCliSim(TestBase):
    @pytest.fixture(autouse=True)
    def setup(self):
        mio_client.cli.TEST_MODE = True

    def reset_workspace(self):
        self.remove_directory(Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_simplest", ".mio")))
        self.remove_directory(Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_simplest", "sim")))
        self.remove_directory(Path(os.path.join(os.path.dirname(__file__), "data", "fsoc", ".mio")))
        self.remove_directory(Path(os.path.join(os.path.dirname(__file__), "data", "fsoc", "sim")))

    def cli_cmp_ip(self, capsys, app: str):
        self.reset_workspace()
        test_project_path = Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_simplest"))
        self.cmp_ip(capsys, test_project_path, app, "def_ss")
        self.clean_ip(capsys, test_project_path, "def_ss")
        self.deep_clean(capsys, test_project_path)

    def cli_cmp_elab_ip(self, capsys, app: str):
        self.reset_workspace()
        test_project_path = Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_simplest"))
        self.cmp_ip(capsys, test_project_path, app, "def_ss_tb")
        self.elab_ip(capsys, test_project_path, app, "def_ss_tb")
        self.clean_ip(capsys, test_project_path, "def_ss_tb")
        self.deep_clean(capsys, test_project_path)

    def cli_cmpelab_ip(self, capsys, app: str):
        self.reset_workspace()
        test_project_path = Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_simplest"))
        self.cmpelab_ip(capsys, test_project_path, app, "def_ss")
        self.clean_ip(capsys, test_project_path, "def_ss")
        self.deep_clean(capsys, test_project_path)

    def cli_cmp_elab_sim_ip(self, capsys, app: str):
        self.reset_workspace()
        test_project_path = Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_simplest"))
        self.cmp_ip(capsys, test_project_path, app, "def_ss_tb")
        self.elab_ip(capsys, test_project_path, app, "def_ss_tb")
        self.sim_ip(capsys, test_project_path, app, "def_ss_tb", "smoke", 1)
        self.clean_ip(capsys, test_project_path, "def_ss_tb")
        self.deep_clean(capsys, test_project_path)

    def cli_cmpelab_sim_ip(self, capsys, app: str):
        self.reset_workspace()
        test_project_path = Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_simplest"))
        self.cmpelab_ip(capsys, test_project_path, app, "def_ss_tb")
        self.sim_ip(capsys, test_project_path, app, "def_ss_tb", "smoke", 1, waves=True, cov=False)
        self.clean_ip(capsys, test_project_path, "def_ss_tb")
        self.deep_clean(capsys, test_project_path)

    def cli_sim_args_ip(self, capsys, app: str):
        self.reset_workspace()
        test_project_path = Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_simplest"))
        defines_boolean = [
            "ABC_BLOCK_ENABLED",
        ]
        defines_value = {
            "DATA_WIDTH": "32",
        }
        args_boolean = [
            "INCLUDE_SECOND_MESSAGE"
        ]
        args_value = {
            "LUCKY_NUMBER": "42",
        }
        result = self.one_shot_sim_ip(capsys, test_project_path, app, "def_ss_tb", "smoke", 1,
                                      waves=False, cov=True, defines_boolean=defines_boolean,
                                      defines_value=defines_value, args_boolean=args_boolean, args_value=args_value)
        log_text = self.get_sim_log_text()
        assert "Hello, World!" in log_text
        assert "DATA_WIDTH=32" in log_text
        assert "ABC_BLOCK is enabled" in log_text
        assert "Your lucky number is 42" in log_text
        self.clean_ip(capsys, test_project_path, "def_ss_tb")
        self.deep_clean(capsys, test_project_path)

    def cli_sim_targets_ip(self, capsys, app: str):
        self.reset_workspace()
        test_project_path = Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_targets"))
        defines_boolean = []
        defines_value = {}
        args_boolean = []
        args_value = {}
        result = self.one_shot_sim_ip(capsys, test_project_path, app, "def_ss_tb#abc", "smoke", 1,
                                      waves=False, cov=True, defines_boolean=defines_boolean,
                                      defines_value=defines_value, args_boolean=args_boolean, args_value=args_value)
        log_text = self.get_sim_log_text()
        assert "My number is 456" in log_text
        assert "DATA_WIDTH is 64" in log_text
        assert "ABC_BLOCK_ENABLED is true" in log_text
        result = self.one_shot_sim_ip(capsys, test_project_path, app, "def_ss_tb", "smoke", 1,
                                      waves=False, cov=True, defines_boolean=defines_boolean,
                                      defines_value=defines_value, args_boolean=args_boolean, args_value=args_value)
        log_text = self.get_sim_log_text()
        assert "My number is 123" in log_text
        assert "DATA_WIDTH is 32" in log_text
        assert "ABC_BLOCK_ENABLED is true" in log_text
        self.clean_ip(capsys, test_project_path, "def_ss_tb")
        self.deep_clean(capsys, test_project_path)

    def cli_prep_dut_fsoc(self, capsys, app: str):
        self.reset_workspace()
        test_project_path = Path(os.path.join(os.path.dirname(__file__), "data", "fsoc"))
        self.prep_dut_ip(capsys, test_project_path, app, "tb")

    def cli_cmpelab_fsoc(self, capsys, app: str):
        self.reset_workspace()
        test_project_path = Path(os.path.join(os.path.dirname(__file__), "data", "fsoc"))
        self.cmpelab_ip(capsys, test_project_path, app, "tb")

    def cli_cmp_elab_fsoc(self, capsys, app: str):
        self.reset_workspace()
        test_project_path = Path(os.path.join(os.path.dirname(__file__), "data", "fsoc"))
        self.cmp_ip(capsys, test_project_path, app, "tb")
        self.elab_ip(capsys, test_project_path, app, "tb")

    # DSim
    @pytest.mark.dsim
    def test_cli_cmp_ip_dsim(self, capsys):
        self.cli_cmp_ip(capsys, "dsim")

    @pytest.mark.dsim
    def test_cli_cmp_elab_ip_dsim(self, capsys):
        self.cli_cmp_elab_ip(capsys, "dsim")

    #@pytest.mark.dsim
    def test_cli_cmpelab_ip_dsim(self, capsys):
        self.cli_cmpelab_ip(capsys, "dsim")

    @pytest.mark.dsim
    def test_cli_cmp_elab_sim_ip_dsim(self, capsys):
        self.cli_cmp_elab_sim_ip(capsys, "dsim")

    @pytest.mark.dsim
    def test_cli_cmpelab_sim_ip_dsim(self, capsys):
        self.cli_cmpelab_sim_ip(capsys, "dsim")

    @pytest.mark.dsim
    def test_cli_sim_args_ip_dsim(self, capsys):
        self.cli_sim_args_ip(capsys, "dsim")

    @pytest.mark.dsim
    def test_cli_sim_targets_ip_dsim(self, capsys):
        self.cli_sim_targets_ip(capsys, "dsim")


    @pytest.mark.dsim
    def test_cli_prep_dut_fsoc_dsim(self, capsys):
        self.cli_prep_dut_fsoc(capsys, "dsim")

    @pytest.mark.dsim
    def test_cli_cmp_elab_fsoc_dsim(self, capsys):
        self.cli_cmp_elab_fsoc(capsys, "dsim")

    @pytest.mark.dsim
    def test_cli_cmpelab_fsoc_dsim(self, capsys):
        self.cli_cmpelab_fsoc(capsys, "dsim")


    # Vivado
    @pytest.mark.vivado
    def test_cli_cmp_ip_vivado(self, capsys):
        self.cli_cmp_ip(capsys, "vivado")

    @pytest.mark.vivado
    def test_cli_cmp_elab_ip_vivado(self, capsys):
        self.cli_cmp_elab_ip(capsys, "vivado")

    @pytest.mark.vivado
    def test_cli_cmp_elab_sim_ip_vivado(self, capsys):
        self.cli_cmp_elab_sim_ip(capsys, "vivado")

    @pytest.mark.vivado
    def test_cli_sim_args_ip_vivado(self, capsys):
        self.cli_sim_args_ip(capsys, "vivado")

    @pytest.mark.vivado
    def test_cli_sim_targets_ip_vivado(self, capsys):
        self.cli_sim_targets_ip(capsys, "vivado")


