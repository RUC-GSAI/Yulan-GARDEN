from utils.settings import *
from utils.process import process_work

def run_zhem(conf_path: str):
    # load settings
    setting_module = Settings()
    setting_module.load_settings(conf_path)

    # process work
    ret_args = process_work(setting_module)
    return ret_args