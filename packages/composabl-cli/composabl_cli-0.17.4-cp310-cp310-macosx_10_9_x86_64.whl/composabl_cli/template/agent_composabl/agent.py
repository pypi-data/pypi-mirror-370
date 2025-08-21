# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import os
from typing import Dict

from composabl import Agent, MaintainGoal, Sensor, Skill, Trainer

# Accept the EULA
os.environ["COMPOSABL_EULA_AGREED"] = "1"

# Set the license
# os.environ["COMPOSABL_LICENSE"] = "YOUR_LICENSE_KEY"


class BalanceTeacher(MaintainGoal):
    def __init__(self, *args, **kwargs):
        super().__init__(
            "pole_theta", "Maintain pole to upright", target=0, stop_distance=0.418
        )

        # defaults the BL and BR

    async def compute_action_mask(self, transformed_sensors: Dict, action):
        # Cartpole might not use an action mask, so this can return None
        return None

    async def transform_sensors(self, sensors, action):
        # For Cartpole, might just return sensors directly
        return sensors

    async def transform_action(self, transformed_sensors: Dict, action):
        # No transformation needed for discrete action space
        return action

    async def filtered_sensor_space(self):
        # Return relevant sensors
        return ["cart_pos", "cart_vel", "pole_theta", "pole_alpha"]


def main():
    # Create the agent
    a = Agent()

    # https://gymnasium.farama.org/environments/classic_control/cart_pole/#observation-space
    a.add_sensors(
        [
            Sensor(
                "cart_pos",
                "The Cart Position between [-4.8, 4.8]",
                lambda sensors: sensors[0],
            ),
            Sensor(
                "cart_vel",
                "The Cart Position between  [-inf, inf]",
                lambda sensors: sensors[1],
            ),
            Sensor(
                "pole_theta",
                "The Pole Angle [-0.418 rad, 0.418 rad]",
                lambda sensors: sensors[2],
            ),
            Sensor(
                "pole_alpha",
                "The Pole Angular Velocity [-inf, inf]",
                lambda sensors: sensors[3],
            ),
        ]
    )

    skill = Skill("pole-balance", BalanceTeacher)
    a.add_skill(skill)

    # Create trainer and train the agent
    r = Trainer(
        {
            "target": {"composabl"},
            "resources": {
                "sim_count": 2,
            },
        }
    )

    r.train(a, train_cycles=5)
    r.close()


if __name__ == "__main__":
    main()
