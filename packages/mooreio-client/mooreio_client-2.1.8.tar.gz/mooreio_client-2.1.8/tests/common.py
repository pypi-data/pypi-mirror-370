# Copyright 2020-2025 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
import os
import shutil
import tarfile
from pathlib import Path
from typing import Any

import pytest

import mio_client.cli
from pydantic import ValidationError


class OutputCapture:
    def __init__(self, return_code: int, text: str):
        self.return_code = return_code
        self.text = text

class TestBase:
    def model_creation(self, cls, data) -> Any:
        try:
            instance = cls(**data)
        except ValidationError as e:
            error_text = e.json()
            raise e
        except Exception as e:
            raise e
        else:
            return instance

    def remove_directory(self, path:Path):
        try:
            if not os.path.exists(path):
                return
            shutil.rmtree(path)
        except OSError as e:
            print(f"An error occurred while removing directory '{path}': {e}")

    def remove_file(self, path: Path):
        try:
            if not os.path.exists(path):
                return
            os.remove(path)
        except Exception as e:
            print(f"An error occurred while removing file '{path}': {e}")

    def assert_file_exists(self, path: Path):
        assert os.path.isfile(path)

    def assert_directory_exists(self, path: Path):
        assert os.path.isdir(path)

    def run_cmd(self, capsys, args: [str]) -> OutputCapture:
        return_code = mio_client.cli.main(args)
        text = capsys.readouterr().out.rstrip()
        return OutputCapture(return_code, text)

    def login(self, capsys, username: str, password: str) -> OutputCapture:
        os.environ['MIO_AUTHENTICATION_PASSWORD'] = password
        result = self.run_cmd(capsys, ['--dbg', 'login', f'-u {username}', f'--no-input'])
        assert result.return_code == 0
        assert "Logged in successfully" in result.text
        assert mio_client.cli.root_manager.user.authenticated == True
        return result

    def logout(self, capsys) -> OutputCapture:
        result = self.run_cmd(capsys, ['--dbg', 'logout'])
        assert result.return_code == 0
        assert "Logged out successfully" in result.text
        assert mio_client.cli.root_manager.user.authenticated == False
        return result

    def package_ip(self, capsys, project_path: Path, ip_name: str, destination:Path) -> OutputCapture:
        if destination.exists():
            destination.unlink()
        result = self.run_cmd(capsys, [f'--wd={project_path}', '--dbg', 'package', ip_name, str(destination)])
        assert result.return_code == 0
        assert "Packaged IP" in result.text
        assert "successfully" in result.text
        assert destination.exists()
        assert destination.is_file()
        assert destination.stat().st_size > 0, "Packaged IP file is empty"
        with tarfile.open(destination, "r:gz") as tar:
            assert tar.getmembers(), "Packaged IP file is not a valid compressed tarball or is empty"
        return result

    def publish_ip(self, capsys, project_path: Path, ip_name: str, customer:str="") -> OutputCapture:
        if customer!="":
            result = self.run_cmd(capsys, [f'--wd={project_path}', '--dbg', 'publish', ip_name, f"-c {customer}"])
        else:
            result = self.run_cmd(capsys, [f'--wd={project_path}', '--dbg', 'publish', ip_name])
        assert result.return_code == 0
        assert "Published IP" in result.text
        assert "successfully" in result.text
        return result

    def install_ip(self, capsys, project_path:Path, ip_name:str="") -> OutputCapture:
        if ip_name == "":
            result = self.run_cmd(capsys, [f'--wd={project_path}', '--dbg', 'install'])
        else:
            result = self.run_cmd(capsys, [f'--wd={project_path}', '--dbg', 'install', ip_name])
        assert result.return_code == 0
        if ip_name == "":
            assert "Installed all IPs successfully" in result.text
        else:
            assert "Installed IP" in result.text
            assert "successfully" in result.text
        return result

    def uninstall_ip(self, capsys, project_path:Path, ip_name:str="") -> OutputCapture:
        if ip_name == "":
            result = self.run_cmd(capsys, [f'--wd={project_path}', '--dbg', 'uninstall'])
        else:
            result = self.run_cmd(capsys, [f'--wd={project_path}', '--dbg', 'uninstall', ip_name])
        assert result.return_code == 0
        if ip_name == "":
            assert "Uninstalled all IPs successfully" in result.text
        else:
            assert "Uninstalled IP" in result.text
            assert "successfully" in result.text
        return result

    def prep_dut_ip(self, capsys, project_path: Path, app: str, ip_name: str) -> OutputCapture:
        if ip_name == "":
            raise Exception(f"IP name cannot be empty!")
        result = self.run_cmd(capsys, [f'--wd={project_path}', '--dbg', 'sim', ip_name, '-D', '-a', app])
        assert result.return_code == 0
        return result

    def cmp_ip(self, capsys, project_path: Path, app: str, ip_name: str) -> OutputCapture:
        if ip_name == "":
            raise Exception(f"IP name cannot be empty!")
        result = self.run_cmd(capsys, [f'--wd={project_path}', '--dbg', 'sim', ip_name, '-DC', '-a', app])
        assert result.return_code == 0
        return result

    def elab_ip(self, capsys, project_path: Path, app: str, ip_name: str) -> OutputCapture:
        if ip_name == "":
            raise Exception(f"IP name cannot be empty!")
        result = self.run_cmd(capsys, [f'--wd={project_path}', '--dbg', 'sim', ip_name, '-DE', '-a', app])
        assert result.return_code == 0
        return result

    def cmpelab_ip(self, capsys, project_path: Path, app: str, ip_name: str) -> OutputCapture:
        if ip_name == "":
            raise Exception(f"IP name cannot be empty!")
        result = self.run_cmd(capsys, [f'--wd={project_path}', '--dbg', 'sim', ip_name, '-DCE', '-a', app])
        assert result.return_code == 0
        return result


    def sim_ip(self, capsys, project_path: Path, app: str, ip_name:str, test_name: str, seed: int=1, waves: bool=False,
               cov: bool=False, args_boolean: list[str]=[], args_value: dict[str,str]={}) -> OutputCapture:
        if ip_name == "":
            raise Exception(f"IP name cannot be empty!")
        optional_args = []
        if waves:
            optional_args.append('-w')
        if cov:
            optional_args.append('-c')
        if len(args_boolean) > 0 or len(args_value) > 0:
            plus_args = ["-+"]
            for arg in args_boolean:
                plus_args.append(f"+{arg}")
            for arg in args_value:
                plus_args.append(f"+{arg}={args_value[arg]}")
        else:
            plus_args = []
        result = self.run_cmd(capsys, [
            f'--wd={project_path}', 'sim', ip_name, '-S', f'-t {test_name}', f'-s {seed}', '-a', app
        ] + optional_args + plus_args)
        assert result.return_code == 0
        return result

    def one_shot_sim_ip(self, capsys, project_path: Path, app: str, ip_name: str, test_name: str, seed: int=1, waves: bool=False,
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
            f'--wd={project_path}', '--dbg', 'sim', '-D', '-C', '-E', '-S', ip_name, f'-t {test_name}', f'-s {seed}',
            '-v', 'high', '-a', app, '-w'
        ] + optional_args + plus_args)
        assert result.return_code == 0
        if cov:
            assert os.path.isdir(mio_client.cli.root_manager.command.coverage_merge_report.output_path)
            if mio_client.cli.root_manager.command.coverage_merge_report.has_html_report:
                assert os.path.isdir(mio_client.cli.root_manager.command.coverage_merge_report.html_report_path)
                assert os.path.isfile(mio_client.cli.root_manager.command.coverage_merge_report.html_report_index_path)
                assert os.path.getsize(mio_client.cli.root_manager.command.coverage_merge_report.html_report_index_path) > 0
            if mio_client.cli.root_manager.command.coverage_merge_report.has_merge_log:
                assert os.path.isfile(mio_client.cli.root_manager.command.coverage_merge_report.merge_log_file_path)
                assert os.path.getsize(mio_client.cli.root_manager.command.coverage_merge_report.merge_log_file_path) > 0
        return result

    def one_shot_siarx_sim_ip(self, capsys, project_path: Path, app: str, ip_name: str, test_name: str, seed: int=1, waves: bool=False,
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
            f'--wd={project_path}', '--dbg', 'sim', ip_name, f'-t {test_name}', f'-s {seed}', '-v', 'high', '-a', app, '-w'
        ] + optional_args + plus_args)
        assert result.return_code == 0
        if cov:
            assert os.path.isdir(mio_client.cli.root_manager.command.coverage_merge_report.output_path)
            if mio_client.cli.root_manager.command.coverage_merge_report.has_html_report:
                assert os.path.isdir(mio_client.cli.root_manager.command.coverage_merge_report.html_report_path)
                assert os.path.isfile(mio_client.cli.root_manager.command.coverage_merge_report.html_report_index_path)
                assert os.path.getsize(mio_client.cli.root_manager.command.coverage_merge_report.html_report_index_path) > 0
            if mio_client.cli.root_manager.command.coverage_merge_report.has_merge_log:
                assert os.path.isfile(mio_client.cli.root_manager.command.coverage_merge_report.merge_log_file_path)
                assert os.path.getsize(mio_client.cli.root_manager.command.coverage_merge_report.merge_log_file_path) > 0
        return result

    def clean_ip(self, capsys, project_path: Path, ip_name: str) -> OutputCapture:
        if ip_name == "":
            raise Exception(f"IP name cannot be empty!")
        result = self.run_cmd(capsys, [f'--wd={project_path}', '--dbg', 'clean', ip_name])
        return result

    def deep_clean(self, capsys, project_path: Path) -> OutputCapture:
        result = self.run_cmd(capsys, [f'--wd={project_path}', '--dbg', 'clean', '--deep'])
        assert result.return_code == 0
        assert not (project_path / ".mio").exists()
        return result

    def check_ip_database(self, exp_count:int):
        if mio_client.cli.root_manager.ip_database.num_ips != exp_count:
            raise Exception(f"Expected {exp_count} IPs in database, found {mio_client.cli.root_manager.ip_database.num_ips}")

    def regr_ip(self, capsys, app: str, project_path: Path, ip_name: str, regression_name: str="", dry_mode: bool=False, target_name: str="", test_suite_name: str="") -> OutputCapture:
        if ip_name == "":
            raise Exception(f"IP name cannot be empty!")
        if target_name != "":
            ip_str = f"{ip_name}#{target_name}"
        else:
            ip_str = ip_name
        if test_suite_name != "":
            regression_str = f"{test_suite_name}.{regression_name}"
        else:
            regression_str = regression_name
        optional_args = []
        if app != "":
            optional_args.append(f'--app={app}')
        if dry_mode:
            optional_args.append('--dry')
        results: OutputCapture = self.run_cmd(capsys, [
            f'--wd={project_path}', '--dbg', 'regr', ip_str, regression_str
        ] + optional_args)
        assert results.return_code == 0
        return results

    def check_regr_results(self, result: OutputCapture, app: str, dry_mode: bool, num_tests_expected: int):
        if dry_mode:
            assert f'Regression Dry Mode - {num_tests_expected} tests would have been run:' in result.text
            if app == "dsim":
                assert f"DSim Cloud Simulation Job File:" in result.text
        else:
            assert f'Regression passed: {num_tests_expected} tests' in result.text

    def get_sim_log_text(self):
        log_path = mio_client.cli.root_manager.command.simulation_report.log_path
        with open(log_path, 'r') as log_file:
            log_text = log_file.read()
        return log_text
