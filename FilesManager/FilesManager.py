import os
import sys
import re
import csv
import configparser


def check_file(pathToFile, extension):
    if os.path.exists(pathToFile):
        if pathToFile.endswith(extension):
            return True
        else:
            print("File has wrong extension, expected {}".format(extension), file=sys.stderr)
            raise IOError
    else:
        print("File {} is not found".format(pathToFile), file=sys.stderr)
        raise FileNotFoundError


class FilesManager:
    """
    Class is managing input and output files.
    """

    def __init__(self, input_file, output_file, config_file, separator):
        check_file(input_file, ".mrc")
        check_file(config_file, ".ini")

        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.fields = dict(self.config["FIELDS"].items())
        self.input_file = input_file
        self.output_file = output_file
        self.separator = separator



    def process_record(self, record, o_file):
        processed = {}
        clear_lambda = lambda lin: re.sub("\$\S?", "", lin)
        for line in record:
            line = re.sub("\n", "", line)
            field = ""
            if len(line) > 0:
                field = line.split()[0]
            if field in list(dict(self.fields.items()).keys()):
                if line.startswith(field):

                    for subfield_tag in str(self.fields[field]).split():

                        vals = list(map(lambda l: re.sub("\$\S?", "", l), list(filter(lambda s: len(s) > 0, list(map(lambda subfield: subfield if str(subfield).startswith(subfield_tag) else "",
                                 re.findall("\$\S?[^\$\n]*", line)))))))

                        if field in processed:
                            processed[field] += vals
                        else:
                            processed[field] = vals
        return processed

    def joiner(self, record_dict):
        merged_fields = {}
        for key, value in dict(record_dict).items():
            merged_fields[key] = str(self.separator).join(value)

        return merged_fields

    def convert(self):
        with open(self.input_file) as iFile:

            with open(self.output_file, "w+") as o_file:
                marc_record = []

                csv_writer = csv.DictWriter(o_file, fieldnames=self.fields)
                csv_writer.writeheader()

                for line in iFile:

                    if line.startswith("LEADER") and len(marc_record) > 0:
                        csv_writer.writerow(self.joiner(self.process_record(record=marc_record, o_file=o_file)))
                        marc_record.clear()
                        marc_record.append(line)
                    else:
                        marc_record.append(line)

                self.process_record(record=marc_record, o_file=o_file)
