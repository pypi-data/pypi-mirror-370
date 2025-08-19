# Copyright 2020-2025 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
import datetime
import os
import re
import warnings
from pathlib import Path
from random import randint
from typing import Optional, List, Dict, Union, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from xml.etree import ElementTree

from jinja2 import Template
from semantic_version import Version
from tqdm import tqdm

import yaml
from pydantic import PositiveInt, PositiveFloat
from pydantic.types import constr
from enum import Enum

from ..core.configuration import LogicSimulators
from ..core.scheduler import JobScheduler, Job, JobSchedulerConfiguration, JobResults
from ..core.service import Service, ServiceType
from ..core.ip import Ip
from ..core.model import Model, VALID_NAME_REGEX
from ..core.phase import Phase
from .simulation import LogicSimulatorSimulationRequest, LogicSimulatorCompilationRequest, \
    LogicSimulatorElaborationRequest, LogicSimulatorCompilationAndElaborationRequest, \
    LogicSimulatorSimulationReport, LogicSimulator, LogicSimulatorCompilationReport, LogicSimulatorElaborationReport, \
    LogicSimulatorCompilationAndElaborationReport, SimulatorMetricsDSim, DSimCloudJob, DSimCloudSimulationRequest, \
    UvmVerbosity, LogicSimulatorCoverageMergeRequest, LogicSimulatorCoverageMergeReport


#######################################################################################################################
# API Entry Point
#######################################################################################################################
def get_services():
    return [RegressionDatabase]


#######################################################################################################################
# Models
#######################################################################################################################
VALID_TARGET_NAME_REGEX = re.compile(r"^((\*)|(\w+))$")

class TestSpecTypes(Enum):
    NUM_RAND_SEEDS = "repeat"
    SEED_LIST = "seed_list"


class About(Model):
    name: constr(pattern=VALID_NAME_REGEX)
    ip: constr(pattern=VALID_NAME_REGEX)
    target: List[constr(pattern=VALID_TARGET_NAME_REGEX)]
    cov: Optional[List[constr(pattern=VALID_NAME_REGEX)]] = []
    waves: Optional[List[constr(pattern=VALID_NAME_REGEX)]] = []
    max_duration: Optional[Dict[constr(pattern=VALID_NAME_REGEX), PositiveFloat]] = {}
    max_errors: Optional[Dict[constr(pattern=VALID_NAME_REGEX), PositiveInt]] = {}
    max_jobs: Optional[Dict[constr(pattern=VALID_NAME_REGEX), PositiveInt]] = {}
    verbosity: Optional[Dict[constr(pattern=VALID_NAME_REGEX), UvmVerbosity]] = {}


class ResolvedTestSpec:
    def __init__(self):
        self.test_name: str = ""
        self.spec_type: TestSpecTypes = TestSpecTypes.NUM_RAND_SEEDS
        self.num_rand_seeds: int = 0
        self.specific_seeds: List[int] = []
        self.args: Dict[str, Union[bool, str]] = {}
        self.test_suite: 'TestSuite' = None
        self.regression: 'Regression' = None
        self.test_set: 'TestSet' = None
        self.test_group: 'TestGroup' = None


class TestGroup:
    def __init__(self, name: str, test_set: 'TestSet'):
        self.name: str = name
        self.test_set: 'TestSet' = test_set
        self.test_specs: List[ResolvedTestSpec] = []
        self.regression: 'Regression' = test_set.regression
        self.test_suite: 'TestSuite' = self.regression.test_suite
    
    def add_test_spec(self, test_spec: ResolvedTestSpec):
        test_spec.test_group = self
        test_spec.test_set = self.test_set
        test_spec.regression = self.regression
        test_spec.test_suite = self.test_suite
        self.test_specs.append(test_spec)


class TestSet:
    def __init__(self, name: str, regression: 'Regression'):
        self.name: str = name
        self.test_groups: Dict[str, TestGroup] = {}
        self.regression: 'Regression' = regression
        self.test_suite: 'TestSuite' = regression.test_suite
    
    def add_test_group(self, name: str) -> TestGroup:
        if name in self.test_groups:
            return self.test_groups[name]
        else:
            test_group = TestGroup(name, self)
            self.test_groups[name] = test_group
            return test_group


