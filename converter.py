import argparse

from filesmanager import FilesManager

parser = argparse.ArgumentParser()
parser.add_argument("--config", help="Path to configuration file .ini.", required=True)
parser.add_argument("--input", help="Path to input .mrc file.", required=True)
parser.add_argument("--output", help="Path to output .csv file.", required=True)
parser.add_argument("--separator", help="Separator string.", default="$|$")
parser.add_argument("--step", help="Step for statistics.", default=100)
args = parser.parse_args()

if __name__ == "__main__":
    filesManager = FilesManager.FilesManager(input_file=args.input, output_file=args.output, config_file=args.config,
                                             separator=args.separator, step=args.step)
    filesManager.convert()
