import argparse

from utils.quick_start import run_zhem

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('--conf', type=str, default='./settings/example.json')
    parser.add_argument('--conf', type=str, default='./settings.json')
    args = parser.parse_args()

    # run zhem
    ret_args = run_zhem(args.conf)