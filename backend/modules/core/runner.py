import json
import threading
import time
import traceback
from threading import Thread
import datetime
from modules.api.HIL_socket_API import HIL_socket
from modules.data import variables
from modules.data.constants import Constants


class TestRunner(Thread):
    """
    class used for calling the API for device
    In multi mode (manager) it calls the API inside a thread, which allows for non-blocking
    functionality for the application
    In async mode (manager) it runs the API within the calling thread, also non-blocking except the API I/O methods
    """

    def __init__(self, hil_def):
        # constructor
        Thread.__init__(self)
        self.hil_def = hil_def
        self.hil_socket = hil_def["function"]["socket"]

        self.hil = HIL_socket(self.hil_def["data"]["ip"], self.hil_def["data"]["port"])

        self.t0 = time.time()
        self.t = self.t0
        self.t_start = self.t0
        self.t_string = ""
        self.TS = 0.1

        self.log = False

        self.flag_send_data = False
        self.msg_out = "100"

        # print(variables.sensorModel)

        self._stop_flag = threading.Event()


    def stop(self):
        """
        stop request, end thread, close device thread (in the multi mode)
        """
        self._stop_flag.set()

    def stop_request(self):
        """
        check if there is a stop request, that would end the thread (in the multi mode)
        :return: boolean
        """
        return self._stop_flag.is_set()

    def update_test_timer(self):
        """
        update test timer for the current device
        :param hil_def: the hil device object
        """

        self.t_string = "%.4f" % (time.time() - self.t_start)

    def update_sensor_data(self, id, value):
        tm = datetime.datetime.now()
        tim = time.time()
        # print("update ", id)
        for s in variables.sensor_data:
            if s['id'] == id:
                s['value'] = value
                s['value1'] = value
                s['value2'] = value
                s['recent'] = True
                s['tim'] = tim
                s['ts'] = tm.strftime("%H:%M:%S.%f")
                break

    def get_response_data(self, resp):
        if resp[0] == 100:
            # device data
            device_data = variables.device_data[self.hil_def["data"]["index"]]
            device_data["in"] = str(resp)
            device_data["rx_counter"] += 1

            for sensor_def in variables.sensor_model:
                if self.hil_def["data"]["info"] is not None:
                    if self.hil_def["data"]["info"]["type"] == Constants.NODE_FLOW_SENSOR:
                        for e in sensor_def['data']:
                            try:
                                self.update_sensor_data(e["node_id"], resp[e['pos']])
                            except:
                                pass

    def send_data(self, data):
        self.msg_out = data
        self.t0 = self.t
        self.flag_send_data = True

    def run_async(self):
        self.t = time.time()
        self.update_test_timer()
        if not self.hil_socket.is_connected():
            self.hil_socket.newSocket()
            self.hil_socket.connect()

        if self.t - self.t0 >= self.TS:
            # cyclic msg, request data from devices
            self.t0 = self.t
            self.msg_out = "100"
            if self.hil_def["data"]["info"] is not None:
                if self.hil_def["data"]["info"]["type"] == Constants.NODE_FLOW_SENSOR:
                    # flow measurement node
                    self.msg_out = "100,3"
            self.flag_send_data = True


        if self.flag_send_data:
            self.flag_send_data = False

            t_req = time.time()
            # variables.log2(self.__class__.__name__, 'sending to "%s" "%s"' % (self.hil_def["data"]["ip"], self.msg_out))
            res = self.hil_socket.request(self.msg_out)
            t_req = time.time() - t_req

            if self.log:
                variables.log2(self.__class__.__name__, 'recv from "%s" "%s", time ms "%d"' % (self.hil_def["data"]["ip"], res[1], t_req*1000))
            if res[0] == -1:
                self.hil_socket.reset_connection()
            else:
                self.get_response_data(res[1])



    def run(self):
        variables.log2("[TestRunner]", "started")
        while True:
            time.sleep(variables.LOOP_DELAY)
            self.run_async()
            if self.stop_request():
                break
        variables.log2(self.__class__.__name__, "stopped")
