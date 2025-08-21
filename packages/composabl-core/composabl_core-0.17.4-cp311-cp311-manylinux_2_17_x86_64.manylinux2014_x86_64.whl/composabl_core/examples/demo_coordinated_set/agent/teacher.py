# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential


from typing import Dict

from composabl_core import SkillTeacher


class IncrementTeacher(SkillTeacher):
    def __init__(self, *args, **kwargs):
        self.past_obs = None
        self.counter = 0

    async def compute_reward(self, transformed_sensors: Dict, action, sim_reward):
        self.counter += 1
        return 1

    async def compute_action_mask(self, transformed_sensors: Dict, action):
        return None

    async def compute_success_criteria(self, transformed_sensors: Dict, action):
        # keep the episodes short to make testing quicker
        return self.counter > 5

    async def compute_termination(self, transformed_sensors: Dict, action):
        return False

    async def transform_sensors(self, sensors, action):
        return sensors

    async def transform_action(self, transformed_sensors: Dict, action):
        return action

    async def filtered_sensor_space(self):
        return ["state1", "time_counter"]
