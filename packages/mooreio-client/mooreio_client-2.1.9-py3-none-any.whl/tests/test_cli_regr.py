# Copyright 2020-2024 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
import os
from pathlib import Path
from unittest import SkipTest

import pytest
import shutil

from docutils.nodes import target

import mio_client.cli
from .common import OutputCapture, TestBase


class TestCliRegr(TestBase):
    @pytest.fixture(autouse=True)
    def setup(self):
        mio_client.cli.TEST_MODE = True

    def reset_workspace(self):
        self.remove_directory(Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_simplest", ".mdc")))
        self.remove_directory(Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_targets" , ".mdc")))
        self.remove_directory(Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_simplest", ".mio")))
        self.remove_directory(Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_targets" , ".mio")))
        self.remove_directory(Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_simplest", "sim")))
        self.remove_directory(Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_targets" , "sim")))
        self.remove_file(Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_simplest", "mdc_config.yml")))
        self.remove_file(Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_simplest", "mdc_ignore")))
        self.remove_file(Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_targets" , "mdc_config.yml")))
        self.remove_file(Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_targets" , "mdc_ignore")))

    def cli_regr_dry_no_target_no_ts(self, capsys, app: str):
        self.reset_workspace()
        test_project_path = Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_simplest"))
        results = self.regr_ip(capsys, app, test_project_path, "def_ss_tb", "sanity", True)
        self.check_regr_results(results, app, True, 1)
        self.clean_ip(capsys, test_project_path, "def_ss_tb")
        self.deep_clean(capsys, test_project_path)

    def cli_regr_dry_target_no_ts(self, capsys, app: str):
        self.reset_workspace()
        test_project_path = Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_targets"))
        results = self.regr_ip(capsys, app, test_project_path, "def_ss_tb", "nightly", True, 'abc')
        self.check_regr_results(results, app, True, 2)
        self.clean_ip(capsys, test_project_path, "def_ss_tb")
        self.deep_clean(capsys, test_project_path)

    def cli_regr_dry_target_ts(self, capsys, app: str):
        self.reset_workspace()
        test_project_path = Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_targets"))
        results = self.regr_ip(capsys, app, test_project_path, "def_ss_tb", "weekly", True, 'abc', 'special')
        self.check_regr_results(results, app, True, 4)
        self.clean_ip(capsys, test_project_path, "def_ss_tb")
        self.deep_clean(capsys, test_project_path)

    def cli_regr_wet_no_target_no_ts(self, capsys, app: str):
        self.reset_workspace()
        test_project_path = Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_simplest"))
        results = self.regr_ip(capsys, app, test_project_path, "def_ss_tb", "bugs", False)
        self.check_regr_results(results, app, False, 1)
        self.clean_ip(capsys, test_project_path, "def_ss_tb")
        self.deep_clean(capsys, test_project_path)

    def cli_regr_wet_target_no_ts(self, capsys, app: str):
        self.reset_workspace()
        test_project_path = Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_targets"))
        results = self.regr_ip(capsys, app, test_project_path, "def_ss_tb", "weekly", False, 'abc')
        self.check_regr_results(results, app, False, 3)
        self.clean_ip(capsys, test_project_path, "def_ss_tb")
        self.deep_clean(capsys, test_project_path)

    def cli_regr_wet_target_ts(self, capsys, app: str):
        self.reset_workspace()
        test_project_path = Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_targets"))
        results = self.regr_ip(capsys, app, test_project_path, "def_ss_tb", "nightly", False, 'abc', 'special')
        self.check_regr_results(results, app, False, 3)
        self.clean_ip(capsys, test_project_path, "def_ss_tb")
        self.deep_clean(capsys, test_project_path)

    # DSim
    @pytest.mark.dsim
    def test_cli_regr_dry_no_target_no_ts_dsim(self, capsys):
        self.cli_regr_dry_no_target_no_ts(capsys, "dsim")

    @pytest.mark.dsim
    def test_cli_regr_dry_target_no_ts_dsim(self, capsys):
        self.cli_regr_dry_target_no_ts(capsys, "dsim")

    @pytest.mark.dsim
    def test_cli_regr_dry_target_ts_dsim(self, capsys):
        self.cli_regr_dry_target_ts(capsys, "dsim")

    @pytest.mark.dsim
    def test_cli_regr_wet_no_target_no_ts_dsim(self, capsys):
        self.cli_regr_wet_no_target_no_ts(capsys, "dsim")

    @pytest.mark.dsim
    def test_cli_regr_wet_target_no_ts_dsim(self, capsys):
        self.cli_regr_wet_target_no_ts(capsys, "dsim")

    @pytest.mark.dsim
    def test_cli_regr_wet_target_ts_dsim(self, capsys):
        self.cli_regr_wet_target_ts(capsys, "dsim")

    # Vivado
    @pytest.mark.vivado
    def test_cli_regr_dry_no_target_no_ts_vivado(self, capsys):
        self.cli_regr_dry_no_target_no_ts(capsys, "vivado")

    @pytest.mark.vivado
    def test_cli_regr_dry_target_no_ts_vivado(self, capsys):
        self.cli_regr_dry_target_no_ts(capsys, "vivado")

    @pytest.mark.vivado
    def test_cli_regr_dry_target_ts_vivado(self, capsys):
        self.cli_regr_dry_target_ts(capsys, "vivado")

    @pytest.mark.vivado
    def test_cli_regr_wet_no_target_no_ts_vivado(self, capsys):
        self.cli_regr_wet_no_target_no_ts(capsys, "vivado")

    @pytest.mark.vivado
    def test_cli_regr_wet_target_no_ts_vivado(self, capsys):
        self.cli_regr_wet_target_no_ts(capsys, "vivado")

    @pytest.mark.vivado
    def test_cli_regr_wet_target_ts_vivado(self, capsys):
        self.cli_regr_wet_target_ts(capsys, "vivado")