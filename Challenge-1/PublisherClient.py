#
# Copyright 2021 HiveMQ GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import time
import random
import paho.mqtt.client as paho
from paho import mqtt
from dotenv import load_dotenv

# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    """
        Prints the result of the connection with a reasoncode to stdout ( used as callback for connect )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param flags: these are response flags sent by the broker
        :param rc: stands for reasonCode, which is a code for the connection result
        :param properties: can be used in MQTTv5, but is optional
    """
    print("CONNACK received with code %s." % rc)

# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    """
        Prints mid to stdout to reassure a successful publish ( used as callback for publish )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param properties: can be used in MQTTv5, but is optional
    """
    print("mid: " + str(mid))

# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    """
        Prints a reassurance for successfully subscribing
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param granted_qos: this is the qos that you declare when subscribing, use the same one for publishing
        :param properties: can be used in MQTTv5, but is optional
    """
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    """
        Prints a mqtt message to stdout ( used as callback for subscribe )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param msg: the message with topic and payload
    """
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

load_dotenv(dotenv_path='./credentials.env')
    
broker_address = os.environ.get('BROKER_ADDRESS')
broker_port = int(os.environ.get('BROKER_PORT'))
username = os.environ.get('USER_NAME')
password = os.environ.get('PASSWORD')

# using MQTT version 5 here, for 3.1.1: MQTTv311, 3.1: MQTTv31
# userdata is user defined data of any type, updated by user_data_set()
# client_id is the given name of the client
client0 = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="Client0", userdata=None, protocol=paho.MQTTv5)
client0.on_connect = on_connect
client0.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS) # enable TLS for secure connection
client0.username_pw_set(username, password) # set username and password
client0.connect(broker_address, broker_port) # connect to HiveMQ Cloud on port 8883 (default for MQTT)

client1 = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="Client1", userdata=None, protocol=paho.MQTTv5)
client1.on_connect = on_connect
client1.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS) # enable TLS for secure connection
client1.username_pw_set(username, password) # set username and password
client1.connect(broker_address, broker_port) # connect to HiveMQ Cloud on port 8883 (default for MQTT)

# setting callbacks, use separate functions like above for better visibility
client0.on_subscribe = on_subscribe
client0.on_publish = on_publish

client1.on_subscribe = on_subscribe
client1.on_publish = on_publish

client0.loop_start()
client1.loop_start()

while True:
    rand0 = str(random.randint(-1000,1000)) # Generate random integer between -1000 and 1000
    client0.publish("encyclopedia/publisher0", payload=rand0, qos=1)

    rand1 = str(random.randint(-1000,1000)) # Generate random integer between -1000 and 1000
    client1.publish("encyclopedia/publisher1", payload=rand1, qos=1)

    time.sleep(3) # 3 second delay

client0.loop_stop()
client1.loop_stop()