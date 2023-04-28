"""
This environment only allows placing transverse frames
"""
from gym import Env
from gym.spaces import Discrete, Box, Dict
import numpy as np
from piascomms.internal_geometry.shape_manipulation.xml_request import RemovePhysicalPlane
from piascomms.utils import observation_space
from piascomms.layout_properties import PlaneData
from pathlib import Path
from utils import *
from Simulator.simulator import required_index
from layout_script import RenderLayoutModule
from empty_layout import DenseLayout
from piascomms.client import Client
from time import sleep
from typing import Dict, List
from attained_index import attained_index
import logging

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
date_format = '%(d)s-%(b)s-%(y)s %(H)s:%(M)s:%(S)s'
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

f_handler = logging.FileHandler("ENV_0.log")
f_handler.setLevel(logging.DEBUG)
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)


formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_handler.setFormatter(formatter)
c_handler.setFormatter(formatter)

logger.addHandler(f_handler) 
logger.addHandler(c_handler)


class LayoutEnv(Env):
    def __init__(self,
                 length: float,
                 breadth: float,
                 depth: float,
                 max_volume: int,
                 vcg: float,
                 lightship_weight) -> None:
        self.light_ship_weight = lightship_weight
        self.vcg = vcg
        self.max_volume = max_volume
        self.max_breadth = breadth
        self.max_depth = depth
        
        self.data_source = Path(
            r"C:\Users\cursist\Dorus\OpenGym\recieved_data.xml")
        self.length = length
        self.r = required_index(self.length) + 0.5
        # self.action_space = Dict(
        #     {
        #         "orientation": Discrete(3),
        #         "position": Box(low=-1, high=1, shape=(1,), dtype=np.float32),
        #     }
        # )
        self.action_space = Box(low=-1, high=1, shape=(1,), dtype=np.float32)
        self.observation_space = Box(
            low=-1, high=1, shape=(100, 1, 5), dtype=np.float32)
        self.time_step = 0

    @property
    def planes_list(self):
        return PlaneData(self.data_source).list_of_planes

    @property
    def plane_names(self) -> List[str]:
        return [plane.name for plane in self.planes_list if plane.name[:8] != 'Uiterste']

    @property
    def plane_id(self) -> Dict[str, int]:
        return {plane.name: plane.physical_plane_id for plane in self.planes_list}

    def _info(self, att_idx):
        logger.info("required subdivision idx: %s, attained subdivision idx: %s", self.r, att_idx)
        return {"Required subdivision idx": self.r, "Attained subdivision idx": att_idx}

    def _observation(self):
        ROWS, COLS = 50, 4
        obs = np.arange(ROWS*1*COLS).reshape((ROWS, COLS))
        obs = np.full_like(obs, fill_value=np.nan, dtype=np.float32)
        layout = observation_space(self.data_source, _print=False)
        for idx, prop in enumerate(layout.values()):
            if prop.get('volume'):
                obs[idx][0] = inverse_rescale_actions(
                    prop.get('volume'), low=0, high=self.max_volume)
                obs[idx][1] = inverse_rescale_actions(
                    prop.get('centroid_x'), low= -self.max_breadth / 2, high=self.max_breadth /2)
                obs[idx][2] = inverse_rescale_actions(
                    prop.get('centroid_y'), low=0, high=self.max_depth)
                obs[idx][3] = inverse_rescale_actions(
                    prop.get('centroid_z'), low=0, high=self.length)
        return obs, layout

    def _reward(self, att_idx):
        upper = self.r * 1.1
        lower = self.r * 0.9
        if lower < att_idx < upper:
            reward = 2
            logger.info("_reward %s", reward)
            return reward
        elif att_idx > self.r:
            reward = 1
            logger.info("_reward %s", reward)
            return reward

    def _truncated(self, max_time_steps: int):
        """An episode is truncated when the max number of timestep is reached.
        """
        if self.time_step >= max_time_steps:
            logger.info(f"func name: _truncated {self.time_step} >= {max_time_steps}")
            return True

    def _terminated(self, reward):
        "An episode is terminated when the required index is met"
        if reward:
            logger.info(f"func name: _terminated with reward {reward}")
            return True
        return False

    def step(self, action):
        logger.info(f"LayoutEnv.step() @timestep {self.time_step}")
        lower = 0
        upper = self.length
        position = rescale_actions(action, lower, upper)
        logger.info(f"LayoutEnv.step, arg: action: {action}, scaled: {position}, lower_bound: {lower}, {upper}")
        
        request = AddPhysicalPlane(self.planes_list, "Frame", -position, 5, 6)
        request.boundary_contour_vertices = [(5, 4, 0, 0, 2), (5, 3, 0, 0, 2), (6, 3, 0, 0, 2), (5, 4, 0, 0, 2)]
        send(request)
        observation, layout = self._observation()
        att_idx = attained_index(layout, vcg=self.vcg, lightship_weight=self.light_ship_weight, floodable_length=self.length)
        
        info = self._info(att_idx)
        reward = self._reward(att_idx)
        return observation, reward, self._terminated(reward), self._truncated(max_time_steps=15), info

    def render(self):
        c = Client()
        renderer = RenderLayoutModule()
        renderer.module = r"C:\Users\cursist\Dorus\OpenGym\envs\temp.bat"
        copy = DenseLayout()
        copy.source = Path(r"C:\Users\cursist\Dorus\ThesisResearch\PiasExampleFiles\NoTrans")
        copy.copy()
        logger.info(f"func name: reder(), arg: source: {copy.source}")
        renderer.start_proces()
        while not c.server_check():
            print('loading.....')
        print('server live')
        sleep(3)

    def reset(self):
        # reload the vessel layout xml file because the compartment names change during interactions with the layout.
        default = ["Frame 80 (40.000 m)", "Frame 160 (80.000 m)", "Deck 4.000 m", "Deck 1.000 m", "Longitudinal bulkhead 0.000 m", "Longitudinal bulkhead 2.350 m", "Longitudinal bulkhead -2.350 m", "Longitudinal bulkhead 4.000 m", "Longitudinal bulkhead -4.000 m" ]
        for plane in self.plane_names:
            if plane in default:
                continue
            else:
                _id = self.plane_id.get(plane)            
                request = RemovePhysicalPlane(_id)
                client = Client()
                try:
                    client.send_from_stream(request.to_xml_string())
                except ConnectionResetError as e:
                    logging.exception(f"{e}")
                    logging.exception('%s', e)
        request_layout()
        observation, _ = self._observation()
        return observation, self._info(0)


if __name__ == "__main__":
    env = LayoutEnv(length=96, breadth=11.5, depth=6.0, max_volume=5000, vcg=4.82, lightship_weight=2500)
    number_of_episodes = 5
    total_reward = []
    env.render()
 
    for episode in range(number_of_episodes):
        obs, info = env.reset()
        env.time_step = 0
        done = False
        while not done:
    
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            env.time_step += 1
            request_layout()

            done = terminated or truncated
   
