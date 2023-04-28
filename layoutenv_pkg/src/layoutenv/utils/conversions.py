import numpy as np

def rescale_actions(tanh_output, low, high) -> float:
    range = high - low
    return tanh_output * range / 2 + (low + (0.5 * range))

def inverse_rescale_actions(y, low, high):
    range = high - low
    val =  (2 / range) * (y - (low + (0.5 * range)))
    if -1 > val > 1:
        raise ValueError(f'Normalized values should lie between -1 and 1. val is {val}')
    else:
        return val


def convert_action(action: dict, max_length: int, min_length: int = 0) -> tuple:
    """Converts the action from the action space to a tuple of the orientation and position.

    Args:
        action (dict): The action from the action space.
        max_length (int): The maximum length of the action.

    Returns:
        tuple: orientation, position, boundary vertex 1, boundary vertex 2
    """
    ORIENTATION = {
        0: "Longitudinal bulkhead",
        1: "Frame",
        2: "Deck",
    }
    BOUNDARIES = {
        "Longitudinal bulkhead": (1, 2),
        "Frame": (5, 6),
        "Deck": (1, 2)
    }
    position = rescale_actions(action['position'], low=0, high=max_length) 
    orientation = ORIENTATION[action['orientation']]
    return orientation, position[0] * -1, *BOUNDARIES[orientation]

def convert_observation(observation: dict, max_volume: int, max_length: int, max_breadth: int, max_height: int) -> dict:
    """Converts the observation from the observation space to a dictionary with the actual values.

    Args:
        observation (dict): The observation from the observation space.
        max_volume (int): The maximum volume of the observation.
        max_length (int): The maximum length of the observation.
        max_breadth (int): The maximum breadth of the observation.
        max_height (int): The maximum height of the observation.

    Returns:
        dict: The observation with the actual values.
    """
    observation['volume'] = observation['volume'] * max_volume
    observation['center_of_gravity'] = observation['center_of_gravity'] * np.array([max_length, max_breadth, max_height])
    return observation