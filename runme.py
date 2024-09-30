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

with open('./config.yaml', 'r') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)

# Access the YAML data
#print(data)

my_agent='host'
timing = data['timing']
advertize = data['advertize']

broker = data[my_agent]['broker']
port = data[my_agent]['port']
username = data[my_agent]['username']
password = data[my_agent]['password']

# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
topic_state = ''.join(["homeassistant/sensor/",sysName,"/state"])

# Set the names and the config queues
for x in range(len(data["report"])):
    data["report"][x]['name_'] = sysName + ' ' + data["report"][x]['name']
    data["report"][x]['topic_'] = data["report"][x]['name_'].lower().replace(" ", "_")
    data["report"][x]['topic_config_'] = ''.join(['homeassistant/sensor/',sysName,'/',data["report"][x]['topic_'],'/config'])
    data["report"][x]['config_'] = ''.join(["{\"name\":\"",data["report"][x]['name_'],"\",\"state_topic\": \"",topic_state,"\",\"unit_of_measurement\":\"",data["report"][x]['unit_of_measurement'],"\",\"value_template\":\"{{",data["report"][x]['value_template'],"}}\"}"])

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    client = mqtt_client.Client(client_id)  #mqtt_client.CallbackAPIVersion.VERSION1,
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def parse (rx,data_,no1,no2):
    patt = re.compile(rx)
    return patt.findall(data_.stdout.splitlines()[no1].decode('utf-8'))[no2]

def parse_top (data_, splitlines_):
    return data_.stdout.splitlines()[0].decode('utf-8')[splitlines_[0]:splitlines_[1]]

def getMem (data):
    for x in range(len(data["report"])):
        if data["report"][x]['command'] == 'free':
            for y in range(len(data["commands"])):
                if data["commands"][y]['name'] == data["report"][x]['command']:
                    if not data["commands"][y]['ranit']:
                        data["commands"][y]['result'] = Run(data["commands"][y]['command'], capture_output=True, shell=True)
                    data["report"][x]['result'] = parse (data["report"][x]['rx'],data["commands"][y]['result'],data["report"][x]['no1'],data["report"][x]['no2'])
                    data["commands"][y]['ranit'] = True
        if data["report"][x]['command'] == 'top':
            for y in range(len(data["commands"])):
                if data["commands"][y]['name'] == data["report"][x]['command']:
                    if not data["commands"][y]['ranit']:
                        data["commands"][y]['result'] = Run(data["commands"][y]['command'], capture_output=True, shell=True)
                    data["report"][x]['result'] = parse_top (data["commands"][y]['result'],data["report"][x]['splitlines_'])
                    data["commands"][y]['ranit'] = True        
    srt = "{"
    for x in range(len(data["report"])):
        srt = srt + "\""+data["report"][x]['value']+"\":" + data["report"][x]['result']
        
        if x < len(data["report"])-1:
            srt = srt + ","
    srt = srt + "}"
    return srt

def configure(client):
    for x in range(len(data["report"])):
        result = client.publish(data["report"][x]['topic_config_'], data["report"][x]['config_'] )
        time.sleep(1)
 
def publish(client):
    msg_count = 1
    configure(client)
    
    while True:
        msg = getMem (data)
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


