# Copyright 2020-2024 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
import os
from pathlib import Path
from typing import List

import pytest
from semantic_version import Version

from mio_client.core.command import Command
from mio_client.core.phase import Phase
from mio_client.core.root_manager import RootManager
from mio_client.services.simulation import SimulatorMetricsDSim
from mio_client.services.simulation import SimulatorXilinxVivado
from .common import OutputCapture, TestBase

#######################################################################################################################
# Test (ie mock) classes
#######################################################################################################################
TEST_COMMAND_HELP_TEXT = """Moore.io Test Command"""
class TestCommand(Command):
    def __init__(self):
        super().__init__()
        self._numbers: List[int] = []

    @property
    def numbers(self) -> List[int]:
        return self._numbers

    @staticmethod
    def name() -> str:
        return "test"

    @staticmethod
    def add_to_subparsers(subparsers):
        parser_test = subparsers.add_parser('test', help=TEST_COMMAND_HELP_TEXT, add_help=False)

    @property
    def executes_main_phase(self) -> bool:
        return True

    def needs_authentication(self) -> bool:
        return False

    def phase_init(self, phase: Phase):
        self._numbers.append(1)

    def phase_pre_load_default_configuration(self, phase):
        self._numbers.append(2)

    def phase_post_load_default_configuration(self, phase):
        self._numbers.append(3)

    def phase_pre_locate_project_file(self, phase: Phase):
        self._numbers.append(4)

    def phase_post_locate_project_file(self, phase: Phase):
        self._numbers.append(5)

    def phase_pre_create_common_files_and_directories(self, phase: Phase):
        self._numbers.append(6)

    def phase_create_common_files_and_directories(self, phase: Phase):
        self._numbers.append(7)

    def phase_post_create_common_files_and_directories(self, phase: Phase):
        self._numbers.append(8)

    def phase_pre_load_project_configuration(self, phase: Phase):
        self._numbers.append(9)

    def phase_post_load_project_configuration(self, phase: Phase):
        self._numbers.append(10)

    def phase_pre_load_user_configuration(self, phase: Phase):
        self._numbers.append(11)

    def phase_post_load_user_configuration(self, phase: Phase):
        self._numbers.append(12)

    def phase_pre_validate_configuration_space(self, phase: Phase):
        self._numbers.append(13)

    def phase_post_validate_configuration_space(self, phase: Phase):
        self._numbers.append(14)

    def phase_pre_load_user_data(self, phase: Phase):
        self._numbers.append(15)

    def phase_post_load_user_data(self, phase: Phase):
        self._numbers.append(16)

    def phase_pre_authenticate(self, phase: Phase):
        self._numbers.append(17)

    def phase_post_authenticate(self, phase: Phase):
        self._numbers.append(18)

    def phase_pre_save_user_data(self, phase: Phase):
        self._numbers.append(19)

    def phase_post_save_user_data(self, phase: Phase):
        self._numbers.append(20)

    def phase_pre_scheduler_discovery(self, phase: Phase):
        self._numbers.append(21)

    def phase_post_scheduler_discovery(self, phase: Phase):
        self._numbers.append(22)

    def phase_pre_service_discovery(self, phase: Phase):
        self._numbers.append(23)

    def phase_post_service_discovery(self, phase: Phase):
        self._numbers.append(24)

    def phase_pre_ip_discovery(self, phase: Phase):
        self._numbers.append(25)

    def phase_post_ip_discovery(self, phase: Phase):
        self._numbers.append(26)

    def phase_pre_main(self, phase: Phase):
        self._numbers.append(27)

    def phase_main(self, phase: Phase):
        self._numbers.append(28)

    def phase_post_main(self, phase: Phase):
        self._numbers.append(29)

    def phase_pre_check(self, phase: Phase):
        self._numbers.append(30)

    def phase_check(self, phase: Phase):
        self._numbers.append(31)

    def phase_post_check(self, phase: Phase):
        self._numbers.append(32)

    def phase_pre_report(self, phase: Phase):
        self._numbers.append(33)

    def phase_report(self, phase: Phase):
        self._numbers.append(34)

    def phase_post_report(self, phase: Phase):
        self._numbers.append(35)

    def phase_pre_cleanup(self, phase: Phase):
        self._numbers.append(36)

    def phase_cleanup(self, phase: Phase):
        self._numbers.append(37)

    def phase_post_cleanup(self, phase: Phase):
        self._numbers.append(38)

    def phase_pre_shutdown(self, phase: Phase):
        self._numbers.append(39)

    def phase_shutdown(self, phase: Phase):
        self._numbers.append(40)

    def phase_post_shutdown(self, phase: Phase):
        self._numbers.append(41)

    def phase_pre_final(self, phase: Phase):
        self._numbers.append(42)

    def phase_final(self, phase: Phase):
        self._numbers.append(43)

    def phase_post_final(self, phase: Phase):
        self._numbers.append(44)


