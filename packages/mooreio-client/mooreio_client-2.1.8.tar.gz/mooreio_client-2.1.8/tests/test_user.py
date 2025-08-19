# Copyright 2020-2024 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
import os
from typing import Dict

import pytest
import yaml

import mio_client.cli
from .common import TestBase
from mio_client.core.user import User


def get_fixture_data(file: str) -> Dict:
    file_path = os.path.join(os.path.dirname(__file__), "data", "user", file) + ".yml"
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="session")
def valid_local_1_data():
    return get_fixture_data("valid_local_1")

@pytest.fixture(scope="session")
def valid_authenticated_1():
    return get_fixture_data("valid_authenticated_1")


class TestUser(TestBase):
    @pytest.fixture(autouse=True)
    def setup(self, valid_local_1_data, valid_authenticated_1):
        mio_client.cli.TEST_MODE = True
        self.valid_local_1_data = valid_local_1_data
        self.valid_authenticated_1 = valid_authenticated_1

    @pytest.mark.core
    def test_user_instance_creation(self):
        config_instance = self.model_creation(User, self.valid_local_1_data)
        assert isinstance(config_instance, User)

    @pytest.mark.core
    def test_user_instance_required_fields(self):
        config_instance = self.model_creation(User, self.valid_local_1_data)
        assert hasattr(config_instance, 'authenticated')

    @pytest.mark.core
    def test_user_instance_has_all_fields(self):
        config_instance = self.model_creation(User, self.valid_authenticated_1)
        assert hasattr(config_instance, 'authenticated')
        assert hasattr(config_instance, 'username')

