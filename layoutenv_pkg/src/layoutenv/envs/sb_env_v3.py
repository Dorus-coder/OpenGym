from .sb_layout_env import LayoutEnv2
from piascomms.client import Client
from piascomms.internal_geometry.shape_manipulation.xml_request import RemovePhysicalPlane, AddPhysicalPlane
from collections import namedtuple
from gym import spaces
from .empty_layout import Copy
from random import randint
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
        self.episode_count = 0

    def _add_physical_plane(self, action: np.array):
        PlaneInfo = namedtuple("PlaneInfo", ["orientation", "upper_limit", "boundary_vertices"])
        plane_info = {0: PlaneInfo("Longitudinal bulkhead", 11.5 / 2, [(2, 5), (1, 5), (1, 6), (2, 6), (2, 5)]),
                1: PlaneInfo("Frame", 96, [(5, 4), (5, 3), (6, 3), (5, 4)]),
                2: PlaneInfo("Deck", 10, [(1, 4), (2, 4), (2, 3), (1, 3), (1, 4)])}
        
        discrete_action = lutils.normalized_to_discrete(action[0])
        upper = plane_info[discrete_action].upper_limit

        position = lutils.rescale_actions(action[1], 0, upper)

        request = AddPhysicalPlane(self.planes_list,
                                   plane_info[discrete_action].orientation, 
                                   -position,
                                   plane_info[discrete_action].boundary_vertices)

        # ensure longitudinal bulkheads are symmetrical along the center plane
        if plane_info[discrete_action][0] == "Longitudinal bulkhead" and action[1] != -1:
            request_symmetry = AddPhysicalPlane(self.planes_list, 
                                       plane_info[discrete_action].orientation, 
                                       position,
                                       plane_info[discrete_action].boundary_vertices)
            lutils.send(request_symmetry)

        self.logger.info(f"LayoutEnv._add_physical_plane, arg: {plane_info[discrete_action].orientation}: {action}, scaled: {discrete_action},{position}, bounds: 0, {plane_info[discrete_action].upper_limit}, vertices: {plane_info[discrete_action].boundary_vertices}")
        lutils.send(request)

    def step(self, action: np.array):
        self.logger.info(f"LayoutEnv.step() @timestep {self.time_step}")
        self.time_step += 1
      
        self._add_physical_plane(action)

        att_idx = lutils.start_damage_stability_calc(self.config['ai_results'])
        req_idx = lutils.required_index(self.config["length"])

        observation, layout = self._observation()
        
        info = self._info(att_idx, req_idx)
        reward = lutils.reward(att_idx, req_idx, layout, self.config["min_compartment_volume_a"])
        self.cum_reward.append(reward)
        copy = self.config["temp_file_no_suffix"], f"layouts\\improved_term\\episode_{self.episode_count}"
        done = lutils.terminated(self.cum_reward, copy) | self._truncated(max_time_steps=self.config["max_episode_length"])

        return observation, reward, done, info
    
    def reset(self):
        # reload the vessel layout xml file because the compartment names change during interactions with the layout.
        if self.renderer.process_is_running():
            self.renderer.kill_process()
        self.episode_count += 1
        self.logger.info(f"LayoutEnv2.reset() called. at episode :{self.episode_count} and timestep :{self.time_step}")
    
        self.time_step = 0
        self.cum_reward = []

        c = Client()
        
        copy = Copy()
        copy.source = self.config["hull_source"][randint(0, 1)]
        copy.copy()
        self.logger.info(f"func name: render(), arg: source: {copy.source}")
        self.renderer.start_process()
        while not c.server_check():
            print('loading.....')
        print('server live')
        time.sleep(2)

        lutils.request_layout()
        self.comp_ids = list(self.compartments.name_id.values())
        observation, _ = self._observation()
        return observation

    def render(self, mode="noHMI"):
        self.renderer = lutils.RenderLayoutModule(source=self.config["temp_file"], serverport=self.config['serverport'], servermode=mode)
        
    