# Copyright 2020-2024 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
import os
import shutil
from pathlib import Path
from typing import Dict
from unittest import SkipTest

import pytest

import mio_client.cli
from .common import OutputCapture, TestBase


class TestCliInit(TestBase):
    @pytest.fixture(autouse=True)
    def setup(self):
        mio_client.cli.TEST_MODE = True
        self.uninit_local_simplest_path: Path = Path(os.path.join(os.path.dirname(__file__), "data", "project", "uninit_local_simplest"))
        self.uninit_local_simplest_project_answers_path: Path = Path(os.path.join(self.uninit_local_simplest_path, "init_answers.yml"))
        self.uninit_local_simplest_def_ss_path: Path = Path(os.path.join(self.uninit_local_simplest_path, "dir_a", "def_ss"))
        self.uninit_local_simplest_def_ss_answers_path: Path = Path(os.path.join(self.uninit_local_simplest_def_ss_path, "init_answers.yml"))
        self.uninit_local_simplest_def_ss_tb_path: Path = Path(os.path.join(self.uninit_local_simplest_path, "dir_b", "def_ss_tb"))
        self.uninit_local_simplest_def_ss_tb_answers_path: Path = Path(os.path.join(self.uninit_local_simplest_def_ss_tb_path, "init_answers.yml"))
        self.assert_file_exists(self.uninit_local_simplest_project_answers_path)
        self.assert_file_exists(self.uninit_local_simplest_def_ss_answers_path)
        self.assert_file_exists(self.uninit_local_simplest_def_ss_tb_answers_path)

    def reset_workspace(self):
        self.remove_directory(self.uninit_local_simplest_path / ".mio")
        self.remove_file(self.uninit_local_simplest_path / "mio.toml")
        self.remove_file(self.uninit_local_simplest_def_ss_path / "ip.yml")
        self.remove_file(self.uninit_local_simplest_def_ss_tb_path / "ip.yml")
        self.remove_file(self.uninit_local_simplest_def_ss_tb_path / "ts.yml")

    def init(self, capsys, project_path: Path, input_file: Path) -> OutputCapture:
        result = self.run_cmd(capsys, [f'--wd={project_path}', '--dbg', 'init', f'-i {input_file}'])
        assert result.return_code == 0
        return result

    def sim_ip(self, capsys, project_path: Path, app: str, ip_name: str, test_name: str, seed: int=1, waves: bool=False,
                        cov: bool=False, defines_boolean: list[str]=[], defines_value: dict[str,str]={},
                        args_boolean: list[str]=[], args_value: dict[str,str]={}) -> OutputCapture:
        if ip_name == "":
            raise Exception(f"IP name cannot be empty!")
        optional_args = []
        if waves:
            optional_args.append('-w')
        if cov:
            optional_args.append('-c')
        if len(defines_boolean) > 0 or len(defines_value) > 0 or len(args_boolean) > 0 or len(args_value) > 0:
            plus_args = ["-+"]
            for define in defines_boolean:
                plus_args.append(f"+define+{define}")
            for define in defines_value:
                plus_args.append(f"+define+{define}={defines_value[define]}")
            for arg in args_boolean:
                plus_args.append(f"+{arg}")
            for arg in args_value:
                plus_args.append(f"+{arg}={args_value[arg]}")
        else:
            plus_args = []
        result = self.run_cmd(capsys, [
            f'--wd={project_path}', 'sim', ip_name, f'-t {test_name}', f'-s {seed}', '-a', app
        ] + optional_args + plus_args)
        assert result.return_code == 0
        return result

    @pytest.mark.core
    def test_cli_init_project(self, capsys):
        self.reset_workspace()
        result = self.init(capsys, self.uninit_local_simplest_path, self.uninit_local_simplest_project_answers_path)

    @pytest.mark.core
    def test_cli_init_project_ip(self, capsys):
        self.reset_workspace()
        result = self.init(capsys, self.uninit_local_simplest_path, self.uninit_local_simplest_project_answers_path)
        result = self.init(capsys, self.uninit_local_simplest_def_ss_path, self.uninit_local_simplest_def_ss_answers_path)
        result = self.init(capsys, self.uninit_local_simplest_def_ss_tb_path, self.uninit_local_simplest_def_ss_tb_answers_path)

    def cli_init_project_ip_sim(self, capsys, app: str):
        self.reset_workspace()
        result = self.init(capsys, self.uninit_local_simplest_path, self.uninit_local_simplest_project_answers_path)
        result = self.init(capsys, self.uninit_local_simplest_def_ss_path, self.uninit_local_simplest_def_ss_answers_path)
        result = self.init(capsys, self.uninit_local_simplest_def_ss_tb_path, self.uninit_local_simplest_def_ss_tb_answers_path)
        result = self.sim_ip(capsys, self.uninit_local_simplest_path, app, "def_ss_tb", "smoke", 1)

    @pytest.mark.dsim
    def test_cli_init_project_ip_sim_dsim(self, capsys):
        self.cli_init_project_ip_sim(capsys, 'dsim')

    @pytest.mark.vivado
    def test_cli_init_project_ip_sim_vivado(self, capsys):
        self.cli_init_project_ip_sim(capsys, 'vivado')


