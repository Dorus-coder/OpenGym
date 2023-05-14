#iwbsSARC#sarc
from .sb_layout_env import LayoutEnv2
from gym import spaces
import numpy as np
from stable_baselines3.common.utils import set_random_seed
from typing import Optional


class LayoutEnv3(LayoutEnv2):
    # Add class id here and create an isolated pias environment in the form of an isolated file.
    def __init__(self) -> None:
        """
        This environment has an improved reward function
        """
        super().__init__()
        self.action_space = spaces.Box(low=-1, high=1, shape=(2,), dtype=np.float64)
        self.episode_count = -1
        self.previous_att_idx = 0
        self.max_volume = None


    def reward(self, att_idx: float, reg_idx: float, layout: dict):
        try:
            volume = max(layout.values(), key=lambda x: x['volume'])['volume']
        except ValueError as e:
            volume = 0
            self.logger.exception(f"{e}")
            self.logger.error(f"lenght layout {len(layout.values())}")

        if att_idx >= reg_idx:

                if not self.max_volume:
                    # This is the first timesteps
                    reward = (volume - self.config['min_compartment_volume_a']) * 0.01
                    self.logger.info(f"reward = {reward} @ total_timestep {self.total_timesteps} and max _volume {volume}")
                    self.max_volume = volume
                    return reward

                elif self.max_volume and volume > self.max_volume:
                    # The biggest compartment volume is bigger as the biggest compartment volume in the previous timestep.
                    reward = (volume - self.config['min_compartment_volume_a']) * 0.01
                    self.logger.info(f"reward = {reward} @ total_timestep {self.total_timesteps} and max _volume {volume}")
                    self.max_volume = volume
                    return reward
                else:
                    # There were previous volumetric rewards only the biggest compartment is equal or smaller as the biggest
                    # compartment in the previous timestep.
                    reward = 0.0 
                    self.logger.info(f"reward = {reward} @ total_timestep {self.total_timesteps} and max _volume {volume}")
                    self.max_volume = volume
                    return reward
                
        self.max_volume = volume
        reward = -1
        self.logger.info(f"reward = {reward} @ total_timestep {self.total_timesteps} and max _volume {volume}")
        return -1
    

    def seed(self, seed: Optional[int] = None):
        """Sets the seed for this env's random number generator(s).

        Note:
            Some environments use multiple pseudorandom number generators.
            We want to capture all such seeds used in order to ensure that
            there aren't accidental correlations between multiple generators.

        Returns:
            list<bigint>: Returns the list of seeds used in this env's random
            number generators. The first value in the list should be the
            "main" seed, or the value which a reproducer should pass to
            'seed'. Often, the main seed equals the provided 'seed', but
            this won't be true if seed=None, for example.
        """
        if seed:
            set_random_seed(seed)
            
        return [seed]

        
    