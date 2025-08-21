# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

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
        """
        Compute action in a programme selector is to select the best skill based in a rule or an optimization.
        Let's supose that we have three skills:
        1 - Decrease counter
        2 - Increase counter
        3 - Stop
        """
        # return Skill 1 = decrease
        if self.counter > 10:
            return [0]
        # return Skill 2 = increase
        elif self.counter < 10:
            return [1]
        # return Skill 3 = stop
        else:
            return [3]

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
