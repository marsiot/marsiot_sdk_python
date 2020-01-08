# -*- coding: utf-8 -*-

import sys
if sys.version >'3':
    import configparser
else:
    import ConfigParser

import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import datetime
import platform
import time
import json
import os

def get_hardware_id():
    serial = '';

    if os.path.isfile("/sbin/ifconfig"):
        macaddr = os.popen('LANG=C /sbin/ifconfig eth0 2>&1 |awk \'/HWaddr/{print $5}\'').read()
        if len(macaddr) > 0:
            serial += macaddr.strip().replace(':','')
            return serial

    if os.path.isfile("/sbin/ifconfig"):
        macaddr = os.popen('LANG=C /sbin/ifconfig wlan0 2>&1 |awk \'/HWaddr/{print $5}\'').read()
        if len(macaddr) > 0:
            serial += macaddr.strip().replace(':','')
            return serial

    if os.path.isfile("/sbin/ifconfig"):
        macaddr = os.popen('LANG=C /sbin/ifconfig eth0 2>&1 |awk \'/ether/{print $2}\'').read()
        if len(macaddr) > 0:
            serial += macaddr.strip().replace(':','')
            return serial

    if os.path.isfile("/sbin/ifconfig"):
        macaddr = os.popen('LANG=C /sbin/ifconfig wlan0 2>&1 |awk \'/ether/{print $2}\'').read()
        if len(macaddr) > 0:
            serial += macaddr.strip().replace(':','')
            return serial

    if os.path.isfile("/proc/cpuinfo"):
        with open('/proc/cpuinfo') as f:
            for line in f:
                line.strip()
                if line.rstrip('\n').startswith('Serial'):
                    serial += line.rstrip('\n').split(':')[1].strip()
                    return serial

    if os.path.isfile("/usr/sbin/ifconfig"):
        macaddr = os.popen('LANG=C /usr/sbin/ifconfig eth0 |awk \'/ether/{print $2}\'').read()
        if len(macaddr) > 0:
            serial += macaddr.strip().replace(':','')
            return serial

    if os.path.isfile("/sbin/ifconfig"):
        macaddr = os.popen('LANG=C /sbin/ifconfig eth0 |awk \'/ether/{print $2}\'').read()
        if len(macaddr) > 0:
            serial += macaddr.strip().replace(':','')
            return serial

    if len(serial) > 0:
        return serial

    return serial

def on_connect(client, userdata, flags, rc):
    marsiot = userdata
    print("\nregister to " + marsiot.site_token + " ... "),

    my_request = {}
    my_request_body = {}
    my_request_metadata = {}

    my_request['type'] = 'RegisterDevice'
    my_request['hardwareId'] = marsiot.hardware_id

    my_request_body['siteToken'] = marsiot.site_token
    my_request_body['specificationToken'] = marsiot.specification_token
    my_request_body['hardwareId'] = marsiot.hardware_id

    my_request_metadata['model-name'] = marsiot.module_name
    my_request_metadata['model-description'] = marsiot.module_description

    my_request_body['metadata'] = my_request_metadata
    my_request['request'] = my_request_body

    my_request_string = json.dumps(my_request)
    publish.single("marsiot/input/json", my_request_string, hostname=marsiot.host_name)

def on_message_system(client, userdata, msg):
    marsiot = userdata

    if sys.version >'3':
        my_message = json.loads(bytes.decode(msg.payload))
    else:
        my_message = json.loads(msg.payload)

    if (my_message['systemCommand']['type'] == 'RegistrationAck'):
        print("\nok")
        marsiot.send_message("message", "regster ok")

