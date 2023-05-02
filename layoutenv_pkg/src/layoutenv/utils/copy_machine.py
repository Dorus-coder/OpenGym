import shutil
from pathlib import Path
from tkinter import Tk, messagebox
import random
import time 
import os
def copy_layout_random_source(source: dict):
    """
    Arg:
        source (dict): config file of the environment with pias file locations\n
                       including layout extensions and temp file locations 
    return:
        the random picked source file for debuging purposes
    """
    cwd = Path.cwd()
    layout = cwd / Path(source["layout_arrangement"][random.randint(0, 1)])
    for extension in source["layout_file_extensions"]:
        file = layout.with_suffix(extension)
        shutil.copy2(src=file, dst=source["temp_dir"])
    return layout

CURRENT_TIME = time.strftime('%Y-%m-%d-%H-%M-%S')

def copy_files_after_termination(source: dict, episode: int):
    cwd = Path.cwd()
    destiny = cwd / Path(source["results_dir"]) / source["model"] / f"{CURRENT_TIME}" / str(episode)
    os.makedirs(destiny)
    extensions = source["probdam_extensions"] + source["layout_file_extensions"]
    for extension in extensions:
        file = cwd / Path(source["temp_file"]).with_suffix(extension)
        shutil.copy2(src=file, dst=destiny)

class Copy:
    def __init__(self) -> None:
        self.source = ""
        self.destination = Path(r"C:\Users\cursist\Dorus\ThesisResearch\PiasExampleFiles\temp")

    def copy_all(self):
        """
        Copies all files from the source directory
        """
        return shutil.copytree(src=Path(self.source), dst=self.destination, dirs_exist_ok=True)
    
    def query_user_empty_layout(self):
        """
        Verify with the user if an empty layout is desired.
        """
        your = MessageBox('empty layout')
        if your.question("Do you want to start with a new layout?") == 'yes':
           self.copy_all()
    
    def query_cmd(self):
        user_input = input('Do you like to start with a fresh layout?[Y/N]\n')
        if user_input.lower() == 'y' or 'yes':
            self.copy()

    def __str__(self):
        return f"source directory: {self.source}\ndestination directory: {self.destination}"
    
class MessageBox:
    def __init__(self, title: str, size="300*200"):
        self.title = title
        self.root = Tk()
            
    def question(self, question: str):
        return messagebox.askquestion(self.title, question)

    def warning(self, text: str):
        return messagebox.showwarning(self.title, text)
    

