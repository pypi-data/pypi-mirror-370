# Copyright 2020-2024 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
import os
from typing import Dict

import pytest
import yaml
from semantic_version import SimpleSpec

from .common import TestBase
from mio_client.core.ip import Ip
from mio_client.services.regression import TestSuite
import mio_client.cli


def get_fixture_data(file: str) -> Dict:
    file_path = os.path.join(os.path.dirname(__file__), "data", "ts", file) + ".ts.yml"
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="session")
def basic_valid_1_data():
    return get_fixture_data("basic_valid_1")


class TestTs(TestBase):
    @pytest.fixture(autouse=True)
    def setup(self, basic_valid_1_data):
        mio_client.cli.TEST_MODE = True
        self.basic_valid_1_data = basic_valid_1_data

    @pytest.mark.core
    def test_ts_instance_creation(self):
        ts_instance = self.model_creation(TestSuite, self.basic_valid_1_data)
        assert isinstance(ts_instance, TestSuite)

    @pytest.mark.core
    def test_ts_instance_required_fields(self):
        ts_instance = self.model_creation(TestSuite, self.basic_valid_1_data)
        assert hasattr(ts_instance, 'ts')
        assert hasattr(ts_instance.ts, 'name')
        assert hasattr(ts_instance.ts, 'ip')
        assert hasattr(ts_instance.ts, 'target')
        assert hasattr(ts_instance, 'tests')

    @pytest.mark.core
    def test_ts_instance_has_all_fields(self):
        ts_instance = self.model_creation(TestSuite, self.basic_valid_1_data)
        assert hasattr(ts_instance, 'ts')
        assert hasattr(ts_instance.ts, 'name')
        assert hasattr(ts_instance.ts, 'ip')
        assert hasattr(ts_instance.ts, 'target')
        assert hasattr(ts_instance.ts, 'waves')
        assert hasattr(ts_instance.ts, 'cov')
        assert hasattr(ts_instance.ts, 'verbosity')
        assert hasattr(ts_instance.ts, 'max_duration')
        assert hasattr(ts_instance.ts, 'max_jobs')
        assert 'sanity' in ts_instance.ts.waves
        assert 'bugs' in ts_instance.ts.waves
        assert 'nightly' in ts_instance.ts.cov
        assert 'weekly' in ts_instance.ts.cov
        assert 'sanity' in ts_instance.ts.verbosity
        assert 'nightly' in ts_instance.ts.verbosity
        assert 'weekly' in ts_instance.ts.verbosity
        assert 'bugs' in ts_instance.ts.verbosity
        assert 'sanity' in ts_instance.ts.max_duration
        assert 'nightly' in ts_instance.ts.max_duration
        assert 'weekly' in ts_instance.ts.max_duration
        assert 'bugs' in ts_instance.ts.max_duration
        assert 'sanity' in ts_instance.ts.max_jobs
        assert 'nightly' in ts_instance.ts.max_jobs
        assert 'weekly' in ts_instance.ts.max_jobs
        assert 'bugs' in ts_instance.ts.max_jobs

        assert hasattr(ts_instance, 'tests')

        assert 'functional' in ts_instance.tests
        functional_set = ts_instance.tests['functional']
        assert 'fixed_stim' in functional_set
        fixed_stim_test = functional_set['fixed_stim']
        assert 'sanity' in fixed_stim_test
        assert 'nightly' in fixed_stim_test
        assert 'weekly' in fixed_stim_test
        assert 'rand_stim' in functional_set
        rand_stim_test = functional_set['rand_stim']
        sanity_regression = rand_stim_test['sanity']
        assert 'group_a' in sanity_regression
        group_a = sanity_regression['group_a']
        args = group_a.args
        assert 'ABC' in args
        assert 'DEF' in args
        group_b= sanity_regression['group_b']
        args = group_b.args
        assert 'XYZ' in args
        assert 'DEF' in args
        nightly_regression = rand_stim_test['nightly']
        args = nightly_regression.args
        assert 'DEF' in args
        assert 'weekly' in rand_stim_test
        assert 'bugs' in rand_stim_test

        assert 'error' in ts_instance.tests
        error_set = ts_instance.tests['error']
        assert 'fixed_err_stim' in error_set
        fixed_err_stim_test = error_set['fixed_err_stim']
        assert 'sanity' in fixed_err_stim_test
        assert 'nightly' in fixed_err_stim_test
        assert 'weekly' in fixed_err_stim_test
        assert 'bugs' in fixed_err_stim_test
        rand_err_stim_test = error_set['rand_err_stim']
        sanity_regression = rand_err_stim_test['sanity']
        args = sanity_regression.args
        assert 'ABC' in args
        assert 'DEF' in args
        nightly_regression = rand_err_stim_test['nightly']
        args = nightly_regression.args
        assert 'DEF' in args
        assert 'weekly' in rand_err_stim_test

    @pytest.mark.core
    def test_ts_invalid_name(self):
        invalid_data = self.basic_valid_1_data.copy()
        invalid_data['ts']['name'] = ""
        with pytest.raises(ValueError):
            ts_instance = self.model_creation(TestSuite, invalid_data)

    @pytest.mark.core
    def test_ts_invalid_ip(self):
        invalid_data = self.basic_valid_1_data.copy()
        invalid_data['ts']['ip'] = ""
        with pytest.raises(ValueError):
            ts_instance = self.model_creation(TestSuite, invalid_data)

    @pytest.mark.core
    def test_ts_invalid_target(self):
        invalid_data = self.basic_valid_1_data.copy()
        invalid_data['ts']['target'] = []
        with pytest.raises(ValueError):
            ts_instance = self.model_creation(TestSuite, invalid_data)
