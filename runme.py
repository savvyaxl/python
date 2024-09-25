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

with open('/home/alex/python/config.yaml', 'r') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)

# Access the YAML data
print(data)

my_agent='host'
is_host=1
timing = data['timing']
advertize = data['advertize']
do_publish = True

broker = data[my_agent]['broker']
port = data[my_agent]['port']
username = data[my_agent]['username']
password = data[my_agent]['password']

# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
topic_state = ''.join(["homeassistant/sensor/",sysName,"/state"])

# Set the names and the config queues
for x in range(len(data["report"])):
    if data["report"][x]['enabled']:
        data["report"][x]['name_'] = data["report"][x]['name'] + sysName
        data["report"][x]['topic_'] = data["report"][x]['name_'].lower().replace(" ", "_")
        data["report"][x]['topic_config_'] = ''.join(['homeassistant/sensor/',sysName,'/',data["report"][x]['topic_'],'/config'])
        data["report"][x]['config_'] = ''.join(["{\"name\":\"",data["report"][x]['name_'],"\",\"state_topic\": \"",topic_state,"\",\"unit_of_measurement\":\"",data["report"][x]['unit_of_measurement'],"\",\"value_template\":\"{{",data["report"][x]['value_template'],"}}\"}"])

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
    for x in range(len(data["report"])):
        if data["report"][x]['enabled']:
            if data["report"][x]['name'] == 'free':
                print("bob")
                


    cmd = 'free'
    data = Run(cmd, capture_output=True, shell=True)
    cmd2 = 'top -bn1 | grep \'%Cpu\' | sed \'s/^%Cpu(s)://\''
    data2 = Run(cmd2, capture_output=True, shell=True)
    if is_host:
        cmd3 = 'cat /sys/class/thermal/thermal_zone0/temp | sed \'s/\(.\)..$//\''
        data3 = Run(cmd3, capture_output=True, shell=True)

    patt = re.compile("[^\s]+")
    total_ = patt.findall(data.stdout.splitlines()[1].decode('utf-8'))[1]
    free_ = patt.findall(data.stdout.splitlines()[1].decode('utf-8'))[3]
    tmp_string = data2.stdout.splitlines()[0].decode('utf-8')
    tmp_string3 = data3.stdout.splitlines()[0].decode('utf-8')
    id_ = tmp_string[27:32]
    si_ = tmp_string[54:59]
    st_ = tmp_string[63:68]
    if is_host:
        wa_ = tmp_string[36:41]
        hi_ = tmp_string[45:50]
        temp_ = tmp_string3[0:2]
    
    srt = "{"

    # srt = srt + ",\"used\":" + "\"" + used_  + "\""
    # srt = srt + ",\"us\":" + "\"" + us_  + "\""
    # srt = srt + ",\"sy\":" + "\"" + sy_  + "\""
    # srt = srt + ",\"ni\":" + "\"" + ni_  + "\""
    srt = srt + "\"id\":" + "\"" + id_  + "\""
    srt = srt + ",\"total\":" + "\"" + total_  + "\""
    srt = srt + ",\"free\":" + "\"" + free_  + "\""
    srt = srt + ",\"si\":" + "\"" + si_  + "\""
    srt = srt + ",\"st\":" + "\"" + st_  + "\""
    if is_host:
        srt = srt + ",\"wa\":" + "\"" + wa_  + "\""
        srt = srt + ",\"hi\":" + "\"" + hi_  + "\""
        srt = srt + ",\"temp\":" + "\"" + temp_  + "\""
    srt = srt + "}"
    return srt


def configure(client):
    for x in range(len(data["report"])):
        if data["report"][x]['enabled']:
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


