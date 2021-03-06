import os
import sys
import re
import csv
import configparser
import subprocess
from preprocessing.Preprocessing import Preprocessing


def check_file(path_to_file, extension):
    if os.path.exists(path_to_file):
        if path_to_file.endswith(extension):
            return True
        else:
            print("File has wrong extension, expected {}".format(extension), file=sys.stderr)
            raise IOError
    else:
        print("File {} is not found".format(path_to_file), file=sys.stderr)
        raise FileNotFoundError


class FilesManager:
    """
    Class is managing input and output files.
    """

    def __init__(self, is_stop_words, input_file, output_file, config_file, separator, step):
        check_file(input_file, ".mrc")
        check_file(config_file, ".ini")
        stop_words = []

        self.step = step
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        if is_stop_words:
            string_stop_words = self.config["PREPROCESSING"]["STOP_WORDS"]
            stop_words += list(map(lambda x: x.replace('"', ""), re.findall('"[^"]*"', string_stop_words)))
            stop_words += re.sub('"[^"]*"', "", string_stop_words).split()
        self.input_file = input_file
        self.output_file = output_file
        self.separator = separator
        self.preprocessor = Preprocessing(stop_words=stop_words, values=None,
                                          tagger=self.config["PREPROCESSING"]["TAGGER"],
                                          taggerPOS=self.config["PREPROCESSING"]["TAGGER_POS"])

    def process_record(self, record):
        processed = {}
        lemmatize_fields = self.config["PREPROCESSING"]["LEMMATIZE_FIELDS"].split()

        for line in record:
            line = re.sub("\n", "", line)
            field = ""
            if len(line) > 0:
                field = line.split()[0]
            if field in list(dict(dict(self.config["FIELDS"].items()).items()).keys()):
                if line.startswith(field):

                    for subfield_tag in str(dict(self.config["FIELDS"].items())[field]).split():

                        vals = list(map(lambda l: re.sub("\$\S?", "", l), list(filter(lambda s: len(s) > 0, list(
                            map(lambda subfield: subfield if str(subfield).startswith(subfield_tag) else "",
                                re.findall("\$\S?[^\$\n]*", line)))))))

                        if field in processed:
                            processed[field] += vals
                        else:
                            processed[field] = vals

                        if field in lemmatize_fields:
                            field = field + "_lemm"
                            self.preprocessor.setParams(values=vals)
                            if field in processed:
                                processed[field] += self.preprocessor.start()
                            else:
                                processed[field] = self.preprocessor.start()

        return processed

    def joiner(self, record_dict):
        merged_fields = {}
        for key, value in dict(record_dict).items():
            merged_fields[key] = str(self.separator).join(value)

        return merged_fields

    def convert(self):
        print("Counting records.")
        amount_of_records = int(
            subprocess.check_output('grep {} -e "^LEADER" | wc -l'.format(self.input_file), stderr=subprocess.STDOUT,
                                    shell=True))
        print("Total {} records".format(amount_of_records))
        counter = 0
        processed = 0
        list_of_processed_records = []
        with open(self.input_file) as iFile:

            with open(self.output_file, "w+") as o_file:
                marc_record = []
                fields = list(
                    map(lambda x: x + "_lemm", self.config["PREPROCESSING"]["LEMMATIZE_FIELDS"].split())) + list(
                    dict(self.config["FIELDS"].items()).keys())

                csv_writer = csv.DictWriter(o_file, fieldnames=fields)
                csv_writer.writeheader()

                for line in iFile:

                    if line.startswith("LEADER") and len(marc_record) > 0:
                        list_of_processed_records.append(self.joiner(self.process_record(record=marc_record)))
                        processed += 1
                        counter += 1
                        marc_record.clear()

                    if counter >= self.step:
                        counter = 0
                        print("{} of {} records processed".format(processed, amount_of_records))

                    if len(list_of_processed_records) >= self.step:
                        csv_writer.writerows(list_of_processed_records)
                        list_of_processed_records.clear()

                    marc_record.append(line)

                list_of_processed_records.append(self.joiner(self.process_record(record=marc_record)))
                csv_writer.writerows(list_of_processed_records)
                processed += 1
                print("{} of {} records processed".format(processed, amount_of_records))
