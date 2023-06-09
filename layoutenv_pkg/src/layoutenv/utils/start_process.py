from layoutenv import logger_module
from pathlib import Path
import subprocess
import time
import pandas as pd
import layoutenv.logger_module as logger_mod
import __main__
import shutil 
import os
from dataclasses import dataclass

logger = logger_mod.get_logger_from_config(name=__main__.__name__)

import subprocess
import psutil

def copy_pias_config():
    cwd = Path.cwd()
    shutil.copy2(src=cwd / "PiasFiles\\back_up_empty_ship\\goa1.cnf1", 
                 dst=cwd / "PiasFiles\\temp\\goa1.cnf1")


class RenderLayoutModule:
    def __init__(self, source: str, serverport: int, servermode: str) -> None:    
        self.command = [r"C:\\SARC_local\\sarc_en\\layout.exe", f"piasnaam={source}", f"-XMLserverport={serverport}", f"-servermode={servermode}"]
        self.process = None
        
    def start_process(self):
        copy_pias_config()
        self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
    def kill_process(self):
        if self.process:
            self.process.kill()
            logger.info(f"{self.process} killed")
        else:
            logger.warning("No process running.")
    
    def process_is_running(self):
        if self.process:
            return psutil.pid_exists(self.process.pid)
        else:
            return False

def read_ai(source):
    global logger
    try:
        df = pd.read_csv(source)
        logger.info(f"read {source}")
    except PermissionError as e:
        logger.exception(f"{e}")
        return 0.0
    except pd.errors.EmptyDataError as e:
        logger.exception(f"{e}")
        return 0.0
    # save the ai index in its own dataframe to prevent losing important ai data
    df_ai = df['ai']
    df_ai.dropna(inplace=True)
    _idx1 = int(len(df_ai) / 3)
    _idx2 = _idx1 * 2
    

    a_sp  = sum(df_ai[:_idx2]) * 0.4
    a_d = sum(df_ai[_idx2:]) * 0.2
    
    
    return a_sp + a_d

def copy_pd1(time):
    cwd = Path.cwd()
    if os.path.getmtime(cwd / "PiasFiles\\temp\\goa1.pd1") != time:
        shutil.copy2(src=cwd / "PiasFiles\\back_up_empty_ship\\goa1.pd1", 
                    dst=cwd / "PiasFiles\\temp\\goa1.pd1")
        

@dataclass
class PD1_time:
    PD1: float = os.path.getmtime(Path.cwd() / "PiasFiles\\temp\\goa1.pd1")



def start_damage_stability_calc(source: str) -> float:
    global logger
    global PD1


    cwd = Path.cwd()

    if os.path.getmtime(cwd / "PiasFiles\\temp\\goa1.pd1") != PD1_time().PD1:
        shutil.copy2(src=cwd / "PiasFiles\\back_up_empty_ship\\goa1.pd1", 
                    dst=cwd / "PiasFiles\\temp\\goa1.pd1")
        logger.warning("PD1 file corupted, copied from back up.")
    copy_pias_config()


    pd0_path = Path(source)
    if pd0_path.suffix != ".csv":
        pd0_path = Path(source).with_suffix('.csv')
    
    if pd0_path.is_file():
        pd0_path.unlink()
        logger.info(f"{pd0_path} unlinked")

    process = subprocess.Popen(['C:\SARC_local\sarc_en\probdam.exe', fr'piasnaam={source}', 'execute_directly=ja'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logger.info(f'Probdam started with file: {source}')
    
    while not pd0_path.is_file():
        time.sleep(0.5)
    
    ai = read_ai(pd0_path)
    logger.info(f"Damage stability done total attained index: {ai}")
    
    process.kill()
    return ai

def _main_1():
    import time
    
    # render = RenderLayoutModule(source="C:\\Users\\cursist\\Dorus\\ThesisResearch\\PiasExampleFiles\\temp\\goa1", servermode='noHMI', serverport=14100)
    # render.start_proces()
    # time.sleep(3)

    def kill_process_if_running(process_name: str):
        for line in subprocess.Popen('tasklist', stdout=subprocess.PIPE).stdout:
            if process_name.encode() in line:
                pid = int(line.decode().split()[1])
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(pid)])
                print(f"{process_name} process (PID: {pid}) killed.")
                return True
        print(f"{process_name} process is not running.")
        return False
    for line in subprocess.Popen('tasklist', stdout=subprocess.PIPE).stdout:
        if "la".encode() in line:
            print(line)
        elif "pi".encode() in line:
            print(line)
    kill_process_if_running('layout.exe')

def _main_2():
    source = r"C:\Users\cursist\Dorus\ThesisResearch\PiasExampleFiles\csv_example.csv"
    ai = read_ai(source)
    print(f"{ai = }")


if __name__ == "__main__":
    _main_2()

