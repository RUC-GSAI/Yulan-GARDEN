import argparse

from utils.quick_start import run_zhem

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('--conf', type=str, default='./settings/example.json')
    parser.add_argument('--conf', type=str, default='./settings.json')
    parser.add_argument('--f', type=int, default=0)
    parser.add_argument('--o', type=int, default=0)
    args = parser.parse_args()

    # run Yulan-GARDEN
    ret_args = run_zhem(args.conf, args.f, args.o)