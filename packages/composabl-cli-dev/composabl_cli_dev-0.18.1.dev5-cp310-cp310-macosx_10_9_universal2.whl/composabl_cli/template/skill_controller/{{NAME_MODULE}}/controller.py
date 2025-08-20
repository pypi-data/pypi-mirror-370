# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from random import randint
from typing import Dict, List

from composabl_core import SkillController


class Controller(SkillController):
    """
    We start at 10 reward and count down to 0 the goal is that the agent stays
    above or equal to 0 this means it learned to cound +1 each time
    """

    def __init__(self, *args, **kwargs):
        self.past_obs = None
        self.counter = 10
        self.sensor_name = "counter"

    async def compute_action(self, transformed_sensors: Dict, action) -> List[float]:
        # generate a random action between -5 and 5
        action = [randint(-5, 5)]
        return action

    async def compute_success_criteria(self, transformed_sensors: Dict, action) -> bool:
        return bool(transformed_sensors[self.sensor_name] >= 10)

    async def compute_termination(self, transformed_sensors: Dict, action) -> bool:
        return bool(transformed_sensors[self.sensor_name] <= -10)

    async def transform_sensors(self, sensors, action) -> str:
        return sensors

    async def transform_action(self, transformed_sensors: Dict, action) -> float:
        return action

    async def filtered_sensor_space(self) -> List[str]:
        return ["counter"]