class TestSimulatorDSimCommand(Command):
    def __init__(self):
        super().__init__()

    @staticmethod
    def name() -> str:
        return "test_simulator_dsim"

    @staticmethod
    def add_to_subparsers(subparsers):
        parser_test_simulator_dsim = subparsers.add_parser('test_simulator_dsim', help=TEST_COMMAND_HELP_TEXT, add_help=False)

    @property
    def executes_main_phase(self) -> bool:
        return True

    def needs_authentication(self) -> bool:
        return False

    def phase_main(self, phase: Phase):
        super().phase_main(phase)
        installation_dir: Path = Path(os.path.join(os.path.dirname(__file__), "data", "environment", "valid_1", "tools", "dsim"))
        self.rmh.configuration.logic_simulation.altair_dsim_installation_path = str(installation_dir)
        dsim_simulator: SimulatorMetricsDSim = SimulatorMetricsDSim(self.rmh)
        dsim_simulator.init()
        assert dsim_simulator.is_available


class TestSimulatorVivadoCommand(Command):
    def __init__(self):
        super().__init__()

    @staticmethod
    def name() -> str:
        return "test_simulator_vivado"

    @staticmethod
    def add_to_subparsers(subparsers):
        parser_test_simulator_vivado = subparsers.add_parser('test_simulator_vivado', help=TEST_COMMAND_HELP_TEXT, add_help=False)

    @property
    def executes_main_phase(self) -> bool:
        return True

    def needs_authentication(self) -> bool:
        return False

    def phase_main(self, phase: Phase):
        super().phase_main(phase)
        installation_dir: Path = Path(os.path.join(os.path.dirname(__file__), "data", "environment", "valid_1", "tools", "vivado"))
        self.rmh.configuration.logic_simulation.xilinx_vivado_installation_path = str(installation_dir)
        vivado_simulator: SimulatorXilinxVivado = SimulatorXilinxVivado(self.rmh)
        vivado_simulator.init()
        assert vivado_simulator.is_available


#######################################################################################################################
# Tests
#######################################################################################################################
class TestCore(TestBase):
    @pytest.fixture(autouse=True)
    def setup(self):
        pass

    def create_root_manager(self, work_directory: Path, user_directory: Path):
        self.rmh: RootManager = RootManager("Test Root Manager", work_directory, True, user_directory)

    def run_command(self, command_type, work_directory: Path, user_directory: Path):
        self.create_root_manager(work_directory, user_directory)
        return_code: int = self.rmh.run(command_type)
        assert return_code == 0

    @pytest.mark.core
    def test_root_manager_phase_order(self):
        wd: Path = Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_simplest"))
        user_home: Path = Path(os.path.join(os.path.dirname(__file__), "data", "user", "home_dirs", "valid_local_1"))
        self.run_command(TestCommand, wd, user_home)
        assert self.rmh.command.numbers == list(range(1, 45))

    @pytest.mark.core
    def test_simulator_dsim_init(self):
        wd: Path = Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_simplest"))
        user_home: Path = Path(os.path.join(os.path.dirname(__file__), "data", "user", "home_dirs", "valid_local_1"))
        self.run_command(TestSimulatorDSimCommand, wd, user_home)

    @pytest.mark.core
    def test_simulator_vivado_init(self):
        wd: Path = Path(os.path.join(os.path.dirname(__file__), "data", "project", "valid_local_simplest"))
        user_home: Path = Path(os.path.join(os.path.dirname(__file__), "data", "user", "home_dirs", "valid_local_1"))
        self.run_command(TestSimulatorVivadoCommand, wd, user_home)
