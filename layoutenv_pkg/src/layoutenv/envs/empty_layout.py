import shutil
from pathlib import Path
from tkinter import Tk, messagebox


class Copy:
    def __init__(self) -> None:
        self.source = ""
        self.destination = Path(r"C:\Users\cursist\Dorus\ThesisResearch\PiasExampleFiles\temp")

    def copy(self):
        return shutil.copytree(src=Path(self.source), dst=self.destination, dirs_exist_ok=True)
    
    def query_user_empty_layout(self):
        """
        Verify with the user if an empty layout is desired.
        """
        your = MessageBox('empty layout')
        if your.question("Do you want to start with a new layout?") == 'yes':
           self.copy()
    
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
    

