#iwbsSARC#sarc
from .sb_layout_env import LayoutEnv2
from piascomms.client import Client
from gym import spaces
import layoutenv.utils as lutils
import numpy as np
import time

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

                if self.max_volume and volume > self.max_volume:
                    # The biggest compartment volume is bigger as the biggest compartment volume in the previous timestep.
                    reward = (volume - self.config['min_compartment_volume_a']) * 0.01
                    self.logger.info(f"reward = {reward} @ total_timestep {self.total_timesteps}")
                    return reward
                elif not self.max_volume:
                    # This is the first timesteps
                    reward = (volume - self.config['min_compartment_volume_a']) * 0.01
                    self.logger.info(f"reward = {reward} @ total_timestep {self.total_timesteps}")
                    return reward
                else:
                    # There were previous volumetric rewards only the biggest compartment is equal or smaller as the biggest
                    # compartment in the previous timestep.
                    reward = 0.0 
                    self.logger.info(f"reward = {reward} @ total_timestep {self.total_timesteps}")
                    return reward
                
        self.max_volume = volume
        reward = -1
        self.logger.info(f"reward = {reward} @ total_timestep {self.total_timesteps}")
        return -1
    

        
    