import argparse
import json
import os

from utils.settings import *
from utils.parallel import *
from utils.rules import *
from utils.workers import *
from utils.logger import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('--conf', type=str, default='./settings/example.json')
    parser.add_argument('--conf', type=str, default='./settings.json')
    args = parser.parse_args()

    # load settings (todo: cleaner and filter params)
    setting_module = Settings()
    setting_module.load_settings(args.conf)

    # process work (todo: with debug)
    ret_args = process_work(setting_module)
