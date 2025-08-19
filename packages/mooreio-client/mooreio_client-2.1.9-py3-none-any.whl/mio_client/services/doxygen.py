# Copyright 2020-2025 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
import os
from abc import ABC
from pathlib import Path
from typing import List, Optional, Dict

from semantic_version import Version

from ..core.scheduler import JobScheduler, Job, JobSchedulerConfiguration
from ..core.service import Service, ServiceType
from ..core.ip import Ip
from ..core.model import Model


#######################################################################################################################
# API Entry Point
#######################################################################################################################
def get_services():
    return [DoxygenService]


#######################################################################################################################
# Support Classes
#######################################################################################################################
class DoxygenServiceRequest:
    def __init__(self):
        self.dry_mode: bool = False
        self.private: bool = False

class DoxygenServiceReport(Model):
    scheduler_config: Optional[JobSchedulerConfiguration] = None
    success: Optional[bool] = False
    jobs: Optional[List[Job]] = []
    output_path: Optional[Path] = Path()
    tagfile_path: Optional[Path] = Path()
    html_output_path: Optional[Path] = Path()
    html_index_path: Optional[Path] = Path()


#######################################################################################################################
# Service
#######################################################################################################################
class DoxygenService(Service):
    def __init__(self, rmh: 'RootManager'):
        super().__init__(rmh, 'dimitri_van_heesch', 'doxygen', 'Doxygen')
        self._type = ServiceType.DOCUMENTATION_GENERATOR
        self._installation_path: Path = Path(self.rmh.configuration.docs.doxygen_installation_path)
        self._output_path: Path = Path(self.rmh.project_root_path, self.rmh.configuration.docs.root_path) / "doxygen_output"

    def is_available(self) -> bool:
        return self.rmh.directory_exists(self._installation_path)

    def create_directory_structure(self):
        self.rmh.create_directory(self._output_path)

    def create_files(self):
        pass

    def get_version(self) -> Version:
        return Version('1.0.0')

    def generate_documentation(self, ip: Ip, request: DoxygenServiceRequest, scheduler: JobScheduler) -> DoxygenServiceReport:
        # 1. Initialize report
        report = DoxygenServiceReport()
        report.output_path = self._output_path / ip.lib_name
        # 2. Remove previous outputs
        self.rmh.remove_directory(report.output_path)
        # 3. Get list of existing, local doxygen outputs for tagfiles
        tagfiles = [str(path) for path in self._output_path.iterdir() if path.is_dir()]
        # 4. Prepare report and directory structure
        report.tagfile_path = report.output_path / f"{ip.lib_name}.tag"
        report.html_output_path = report.output_path / "html"
        report.html_index_path = report.html_output_path / "index.html"
        self.rmh.create_directory(report.output_path)
        self.rmh.create_directory(report.html_output_path)
        report.scheduler_config = JobSchedulerConfiguration(self.rmh)
        report.scheduler_config.dry_run = request.dry_mode
        report.scheduler_config.output_to_terminal = self.rmh.print_trace
        # 5. Prepare Job arguments and environment variables
        pre_args: List[str] = []
        tagfiles_paths_str: str = ""
        for tagfile in tagfiles:
            tagfiles_paths_str += f"{tagfile} "
        pre_args.append(f"OUTPUT_PATH='{report.output_path}'")
        pre_args.append(f"PROJECT_NAME='{ip}'")
        pre_args.append(f"PROJECT_BRIEF='{ip}'")
        pre_args.append(f"IP_NAME='{ip.ip.name}'")
        pre_args.append(f"PROJECT_NUMBER='{ip.ip.name}'")
        pre_args.append(f"SRC_PATH='{ip.resolved_src_path}'")
        pre_args.append(f"MIO_HOME='{self.rmh.data_files_path}'")
        pre_args.append(f"GENERATE_TAGFILE='{report.tagfile_path}'")
        pre_args.append(f"TAGFILES='{tagfiles_paths_str}'")
        if ip.has_docs:
            pre_args.append(f"DOCS_PATH='{ip.resolved_docs_path}'")
            pre_args.append(f"IMAGE_PATH='{ip.resolved_docs_path}'")
            pre_args.append(f"INPUT='{ip.resolved_docs_path}'")
        if ip.has_examples:
            pre_args.append(f"EXAMPLE_PATH='{ip.resolved_examples_path}'")
        args: List[str] = []
        if request.private:
            args.append(str(self.rmh.data_files_path / "doxygen.private.cfg"))
        else:
            args.append(str(self.rmh.data_files_path / "doxygen.public.cfg"))
        # 6. Prepare and submit Job
        job_generate: Job = Job(self.rmh, self.rmh.temp_dir, f"doyxgen_{ip.lib_name}",
                                Path(os.path.join(self._installation_path, "doxygen")), args)
        job_generate.pre_arguments = pre_args
        report.jobs.append(job_generate)
        if request.dry_mode:
            report.success = True
        else:
            results_generate = scheduler.dispatch_job(job_generate, report.scheduler_config)
            report.success = (results_generate.return_code == 0)
        return report
    