class Regression:
    def __init__(self, name: str, test_suite: 'TestSuite'):
        self.name: str = name
        self.directory_name: str = ""
        self.results_path: Path = Path()
        self.test_suite = test_suite
        self.db: 'RegressionDatabase' = self.test_suite.db
        self.rmh: 'RootManager' = self.db.rmh
        self.ip: Ip = None
        self.timestamp_start: datetime.datetime = datetime.datetime.now()
        self.timestamp_end: datetime.datetime = None
        self.duration: datetime.timedelta = datetime.timedelta()
        self.test_sets: Dict[str, TestSet] = {}
        self.waves_enabled: bool = False
        self.cov_enabled: bool = False
        self.verbosity: UvmVerbosity = UvmVerbosity.MEDIUM
        self.max_errors: int = 10
        self.max_duration: float = 1.0
        self.max_jobs: int = 1
        self.test_suite: 'TestSuite'
        self.test_specs: Dict[int, ResolvedTestSpec] = {}

    def set_ip(self, ip: Ip):
        self.ip = ip
        self.test_suite.resolved_ip = self.ip
        sim_path: Path = self.rmh.project_root_path / self.rmh.configuration.logic_simulation.root_path
        regression_dir_name: str = self.rmh.configuration.logic_simulation.regression_directory_name
        timestamp_start: str = self.timestamp_start.strftime("%Y_%m_%d_%H_%M_%S")
        self.directory_name: str = f"{self.ip.result_file_name}_{self.name}_{timestamp_start}"
        self.results_path: Path = Path(os.path.join(sim_path, regression_dir_name, self.directory_name))

    def add_test_set(self, name: str) -> TestSet:
        if name in self.test_sets:
            return self.test_sets[name]
        else:
            test_set = TestSet(name, self)
            self.test_sets[name] = test_set
            return test_set
    
    def render_cmp_config(self, target_name: str="default") -> LogicSimulatorCompilationRequest:
        config = LogicSimulatorCompilationRequest()
        config.use_custom_logs_path = True
        config.custom_logs_path = self.results_path
        config.max_errors = self.max_errors
        config.enable_waveform_capture = self.waves_enabled
        config.enable_coverage = self.waves_enabled
        config.target = target_name
        return config
    
    def render_elab_config(self, target_name: str="default") -> LogicSimulatorElaborationRequest:
        config = LogicSimulatorElaborationRequest()
        config.use_custom_logs_path = True
        config.custom_logs_path = self.results_path
        return config
    
    def render_cmp_elab_config(self, target_name: str="default") -> LogicSimulatorCompilationAndElaborationRequest:
        config = LogicSimulatorCompilationAndElaborationRequest()
        config.use_custom_logs_path = True
        config.custom_sim_results_path = self.results_path
        config.max_errors = self.max_errors
        config.enable_waveform_capture = self.waves_enabled
        config.enable_coverage = self.waves_enabled
        config.target = target_name
        return config
    
    def render_sim_configs(self, target_name: str="default") -> Dict[int, LogicSimulatorSimulationRequest]:
        sim_configs: Dict[int, LogicSimulatorSimulationRequest] = {}
        for set_name in self.test_sets:
            for group_name in self.test_sets[set_name].test_groups:
                for test_spec in self.test_sets[set_name].test_groups[group_name].test_specs:
                    seeds = []
                    if test_spec.spec_type == TestSpecTypes.SEED_LIST:
                        seeds = test_spec.specific_seeds
                    elif test_spec.spec_type == TestSpecTypes.NUM_RAND_SEEDS:
                        for _ in range(test_spec.num_rand_seeds):
                            random_int = randint(1, ((1 << 31) - 1))
                            while random_int in sim_configs:
                                random_int = randint(1, ((1 << 31) - 1))
                            seeds.append(random_int)
                    for seed in seeds:
                        config = LogicSimulatorSimulationRequest()
                        config.use_custom_logs_path = True
                        config.custom_logs_path = self.results_path
                        config.seed = seed
                        config.verbosity = self.verbosity
                        config.max_errors = self.max_errors
                        config.gui_mode = False
                        config.enable_waveform_capture = self.waves_enabled
                        config.enable_coverage = self.cov_enabled
                        config.test_name = test_spec.test_name
                        config.print_to_terminal = False
                        for key, value in test_spec.args.items():
                            if isinstance(value, bool):
                                if value:
                                    config.args_boolean.append(key)
                            else:
                                config.args_value[key] = value
                        config.target = target_name
                        sim_configs[seed] = config
                        self.test_specs[seed] = test_spec
        return sim_configs


SpecTestArg = Union[str, int, float, bool]

class TestSpec(Model):
    seeds: Union[PositiveInt, List[PositiveInt]]
    args: Optional[Dict[constr(pattern=VALID_NAME_REGEX), SpecTestArg]] = {}

SpecTestGroups = Dict[constr(pattern=VALID_NAME_REGEX), TestSpec]
SpecRegression = Union[TestSpec, SpecTestGroups, PositiveInt, List[PositiveInt]]
SpecTest = Dict[constr(pattern=VALID_NAME_REGEX), SpecRegression]
SpecTestSet = Dict[constr(pattern=VALID_NAME_REGEX), SpecTest]


