# Copyright 2020-2024 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
import os
import tarfile
from pathlib import Path
from unittest import SkipTest

import pytest
import shutil

import mio_client.cli
from .common import OutputCapture, TestBase


class TestCliIp(TestBase):
    @pytest.fixture(autouse=True)
    def setup(self):
        mio_client.cli.TEST_MODE = True

    def reset_workspace(self):
        p1_path = Path(os.path.join(os.path.dirname(__file__), "data", "integration", "p1"))
        p2_path = Path(os.path.join(os.path.dirname(__file__), "data", "integration", "p2"))
        p3_path = Path(os.path.join(os.path.dirname(__file__), "data", "integration", "p3"))
        p4_path = Path(os.path.join(os.path.dirname(__file__), "data", "integration", "p4"))
        self.remove_directory(p1_path / ".mio")
        self.remove_directory(p2_path / ".mio")
        self.remove_directory(p3_path / ".mio")
        self.remove_directory(p4_path / ".mio")
        self.remove_directory(p1_path / "sim")
        self.remove_directory(p2_path / "sim")
        self.remove_directory(p3_path / "sim")
        self.remove_directory(p4_path / "sim")

    @pytest.mark.core
    def test_cli_list_ip(self, capsys):
        self.reset_workspace()
        test_project_path = os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_simplest")
        result = self.run_cmd(capsys, [f'--wd={test_project_path}', '--dbg', 'list'])
        assert result.return_code == 0
        assert "Found 3" in result.text

    @pytest.mark.core_single
    def test_cli_package_ip(self, capsys):
        self.reset_workspace()
        p1_path = Path(os.path.join(os.path.dirname(__file__), "data", "integration", "p1"))
        wd_path = Path(os.path.join(os.path.dirname(__file__), "wd"))
        self.package_ip(capsys, p1_path, "a_vlib", Path(wd_path / "a_vlib.tgz"))

