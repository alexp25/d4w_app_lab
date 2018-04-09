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
            # self.data["series_array"] = data

        return self.data

    def write_data(self, file, data, dim):
        with open(file, 'w', newline="") as dest_f:
            cw = csv.writer(dest_f,
                       delimiter=',',
                       quotechar='"')

            if dim==1:
                cw.writerow(data)
            elif dim==2:
                for row in data:
                    cw.writerow(row)