class TestSuite(Model):
    ts: About
    tests: Dict[constr(pattern=VALID_NAME_REGEX), SpecTestSet]

    def __init__(self, **data: Any):
        super().__init__(**data)
        self._db: 'RegressionDatabase' = None
        self._file_path: Path = None
        self._file_path_set: bool = False
        self._resolved_ip: Ip = None
        self._supports_all_targets: bool = False
        self._resolved_valid_targets: List[str] = []
        self._resolved_regressions: Dict[str, Regression] = {}

    def __str__(self):
        return f"{self.ts.ip}/{self.ts.name}"
    
    @property
    def db(self) -> 'RegressionDatabase':
        return self._db

    @classmethod
    def load(cls, db: 'RegressionDatabase', file_path: Path):
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
            if data is None:
                data = {}
            instance = cls(**data)
            instance._db = db
            instance._file_path = file_path
            return instance
    
    def save(self, path: Path):
        with open(path, 'w') as f:
            yaml.dump(self.model_dump(), f)

    @property
    def name(self) -> str:
        return self.ts.name

    @property
    def file_path(self) -> Path:
        return self._file_path
    
    @property
    def resolved_ip(self) -> Ip:
        return self._resolved_ip
    @resolved_ip.setter
    def resolved_ip(self, value: Ip):
        self._resolved_ip = value
    
    @property
    def supports_all_targets(self) -> bool:
        return self._supports_all_targets
    
    @property
    def resolved_valid_targets(self) -> List[str]:
        return self._resolved_valid_targets

    @property
    def resolved_regressions(self) -> Dict[str, Regression]:
        return self._resolved_regressions

    def add_regression(self, name:str) -> Regression:
        if name in self._resolved_regressions:
            return self._resolved_regressions[name]
        else:
            regression = Regression(name, self)
            self._resolved_regressions[name] = regression
            return regression
    
    def check(self):
        # Check targets
        if len(self.ts.target) == 0:
            raise Exception(f"Must specify target(s)")
        for target in self.ts.target:
            clean_target = target.strip().lower()
            if clean_target == "*":
                self._supports_all_targets = True
                if len(self.ts.target) > 1:
                    self.db.rmh.warning(
                        f"Warning for test suite '{self}': target entries are being ignored due to the presence of wildcard '*' in the target list.")
                break
            else:
                self._resolved_valid_targets.append(clean_target)
        # Resolve test sets/groups/specs/regressions
        for test_set_name in self.tests:
            test_set_spec = self.tests[test_set_name]
            for test_name in test_set_spec:
                test_spec = test_set_spec[test_name]
                for regression_name in test_spec:
                    regression = self.add_regression(regression_name)
                    test_set = regression.add_test_set(test_set_name)
                    regression_data = test_spec[regression_name]
                    if type(regression_data) is int:
                        resolved_test_spec = ResolvedTestSpec()
                        resolved_test_spec.test_name = test_name
                        resolved_test_spec.spec_type = TestSpecTypes.NUM_RAND_SEEDS
                        resolved_test_spec.num_rand_seeds = int(regression_data)
                        test_group = test_set.add_test_group("default")
                        test_group.add_test_spec(resolved_test_spec)
                    elif type(regression_data) is TestSpec:
                        resolved_test_spec = ResolvedTestSpec()
                        resolved_test_spec.test_name = test_name
                        if 'args' in regression_data:
                            resolved_test_spec.args = regression_data['args']
                        if type(regression_data['seeds']) is int:
                            resolved_test_spec.spec_type = TestSpecTypes.NUM_RAND_SEEDS
                            resolved_test_spec.num_rand_seeds = regression_data['seeds']
                        elif type(regression_data['seeds']) is list:
                            resolved_test_spec.spec_type = TestSpecTypes.SEED_LIST
                            resolved_test_spec.specific_seeds = regression_data['seeds']
                        test_group = test_set.add_test_group("default")
                        test_group.add_test_spec(resolved_test_spec)
                    elif type(regression_data) is dict:
                        for test_group_name in regression_data:
                            test_group_spec = regression_data[test_group_name]
                            resolved_test_spec = ResolvedTestSpec()
                            resolved_test_spec.test_name = test_name
                            if 'args' in test_group_spec:
                                resolved_test_spec.args = test_group_spec['args']
                            if type(test_group_spec['seeds']) is int:
                                resolved_test_spec.spec_type = TestSpecTypes.NUM_RAND_SEEDS
                                resolved_test_spec.num_rand_seeds = test_group_spec['seeds']
                            elif type(test_group_spec['seeds']) is list:
                                resolved_test_spec.spec_type = TestSpecTypes.SEED_LIST
                                resolved_test_spec.specific_seeds = test_group_spec['seeds']
                            test_group = test_set.add_test_group(test_group_name)
                            test_group.add_test_spec(resolved_test_spec)
                    elif type(regression_data) is list:
                        resolved_test_spec = ResolvedTestSpec()
                        resolved_test_spec.test_name = test_name
                        resolved_test_spec.spec_type = TestSpecTypes.SEED_LIST
                        resolved_test_spec.specific_seeds = regression_data
                        test_group = test_set.add_test_group("default")
                        test_group.add_test_spec(resolved_test_spec)
        # Ensure regression names in settings exist and apply settings to regressions
        for regression_name in self.ts.cov:
            if regression_name not in self._resolved_regressions:
                self.db.rmh.warning(f"Regression '{regression_name}' does not exist and its coverage setting is ignored")
            else:
                self._resolved_regressions[regression_name].cov_enabled = True
        for regression_name in self.ts.waves:
            if regression_name not in self._resolved_regressions:
                self.db.rmh.warning(f"Regression '{regression_name}' does not exist and its wave capture setting is ignored")
            else:
                self._resolved_regressions[regression_name].waves_enabled = True
        for regression_name in self.ts.max_duration:
            if regression_name not in self._resolved_regressions:
                self.db.rmh.warning(f"Regression '{regression_name}' does not exist and its max duration setting is ignored")
            else:
                self._resolved_regressions[regression_name].max_duration = self.ts.max_duration[regression_name]
        for regression_name in self.ts.max_errors:
            if regression_name not in self._resolved_regressions:
                self.db.rmh.warning(f"Regression '{regression_name}' does not exist and its max errors setting is ignored")
            else:
                self._resolved_regressions[regression_name].max_errors = self.ts.max_errors[regression_name]
        for regression_name in self.ts.max_jobs:
            if regression_name not in self._resolved_regressions:
                self.db.rmh.warning(f"Regression '{regression_name}' does not exist and its max jobs setting is ignored")
            else:
                self._resolved_regressions[regression_name].max_jobs = self.ts.max_jobs[regression_name]
        for regression_name in self.ts.verbosity:
            if regression_name not in self._resolved_regressions:
                self.db.rmh.warning(f"Regression '{regression_name}' does not exist and its verbosity setting is ignored")
            else:
                self._resolved_regressions[regression_name].verbosity = self.ts.verbosity[regression_name]


