from concurrent.futures import ThreadPoolExecutor

from pilot.generater.vertexai import VertexAISingleton
from pilot.control.control_interface import ControlInterface
from pilot.unit.impl.base_unit import BaseUnit
from pilot.config.config_reader import ConfigReader


class BaseController(ControlInterface):

    def __init__(self):
        vertexai: VertexAISingleton = VertexAISingleton.get_instance()

    def _init_unit(self):
        return BaseUnit()

    def run(self):
        import time
        config_dto = ConfigReader().get_dto()
        def worker():
            unit = self._init_unit()
            unit.run()
        with ThreadPoolExecutor(max_workers=config_dto.threads) as executor:
            futures = []
            for _ in range(config_dto.threads):
                futures.append(executor.submit(worker))
                time.sleep(0.2)
            for future in futures:
                future.result()
