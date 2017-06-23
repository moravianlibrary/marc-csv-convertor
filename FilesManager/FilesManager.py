import os
import sys
import re


class FilesManager:
    """
    Class is managing input and output files.
    """

    def __init__(self, input_file, output_file, fields, all):
        self.input_file = input_file
        self.output_file = output_file
        self.fields = fields
        self.all = all
        self.check_file(self.input_file, ".mrc")

    def check_file(self, pathToFile, extension):
        if os.path.exists(pathToFile):
            if pathToFile.endswith(extension):
                return True
            else:
                print("File has wrong extension, expected {}".format(extension), file=sys.stderr)
                raise IOError
        else:
            print("File {} is not found".format(pathToFile), file=sys.stderr)
            raise FileNotFoundError

    def process_record(self, record, o_file):
        processed = {}
        clearLambda = lambda lin: re.sub("\$\S?", "", lin)
        for line in record:
            line = re.sub("\n", "", line)
            field = ""
            if len(line) > 0:
                field = line.split()[0]
            if field in self.fields:
                if line.startswith(field):
                    if self.all:
                        if field in processed:
                            processed[field] += list(map(clearLambda, re.findall("\$\S?[^\$\n]*", line)))
                        else:
                            processed[field] = list(map(clearLambda, re.findall("\$\S?[^\$\n]*", line)))
                    else:
                        if field in processed:
                            processed[field] += list(
                                map(lambda lin: re.sub("\$\S?", "", lin), [re.search("\$\S?[^\$\n]*", line).group()]))
                        else:
                            processed[field] = list(
                                map(lambda lin: re.sub("\$\S?", "", lin), [re.search("\$\S?[^\$\n]*", line).group()]))
        return processed

    def convert(self):

        with open(self.input_file) as iFile:

            with open(self.output_file, "w+") as o_file:
                marc_record = []

                for line in iFile:

                    if line.startswith("LEADER") and len(marc_record) > 0:
                        aux = self.process_record(record=marc_record, o_file=o_file)
                        print(aux)
                        marc_record.clear()
                        marc_record.append(line)
                    else:
                        marc_record.append(line)

                self.process_record(record=marc_record, o_file=o_file)
