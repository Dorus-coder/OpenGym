import numpy as np

def convert_action(action: dict, max_length: int) -> tuple:
    """Converts the action from the action space to a tuple of the orientation and position.

    Args:
        action (int): The action from the action space.
        orientation (int): The orientation of the action.
        max_length (int): The maximum length of the action.

    Returns:
        tuple: The orientation and position of the action.
    """
    ORIENTATION = {
        0: "longitudinal",
        1: "transverse",
        2: "horizontal  ",
    }
    position = action['position'] * max_length
    orientation = ORIENTATION[action['orientation']]
    return orientation, position[0]

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