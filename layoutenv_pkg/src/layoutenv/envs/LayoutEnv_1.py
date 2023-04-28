"""
This environment follows the strategy of incrementally deleting planes from a dense layout.
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
from typing import List
from attained_index import attained_index


def delete(plane_id: int):
    """Implement Pias delete function here
    """
    rplane = RemovePhysicalPlane(plane_id)
    client = Client()
    client.send_from_stream(rplane.to_xml_string())

class LayoutEnv(Env):
    def __init__(self,
                 length: float,
                 breadth: float,
                 depth: float,
                 max_volume: int,
                 draft: float,
                   vcg: float,
                 lightship_weight) -> None:
        self.draft = draft
        self.light_ship_weight = lightship_weight
        self.vcg = vcg
        self.max_volume = max_volume
        self.max_breadth = breadth
        self.max_depth = depth
        
        self.data_source = Path(
            r"C:\Users\cursist\Dorus\OpenGym\recieved_data.xml")
        self.length = length
        self.r = required_index(self.length)
        self.action_space = Dict(
            {
                "orientation": Discrete(3),
                "position": Box(low=-1, high=1, shape=(1,), dtype=np.float32),
            }
        )
        self.observation_space = Box(
            low=-1, high=1, shape=(100, 1, 5), dtype=np.float32)
        self.time_step = 0

    @property
    def planes_list(self):
        return PlaneData(self.data_source).list_of_planes

    @property
    def plane_names(self) -> list:
        return [plane.name for plane in self.planes_list if plane.name[:8] != 'Uiterste']

    @property
    def plane_id(self):
        return {plane.name: plane.physical_plane_id for plane in self.planes_list}

    def _info(self):
        return {}

    def _observation(self):
        layout = observation_space(self.data_source, _print=True)
        ROWS, COLS = len(list(layout.values())), 4
        obs = np.arange(ROWS*1*COLS).reshape((ROWS, COLS))
        obs = np.full_like(obs, fill_value=np.nan, dtype=np.float32)
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
            return 1

    def _truncated(self, max_time_steps: int):
        """An episode is truncated when the max number of timestep is reached.
        """
        if self.time_step >= max_time_steps:
            return True

    def _terminated(self):
        "An episode is terminated when the required index is met"
        # Not implemented yet
        return False

    def step(self, action):
        orientation, position, b_1, b_2 = convert_action(
            action, max_length=self.length, min_length=0)
        planes = planes_of_type(orientation, self.planes_list)
        plane_to_delete = list(planes.keys())[
            find_nearest_idx(list(planes.values()), position)]
        delete(plane_id=self.plane_id.get(plane_to_delete))

        observation, layout = self._observation()
        att_idx = attained_index(layout, draft=self.draft, vcg=self.vcg, lightship_weight=self.light_ship_weight, floodable_length=self.length)

        reward = self._reward(att_idx)
        return observation, reward, self._terminated(), self._truncated(max_time_steps=30), self._info()

    def render(self):
        c = Client()
        copy = DenseLayout()
        copy.source = Path(r"C:\Users\cursist\Dorus\ThesisResearch\PiasExampleFiles\full_layout")
        copy.copy()
        renderer = RenderLayoutModule()
        renderer.module = r"C:\Users\cursist\Dorus\OpenGym\envs\temp.bat"
        renderer.start_proces()
        while not c.server_check():
            print('loading.....')
        print('server live')
        sleep(2)

    def reset(self, seed=None, options={}):
        # reload the vessel layout xml file because the compartment names change during interactions with the layout.
        # request_layout()
        observation, _ = self._observation()
        return observation, self._info()


if __name__ == "__main__":
    env = LayoutEnv(length=96, breadth=11.5, depth=6.0, max_volume=90000, draft=3.438, vcg=3.677, lightship_weight=1667.445)
    number_of_episodes = 5
    total_reward = []




    env.render()

    for episode in range(number_of_episodes):
        obs, info = env.reset()

        done = False
        while not done:

            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)

            done = terminated or truncated
