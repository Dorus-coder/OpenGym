from gym import Env
from gym.spaces import Discrete, Box, Dict
import numpy as np
from piascomms.internal_geometry.shape_manipulation.xml_request import AddPhysicalPlane, RequestFactory, RequestVolume
from piascomms.utils import observation_space
from piascomms.internal_geometry.shape_manipulation.xml2dataclasses.physical_planes import physical_planes_from_xml
from piascomms.compartments import CompartmentData
from pathlib import Path
from piascomms.client import Client, TranslateReply, RecievedMessage

class LayoutEnv(Env):
    def __init__(self) -> None:
        self.action_space = Dict(
                                {
                                    "orientation": Discrete(3),
                                    "position": Box(low=0, high=1, dtype=np.float32),
                                }   
                            )
        self.observation_space = Dict(
                                {
                                    "volume": Box(low=0, high=1, shape=(1,)),
                                    "center_of_gravity": Box(low=np.array([0, 0, 0]), high=np.array([1, 1, 1]), dtype=np.float32),
                                    "survival": Box(low=0, high=1),
                                }
                            ) 
    
    def step(self, action):
        AddPhysicalPlane(planes=planes,
                         orientation='transverse',
                        distance=-30,

    def render(self):
        raise NotImplementedError('is this necessary?')
    
    def reset(self):
        pass    