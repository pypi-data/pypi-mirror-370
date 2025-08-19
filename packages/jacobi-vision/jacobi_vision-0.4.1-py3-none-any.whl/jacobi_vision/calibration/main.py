from argparse import ArgumentParser
from pathlib import Path

from .analyze import analyze
from .record import record


def main():
    parser = ArgumentParser(description='Extrinsic calibration between robots and cameras.')
    subparsers = parser.add_subparsers(title='task', required=True, help='Task for the calibration script.')

    parser_analyze = subparsers.add_parser('analyze')
    parser_analyze.add_argument('marker', type=str, choices=['ball'], help='Marker type to detect.')
    parser_analyze.add_argument('directory', type=Path, help='Directory of the images to analyze.')
    parser_analyze.add_argument('--visualize', action='store_true', help='Visualize the detected pattern.')
    parser_analyze.add_argument('--project', default=None, type=str, help='Studio project name or path.')
    parser_analyze.add_argument('--studio', action='store_true', help='Update the camera position in Studio.')
    parser_analyze.set_defaults(func=analyze)

    parser_record = subparsers.add_parser('record')
    parser_record.add_argument('--camera', required=True, help='Camera model.')
    parser_record.add_argument('--name', default=None, help='Name or ID of the specific camera.')
    parser_record.add_argument('--robot', default=None, help='Model of the robot.')
    parser_record.add_argument('--robot-host', default=None, help='IP address of the robot.')
    parser_record.add_argument('--output', default=Path(), type=Path, help='Output directory of the recorded images.')
    parser_record.set_defaults(func=record)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
