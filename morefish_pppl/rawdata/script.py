import json
import os
import re


class extractor:

    def __init__(self, *dformat):
        self.dformat = list(dformat)

    def __extract__(self, data):
        i = 0
        while i < len(self.dformat):
            self.read_json(self.dformat[i])
            print("Save.read_json --->", self.read_json(self.dformat[i]))
            if self.extract_values(data) is not None:
                return self.fmt, self.extract_values(data)
            i += 1

    # reading data format from json file

    def read_json(self, dformat):
        base_url = os.path.join(os.getcwd(), 'rawdata')
        with open(os.path.join(base_url, 'data.json'), 'r') as file:
            data = json.load(file)
            print("dformat------>",data)
            self.extract_fields(data, dformat)
            print("data format ------->",self.extract_fields(data, dformat))

    # extract data fields
    def extract_fields(self, fmt_data, dformat):
        self.seps = fmt_data[dformat]['sep']
        self.fields = fmt_data[dformat]['fields']
        print("fields -------->",dformat)
        self.fmt = dformat

    # extract values corresponding to data fields
    def extract_values(self, data):
        regexPattern = '|'.join(map(re.escape, tuple(self.seps)))
        data = re.split(regexPattern, data)
        print("data------>",data)
        if len(data) == len(self.fields):
            return {**self.extract_field_data(data)}
        else:
            return None

    def extract_field_data(self, data):
        i = 0
        for key in self.fields.keys():
            self.fields[key] = data[i]
            i += 1
        return self.fields


def data_formatePadma(dfmt, data):
    o1 = extractor(dfmt)
    dict1 = o1.__extract__(data)
    return dict1

# if __name__ == "__main__":
#     ### example data
#     data1 = 'GID:8020002203220000, DID:802102206290004, Analog: 1000 142 0 476'
#     data2 = ' GID:8020002203220000, connected'
#     data3 = 'GID:8020002203220000, connected'
#
#     # ### data format
#     dfmt1 = 'Dfmt8020001'
#     dfmt2 = 'Dfmt8020002'
#     dfmt3 = 'Dfmt8020003'
#
#     ### creating object with various data format
#     o1 = extractor(dfmt3, dfmt1, dfmt2)
#     o2 = extractor(dfmt1, dfmt3, dfmt2)
#     o3 = extractor(dfmt1, dfmt3, dfmt2)
#
#     ### will return dictionary as defined in file.json
#     dict1 = o1.__extract__(data1)
#     dict2 = o2.__extract__(data2)
#     dict3 = o3.__extract__(data3)
#
#     print(dict1)
#     print(dict2)
#     print(dict3)
