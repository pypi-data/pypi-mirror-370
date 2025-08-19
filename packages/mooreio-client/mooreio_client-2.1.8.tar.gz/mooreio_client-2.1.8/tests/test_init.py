# Copyright 2020-2024 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
import os
import shutil
from pathlib import Path
from typing import Dict
from unittest import SkipTest

import pytest
import yaml

import mio_client.cli
from mio_client.services.init import InitProjectRequest, InitIpRequest
from .common import OutputCapture, TestBase


def get_fixture_data(file: Path) -> Dict:
    with open(file, "r") as file:
        return yaml.safe_load(file)

@pytest.fixture(scope="session")
def uninit_local_simplest_project_answers_data():
    file_path = Path(os.path.join(os.path.dirname(__file__), "data", "project", "uninit_local_simplest", "init_answers.yml"))
    return get_fixture_data(file_path)

@pytest.fixture(scope="session")
def uninit_local_simplest_def_ss_answers_data():
    file_path = Path(os.path.join(os.path.dirname(__file__), "data", "project", "uninit_local_simplest", "dir_a", "def_ss", "init_answers.yml"))
    return get_fixture_data(file_path)

@pytest.fixture(scope="session")
def uninit_local_simplest_def_ss_tb_answers_data():
    file_path = Path(os.path.join(os.path.dirname(__file__), "data", "project", "uninit_local_simplest", "dir_b", "def_ss_tb", "init_answers.yml"))
    return get_fixture_data(file_path)


class TestInit(TestBase):
    @pytest.fixture(autouse=True)
    def setup(self, uninit_local_simplest_project_answers_data, uninit_local_simplest_def_ss_answers_data, uninit_local_simplest_def_ss_tb_answers_data):
        self.uninit_local_simplest_project_answers_data = uninit_local_simplest_project_answers_data
        self.uninit_local_simplest_def_ss_answers_data = uninit_local_simplest_def_ss_answers_data
        self.uninit_local_simplest_def_ss_tb_answers_data = uninit_local_simplest_def_ss_tb_answers_data

    def init_project_configuration_creation(self, data: Dict):
        init_project_configuration = InitProjectRequest(**data)
        assert isinstance(init_project_configuration, InitProjectRequest)

    def init_ip_configuration_creation(self, data: Dict):
        init_ip_configuration = InitIpRequest(**data)
        assert isinstance(init_ip_configuration, InitIpRequest)

    @pytest.mark.core
    def test_init_project_configuration_creation(self):
        self.init_project_configuration_creation(self.uninit_local_simplest_project_answers_data)

    @pytest.mark.core
    def test_init_ip_configuration_creation_def_ss(self):
        self.init_ip_configuration_creation(self.uninit_local_simplest_def_ss_answers_data)

    @pytest.mark.core
    def test_init_ip_configuration_creation_def_ss_tb(self):
        self.init_ip_configuration_creation(self.uninit_local_simplest_def_ss_tb_answers_data)
