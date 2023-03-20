from gymnasium.spaces import Discrete, Dict, Box
import numpy as np
import pprint
from utils import convert_action

max_length = 100

orientation = {
    0: "longitudinal",
    1: "transverse",
    2: "horizontal  ",
}

action_space = Dict(
    {
        "orientation": Discrete(3),
        "position": Box(low=-1, high=1, dtype=np.float32),
    }
)


sample = dict(action_space.sample())
pp = pprint.pformat(sample)
print(pp)

act = convert_action(sample, max_length)
pp = pprint.pformat(act)
print(pp)

def rescale_actions(tanh_output, low, high):
    range = high - low
    return tanh_output * range / 2 + (low + (0.5 * range))

dis = rescale_actions(sample['position'][0], 0, max_length)
print(f"{dis = }")
