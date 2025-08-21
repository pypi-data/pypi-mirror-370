import os

from src.pilot.unit.unit_interface import UnitInterface
from src.pilot.job.impl.base_job import BaseJob
from src.pilot.config.config_reader import ConfigReader

class BaseUnit(UnitInterface):
    config_dto = None
    joblist = []

    def __init__(self):
        self.config_dto  = ConfigReader().get_dto()


    def _init_job(self,step):
        return BaseJob()

    def run(self):
        steps = self.config_dto.steps
        skipsteps = self.config_dto.skipsteps
        for index, step in enumerate(steps):
            if step in skipsteps:
                continue
            self._run_jobs_in_step_dir(self.config_dto.work_space+ "/" +step,step,index)

    def _run_jobs_in_step_dir(self, current_step_dir, step,index):
        for dirpath, _, filenames in os.walk(current_step_dir):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                job = self._init_job(step)
                job.current_step = step
                job.step_index = index
                job.file_path = file_path
                if self.job_need_run(job,filename,index):
                    job.run()


    def job_need_run(self, job:BaseJob,filename: str,index):
        return True