class RegressionRequest:
    def __init__(self):
        self.target: str = ""
        self.dry_mode: bool = False
        self.app: LogicSimulators = LogicSimulators.UNDEFINED
        self.compilation_request: LogicSimulatorCompilationRequest = None
        self.elaboration_request: LogicSimulatorElaborationRequest = None
        self.compilation_and_elaboration_request: LogicSimulatorCompilationAndElaborationRequest = None
        self.simulation_requests: Dict[int, LogicSimulatorSimulationRequest] = {}

class RegressionSimulationReport:
    def __init__(self):
        self.test_spec: ResolvedTestSpec
        self.sim_report: LogicSimulatorSimulationReport

class TestGroupReport(Model):
    name: Optional[str] = ""
    success: Optional[bool] = False
    num_tests: Optional[PositiveInt] = 0
    num_passed_tests: Optional[PositiveInt] = 0
    num_passed_tests_with_no_warnings: Optional[PositiveInt] = 0
    num_passed_tests_with_warnings: Optional[PositiveInt] = 0
    num_failed_tests: Optional[PositiveInt] = 0
    passing_tests_percentage: Optional[PositiveFloat] = 0
    failing_tests_percentage: Optional[PositiveFloat] = 0
    simulation_reports: Optional[List[LogicSimulatorSimulationReport]] = []
    passed_tests: Optional[List[LogicSimulatorSimulationReport]] = []
    passed_tests_with_no_warnings: Optional[List[LogicSimulatorSimulationReport]] = []
    passed_tests_with_warnings: Optional[List[LogicSimulatorSimulationReport]] = []
    failed_tests: Optional[List[LogicSimulatorSimulationReport]] = []
    test_set_report: Optional['TestSetReport'] = None

class TestSetReport(Model):
    name: Optional[str] = ""
    success: Optional[bool] = False
    num_tests: Optional[PositiveInt] = 0
    num_passed_tests: Optional[PositiveInt] = 0
    num_passed_tests_with_no_warnings: Optional[PositiveInt] = 0
    num_passed_tests_with_warnings: Optional[PositiveInt] = 0
    num_failed_tests: Optional[PositiveInt] = 0
    passing_tests_percentage: Optional[PositiveFloat] = 0
    failing_tests_percentage: Optional[PositiveFloat] = 0
    test_group_reports: Optional[List[TestGroupReport]] = []

