import argparse

from FilesManager import FilesManager

parser = argparse.ArgumentParser()
parser.add_argument("--fields", help="Defines columns names of result CSV files", nargs="+", required=True)
parser.add_argument("--all", help="If parameter is turned on, all separated parts of fields will be used,"
                                  " otherwise only first.", action="store_true")
parser.add_argument("--input", help="Path to input .mrc file.", required=True)
parser.add_argument("--output", help="Path to output .csv file.", required=True)
args = parser.parse_args()



if __name__ == "__main__":
    filesManager = FilesManager.FilesManager(input_file=args.input, output_file=args.output, fields=args.fields, all=args.all)
    filesManager.convert()
