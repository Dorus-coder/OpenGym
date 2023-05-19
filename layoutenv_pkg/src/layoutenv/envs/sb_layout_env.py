"""
This environment only allows placing transverse frames
"""
from gym import Env
from gym import spaces
import numpy as np
from piascomms.utils import observation_space_by_id
from piascomms.layout_properties import PlaneData, CompartmentData
from pathlib import Path
from piascomms.client import Client
from typing import Dict, List
import layoutenv.logger_module as logger_mod
import json
from pathlib import Path
import layoutenv.utils as lutils
import time
import __main__
from typing import Optional
from stable_baselines3.common.utils import set_random_seed

class LayoutEnv2(Env):
    metadata = {'render.modes': ['GUIviewer', 'noHMI']}
    def __init__(self, mode="noHMI") -> None:
        
        config_file = Path(r"OpenGym\\layoutenv_pkg\\src\\configs\\config.json").open('r')
        self.config = json.loads(config_file.read())
        
        self.episode_count = -1
        self.total_timesteps = 0
        self.time_step = 0
        self.previous_att_idx = 0
        self.max_volume = None

        self.renderer = lutils.RenderLayoutModule(source=self.config["temp_file"], serverport=self.config['serverport'], servermode=mode)

        self.action_space = spaces.Box(low=-1, high=1, shape=(2,), dtype=np.float64)
        self.observation_space = spaces.Box(low=-1, high=1, shape=(50, 4), dtype=np.float64)
        self.cum_reward = []

        self.logger = logger_mod.get_logger_from_config(name=__main__.__name__)
    

    @property
    def planes_list(self):
        return PlaneData(self.config["data_source"]).list_of_planes

    @property
    def plane_names(self) -> List[str]:
        return [plane.name for plane in self.planes_list if plane.name[:8] != 'Uiterste']

    @property
    def plane_name_by_id(self) -> Dict[int, str]:
        return {plane.physical_plane_id: plane.name for plane in self.planes_list}

    @property
    def compartments(self) -> CompartmentData:
        source = Path.cwd() / self.config["data_source"]
        return CompartmentData(xml_path=source)

    def _info(self, att_idx: float, req_idx: float) -> dict:
        self.logger.info(f"required subdivision idx :{req_idx}, attained subdivision idx :{att_idx}")
        return {"Required subdivision idx": req_idx, "Attained subdivision idx": att_idx}

    def _observation(self):
        ROWS, COLS = 50, 4
        obs = np.arange(ROWS*1*COLS).reshape((ROWS, COLS))
        obs = np.full_like(obs, fill_value=-1, dtype=np.float64)
        self.comp_ids += [max(self.comp_ids) + 1]
        layout = observation_space_by_id(_range=(min(self.comp_ids), max(self.comp_ids)), max_volume=self.config["max_volume"])
        for idx, prop in enumerate(list(layout.values())):
            if prop.get('volume'):
                try:
                    obs[idx][0] = lutils.inverse_rescale_actions(
                        prop.get('volume'), low=0, high=self.config["max_volume"])    
                    obs[idx][1] = lutils.inverse_rescale_actions(
                        prop.get('centroid_x'), low=-self.config["breadth"] / 2, high=self.config["breadth"] /2)
                    obs[idx][2] = lutils.inverse_rescale_actions(
                        prop.get('centroid_y'), low=0, high=self.config["depth"])
                    obs[idx][3] = lutils.inverse_rescale_actions(
                        prop.get('centroid_z'), low=0, high=self.config["length"])
                except IndexError as e:
                    self.logger.exception(f"{e}")
        return obs, layout


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

    def _truncated(self, max_time_steps: int) -> bool:
        """An episode is truncated when the max number of timestep is reached.
        """
        if self.time_step >= max_time_steps:
            self.logger.info(f"LayoutEnv1()._truncated {self.time_step} >= {max_time_steps}")
            return True
        else:
            return False

    def step(self, action: np.array):
        self.logger.info(f"LayoutEnv.step() @timestep {self.time_step}")
        self.time_step += 1
        
        lutils.add_physical_plane(action, self.planes_list)

        att_idx = lutils.start_damage_stability_calc(self.config['ai_results'])
        req_idx = lutils.required_index(self.config["length"])

        observation, layout = self._observation()
        
        info = self._info(att_idx, req_idx)
        reward = self.reward(att_idx, req_idx, layout)
        self.previous_att_idx = att_idx
        self.cum_reward.append(reward)
        done = lutils.terminated(self.cum_reward, self.config, self.episode_count, copy=True) | self._truncated(max_time_steps=self.config["max_episode_length"])
        self.total_timesteps += 1
        return observation, reward, done, info

    def render(self, mode="noHMI"):
        raise NotImplementedError("This function is not used")

    def reset(self, seed=None):
        # reload the vessel layout xml file because the compartment names change during interactions with the layout.
        # print("reset"*50)
        self.previous_att_idx = 0
        self.max_volume = None
        self.episode_count += 1
        
        if self.renderer.process_is_running():
            self.renderer.kill_process()

        
        self.logger.info(f"LayoutEnv2.reset() called. at episode :{self.episode_count} and timestep :{self.time_step}")
    
        self.time_step = 0
        self.cum_reward = []

        c = Client()
        
        if seed:
            source = lutils.copy_layout_random_source(source=self.config, seed=seed)
        else:
            source = lutils.copy_layout_random_source(source=self.config, seed=None)

        self.logger.info(f"Reset with filename {source}")
        self.renderer.start_process()
        while not c.server_check():
            print('loading.....')
        print('server live')
        time.sleep(2)

        lutils.request_layout()
        self.comp_ids = list(self.compartments.name_id.values())
        observation, _ = self._observation()
        return observation

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

