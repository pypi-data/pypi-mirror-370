# Copyright 2020-2024 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
import os
import shutil
from pathlib import Path
from unittest import SkipTest

import pytest

import mio_client.cli
from .common import OutputCapture, TestBase


class TestCliDox(TestBase):
    @pytest.fixture(autouse=True)
    def setup(self):
        mio_client.cli.TEST_MODE = True
        self.valid_local_simplest_path: Path = Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_simplest"))
        self.valid_local_simplest_doxygen_output_path: Path = Path(os.path.join(self.valid_local_simplest_path, "docs", "doxygen_output"))

    def reset_workspace(self):
        self.remove_directory(self.valid_local_simplest_path / ".mio")
        self.remove_directory(self.valid_local_simplest_doxygen_output_path)

    def doxygen_ip(self, capsys, project_path: Path, ip: str) -> OutputCapture:
        result = self.run_cmd(capsys, [f'--wd={project_path}', '--dbg', 'dox', ip])
        assert result.return_code == 0
        assert self.valid_local_simplest_doxygen_output_path.is_dir() and any(self.valid_local_simplest_doxygen_output_path.iterdir())
        return result

    def doxygen_all_ip(self, capsys, project_path: Path) -> OutputCapture:
        result = self.run_cmd(capsys, [f'--wd={project_path}', '--dbg', 'dox'])
        assert result.return_code == 0
        assert self.valid_local_simplest_doxygen_output_path.is_dir() and any(self.valid_local_simplest_doxygen_output_path.iterdir())
        return result

    @pytest.mark.core
    def test_cli_dox_ip(self, capsys):
        self.reset_workspace()
        result = self.doxygen_ip(capsys, self.valid_local_simplest_path,'def_ss_tb')

    @pytest.mark.core
    def test_cli_dox_all_ip(self, capsys):
        self.reset_workspace()
        result = self.doxygen_all_ip(capsys, self.valid_local_simplest_path)


