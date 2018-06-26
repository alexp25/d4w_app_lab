import copy
import time
import traceback
import datetime
from threading import Thread

from modules.api.HIL_socket_API import HIL_socket
from modules.core.runner import TestRunner
from modules.data import variables
from modules.data.constants import Constants


class TestRunnerManager(Thread):
    """
    class used for managing test runners
    It can run the tests for each device in 2 modes:
    1. async - single thread, loops through all devices and runs the actions asynchronously
    2. multi - multi thread, uses the dedicated loop for every device and the test actions
    are run in that loop (also asynchronously)
    For scalability (high number of devices), the async mode is recommended
    For performance (low latency), the multi mode is recommended
    For both, a mix of async and multi would be a solution
    *For general purpose, either mode can be used
    """

    def __init__(self):
        # constructor
        Thread.__init__(self)
        # self.mode = 'async'
        self.mode = 'multi'
        self.t0 = time.time()
        self.t = self.t0
        self.TS = variables.app_config["params"]["ts"]
        self.TS_DB = variables.app_config["params"]["t_log"]
        self.t0_db = self.t0

        self.tr = []
        self.hil_object_array = []
        self.hil_device_index = 0

        self.load_hil_devices()
        self.current_device_config = copy.deepcopy(variables.app_config["devices"])

    def update_hil_devices(self):
        """
        check if device list changed and reload devices
        """
        if self.current_device_config != variables.app_config["devices"]:
            self.clear_hil_devices()
            self.load_hil_devices()
            self.current_device_config = copy.deepcopy(variables.app_config["devices"])

    def load_hil_devices(self):
        """
        load hil devices
        """
        self.tr = []
        self.hil_object_array = []
        self.hil_device_index = 0
        for dev in variables.app_config["devices"]:
            if dev["enable"]:
                #  add only devices connected via tcp
                self.add_new_hil_device(dev["ip"], dev["port"], dev)

    def clear_hil_devices(self):
        """
        clear hil devices and close test runner threads
        """
        for i in range(len(self.hil_object_array)):
            try:
                self.tr[i].stop()
                self.tr[i].join()
            except:
                pass
        self.tr = []
        print('hil device clear: stopped threads')
        self.hil_object_array = []
        variables.device_data = []
        self.hil_device_index = 0

    def add_new_hil_device(self, ip, port=9001, dev = None):
        """
        add new hil device and test runner thread
        :param ip: ip
        """

        variables.log2("[add_new_hil_device]", str(self.hil_device_index) + ", " + ip + ":" + str(port))
        self.hil = HIL_socket(ip, port)

        new_device_data = copy.deepcopy(Constants.hil_object_data_model)
        new_device_data["id"] = dev["info"]["id"]
        new_device_data["type"] = dev["info"]["type"]
        new_device_data["ip"] = ip
        new_device_data["port"] = port
        new_device_data["index"] = self.hil_device_index
        if dev is not None:
            if "info" in dev:
                new_device_data["info"] = dev["info"]

        variables.device_data.append(new_device_data)

        if dev["source"] == 0:
            new_hil_object = {
                "function": {
                    "socket": self.hil,
                },
                "data": new_device_data
            }
            self.hil_object_array.append(new_hil_object)
            self.tr.append(TestRunner(new_hil_object))
            if self.mode == 'multi':
                self.tr[self.hil_device_index].start()

        self.hil_device_index += 1


    def set_pump(self, value):
        j = 0
        for (i, dev) in enumerate(variables.app_config["devices"]):
            if dev["enable"]:
                if dev["info"]["type"] == Constants.NODE_PUMP:
                    # variables.log2("set_pump", "dev: " + str(j))
                    self.tr[j].send_data("1," + str(value))
                    # variables.app_flags["pump"] = value
                j += 1

    def run(self):
        """
        check for user input
        check status of test runners
        """
        variables.log2(self.__class__.__name__, "started")

        while True:
            time.sleep(Constants.LOOP_DELAY)
            self.t = time.time()
            try:
                if self.t - self.t0 >= self.TS:
                    self.t0 = self.t

                    if variables.app_flags['log'] == True:
                        variables.log_sensor_data()

                if variables.app_config["app"]["db_logging"]:
                    # database log
                    # logging is done synchronously with latest data
                    # even if data from sensors are slightly delayed
                    # if a sensor is disconnected, the last value will not be
                    # written in the database (if the timeout expires)
                    if ((self.t - self.t0_db) > self.TS_DB):
                        self.t0_db = self.t
                        variables.log2(self.__class__.__name__, "save to db")

                        for s in variables.sensor_data:
                            # only save new data
                            # do not save the same data multiple times in the database
                            if 'recent' in s:
                                if s['recent']:
                                    s['recent'] = False
                                    if variables.cnxn is not None:
                                        cursor = variables.cnxn.cursor()
                                        tm = datetime.datetime.now()
                                        cursor.execute(
                                            "insert into SensorData_Flow(Timestamp, Value, Pipe_ID) values (?, ?, ?)",
                                            tm, s['value2'],
                                            s['id'])
                                        variables.cnxn.commit()
                            s['recent'] = False

                # manage runners
                for (i, hil_def) in enumerate(self.hil_object_array):
                    if self.mode == 'async':
                        self.tr[i].run_async()

            except:
                variables.print_exception(self.__class__.__name__)
                continue



