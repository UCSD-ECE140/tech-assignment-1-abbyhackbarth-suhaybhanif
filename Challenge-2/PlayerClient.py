import os
import json
from dotenv import load_dotenv

import paho.mqtt.client as paho
from paho import mqtt
import time

isGameValid = True

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
    if msg.topic == "games/{lobby_name}/+/game_state": isGameValid = msg.payload

    print("message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

if __name__ == '__main__':
    load_dotenv(dotenv_path='./credentials.env')
    
    broker_address = os.environ.get('BROKER_ADDRESS')
    broker_port = int(os.environ.get('BROKER_PORT'))
    username = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')

    client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="Player1", userdata=None, protocol=paho.MQTTv5)
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS) # enable TLS for secure connection
    client.username_pw_set(username, password)  # set username and password
    client.connect(broker_address, broker_port) # connect to HiveMQ Cloud on port 8883 (default for MQTT)

    client.on_subscribe = on_subscribe # Can comment out to not print when subscribing to new topics
    client.on_message = on_message
    client.on_publish = on_publish # Can comment out to not print when publishing to topics

    lobby_name   = input("Input a lobby name: ")
    # team_name_1   = input("Input Team 1 name: ")
    # player_1a     = input("Input team " + team_name_1 + "'s player 1 name: ")
    # player_1b     = input("Input team " + team_name_1 + "'s player 2 name: ")
    # team_name_2   = input("Input Team 2 name: ")
    # player_2a     = input("Input team " + team_name_2 + "'s player 1 name: ")
    # player_2b     = input("Input team " + team_name_2 + "'s player 2 name: ")

    client.subscribe(f"games/{lobby_name}/lobby")
    client.subscribe(f'games/{lobby_name}/+/game_state')
    client.subscribe(f'games/{lobby_name}/scores')

    # Two teams of two

    client.publish("new_game", json.dumps({'lobby_name'  : lobby_name,
                                           'team_name'   : 'TeamA',
                                           'player_name' : 'a'}))
                                           
    client.publish("new_game", json.dumps({'lobby_name'  : lobby_name,
                                           'team_name'   : 'TeamA',
                                           'player_name' : 'b'}))

    client.publish("new_game", json.dumps({'lobby_name'  : lobby_name,
                                           'team_name'   : 'TeamB',
                                           'player_name' : 'aa'}))
    
    client.publish("new_game", json.dumps({'lobby_name'  : lobby_name,
                                           'team_name'   : 'TeamB',
                                           'player_name' : 'bb'}))

    time.sleep(1) # Wait a second to resolve game start

    client.publish(f"games/{lobby_name}/start", "START")

    i = 1 # Initalize variable that will help us cycle through each player

    while(isGameValid): # currently, an infinite loop TODO: add function to check if game is still valid on GameClient end
        if i > 4: i = 1 # reset to the first player when player 4 is finished
        if i == 1: current_player = 'a' # Set which player we are currently on based on counter
        if i == 2: current_player = 'b'
        if i == 3: current_player = 'aa'
        if i == 4: current_player = 'bb'

        player_move = input(current_player + ", make your move: ") # take in move
        client.publish("games/{lobby_name}/{current_player}/move", player_move) # publish this move to desired player

        i = i + 1 # move to next player

    client.publish("games/{lobby_name}/start", "STOP") # Stop the game. Currently, will never reach this stage

    client.loop_forever()