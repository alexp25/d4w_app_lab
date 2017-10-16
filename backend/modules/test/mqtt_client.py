import threading
from threading import Thread

import time

import paho.mqtt.client as mqtt


class MQTTClient(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._stopEvent = threading.Event()
        self.client = None
        self.t = time.time()

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("$SYS/#")

        client.subscribe("data/temp")
        client.subscribe("outTopic")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        # print(msg.topic+" "+str(msg.payload))

        if msg.topic == "data/temp":
            print("temp: " + msg.payload)
        elif msg.topic == "outTopic":
            print("outTopic: " + msg.payload)

    def run(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect("127.0.0.1", 1883, 60)

        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        # self.client.loop_forever()

        rc = 0
        while rc == 0:
            rc = self.client.loop()
            t1 = time.time()

            # test
            if t1 - self.t >= 1:
                self.t = t1
                self.client.publish("data/temp", 25)
                self.client.publish("inTopic", 100)

        return rc

        print("EXIT MQTT")

