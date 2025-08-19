# Copyright 2020-2025 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
import os
import subprocess
from datetime import datetime
from mio_client.core.scheduler import JobSchedulerConfiguration, JobScheduler, JobResults, Job, JobSet


def get_schedulers():
    return [SubProcessScheduler]


class SubProcessSchedulerConfiguration(JobSchedulerConfiguration):
    pass


class SubProcessScheduler(JobScheduler):
    def __init__(self, rmh: 'RootManager'):
        super().__init__(rmh, "sub_process")
        self._results_in_progress = []

    def is_available(self) -> bool:
        return True

    def init(self):
        pass

    def cleanup(self):
        for result in self._results_in_progress:
            result.kill()

    def do_dispatch_job(self, job: Job, configuration: SubProcessSchedulerConfiguration) -> JobResults:
        results = JobResults()
        results.timestamp_start = datetime.now()
        command_list: list[str] = job.pre_arguments + [str(job.binary)] + job.arguments
        command_str = "  ".join(command_list)
        path = os.environ['PATH']
        path = f"{job.pre_path}:{path}:{job.post_path}"
        final_env_vars = {**job.env_vars, **os.environ}
        final_env_vars['PATH'] = path
        if not configuration.dry_run:
            if configuration.output_to_terminal:
                result = subprocess.Popen(args=command_str, cwd=job.wd, shell=True, env=final_env_vars, text=True)
            else:
                result = subprocess.Popen(args=command_str, cwd=job.wd, shell=True, env=final_env_vars,
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if configuration.kill_job_on_termination:
                self._results_in_progress.append(result)
            result.wait(timeout=configuration.timeout * 60)
            if configuration.kill_job_on_termination:
                self._results_in_progress.append(result)
            if result.stdout:
                results.stdout = str(result.stdout.read())
            if result.stderr:
                results.stderr = str(result.stderr.read())
            results.return_code = result.returncode
        results.timestamp_end = datetime.now()
        return results

    def do_dispatch_job_set(self, job_set: JobSet, configuration: SubProcessSchedulerConfiguration):
        pass
        # TODO IMPLEMENT

