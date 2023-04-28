"""
This environment only allows placing transverse frames
"""
from gym import Env
from gym.spaces import Discrete, Box, Dict
import numpy as np
from piascomms.internal_geometry.shape_manipulation.xml_request import RemovePhysicalPlane
from piascomms.utils import observation_space_by_id
from piascomms.layout_properties import PlaneData
from .utils import *
from .layout_script import RenderLayoutModule
from .empty_layout import Copy
from piascomms.client import Client
from time import sleep
from typing import Dict, List
import logging
import json

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
date_format = '%(d)s-%(b)s-%(y)s %(H)s:%(M)s:%(S)s'
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

f_handler = logging.FileHandler("logs//ENV_0.log")
f_handler.setLevel(logging.DEBUG)
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)


formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_handler.setFormatter(formatter)
c_handler.setFormatter(formatter)

logger.addHandler(f_handler) 
# logger.addHandler(c_handler)


class LayoutEnv1(Env):
    metadata = {'render.modes': ['GUIviewer', 'noHMI']}
    def __init__(self) -> None:
        config_file = Path(r"layoutenv_pkg\\src\\layoutenv\\envs\\config.json").open('r')
        self.config = json.loads(config_file.read())
        self.r = required_index(self.config["length"]) 
        # self.action_space = Dict(
        #     {
        #         "orientation": Discrete(3),
        #         "position": Box(low=-1, high=1, shape=(1,), dtype=np.float32),
        #     }
        # )
        self.action_space = Box(low=-1, high=1, shape=(1,), dtype=np.float64)
        self.observation_space = Box(low=-1, high=1, shape=(50, 4), dtype=np.float64)
        self.time_step = 0

    @property
    def planes_list(self):
        return PlaneData(self.config["data_source"]).list_of_planes

    @property
    def plane_names(self) -> List[str]:
        return [plane.name for plane in self.planes_list if plane.name[:8] != 'Uiterste']

    @property
    def plane_name_by_id(self) -> Dict[int, str]:
        return {plane.physical_plane_id: plane.name for plane in self.planes_list}

    def _info(self, att_idx):
        logger.info("required subdivision idx: %s, attained subdivision idx: %s", self.r, att_idx)
        return {"Required subdivision idx": self.r, "Attained subdivision idx": att_idx}

    def _observation(self):
        ROWS, COLS = 50, 4
        obs = np.arange(ROWS*1*COLS).reshape((ROWS, COLS))
        obs = np.full_like(obs, fill_value=0, dtype=np.float64)
        layout = observation_space_by_id((30, 70))
        for idx, prop in enumerate(layout.values()):
            if prop.get('volume'):
                obs[idx][0] = inverse_rescale_actions(
                    prop.get('volume'), low=0, high=self.config["max_volume"])    
                obs[idx][1] = inverse_rescale_actions(
                    prop.get('centroid_x'), low= -self.config["breadth"] / 2, high=self.config["breadth"] /2)
                obs[idx][2] = inverse_rescale_actions(
                    prop.get('centroid_y'), low=0, high=self.config["depth"])
                obs[idx][3] = inverse_rescale_actions(
                    prop.get('centroid_z'), low=0, high=self.config["length"])
        return obs, layout

    def _reward(self, att_idx):
        upper = self.r * 1.1
        lower = self.r * 1
        if lower < att_idx < upper:
            reward = 2
            logger.info("_reward() %s", reward)
            return reward
        elif att_idx > self.r:
            reward = 1
            logger.info("_reward() %s", reward)
            return reward
        else:
            reward = 0
            logger.info("_reward() %s", reward)
            return reward

    def _truncated(self, max_time_steps: int):
        """An episode is truncated when the max number of timestep is reached.
        """
        if self.time_step >= max_time_steps:
            logger.info(f"func name: _truncated {self.time_step} >= {max_time_steps}")
            return True
        else:
            return False

    def _terminated(self, reward):
        "An episode is terminated when the required index is met"
        if reward:
            logger.info(f"func name: _terminated with reward {reward}")
            return True
        else:
            return False

    def step(self, action):
        logger.info(f"LayoutEnv.step() @timestep {self.time_step}")
        self.time_step += 1
        lower = 0
        upper = self.config["length"]
        position = rescale_actions(action, lower, upper)

        logger.info(f"LayoutEnv.step, arg: action: {action}, scaled: {position}, lower_bound: {lower}, {upper}")

        request = AddPhysicalPlane(self.planes_list, "Frame", -position, 5, 6)
        request.boundary_contour_vertices = [(5, 4, 0, 0, 2), (5, 3, 0, 0, 2), (6, 3, 0, 0, 2), (5, 4, 0, 0, 2)]
        logger.info(f"AddPhysicalPlane, Frame, position {position}")
        send(request)

        att_idx = start_damage_stability_calc(self.config['ai_results'])

        observation, layout = self._observation()
        
        info = self._info(att_idx)
        reward = self._reward(att_idx)
        done = self._terminated(reward) | self._truncated(max_time_steps=self.config["max_episode_length"])

        return observation, reward, done, info

    def render(self, mode="noHMI"):
        c = Client()
        self.renderer = RenderLayoutModule(source=self.config["temp_file"], serverport=self.config['serverport'], servermode=mode)
        copy = Copy()
        copy.source = self.config["hull_source"]
        copy.copy()
        logger.info(f"func name: render(), arg: source: {copy.source}")
        self.renderer.start_proces()
        while not c.server_check():
            print('loading.....')
        print('server live')
        sleep(2)


    def _close(self) -> None:
        logger.info("LayoutEnv.close(): Layout module closed.")
        self.renderer.kill_process()

    def reset(self):
        # reload the vessel layout xml file because the compartment names change during interactions with the layout.
        self.time_step = 0
        default = [("Uiterste achtervlak", 1), (), ("Frame 80 (40.000 m)", 13), ("Frame 160 (80.000 m)", 16), ("Deck 4.000 m", 18), ("Deck 1.000 m", 17), ("Longitudinal bulkhead 0.000 m", 19), ("Longitudinal bulkhead 2.350 m", 20), ("Longitudinal bulkhead -2.350 m", 21), ("Longitudinal bulkhead 4.000 m", 22), ("Longitudinal bulkhead -4.000 m", 23) ]
        logger.info("LayoutEnv1.reset() called.")
        for _id in range(7, 50):
            skip_id = [plane[1] for plane in default]
            if _id in skip_id:
                continue
            else:
                request = RemovePhysicalPlane(_id)

                client = Client()
                logger.info(f"RemovePhysicalPlane with id {_id} and name {self.plane_name_by_id.get(_id)}")
                try:
                    client.send_from_stream(request.to_xml_string())
                except ConnectionResetError as e:
                    logger.exception(f"{e}")
                    logger.warning(f'warning {e}')
        observation, _ = self._observation()
        return observation