def on_message_commands(client, userdata, msg):
    marsiot = userdata

    if sys.version >'3':
        my_message = json.loads(bytes.decode(msg.payload))
    else:
        my_message = json.loads(msg.payload)

    cmd_name = my_message['command']['command']['name']
    cmd_parameters = my_message['command']['command']['parameters']
    cmd_parameter_values = my_message['command']['invocation']['parameterValues']
    for parameter in cmd_parameters:
        parameter['value'] = cmd_parameter_values[parameter['name']]

    try:
        f = getattr(marsiot.default_command_processor, cmd_name)
    except:
        try:
            f = getattr(marsiot.my_command_processor, cmd_name)
        except:
            print("\nerror! pls define '" + cmd_name + "' in my_command.py")
            return

    print("\n")
    print(cmd_name)
    for k,v in cmd_parameter_values.items():
        print("%s:%s"%(k,v))
    print("\n")
    f(cmd_parameter_values) 

class marsiot(object):

    def __init__(self, fix_path):
        self.VERSION = 'v1.0.6'

        self.fix_path = ''
        if len(fix_path) > 0: 
            self.fix_path = fix_path + '/'

        self.ini_file = 'marsiot.ini'
        self.site_token = ''
        self.hardware_id = ''
        self.model_name = 'test'
        self.model_description = 'test'

        if sys.version >'3':
            cf = configparser.ConfigParser()
        else:
            cf = ConfigParser.ConfigParser()

        cf.readfp(open(self.fix_path + self.ini_file))
        self.site_token = cf.get("config","site_token")
        self.host_name = cf.get("config","hostname")
        self.specification_token = cf.get("config","specification_token")

        default_command_class_class = __import__('default_command')

        default_command_class = getattr(default_command_class_class, 'default_command')
        default_command = default_command_class(self)
        self.default_command_processor = default_command

        self.mqtt_client = mqtt.Client(userdata=self)

    def __del__(self):
        if hasattr(self, 'mqtt_client'):
            self.mqtt_client.disconnect()

    def version(self):
        return self.VERSION

    def bind_command_processor(self, command_processor):
        command_class_class = __import__(command_processor)
        command_class = getattr(command_class_class, command_processor)
        command = command_class(self)
        self.my_command_processor = command

    def bind_schedule_processor(self, schedule_processor):
        schedule_class_class = __import__(schedule_processor)
        schedule_class = getattr(schedule_class_class, schedule_processor)
        schedule = schedule_class(self)
        self.my_schedule_processor = schedule

    def set_model_name(self, name):
        self.module_name = name

    def set_model_description(self, description):
        self.module_description = description

    def connect(self):
        self.hardware_id = get_hardware_id()
        if self.hardware_id == '':
            print("\nerror! hardwareId failed")
            return False

        print("\n(hardwareId:" + self.hardware_id + ")\n")

        self.mqtt_client.message_callback_add("marsiot/commands/" + self.hardware_id, on_message_commands)
        self.mqtt_client.message_callback_add("marsiot/system/" + self.hardware_id, on_message_system)
        self.mqtt_client.on_connect = on_connect
        
        print("\nconnect to " + self.host_name + " ..."),
        self.mqtt_client.connect(self.host_name, 1883, 60)
        print("\nok")

        self.mqtt_client.subscribe("marsiot/commands/" + self.hardware_id, 0)
        self.mqtt_client.subscribe("marsiot/system/" + self.hardware_id, 0)

        return True

    def loop_wait_message(self):
        try:
            self.mqtt_client.loop_forever()
        except KeyboardInterrupt:
            self.mqtt_client.disconnect()

    def send_message(self, msgtype, message):
        my_request = {}
        my_request_body = {}
        my_request_metadata = {}

        my_request['type'] = 'DeviceAlert'
        my_request['hardwareId'] = self.hardware_id

        my_request_body['type'] = msgtype
        my_request_body['message'] = message

        now = datetime.datetime.utcnow()
        my_time=time.strftime("%Y-%m-%dT%H:%M:%SZ", now.timetuple())
        my_request_body['eventDate'] = my_time
        my_request['request'] = my_request_body

        my_request_string = json.dumps(my_request)
        publish.single("marsiot/input/json", my_request_string, hostname=self.host_name)





