import os
import json
from dotenv import load_dotenv

import paho.mqtt.client as paho
from paho import mqtt
import time
import random #used to "decide" moves for the bots

isGameValid = True
lobby_name  = "Challenge3Lobby"

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
    print("Player in on_message")
    global isGameValid #python treats isGameValid in function as local unless you add Gloabl
    global lobby_name
    print("message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    #if (msg.topic == f'games/{lobby_name}/lobby' and str(msg.payload) == "Game Over: All coins have been collected"):
    #i don't think this behaves properl, never hits.
    if (msg.topic == f'games/{lobby_name}/lobby' and str(msg.payload) == "Game Over: All coins have been collected"):
        isGameValid = False
    
    #end the loop if Game Over detected, this one does seem to work
    if isinstance(msg.payload, bytes) and "Game Over" in msg.payload.decode():
        print("Game is Over, Lobby no longer exists")
        isGameValid = False
    

def moveGen():
    moveNum = random.randrange(1,5) #returns a number betwen 1(included) and 5(not included). want 1-4 so this works.
    if moveNum == 1:
        return "UP"
    if moveNum == 2:
        return "LEFT"
    if moveNum == 3:
        return "DOWN"
    if moveNum == 4:
        return "RIGHT"

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
    client.loop_start() #NEED loop_start() after connect, loop_forever() doesn't behave how we want it.

    client.on_subscribe = on_subscribe # Can comment out to not print when subscribing to new topics
    client.on_message = on_message
    #client.on_publish = on_publish # Can comment out to not print when publishing to topics

    #player_name = input("Input your name: ") #challenge 2
    #lobby_name  = "Challenge3Lobby"
    #4 players, 2 teams
    teamRock = "TeamRock"
    teamRock_playerA    = "ABBY"
    teamRock_playerB    = "YBBA"
    teamPaper = "TeamPaper"
    teamPaper_playerC   = "SUHAYB"
    teamPaper_playerD    = "BYAHUS"


    client.subscribe(f"games/{lobby_name}/lobby")
    client.subscribe(f'games/{lobby_name}/+/game_state')
    client.subscribe(f'games/{lobby_name}/scores')

    client.publish("new_game", json.dumps({'lobby_name'  : lobby_name,
                                           'team_name'   : teamRock,
                                           'player_name' : teamRock_playerA}))
    
    client.publish("new_game", json.dumps({'lobby_name'  : lobby_name,
                                           'team_name'   : teamRock,
                                           'player_name' : teamRock_playerB}))
    
    client.publish("new_game", json.dumps({'lobby_name'  : lobby_name,
                                           'team_name'   : teamPaper,
                                           'player_name' : teamPaper_playerC}))
    
    client.publish("new_game", json.dumps({'lobby_name'  : lobby_name,
                                           'team_name'   : teamPaper,
                                           'player_name' : teamPaper_playerD}))

    client.publish(f"games/{lobby_name}/start", "START") #start the games, now that all 4 players have been added
    
    time.sleep(1) # Wait a second to resolve game start
    while(isGameValid):
        player_move = moveGen() #all move same direction for now
        client.publish(f"games/{lobby_name}/{teamRock_playerA}/move", str(player_move))
        time.sleep(.1) # Wait a second for message delivery integrity, this may be able to be faster without issue tbh

        client.publish(f"games/{lobby_name}/{teamRock_playerB}/move", str(player_move))
        time.sleep(.1) # Wait a second for message delivery integrity

        client.publish(f"games/{lobby_name}/{teamPaper_playerC}/move", str(player_move))
        time.sleep(.1) # Wait a second for message delivery integrity

        client.publish(f"games/{lobby_name}/{teamPaper_playerD}/move", str(player_move))
        time.sleep(.1) # Wait a second for message delivery integrity

        


    if (isGameValid == False): client.publish(f"games/{lobby_name}/start", "STOP") # Stop the game. once winning condition met

    client.loop_stop() #why was this loop_start()? perhaps required. Changed to loop_stop() -suhayb 4/12 5pm 