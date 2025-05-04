from netmiko import ConnectHandler
from getpass import qetpass
import json
import os
import re
import paramiko

username = getpass('Enter Your UserName')

password = getpass('Enter Your Passord:')

secret = qetpass('Enter Your Eanble Password:')

which_vlan = input("which VLRN do you want to check: ")

vlan_name = input("vlan name?: ")

working_dir = os.getcwd()


try:
    with open(working_dir + './src/devices/devices.json', 'r') as json_file:
              ip_list = json.load(json_file)
except: 
    print('error creating')
    raise