class RegressionReport(Model):
    name: Optional[str] = ""
    full_name: Optional[str] = ""
    target_name: Optional[str] = ""
    test_suite_file_path: Optional[Path] = Path()
    simulator: Optional[LogicSimulators] = LogicSimulators.UNDEFINED
    results_path: Optional[Path] = None
    success: Optional[bool] = False
    compilation_report: Optional[LogicSimulatorCompilationReport] = None
    elaboration_report: Optional[LogicSimulatorElaborationReport] = None
    compilation_and_elaboration_report: Optional[LogicSimulatorCompilationAndElaborationReport] = None
    simulation_reports: Optional[List[RegressionSimulationReport]] = []
    coverage_merge_report: Optional[LogicSimulatorCoverageMergeReport] = None
    num_tests: Optional[PositiveInt] = 0
    num_passing_tests: Optional[PositiveInt] = 0
    num_passing_tests_with_no_warnings: Optional[PositiveInt] = 0
    num_passing_tests_with_warnings: Optional[PositiveInt] = 0
    num_failing_tests: Optional[PositiveInt] = 0
    passing_tests_percentage: Optional[PositiveFloat] = 0
    failing_tests_percentage: Optional[PositiveFloat] = 0
    passing_tests: Optional[List[RegressionSimulationReport]] = []
    passing_tests_with_no_warnings: Optional[List[RegressionSimulationReport]] = []
    passing_tests_with_warnings: Optional[List[RegressionSimulationReport]] = []
    failing_tests: Optional[List[RegressionSimulationReport]] = []
    test_set_reports: Optional[List[TestSetReport]] = []
    dsim_cloud_simulation_job_file_path: Optional[Path] = Path()
    cov_enabled: Optional[bool] = False
    waves_enabled: Optional[bool] = False
    verbosity: Optional[UvmVerbosity] = UvmVerbosity.MEDIUM
    timestamp_start: Optional[datetime.datetime] = datetime.datetime.now()
    timestamp_end: Optional[datetime.datetime] = datetime.datetime.now()
    duration: Optional[datetime.timedelta] = datetime.timedelta()

    def __init__(self, rmh: 'RootManager', **data):
        super().__init__(**data)
        self._rmh = rmh

    @property
    def junit_xml_report_file_name(self) -> Path:
        return self.results_path / "junit_test_report.xml"
    @property
    def html_report_file_name(self) -> Path:
        return self.results_path / "test_report.html"
    @property
    def coverage_report_file_name(self) -> Path:
        return self.coverage_merge_report.html_report_path

    def generate_junit_xml_report_tree(self) -> ElementTree.ElementTree:
        test_suite_path_str: str = str(os.path.relpath(self.test_suite_file_path, self._rmh.project_root_path))
        timestamp_str: str = self.timestamp_start.strftime('%Y-%m-%dT%H:%M:%S')
        root: Element = Element('testsuites')
        root.set('name', self.name)
        root.set('tests', str(len(self.simulation_reports)))
        root.set('time', str(self.duration.total_seconds()))
        root.set('timestamp', timestamp_str)
        root.set('failures', str(len(self.failing_tests)))
        root_testsuite: SubElement = SubElement(root, 'testsuite')
        root_testsuite.set('name', self.name)
        root_testsuite.set('tests', str(len(self.simulation_reports)))
        root_testsuite.set('time', str(self.duration.total_seconds()))
        root_testsuite.set('timestamp', timestamp_str)
        root_testsuite.set('failures', str(len(self.failing_tests)))
        root_testsuite.set('file', test_suite_path_str)
        root_testsuite_properties: SubElement = SubElement(root_testsuite, 'properties')
        target_property: SubElement = SubElement(root_testsuite_properties, 'property')
        target_property.set('name', 'target')
        target_property.set('value', self.target_name)
        coverage_property: SubElement = SubElement(root_testsuite_properties, 'property')
        coverage_property.set('name', 'coverage')
        coverage_property.set('value', str(self.cov_enabled))
        waves_property: SubElement = SubElement(root_testsuite_properties, 'property')
        waves_property.set('name', 'waves')
        waves_property.set('value', str(self.waves_enabled))
        verbosity_property: SubElement = SubElement(root_testsuite_properties, 'property')
        verbosity_property.set('name', 'verbosity')
        verbosity_property.set('value', self.verbosity.value)
        for test_set in self.test_set_reports:
            test_set_testsuite: SubElement = SubElement(root_testsuite_properties, 'testsuite')
            test_set_testsuite.set('name', test_set.name)
            test_set_testsuite.set('tests', str(test_set.num_tests))
            test_set_testsuite.set('failures', str(test_set.num_failed_tests))
            for test_group in test_set.test_group_reports:
                test_group_testsuite: SubElement = SubElement(test_set_testsuite, 'testsuite')
                test_group_testsuite.set('name', test_group.name)
                test_group_testsuite.set('tests', str(test_group.num_tests))
                test_group_testsuite.set('failures', str(test_group.num_failed_tests))
                for simulation_report in test_group.simulation_reports:
                    simulation_report_testcase: SubElement = SubElement(test_group_testsuite, 'testcase')
                    simulation_report_testcase.set('name', simulation_report.test_name)
                    simulation_report_testcase.set('classname', simulation_report.uvm_test_class_name)
                    simulation_report_testcase.set('time', str(simulation_report.duration.total_seconds()))
                    simulation_report_properties: SubElement = SubElement(simulation_report_testcase, 'properties')
                    seed_property: SubElement = SubElement(simulation_report_properties, 'property')
                    seed_property.set('name', 'seed')
                    seed_property.set('value', str(simulation_report.seed))
                    for error_message in simulation_report.errors:
                        error_error: SubElement = SubElement(simulation_report_testcase, 'error')
                        error_error.set('message', error_message)
                    for fatal_message in simulation_report.fatals:
                        fatal_failure: SubElement = SubElement(simulation_report_testcase, 'failure')
                        fatal_failure.set('message', fatal_message)
                    for warning_message in simulation_report.fatals:
                        warning_warning: SubElement = SubElement(simulation_report_testcase, 'warning')
                        warning_warning.set('message', warning_message)
                    for arg in simulation_report.user_args_boolean:
                        arg_property: SubElement = SubElement(simulation_report_properties, 'property')
                        arg_property.set('name', f'+{arg}')
                        arg_property.set('value', 'true')
                    for arg in simulation_report.user_args_value:
                        arg_property: SubElement = SubElement(simulation_report_properties, 'property')
                        arg_property.set('name', f'+{arg}')
                        arg_property.set('value', simulation_report.user_args_value[arg])
        tree = ElementTree.ElementTree(root)
        return tree

    def generate_junit_xml_report(self):
        xml_tree: ElementTree.ElementTree = self.generate_junit_xml_report_tree()
        xml_tree.write(self.junit_xml_report_file_name, encoding='utf-8', xml_declaration=True)

    def generate_html_report_doc(self) -> str:
        template: Template = self._rmh.j2_env.get_template("regression_test_report.html.j2")
        rendered_template: str = template.render(self.model_dump())
        return rendered_template

    def generate_html_report(self):
        html_report_doc: str = self.generate_html_report_doc()
        with open(self.html_report_file_name, 'w') as html_report_file:
            html_report_file.write(html_report_doc)


