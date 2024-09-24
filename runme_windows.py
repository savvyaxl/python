#!/usr/bin/python
# python 3.9

import random
import time
import socket
import os
import re
import yaml
from subprocess import run as Run
from paho.mqtt import client as mqtt_client

sysName = socket.gethostname().split(".")[0]

with open('./config_windows.yaml', 'r') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)

# Access the YAML data
print(data)

my_agent='host'

broker = data[my_agent]['broker']
port = data[my_agent]['port']
username = data[my_agent]['username']
password = data[my_agent]['password']

# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
topic_state = ''.join(["homeassistant/sensor/",sysName,"/state"])

for x in [0]:
    data["report"][x]['name_'] = data["report"][x]['name'] + sysName
    data["report"][x]['topic_'] = data["report"][x]['name_'].lower().replace(" ", "_")
    data["report"][x]['topic_config_'] = ''.join(['homeassistant/sensor/',sysName,'/',data["report"][x]['topic_'],'/config'])
    data["report"][x]['config_'] = ''.join(["{\"name\":\"",data["report"][x]['name_'],"\",\"state_topic\": \"",topic_state,"\",\"unit_of_measurement\":\"",data["report"][x]['unit_of_measurement'],"\",\"value_template\":\"{{value_json.",data["report"][x]['value_template'],"}}\"}"])

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1,client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def getMem ():
   
    srt = "{"

    for x in [0]:
        srt = srt + "\""+data["report"][x]['value']+"\":" + "\"" + Run(data['report'][x]['command'], capture_output=True, shell=True).stdout.splitlines()[x].decode('utf-8')  + "\","
    
    srt = srt + "}"
    return srt


def configure(client):
    for x in [0]:
        result = client.publish(data["report"][x]['topic_config_'], data["report"][x]['config_'] )
        time.sleep(1)
 
def publish(client):
    msg_count = 1
    configure(client)
    
    while True:
        msg = getMem ()
        result = client.publish(topic_state, msg)
        msg_count += 1
        if msg_count > 60:
            configure(client)
            msg_count = 1
        time.sleep(60)


def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)


if __name__ == '__main__':
    run()
