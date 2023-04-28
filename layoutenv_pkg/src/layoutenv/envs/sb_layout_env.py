"""
This environment only allows placing transverse frames
"""
from gym import Env
from gym.spaces import Box, Dict
import numpy as np
from piascomms.internal_geometry.shape_manipulation.xml_request import RemovePhysicalPlane, AddPhysicalPlane
from piascomms.utils import observation_space_by_id
from piascomms.layout_properties import PlaneData, CompartmentData
from pathlib import Path
from .empty_layout import Copy
from piascomms.client import Client
from time import sleep
from typing import Dict, List
import layoutenv.logger_module as logger_mod
import json
import layoutenv.utils as lutils
import __main__

class LayoutEnv2(Env):
    metadata = {'render.modes': ['GUIviewer', 'noHMI']}
    def __init__(self) -> None:
        config_file = Path(r"layoutenv_pkg\\src\\configs\\config.json").open('r')
        self.config = json.loads(config_file.read())
        self.episode_count = 0
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
    def compartments(self) -> dict:
        return CompartmentData(self.config["data_source"])

    def _info(self, att_idx: float, req_idx: float) -> dict:
        self.logger.info(f"required subdivision idx :{req_idx}, attained subdivision idx :{att_idx}")
        return {"Required subdivision idx": req_idx, "Attained subdivision idx": att_idx}

    def _observation(self):
        ROWS, COLS = 50, 4
        obs = np.arange(ROWS*1*COLS).reshape((ROWS, COLS))
        obs = np.full_like(obs, fill_value=0, dtype=np.float64)
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


    def _reward(self, att_idx: float, req_idx, layout: dict) -> float:
        # base the reward function on the gradient of the cummulated reward.
        delta = att_idx - req_idx
        volumetric_reward = 0
        for volume in layout.values():
            if volume['volume'] >= self.config["min_compartment_volume_a"]:
                volumetric_reward += 3
            elif volume['volume'] >= self.config["min_compartment_volume_b"]:
                volumetric_reward += 2 
            elif volume['volume'] >= self.config["min_compartment_volume_c"]:
                volumetric_reward += 1
        reward = delta * volumetric_reward
        if volumetric_reward == 0:
            reward = -5    
        self.logger.info(f"LayoutEnv2._reward(att_idx: float) -> reward = {reward}")
        return reward   

    def _truncated(self, max_time_steps: int) -> bool:
        """An episode is truncated when the max number of timestep is reached.
        """
        if self.time_step >= max_time_steps:
            self.logger.info(f"LayoutEnv1()._truncated {self.time_step} >= {max_time_steps}")
            return True
        else:
            return False

    def step(self, action):
        self.logger.info(f"LayoutEnv.step() @timestep {self.time_step}")
        self.time_step += 1
        lower = 0
        upper = self.config["length"]
        position = lutils.rescale_actions(action, lower, upper)

        self.logger.info(f"LayoutEnv.step, arg: action: {action}, scaled: {position}, lower_bound: {lower}, {upper}")

        request = AddPhysicalPlane(self.planes_list, "Frame", -position, 5, 6)
        request.boundary_contour_vertices = [(5, 4, 0, 0, 2), (5, 3, 0, 0, 2), (6, 3, 0, 0, 2), (5, 4, 0, 0, 2)]
        self.logger.info(f"AddPhysicalPlane, Frame, position {position}")
        lutils.send(request)
        
        att_idx = lutils.start_damage_stability_calc(self.config['ai_results'])

        observation, layout = self._observation()
        
        info = self._info(att_idx)
        reward = self._reward(att_idx, layout)
        self.cum_reward.append(reward)
        done = lutils.terminated(self.cum_reward) | self._truncated(max_time_steps=self.config["max_episode_length"])

        return observation, reward, done, info

    def render(self, mode="noHMI"):
        c = Client()
        self.renderer = lutils.RenderLayoutModule(source=self.config["temp_file"], serverport=self.config['serverport'], servermode=mode)
        copy = Copy()
        copy.source = self.config["hull_source"][0]
        copy.copy()
        self.logger.info(f"func name: render(), arg: source: {copy.source}")
        self.renderer.start_proces()
        while not c.server_check():
            print('loading.....')
        print('server live')
        sleep(2)


    def _close(self) -> None:
        self.logger.info("LayoutEnv.close(): Layout module closed.")
        self.renderer.kill_process()

    def reset(self):
        # reload the vessel layout xml file because the compartment names change during interactions with the layout.
        self.logger.info(f"LayoutEnv2.reset() called. at episode :{self.episode_count} and timestep :{self.time_step}")
        self.episode_count += 1
        self.time_step = 0
        self.cum_reward = []
        default = [("Uiterste achtervlak", 1), ("Uiterste voorvlak", 2), ("Uiterste BBvlak", 3),("Uiterste SBvlak", 4), ("Uiterste ondervlak", 5), ("Uiterste bovenvlak", 6), ("Frame 80 (40.000 m)", 13), ("Frame 160 (80.000 m)", 16), ("Deck 4.000 m", 18), ("Deck 1.000 m", 17), ("Longitudinal bulkhead 0.000 m", 19), ("Longitudinal bulkhead 2.350 m", 20), ("Longitudinal bulkhead -2.350 m", 21), ("Longitudinal bulkhead 4.000 m", 22), ("Longitudinal bulkhead -4.000 m", 23) ]
        # default.pop(random.randint(6, 15)) for an environment with more actions, I want to compare the reward function with env1
        lutils.request_layout()
        self.comp_ids = list(self.compartments.name_id.values())
        for _id, _name in self.plane_name_by_id.items():
            skip_id = [plane[1] for plane in default]
            if _id in skip_id:
                continue
            else:
                request = RemovePhysicalPlane(_id)

                client = Client()
                self.logger.info(f"RemovePhysicalPlane with id {_id} and name {_name}")
                try:
                    client.send_from_stream(request.to_xml_string())
                except ConnectionResetError as e:
                    self.logger.exception(f"{e}")
                    self.logger.warning(f'warning {e}')
        observation, _ = self._observation()
        return observation