class RegressionRunner:
    def __init__(self, db: 'RegressionDatabase', ip: Ip, regression: Regression, simulator: LogicSimulator, request: RegressionRequest):
        self.db: 'RegressionDatabase' = db
        self.rmh: 'RootManager' = self.db.rmh
        self.request: RegressionRequest = request
        self.report: RegressionReport = RegressionReport(self.rmh)
        self.phase: Phase = None
        self.ip: Ip = ip
        self.regression: Regression = regression
        self.simulator: LogicSimulator = simulator
        self.scheduler: JobScheduler = None
    
    def __str__(self):
        return f"{self.ip.lib_name}_{self.regression.name}"
        
    def execute_regression(self, scheduler: JobScheduler) -> RegressionReport:
        self.scheduler = scheduler
        self.request.simulation_requests = self.regression.render_sim_configs(self.request.target)
        self.rmh.create_directory(self.regression.results_path)
        if self.request.app == LogicSimulators.DSIM:
            self.dsim_cloud_simulation()
        else:
            self.parallel_simulation()
        self.report.duration = self.report.timestamp_end - self.report.timestamp_start
        self.fill_report()
        self.merge_coverage()
        return self.report
    
    def parallel_simulation(self):
        if not self.request.dry_mode:
            timeout = self.regression.max_duration * 3600
            with ThreadPoolExecutor(max_workers=self.regression.max_jobs) as executor:
                future_simulations = [executor.submit(self.launch_simulation, self.request.simulation_requests[seed]) for seed in
                                      self.request.simulation_requests]
                with tqdm(total=len(self.request.simulation_requests), desc="Simulations") as pbar:
                    for future in as_completed(future_simulations):
                        try:
                            result = future.result(timeout=timeout)
                        except Exception as e:
                            self.rmh.current_phase.error = e
                        finally:
                            pbar.update(1)
            self.report.timestamp_end = datetime.datetime.now()
            self.report.success = True
            for simulation_report in self.report.simulation_reports:
                self.report.success &= simulation_report.sim_report.success
    
    def launch_simulation(self, request: LogicSimulatorSimulationRequest):
        sim_report: LogicSimulatorSimulationReport = self.simulator.simulate(self.ip, request, self.scheduler)
        test_spec: ResolvedTestSpec = self.regression.test_specs[request.seed]
        regression_sim_report: RegressionSimulationReport = RegressionSimulationReport()
        regression_sim_report.test_spec = test_spec
        regression_sim_report.sim_report = sim_report
        self.report.simulation_reports.append(regression_sim_report)
    
    def dsim_cloud_simulation(self):
        # 1. Prep simulator
        if self.simulator.name != "dsim":
            raise TypeError(
                f"The simulator must be an instance of SimulatorMetricsDSim, got {type(self.simulator).__name__}")
        if not self.rmh.configuration.project.local_mode:
            raise Exception(f"DSim Cloud requires Project to be configured in 'local_mode'")
        simulator: SimulatorMetricsDSim = self.simulator
        simulator.cloud_mode = True
        # 2. Amass configuration objects for compilation/elaboration
        if self.ip.has_vhdl_content:
            self.request.compilation_request = self.regression.render_cmp_config(self.request.target)
            self.request.compilation_request.use_relative_paths = True
            self.request.elaboration_request = self.regression.render_elab_config(self.request.target)
            self.request.elaboration_request.use_relative_paths = True
        else:
            self.request.compilation_and_elaboration_request = self.regression.render_cmp_elab_config(self.request.target)
            self.request.compilation_and_elaboration_request.use_relative_paths = True
        # 3. Create DSim Cloud Configuration object and fill it in from our regression configuration
        cloud_simulation_config: DSimCloudSimulationRequest = DSimCloudSimulationRequest()
        cloud_simulation_config.name = f"{self.ip.ip.name}-{self.regression.name}"
        cloud_simulation_config.name = cloud_simulation_config.name.replace("_", "-")
        cloud_simulation_config.results_path = self.regression.results_path
        cloud_simulation_config.dry_mode = self.request.dry_mode
        cloud_simulation_config.timeout = self.regression.max_duration
        cloud_simulation_config.max_parallel_tasks = self.regression.max_jobs
        cloud_simulation_config.compute_size = self.db.rmh.configuration.logic_simulation.altair_dsim_cloud_max_compute_size
        cloud_simulation_config.compilation_config = self.request.compilation_request
        cloud_simulation_config.elaboration_config = self.request.elaboration_request
        cloud_simulation_config.compilation_and_elaboration_config = self.request.compilation_and_elaboration_request
        for seed in self.request.simulation_requests:
            simulation_config = self.request.simulation_requests[seed]
            cloud_simulation_config.simulation_configs.append(simulation_config)
        # 4. Launch job on the cloud via simulator
        cloud_simulation_report = simulator.dsim_cloud_simulate(self.ip, cloud_simulation_config, self.scheduler)
        # 5. Populate regression report from DSim Cloud Report
        self.report.success = cloud_simulation_report.success
        self.report.timestamp_start = cloud_simulation_report.timestamp_start
        self.report.timestamp_end = cloud_simulation_report.timestamp_end
        self.report.dsim_cloud_simulation_job_file_path = cloud_simulation_report.cloud_job_file_path
        self.report.compilation_report = cloud_simulation_report.compilation_report
        self.report.elaboration_report = cloud_simulation_report.elaboration_report
        self.report.compilation_and_elaboration_report = cloud_simulation_report.compilation_and_elaboration_report
        for simulation_report in cloud_simulation_report.simulation_reports:
            test_spec: ResolvedTestSpec = self.regression.test_specs[simulation_report.seed]
            regression_sim_report: RegressionSimulationReport = RegressionSimulationReport()
            regression_sim_report.test_spec = test_spec
            regression_sim_report.sim_report = simulation_report
            self.report.simulation_reports.append(regression_sim_report)

    def merge_coverage(self):
        if self.report.success and self.regression.cov_enabled:
            coverage_merge_config: LogicSimulatorCoverageMergeRequest = LogicSimulatorCoverageMergeRequest()
            coverage_merge_config.output_path = self.regression.results_path / "coverage_report"
            coverage_merge_config.create_html_report = True
            coverage_merge_config.html_report_path = self.regression.results_path / "coverage_report"
            coverage_merge_config.merge_log_file_path = self.regression.results_path / f"cov_merge.{self.simulator.name}.log"
            for sim_config in self.report.simulation_reports:
                coverage_merge_config.input_simulation_reports.append(sim_config.sim_report)
            self.report.coverage_merge_report = self.simulator.coverage_merge(self.ip, coverage_merge_config, self.scheduler)
            self.report._coverage_report_file_name = self.report.coverage_merge_report.html_report_path


    def fill_report(self):
        self.report.target_name = self.request.target
        self.report.test_suite_file_path = self.regression.test_suite.file_path
        self.report.verbosity = self.regression.verbosity
        if self.request.dry_mode:
            self.report.success = True
            if self.report.compilation_report:
                self.report.compilation_report.success = True
            if self.report.elaboration_report:
                self.report.compilation_report.success = True
            if self.report.compilation_report:
                self.report.compilation_report.success = True
        else:
            self.report.results_path = self.regression.results_path
            self.report.cov_enabled = self.regression.cov_enabled
            self.report.waves_enabled = self.regression.waves_enabled
            test_group_map: Dict[TestGroup, TestGroupReport] = {}
            for test_set_name in self.regression.test_sets:
                test_set = self.regression.test_sets[test_set_name]
                test_set_report = TestSetReport()
                test_set_report.name = test_set_name
                test_set_report.num_tests = 0
                for test_group_name in test_set.test_groups:
                    test_group = test_set.test_groups[test_group_name]
                    test_group_report = TestGroupReport()
                    test_set_report.test_group_reports.append(test_group_report)
                    test_group_map[test_group] = test_group_report
                    test_group_report.test_set_report = test_set_report
                    test_group_report.name = test_group_name
                    test_group_report.num_tests = 0
            for seed in self.regression.test_specs:
                test_spec = self.regression.test_specs[seed]
                for simulation_report in self.report.simulation_reports:
                    if simulation_report.sim_report.seed == seed:
                        test_group_report = test_group_map[test_spec.test_group]
                        test_group_report.num_tests += 1
                        test_group_report.test_set_report.num_tests += 1
                        if simulation_report.sim_report.success:
                            test_group_report.passed_tests.append(simulation_report)
                            test_group_report.num_passed_tests += 1
                            test_group_report.test_set_report.num_passed_tests += 1
                            if simulation_report.sim_report.num_warnings > 0:
                                test_group_report.passed_tests_with_warnings.append(simulation_report)
                                test_group_report.num_passed_tests_with_warnings += 1
                                test_group_report.test_set_report.num_passed_tests_with_warnings += 1
                            else:
                                test_group_report.passed_tests_with_no_warnings.append(simulation_report)
                                test_group_report.num_passed_tests_with_no_warnings += 1
                                test_group_report.test_set_report.num_passed_tests_with_no_warnings += 1
                        else:
                            test_group_report.failed_tests.append(simulation_report)
                            test_group_report.num_failed_tests += 1
                            test_group_report.test_set_report.num_failed_tests += 1
                        break
            for simulation_report in self.report.simulation_reports:
                test_spec: ResolvedTestSpec = self.regression.test_specs[simulation_report.sim_report.seed]
                if simulation_report.sim_report.success:
                    self.report.passing_tests.append(simulation_report)
                    if simulation_report.sim_report.num_warnings == 0:
                        self.report.passing_tests_with_no_warnings.append(simulation_report)
                    else:
                        self.report.passing_tests_with_warnings.append(simulation_report)
                else:
                    self.report.failing_tests.append(simulation_report)
            self.report.simulator = self.request.app
            self.report.num_tests = len(self.report.simulation_reports)
            self.report.num_passing_tests = len(self.report.passing_tests)
            self.report.num_passing_tests_with_no_warnings = len(self.report.passing_tests_with_no_warnings)
            self.report.num_passing_tests_with_warnings = len(self.report.passing_tests_with_warnings)
            self.report.num_failing_tests = len(self.report.failing_tests)
            if self.report.num_passing_tests == 0:
                self.report.passing_tests_percentage = 0
            else:
                self.report.passing_tests_percentage = (self.report.num_passing_tests / self.report.num_tests) * 100
            if self.report.num_failing_tests == 0:
                self.report.failing_tests_percentage = 0
            else:
                self.report.failing_tests_percentage = (self.report.num_failing_tests / self.report.num_tests) * 100
            for test_set_report in self.report.test_set_reports:
                if test_set_report.num_passing_tests == 0:
                    test_set_report.passing_tests_percentage = 0
                else:
                    test_set_report.passing_tests_percentage = (test_set_report.num_passed_tests / test_set_report.num_tests) * 100
                if test_set_report.num_failing_tests == 0:
                    test_set_report.failing_tests_percentage = 0
                else:
                    test_set_report.failing_tests_percentage = (test_set_report.num_failing_tests / test_set_report.num_tests) * 100
                    for test_group_report in test_set_report.test_group_reports:
                        if test_group_report.num_passing_tests == 0:
                            test_group_report.passing_tests_percentage = 0
                        else:
                            test_group_report.passing_tests_percentage = (test_group_report.num_passed_tests / test_group_report.num_tests) * 100
                        if test_group_report.num_failing_tests == 0:
                            test_group_report.failing_tests_percentage = 0
                        else:
                            test_group_report.failing_tests_percentage = (test_group_report.num_failing_tests / test_group_report.num_tests) * 100


