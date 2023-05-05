#iwbsSARC#sarc
from .sb_layout_env import LayoutEnv2
from piascomms.client import Client
from piascomms.internal_geometry.shape_manipulation.xml_request import RemovePhysicalPlane, AddPhysicalPlane
from collections import namedtuple
from gym import spaces
import shutil
from random import randint
import layoutenv.utils as lutils
import numpy as np
import time

class LayoutEnv3(LayoutEnv2):
    # Add class id here and create an isolated pias environment in the form of an isolated file.
    def __init__(self, mode="noHMI") -> None:
        """
        This environment has an improved reward function
        """
        super().__init__()
        self.renderer = lutils.RenderLayoutModule(source=self.config["temp_file"], serverport=self.config['serverport'], servermode=mode)
        self.action_space = spaces.Box(low=-1, high=1, shape=(2,), dtype=np.float64)
        self.episode_count = -1
        self.previous_att_idx = 0

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
            max_volume = max(layout.values(), key=lambda x: x['volume'])['volume']
            volumetric_reward = (max_volume - self.config['min_compartment_volume_a']) * 0.01
            self.logger.info(f"reward(att_idx, req_idx, layout, volume_limit) -> reward = {volumetric_reward}")
            return  volumetric_reward   
        else:
            self.logger.error('No reward given')
            return -10


    def step(self, action: np.array):
        self.logger.info(f"LayoutEnv.step() @timestep {self.time_step}")
        self.time_step += 1
      
        self._add_physical_plane(action)

        att_idx = lutils.start_damage_stability_calc(self.config['ai_results'])
        req_idx = lutils.required_index(self.config["length"])

        observation, layout = self._observation()
        
        info = self._info(att_idx, req_idx)
        reward = self.reward(att_idx, req_idx, layout)
        self.previous_att_idx = att_idx
        self.cum_reward.append(reward)
        done = lutils.terminated(self.cum_reward, self.config, self.episode_count) | self._truncated(max_time_steps=self.config["max_episode_length"])

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
        
        source = lutils.copy_layout_random_source(source=self.config)
        self.logger.info(f"func name: render(), arg: source: {source}")
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
        raise NotImplementedError("This function is not used")
        
    