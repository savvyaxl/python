#!/usr/bin/python
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
name_sy = "CPU SY " + sysName
name_ni = "CPU NI " + sysName
name_id = "CPU ID " + sysName
name_wa = "CPU WA " + sysName
name_hi = "CPU HI " + sysName
name_si = "CPU SI " + sysName
name_st = "CPU ST " + sysName

name_total_topic = name_total.lower().replace(" ", "_")
name_used_topic = name_used.lower().replace(" ", "_")
name_free_topic = name_free.lower().replace(" ", "_")

name_us_topic = name_us.lower().replace(" ", "_")
name_sy_topic = name_sy.lower().replace(" ", "_")
name_ni_topic = name_ni.lower().replace(" ", "_")
name_id_topic = name_id.lower().replace(" ", "_")
name_wa_topic = name_wa.lower().replace(" ", "_")
name_hi_topic = name_hi.lower().replace(" ", "_")
name_si_topic = name_si.lower().replace(" ", "_")
name_st_topic = name_st.lower().replace(" ", "_")

topic_config_total = ''.join(['homeassistant/sensor/',sysName,'/',name_total_topic,'/config'])
topic_config_used = ''.join(['homeassistant/sensor/',sysName,'/',name_used_topic,'/config'])
topic_config_free = ''.join(['homeassistant/sensor/',sysName,'/',name_free_topic,'/config'])

topic_config_us = ''.join(['homeassistant/sensor/',sysName,'/',name_us_topic,'/config'])
topic_config_sy = ''.join(['homeassistant/sensor/',sysName,'/',name_sy_topic,'/config'])
topic_config_ni = ''.join(['homeassistant/sensor/',sysName,'/',name_ni_topic,'/config'])
topic_config_id = ''.join(['homeassistant/sensor/',sysName,'/',name_id_topic,'/config'])
topic_config_wa = ''.join(['homeassistant/sensor/',sysName,'/',name_wa_topic,'/config'])
topic_config_hi = ''.join(['homeassistant/sensor/',sysName,'/',name_hi_topic,'/config'])
topic_config_si = ''.join(['homeassistant/sensor/',sysName,'/',name_si_topic,'/config'])
topic_config_st = ''.join(['homeassistant/sensor/',sysName,'/',name_st_topic,'/config'])

config_total = ''.join(["{\"name\":\"",name_total,"\",\"state_topic\": \"",topic_state,"\",\"unit_of_measurement\":\"GB\",\"value_template\":\"{{value_json.total}}\"}"])
config_used = ''.join(["{\"name\":\"",name_used,"\",\"state_topic\": \"",topic_state,"\",\"unit_of_measurement\":\"%\",\"value_template\":\"{{(100*value_json.used/value_json.total)|round|int}}\"}"])
config_free = ''.join(["{\"name\":\"",name_free,"\",\"state_topic\": \"",topic_state,"\",\"unit_of_measurement\":\"%\",\"value_template\":\"{{(100*value_json.free/value_json.total)|round|int}}\"}"])

