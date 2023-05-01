from layoutenv import logger_module
import __main__
import shutil
from typing import Tuple
import os

logger = logger_module.get_logger_from_config(__main__.__name__)

def normalized_to_discrete(action: float) -> int:
    bins = [(-1, -1/3), (-1/3, 1/3), (1/3, 1)]
    for i, bin in enumerate(bins):
            if action >= bin[0] and action <= bin[1]:
                return i


def _normalized_to_discrete_itertools(action) -> int:
    # slightly slower because of generator object
    bins = [(-1, -1/3), (-1/3, 1/3), (1/3, 1)]
    return next(i for i, bin in enumerate(bins) if action >= bin[0] and action < bin[1])


def copy_directory(src_dir: str, dst_dir: str):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    for item in os.listdir(src_dir):
        src_path = os.path.join(src_dir, item)
        dst_path = os.path.join(dst_dir, item)
        if os.path.isdir(src_path):
            copy_directory(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)

def reward(att_idx: float, req_idx: float, layout: dict, volume_limit: float) -> float:
    # Add an increase in attained index as positive reward and guide the model towards it.
    if att_idx >= req_idx:
        max_volume = max(layout.values(), key=lambda x: x['volume'])['volume']
        volumetric_reward = max_volume / volume_limit
        delta = att_idx - req_idx
        # the ones are a placeholder for the weights
        reward = 1 * volumetric_reward + 1 * delta
        logger.info(f"reward(att_idx, req_idx, layout, volume_limit) -> reward = {reward}")
        logger.info(f"max volume encountered {max_volume}")
        return reward
    else:
        logger.info(f"reward(att_idx, req_idx, layout, volume_limit) -> reward = -1")
        return -1
    
def terminated(rewards: list, copy: Tuple[str, str]) -> bool:
    for idx in range(1, len(rewards)):
        if rewards[idx - 1] > 0 and rewards[idx] < 0:
            logger.info("terminated because a negative reward followed a positive reward.")
            copy_directory(*copy)
            return True 
    return False

def _terminated(rewards: list, copy: Tuple[str, str]) -> bool:
    """
    If the termination condition is met, end the epsiode and save the intermediate results.
    Arg: 
        rewards (list): list of accumaleted rewards
        copy (tuple[str, str]): copy source, destination
    Return (bool)
    """
    num_neg_rewards = 0
    num_pos_rewards = 0
    
    for idx in range(1, len(rewards)):
        if rewards[idx - 1] > 0 and rewards[idx] < 0:
            logger.info("terminated because a negative reward followed a positive reward.")
            return True 

    for idx, reward in enumerate(rewards):

        if reward < 0:
            num_neg_rewards += 1
            # if the second reward is positive but the number of negative rewards is greater as the number of positive rewards terminate the episode
            # This statement causes the episode to terminate as soon as there is a positve reward. But instead we would like to keep learning until rewards become negative



            if idx < len(rewards) - 1 and rewards[idx+1] > 0 and num_neg_rewards >= num_pos_rewards:
                logger.info(f"terminated on condition 1")
                copy_directory(*copy)
                return True
        elif reward > 0:
            num_pos_rewards += 1
            if num_neg_rewards >= num_pos_rewards:
                logger.info(f"terminated because negative reward after postive reward.")
                copy_directory(*copy)
                return True
    
    return False 

def _terminated(rewards: list, copy: Tuple[str, str]) -> bool:
    """
    If the termination condition is met, end the epsiode and save the intermediate results.
    Arg: 
        rewards (list): list of accumaleted rewards
        copy (tuple[str, str]): copy source, destination
    Return (bool)
    """
    # this function terminates the episode as soon as there is a positive reward
    gradient = [rewards[i] - rewards[i-1] for i in range(1, len(rewards))]

    if len(gradient) < 2:
        return False
        
    neg_gradient_count = 0
    pos_gradient_count = 0

    for g in reversed(gradient):
        if g <= 0:
            neg_gradient_count += 1
        else:
            pos_gradient_count += 1
    
    if neg_gradient_count >= len(gradient) // 2:
        logger.info(f"terminated on condition 1")
        copy_directory(*copy)
        return True
    
    return False   





if __name__ == "__main__":
    ...