from utils.settings import *
from utils.process import process_work
import os
import shutil

def run_zhem(conf_path: str, if_force: int):
    # load settings
    setting_module = Settings(conf_path)

    # remove output_path
    if if_force:
        shutil.rmtree(setting_module.settings['output_path'])
        os.makedirs(setting_module.settings['output_path'], exist_ok=True)

    # process work
    ret_args = process_work(setting_module)
    return ret_args