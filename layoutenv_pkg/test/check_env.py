import os 
from pathlib import Path
import shutil

episode = 3


import os
import shutil

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


copy_directory(dst_dir='layouts\\episode_3', src_dir=r"C:\Users\cursist\Dorus\OpenGym\layoutenv_pkg\test")



