# python 3.9

import random
import time
import socket
import os
import re
from subprocess import run as Run
from paho.mqtt import client as mqtt_client

sysName = socket.gethostname().split(".")[0]

broker = '192.168.0.54'
port = 1883
topic_state = ''.join(["homeassistant/sensor/",sysName,"/state"])
name_total = "Memory Total " + sysName
name_used = "Memory Used " + sysName
name_free = "Memory Free " + sysName
name_us = "CPU US " + sysName
name_total_topic = name_total.lower().replace(" ", "_")
name_used_topic = name_used.lower().replace(" ", "_")
name_free_topic = name_free.lower().replace(" ", "_")
name_us_topic = name_us.lower().replace(" ", "_")
topic_config_total = ''.join(['homeassistant/sensor/',sysName,'/',name_total_topic,'/config'])
topic_config_used = ''.join(['homeassistant/sensor/',sysName,'/',name_used_topic,'/config'])
topic_config_free = ''.join(['homeassistant/sensor/',sysName,'/',name_free_topic,'/config'])
topic_config_us = ''.join(['homeassistant/sensor/',sysName,'/',name_us_topic,'/config'])
config_total = ''.join(["{\"name\":\"",name_total,"\",\"state_topic\": \"",topic_state,"\",\"unit_of_measurement\":\"GB\",\"value_template\":\"{{value_json.total}}\"}"])
config_used = ''.join(["{\"name\":\"",name_used,"\",\"state_topic\": \"",topic_state,"\",\"unit_of_measurement\":\"%\",\"value_template\":\"{{(100*value_json.used/value_json.total)|round|int}}\"}"])
config_free = ''.join(["{\"name\":\"",name_free,"\",\"state_topic\": \"",topic_state,"\",\"unit_of_measurement\":\"%\",\"value_template\":\"{{(100*value_json.free/value_json.total)|round|int}}\"}"])
config_us = ''.join(["{\"name\":\"",name_us,"\",\"state_topic\": \"",topic_state,"\",\"unit_of_measurement\":\"%\",\"value_template\":\"{{(value_json.us}}\"}"])
#{"device_class": "illuminance", "name": "Green",               "state_topic": "homeassistant/sensor/tcs_8caab51b443e/state", "unit_of_measurement": "lx", "value_template": "{{ value_json.green8caab51b443e}}" }
#{"device_class": "None",        "name": "Memory_Free_ansible", "state_topic": "homeassistant/sensor/ansible/state",          "unit_of_measurement": "%",  "value_template": "{{value_json.free}}"}
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'emqx'
password = 'public'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def getMem ():
    cmd = 'free'
    cmd2 = 'top -n1 | grep \'%Cpu\' | sed \'s/^%Cpu(s)://\''
    data = Run(cmd, capture_output=True, shell=True)
    data2 = Run(cmd2, capture_output=True, shell=True)
    #return data.stdout.splitlines()[1].decode('utf-8').split("\t")[1]
    patt = re.compile("[^\s]+")
    patt2 = re.compile(",")
    total_ = patt.findall(data.stdout.splitlines()[1].decode('utf-8'))[1]
    used_ = patt.findall(data.stdout.splitlines()[1].decode('utf-8'))[2]
    free_ = patt.findall(data.stdout.splitlines()[1].decode('utf-8'))[3]
    us_ = patt.findall(data2.stdout.splitlines()[1].decode('utf-8'))[1]
    sy_ = patt.findall(data2.stdout.splitlines()[1].decode('utf-8'))[2]
    ni_ = patt.findall(data2.stdout.splitlines()[1].decode('utf-8'))[3]
    id_ = patt.findall(data2.stdout.splitlines()[1].decode('utf-8'))[4]
    wa_ = patt.findall(data2.stdout.splitlines()[1].decode('utf-8'))[5]
    hi_ = patt.findall(data2.stdout.splitlines()[1].decode('utf-8'))[6]
    si_ = patt.findall(data2.stdout.splitlines()[1].decode('utf-8'))[7]
    st_ = patt.findall(data2.stdout.splitlines()[1].decode('utf-8'))[8]
    return ''.join(["{\"total\":",total_,",\"used\":",used_,",\"free\":",free_,",\"us\":",us_,",\"sy\":",sy_,",\"ni\":",ni_,",\"id\":",id_,",\"wa\":",wa_,",\"hi\":",hi_,",\"si\":",si_,",\"st\":",st_,"}"])

def publish(client):
    #msg_count = 0
    result = client.publish(topic_config_total, config_total)
    time.sleep(1)
    result = client.publish(topic_config_used, config_used)
    time.sleep(1)
    result = client.publish(topic_config_free, config_free)
    while True:
        time.sleep(60)
        msg = getMem ()
        result = client.publish(topic_state, msg)
        # result: [0, 1]
        #status = result[0]
        #if status == 0:
        #    print(f"Send `{msg}` to topic `{topic}`")
        #else:
        #    print(f"Failed to send message to topic {topic}")
        #msg_count += 1


def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)


if __name__ == '__main__':
    run()

