# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from typing import Any, Dict, SupportsFloat, Tuple

import composabl_core.utils.logger as logger_util
import gymnasium as gym
from composabl_core.agent.scenario import Scenario
from composabl_core.networking.sim.server_composabl import ServerComposabl
from gymnasium.envs.registration import EnvSpec

from .sim import Env

logger = logger_util.get_logger(__name__)


class SimImpl(ServerComposabl):
    def __init__(self):
        self.env = Env()

    async def make(self, env_id: str, env_init: dict) -> EnvSpec:
        """
        Make the environment

        Args:
        - env_id (str): Environment ID
        - env_init (dict): Environment Initialization

        Returns:
        - EnvSpec: Environment Specification
        """
        spec = {"id": "starship", "max_episode_steps": 400}
        return spec

    async def sensor_space_info(self) -> gym.Space:
        """
        Get the sensor space information

        Returns:
        - Space: Sensor Space in Gymnasium Specification
        """
        return self.env.sensor_space

    async def action_space_info(self) -> gym.Space:
        """
        Get the action space information

        Returns:
        - Space: Action Space in Gymnasium Specification
        """
        return self.env.action_space

    async def action_space_sample(self) -> Any:
        """
        Get the action space sample

        Returns:
        - List[Any]: A list of samples
        """
        return self.env.action_space.sample()

    async def reset(self) -> Tuple[Any, Dict[str, Any]]:
        """
        Reset the environment

        Returns:
        - Tuple[Any, Dict[str, Any]]: The observation and the info
        """
        sensors, info = self.env.reset()
        return sensors, info

    async def step(
        self, action
    ) -> Tuple[Any, SupportsFloat, bool, bool, Dict[str, Any]]:
        """
        Step the environment

        Args:
        - action: The action to take

        Returns:
        - Tuple[Any, SupportsFloat, bool, bool, Dict[str, Any]]: The observation, reward, is_truncated, is_done, info
        """
        return self.env.step(action)

    async def close(self):
        """
        Close the environment
        """
        self.env.close()

    async def set_scenario(self, scenario):
        """
        Set the scenario
        """
        self.env.scenario = scenario

    async def get_scenario(self):
        """
        Get the scenario
        """
        if self.env.scenario is None:
            return Scenario({"dummy": 0})

        return self.env.scenario

    async def get_render(self):
        """
        Get the render

        Args:
        - render_mode: The render mode
        """
        return self.env.get_render_frame()
