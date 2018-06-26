import copy
import threading
from threading import Thread

import time

import paho.mqtt.client as mqtt

from modules.data import variables
from modules.data.constants import Constants


class MQTTClient(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._stopEvent = threading.Event()
        self.client = None
        self.t = time.time()

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        DEFAULT_QOS = 2
        print("Connected with result code "+str(rc))

        # disconnect all connected devices first

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("$SYS/#")
        client.subscribe("aux/node/#", qos=DEFAULT_QOS)
        client.subscribe("data/temp", qos=DEFAULT_QOS)
        client.subscribe("data/node/#", qos=DEFAULT_QOS)

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("Unexpected disconnection.")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        # print(msg.topic+" "+str(msg.payload))
        if "aux/node/" in msg.topic:
            # print(msg.topic + ": " + msg.payload)
            info = msg.payload.split(",")
            info_json = {"ip": info[0], "data": None}
            self.update_client_data(msg.topic, info_json)
        if "data/node/" in msg.topic:
            # print(msg.topic + ": " + msg.payload)
            info_json = {"data": msg.payload}
            self.update_client_data(msg.topic, info_json)

        # print("message received ", str(message.payload.decode("utf-8")))
        # print("message topic=", message.topic)
        # print("message qos=", message.qos)
        # print("message retain flag=", message.retain)
    def update_client_data(self, msg_topic, data):
        cid = msg_topic.split("&")
        cid = cid[1].split("/")
        type = int(cid[0])
        id = int(cid[1])

        for client in variables.device_data:
            if client["info"]["id"] == id and client["info"]["type"] == type:
                if data["data"] is not None:
                    client["in"] = data["data"]
                else:
                    client["ip"] = data["ip"]
                break

    def run(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        while 1:
            try:
                # self.client.connect("127.0.0.1", 1883, 60)
                # self.client.connect("192.168.1.150", 1883, 60)
                self.client.connect("192.168.25.1", 1883, 60)
            except:
                print("Unable to connect")
                time.sleep(5)
                continue

            # Blocking call that processes network traffic, dispatches callbacks and
            # handles reconnecting.
            # Other loop*() functions are available that give a threaded interface and a
            # manual interface.
            # self.client.loop_forever()

            test_counter = 0

            rc = 0
            while rc == 0:
                rc = self.client.loop()
                t1 = time.time()

                # test
                if t1 - self.t >= 0.1:
                    self.t = t1
                    # self.client.publish("data/temp", 25)
                    self.client.publish("cmd/node/&101/4", test_counter)

                    test_counter += 1
                    if test_counter > 1000:
                        test_counter = 0


        print("EXIT MQTT")

        return rc

