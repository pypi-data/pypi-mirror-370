# Copyright 2020-2024 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
import os
from typing import Dict

import pytest
import toml

from .common import TestBase
import mio_client.cli
from mio_client.core.configuration import Configuration


def get_fixture_data(file: str) -> Dict:
    file_path = os.path.join(os.path.dirname(__file__), "data", "configuration", file) + ".toml"
    with open(file_path, "r") as file:
        return toml.load(file)


@pytest.fixture(scope="session")
def valid_local_1_data():
    return get_fixture_data("valid_local_1")
@pytest.fixture(scope="session")
def valid_sync_1_data():
    return get_fixture_data("valid_sync_1")


class TestConfiguration(TestBase):
    @pytest.fixture(autouse=True)
    def setup(self, valid_local_1_data, valid_sync_1_data):
        mio_client.cli.TEST_MODE = True
        self.valid_local_1_data = valid_local_1_data
        self.valid_sync_1_data = valid_sync_1_data

    @pytest.mark.core
    def test_configuration_instance_creation(self):
        config_instance = self.model_creation(Configuration, self.valid_local_1_data)
        assert isinstance(config_instance, Configuration)

    @pytest.mark.core
    def test_configuration_instance_required_fields(self):
        config_instance = self.model_creation(Configuration, self.valid_sync_1_data)
        assert hasattr(config_instance, 'project')
        assert hasattr(config_instance, 'logic_simulation')
        assert hasattr(config_instance, 'logic_synthesis')
        assert hasattr(config_instance, 'lint')
        assert hasattr(config_instance, 'ip')
        assert hasattr(config_instance, 'docs')
        assert hasattr(config_instance, 'encryption')
        assert hasattr(config_instance, 'authentication')
        assert hasattr(config_instance, 'applications')
        assert hasattr(config_instance.authentication, 'offline')

    @pytest.mark.core
    def test_configuration_instance_has_all_fields(self):
        config_instance = self.model_creation(Configuration, self.valid_local_1_data)
        assert hasattr(config_instance, 'project')
        assert hasattr(config_instance.project, 'sync')
        assert hasattr(config_instance.project, 'name')
        assert hasattr(config_instance.project, 'full_name')
        assert hasattr(config_instance, 'logic_simulation')
        assert hasattr(config_instance.logic_simulation, 'root_path')
        assert hasattr(config_instance.logic_simulation, 'regression_directory_name')
        assert hasattr(config_instance.logic_simulation, 'results_directory_name')
        assert hasattr(config_instance.logic_simulation, 'logs_directory')
        assert hasattr(config_instance.logic_simulation, 'test_result_path_template')
        assert hasattr(config_instance.logic_simulation, 'uvm_version')
        assert hasattr(config_instance.logic_simulation, 'timescale')
        assert hasattr(config_instance.logic_simulation, 'altair_dsim_license_path')
        assert hasattr(config_instance.logic_simulation, 'altair_dsim_installation_path')
        assert hasattr(config_instance, 'logic_synthesis')
        assert hasattr(config_instance.logic_synthesis, 'root_path')
        assert hasattr(config_instance, 'lint')
        assert hasattr(config_instance.lint, 'root_path')
        assert hasattr(config_instance, 'ip')
        assert hasattr(config_instance.ip, 'global_paths')
        assert hasattr(config_instance.ip, 'local_paths')
        assert hasattr(config_instance, 'docs')
        assert hasattr(config_instance.docs, 'root_path')
        assert hasattr(config_instance, 'encryption')
        assert hasattr(config_instance.encryption, 'altair_dsim_sv_key_path')
        assert hasattr(config_instance.encryption, 'altair_dsim_vhdl_key_path')
        assert hasattr(config_instance, 'authentication')
        assert hasattr(config_instance, 'applications')
        assert hasattr(config_instance.authentication, 'offline')
