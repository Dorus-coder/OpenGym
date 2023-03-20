from gymnasium.spaces import Dict, Box
import numpy as np
import pprint
from utils import convert_observation

max_volume = 5000
max_lenght = 100
max_breadth = 16
max_height = 7

obj = Dict(
    {
        "volume": Box(low=0, high=1, shape=(1,)),
        "center_of_gravity": Box(low=np.array([0, 0, 0]), high=np.array([1, 1, 1]), dtype=np.float32),
        "survival": Box(low=0, high=1),
}
)

print("Normalized values")
sample = dict(obj.sample())
pp = pprint.pformat(sample)
print(sample, '\n')

observation = convert_observation(sample, max_volume, max_lenght, max_breadth, max_height)

print('actual values')
pp = pprint.pformat(observation)
print(pp)