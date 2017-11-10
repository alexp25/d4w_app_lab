import csv
import numpy as np


class DataClass:

    def __init__(self):
        self.data = {
            "headers": [],
            "series": []
        }

    def read_data(self,file):
        with open(file, 'r') as dest_f:
            data_iter = csv.reader(dest_f,
                                   delimiter=",",
                                   quotechar='"')
            data = [data for data in data_iter]
            data_np = np.array(data)

            self.data["headers"] = data_np[:, 0]
            self.data["series"] = data_np[:, 1:].astype(float)

        return self.data



