#! /usr/bin/env python
from pathlib import Path
from sys import exit

import argparse
import logging


from terramirror.config import Config
from terramirror.main import Main

log_levels = ['INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL']


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('destination', action='store', type=Path)
    parser.add_argument('--log-level', choices=log_levels, default=log_levels[0])
    parser.add_argument('--mirror', default='https://dream.t3r.de/fgscenery/')
    parser.add_argument('--test', action='store_true')

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level))
    config = Config(
        destination=args.destination,
        test_mode=args.test,
        mirror=args.mirror
    )
    main = Main(config)
    exit(main.exec_())


if __name__ == '__main__':
    main()
