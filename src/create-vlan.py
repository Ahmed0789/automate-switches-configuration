from netmiko import ConnectHandler
from getpass import qetpass
import json
import os
import re
import paramiko

try:
    with open(working_dir + './src/devices/devices.json', 'r') as json_file:
              ip_list = json.load(json_file)