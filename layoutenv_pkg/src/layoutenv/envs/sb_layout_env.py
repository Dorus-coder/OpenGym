"""
This environment only allows placing transverse frames
"""
from gym import Env
from gym.spaces import Box, Dict
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

class LayoutEnv2(Env):
    metadata = {'render.modes': ['GUIviewer', 'noHMI']}
    def __init__(self, mode="noHMI") -> None:
        config_file = Path(r"OpenGym\\layoutenv_pkg\\src\\configs\\config.json").open('r')
        self.config = json.loads(config_file.read())
        self.episode_count = 0
        self.total_timesteps = 0
        self.renderer = lutils.RenderLayoutModule(source=self.config["temp_file"], serverport=self.config['serverport'], servermode=mode)
        # self.action_space = Dict(
        #     {
        #         "orientation": Discrete(3),
        #         "position": Box(low=-1, high=1, shape=(1,), dtype=np.float32),
        #     }
        # )
        self.action_space = Box(low=-1, high=1, shape=(1,), dtype=np.float64)
        self.observation_space = Box(low=-1, high=1, shape=(50, 4), dtype=np.float64)
        self.time_step = 0
        self.logger = logger_mod.get_logger_from_config(name=__main__.__name__)
        self.cum_reward = []


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
        if att_idx < reg_idx and att_idx > self.previous_att_idx:
            reward = 1.0
            self.logger.info(f"reward(att_idx, req_idx, layout, volume_limit) -> reward = {reward}")
            return reward
        elif att_idx < reg_idx and att_idx < self.previous_att_idx:
            reward = -1.0
            self.logger.info(f"reward(att_idx, req_idx, layout, volume_limit) -> reward = {reward}")
            return reward 
        elif att_idx < reg_idx and att_idx == self.previous_att_idx:
            reward = -1.0
            self.logger.info(f"reward(att_idx, req_idx, layout, volume_limit) -> reward = {reward}")
            return reward 
        elif att_idx >= reg_idx:
            try:
                volume = max(layout.values(), key=lambda x: x['volume'])['volume']
                if self.max_volume and volume > self.max_volume:
                    # The biggest compartment volume is bigger as the biggest compartment volume in the previous timestep.
                    volumetric_reward  = (volume - self.config['min_compartment_volume_a']) * 0.01
                elif not self.max_volume:
                    # This is the first timesteps
                    volumetric_reward = (volume - self.config['min_compartment_volume_a']) * 0.01
                else:
                    # There were previous volumetric rewards only the biggest compartment is equal or smaller as the biggest
                    # compartment in the previous timestep.
                    volumetric_reward = 0.0
                self.max_volume = volume
            except ValueError as e:
                self.logger.exception(f"{e}")
                self.logger.error(f"lenght layout {len(layout.values())}")
            
            self.logger.info(f"reward(att_idx, req_idx, layout, volume_limit) -> reward = {volumetric_reward}")
            self.logger.info(f"the biggest compartment volume is {volume}")
            return  volumetric_reward  
        else:
            self.logger.error('No reward given')
            return -10  

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
        done = lutils.terminated(self.cum_reward, self.config, self.episode_count) | self._truncated(max_time_steps=self.config["max_episode_length"])
        self.total_timesteps += 1
        return observation, reward, done, info

    def render(self, mode="noHMI"):
        raise NotImplementedError("This function is not used")

    def reset(self, seed=None):
        # reload the vessel layout xml file because the compartment names change during interactions with the layout.
        # print("reset"*50)
        self.max_volume = None

        if self.renderer.process_is_running():
            self.renderer.kill_process()

        self.episode_count += 1
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



