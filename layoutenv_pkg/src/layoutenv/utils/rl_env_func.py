from layoutenv import logger_module
from layoutenv.utils.copy_machine import copy_files_after_termination
import __main__
import shutil
from typing import Tuple
import os
from typing import Optional 

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

    
def terminated(rewards: list, config: dict, episode: Optional[int] = None, copy: bool = False) -> bool:
    # The termination function doesn't terminated when the objective is met
    if len(rewards) >= 2 and rewards[-2] > 0 and rewards[-1] <= 0:
        logger.info("terminated because a negative reward followed a positive reward.")
        if copy:
            copy_files_after_termination(source=config, episode=episode)
            # The objective is met if the case below returns True.
        return True 
    elif rewards[-1] > 1.0:
        return True
    return False


if __name__ == "__main__":

    assert terminated([-1, 0], {}) == False, 'should return True'
    assert terminated([-1, -1, -1, 1, 1, 0], {}) == True, 'should return True'
    assert terminated([1, 1, -1, 5, 5], {}) == True, 'should return True'