config_us = ''.join(["{\"name\":\"",name_us,"\",\"state_topic\": \"",topic_state,"\",\"unit_of_measurement\":\"%\",\"value_template\":\"{{value_json.us}}\"}"])
config_sy = ''.join(["{\"name\":\"",name_sy,"\",\"state_topic\": \"",topic_state,"\",\"unit_of_measurement\":\"%\",\"value_template\":\"{{value_json.sy}}\"}"])
config_ni = ''.join(["{\"name\":\"",name_ni,"\",\"state_topic\": \"",topic_state,"\",\"unit_of_measurement\":\"%\",\"value_template\":\"{{value_json.ni}}\"}"])
config_id = ''.join(["{\"name\":\"",name_id,"\",\"state_topic\": \"",topic_state,"\",\"unit_of_measurement\":\"%\",\"value_template\":\"{{value_json.id}}\"}"])
config_wa = ''.join(["{\"name\":\"",name_wa,"\",\"state_topic\": \"",topic_state,"\",\"unit_of_measurement\":\"%\",\"value_template\":\"{{value_json.wa}}\"}"])
config_hi = ''.join(["{\"name\":\"",name_hi,"\",\"state_topic\": \"",topic_state,"\",\"unit_of_measurement\":\"%\",\"value_template\":\"{{value_json.hi}}\"}"])
config_si = ''.join(["{\"name\":\"",name_si,"\",\"state_topic\": \"",topic_state,"\",\"unit_of_measurement\":\"%\",\"value_template\":\"{{value_json.si}}\"}"])
config_st = ''.join(["{\"name\":\"",name_st,"\",\"state_topic\": \"",topic_state,"\",\"unit_of_measurement\":\"%\",\"value_template\":\"{{value_json.st}}\"}"])

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
    cmd2 = 'top -bn1 | grep \'%Cpu\' | sed \'s/^%Cpu(s)://\''
    data = Run(cmd, capture_output=True, shell=True)
    data2 = Run(cmd2, capture_output=True, shell=True)
    #print(f"Send `{data2}`")
    #return data.stdout.splitlines()[1].decode('utf-8').split("\t")[1]
    patt = re.compile("[^\s]+")
    patt2 = re.compile("[^\s]+")
    total_ = patt.findall(data.stdout.splitlines()[1].decode('utf-8'))[1]
    used_ = patt.findall(data.stdout.splitlines()[1].decode('utf-8'))[2]
    free_ = patt.findall(data.stdout.splitlines()[1].decode('utf-8'))[3]

    tmp_string = data2.stdout.splitlines()[0].decode('utf-8')
    
    us_ = tmp_string[0:5]
    sy_ = tmp_string[9:14]
    ni_ = tmp_string[18:23]
    id_ = tmp_string[27:32]
    wa_ = tmp_string[36:41]
    hi_ = tmp_string[45:50]
    si_ = tmp_string[54:59]
    st_ = tmp_string[63:68]
    # return ''.join(["{\"total\":",total_,",\"used\":",used_,",\"free\":",free_,",\"us\":",us_,",\"sy\":",sy_,",\"ni\":",ni_,",\"id\":",id_,",\"wa\":",wa_,",\"hi\":",hi_,",\"si\":",si_,",\"st\":",st_,"}"])
    srt = "{"
    srt = srt + "\"total\":" + "\"" + total_  + "\""
    srt = srt + ",\"used\":" + "\"" + used_  + "\""
    srt = srt + ",\"free_\":" + "\"" + used_  + "\""
    srt = srt + ",\"us_\":" + "\"" + used_  + "\""
    srt = srt + ",\"sy_\":" + "\"" + used_  + "\""
    srt = srt + ",\"ni_\":" + "\"" + used_  + "\""
    srt = srt + ",\"id_\":" + "\"" + used_  + "\""
    srt = srt + ",\"wa_\":" + "\"" + used_  + "\""
    srt = srt + ",\"hi_\":" + "\"" + used_  + "\""
    srt = srt + ",\"si_\":" + "\"" + used_  + "\""
    srt = srt + ",\"st_\":" + "\"" + used_  + "\""
    srt = srt + "}"
    return srt


def configure(client):
    result = client.publish(topic_config_total, config_total)
    time.sleep(1)
    result = client.publish(topic_config_used, config_used)
    time.sleep(1)
    result = client.publish(topic_config_free, config_free)
    time.sleep(1)
    result = client.publish(topic_config_us, config_us)
    time.sleep(1)
    result = client.publish(topic_config_sy, config_sy)
    time.sleep(1)
    result = client.publish(topic_config_ni, config_ni)
    time.sleep(1)
    result = client.publish(topic_config_id, config_id)
    time.sleep(1)
    result = client.publish(topic_config_wa, config_wa)
    time.sleep(1)
    result = client.publish(topic_config_hi, config_hi)
    time.sleep(1)
    result = client.publish(topic_config_si, config_si)
    time.sleep(1)
    result = client.publish(topic_config_st, config_st)
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