class RegressionDatabase(Service):
    def __init__(self, rmh: 'RootManager'):
        super().__init__(rmh, 'datum', 'regression_database', 'Regression Database')
        self._type = ServiceType.REGRESSION
        self._test_suites: List[TestSuite] = []

    def is_available(self) -> bool:
        return True

    def create_directory_structure(self):
        pass

    def create_files(self):
        pass

    def get_version(self) -> Version:
        return Version('1.0.0')
    
    def discover_test_suites(self, path: Path):
        path = Path(path)  # Ensure `path` is a Path object
        ts_files = path.rglob('*ts.yml')
        for ts_file in ts_files:
            try:
                test_suite = TestSuite.load(self, ts_file)
                self.add_test_suite(test_suite)
            except Exception as e:
                self.rmh.warning(f"Failed to process {ts_file}: {e}")
    
    def add_test_suite(self, test_suite: TestSuite):
        try:
            test_suite.check()
        except Exception as e:
            self.rmh.warning(f"Test Suite {test_suite} failed consistency check: {e}")
        else:
            self.rmh.debug(f"Added test suite '{test_suite}'")
            self._test_suites.append(test_suite)
    
    def find_regression(self, test_suite_name: str, regression_name: str, raise_exception_if_not_found: bool=False):
        # Search for the test suite with the specified name
        for test_suite in self._test_suites:
            if test_suite.name == test_suite_name:
                # Search for the regression in the found test suite
                if regression_name in test_suite.resolved_regressions:
                    return test_suite.resolved_regressions[regression_name]
                else:
                    if raise_exception_if_not_found:
                        raise Exception(f"Regression '{regression_name}' not found in Test Suite '{test_suite_name}'")
                    return None
        # If no matching test suite is found
        if raise_exception_if_not_found:
            raise Exception(f"Test suite '{test_suite_name}' not found")
        return None

    def find_regression_default_test_suite(self, regression_name: str, raise_exception_if_not_found: bool=False):
        test_suite: TestSuite = None
        if len(self._test_suites) == 0:
            raise Exception(f"No Test Suites")
        elif len(self._test_suites) == 1:
            test_suite = self._test_suites[0]
        else:
            for ts in self._test_suites:
                if ts.name == "default":
                    test_suite = ts
                    break
        if not test_suite:
            raise Exception(f"Could not find default Test Suite")
        if regression_name in test_suite.resolved_regressions:
            return test_suite.resolved_regressions[regression_name]
        else:
            if raise_exception_if_not_found:
                raise Exception(f"Regression '{regression_name}' not found in default Test Suite")
            return None
    
    def get_regression_runner(self, ip: Ip, regression: Regression, simulator: LogicSimulator, config: RegressionRequest) -> RegressionRunner:
        regression_runner: RegressionRunner = RegressionRunner(self, ip, regression, simulator, config)
        return regression_runner
    