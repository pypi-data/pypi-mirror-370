# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from typing import Any, Dict, SupportsFloat, Tuple

import gymnasium as gym
import numpy as np

from composabl_core.agent.scenario import Scenario
from composabl_core.networking.sim.server_composabl import ServerComposabl
from composabl_core.examples.rocket_landing.sim.sim import LunarLander

class ServerImpl(ServerComposabl):
    def __init__(self, *args, **kwargs):
        self.env_init = kwargs.get("env_init", {})

    async def make(self, env_id: str, env_init: dict):
        self.env_id = env_id if env_id else self.env_id
        self.env_init = env_init if env_init else self.env_init

        print("Creating Lunar Lander with env_init: ", self.env_init)
        self.env = LunarLander(render_mode="rgb_array")
        return {"id": "LunarLander-v2", "max_episode_steps": 1000}

    async def sensor_space_info(self) -> gym.Space:
        # this is a hack since we can't upgrade to gymnasum 1.0.0
        low = np.array([-20] * 8).astype(np.float32)
        high = np.array([20] * 8).astype(np.float32)

        return gym.spaces.Box(low, high)

    async def action_space_info(self) -> gym.Space:
        return self.env.action_space

    async def action_space_sample(self) -> Any:
        return self.env.action_space.sample()

    async def reset(self) -> Tuple[Any, Dict[str, Any]]:
        sensors, info = self.env.reset()
        return sensors, info

    async def step(
        self, action
    ) -> Tuple[Any, SupportsFloat, bool, bool, Dict[str, Any]]:
        sensors, reward, is_terminated, is_truncated, info = self.env.step(action)
        return sensors, reward, is_terminated, is_truncated, info

    async def close(self):
        self.env.close()

    async def set_scenario(self, scenario):
        return

    async def get_scenario(self) -> Scenario:
        return None

    async def get_render(self):
        return self.env.render()
