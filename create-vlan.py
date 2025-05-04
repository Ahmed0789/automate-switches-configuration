# Import the netmiko library for network automation
from netmiko import ConnectHandler
# Import the getpass library for getting user input securely
from getpass import getpass
# Import the json library for parsing JSON files
import json
# Import the os library for interacting with the operating system
import os
# Import the re library for regular expressions
import re
# Import the paramiko library for SSH connections
import paramiko

# Prompt the user to enter their username, password, and enable password
username = getpass ('Enter Your UserName:')
password = getpass('Enter Your Password:')
secret = getpass('Enter Your Enable Password:')
# Prompt the user to enter the VLAN ID and name that they want to check or create
which_vlan = input("wich VLAN do you want to check?: ")
vlan_name = input("vlan name?: ")
# Get the current working directory
working_dir = os.getcwd()

# Try to open and read the switches.json file that contains the IP addresses of the switches
try:
    with open(working_dir + './src/devices/devices.json', 'r') as json_file:
        ip_list = json.load(json_file)

# If the file is not found, print an error message
except:
    print('No ip list found')
    raise

# Loop through the IP addresses in the ip_list dictionary
for ip in ip_list.values():
    # Create a device dictionary with the device type, IP address, username, password, and secret
    device = {
        'device_type': 'cisco_ios',
        'ip': ip,
        'username': username,
        'password': password,
        'secret': secret
    }
    # Establish a connection to the device using netmiko
    net_connect = ConnectHandler(**device)
    # Enter the enable mode
    net_connect.enable()
    # Send the command 'show run | include hostname' and parse the output using textfsm
    show_run_hostname = net_connect.send_command('show run | include hostname', use_textfsm=True)
    # Use a regular expression to extract the hostname from the output
    match = re.search(r'^hostname\s+([^\n]*)', show_run_hostname, re.IGNORECASE)
    # Assign the hostname to a variable, or "N/A" if not found
    hostname = match.group(1) if match else "N/A"

    # Print 60 asterisks in green color
    print('\033[32m' + '*'*60 + '\033[0m')
    # Print another 60 asterisks in green color
    print('\033[32m' + '*'*60 + '\033[0m')

    # Print the IP address and the hostname of the device
    print(f'Connecting to {ip} {hostname}')

    # Enter the enable mode again
    net_connect.enable()
    # Send the command 'show vlan b' and parse the output using textfsm
    show_vlan_command = net_connect.send_command('show vlan b', use_textfsm=True)

    # Initialize a flag variable to indicate if the VLAN is already configured
    vlan_already_there = False
    # Loop through the output of the show vlan command
    for i in show_vlan_command:
        # If the VLAN ID matches the user input, print a message and set the flag to True
        if i['vlan_id'] == which_vlan:
            print('The VLAN is already configured')
            vlan_already_there = True

    # If the VLAN is not already configured, create a new VLAN with the user input
    if not vlan_already_there:
        # Create a list of commands to create the VLAN and assign a name
        create_new_vlan = [ f'vlan {which_vlan}', f'name {vlan_name}' ]
        # Send the commands to the device using netmiko
        create_vlan = net_connect.send_config_set(create_new_vlan)

        # Send the command 'show vlan b | include <VLAN ID>' and parse the output using textfsm
        show_vlan_command = net_connect.send_command(f'show vlan b | include {which_vlan}', use_textfsm=True)
        # Print the output of the show vlan command
        print(show_vlan_command)

    # Send the command 'show interfaces status' and parse the output using textfsm
    show_interface_command = net_connect.send_command('show interfaces status', use_textfsm=True)

    # Initialize an empty list to store the trunk interfaces
    result = []
    # Loop through the output of the show interfaces command
    for d in show_interface_command:
        # If the VLAN is trunk, append the interface to the result list
        if d['vlan']=='trunk':
            result.append(d)
    # Initialize a counter variable
    y = 0
    # Loop through the result list
    while y < len(result):
        # Assign the port name to a variable
        a = result[y]['port']
        # Print the port name and indicate that it is a trunk interface
        print(f'{a} interface is a trunk')
        # Create a list of commands to add the new VLAN to the trunk interface
        add_new_vlan_to_trunk = [
            (f'interface {a}'),
            (f'switchport trunk allowed vlan add {which_vlan}'),
        ]

        # Send the command 'show run interface <port> | in allowed' and parse the output using textfsm
        show_run_command = net_connect.send_command(f'show run interface {a} | in allowed', use_textfsm=True)

        # Initialize a flag variable to indicate if the trunk is allowed
        trunk_is_allowed = 0
        # If the output is empty, print a message and set the flag to 1
        if show_run_command == "":
            print("trunk is: switch port trunk")
            trunk_is_allowed = 1

        # Initialize a flag variable to indicate if the VLAN is in the trunk
        vlan_in_trunk = False

        # If the output is not empty and contains the VLAN ID, print a message and set the flag to True
        if show_run_command != "" and (f'{which_vlan}') in show_run_command:
            vlan_in_trunk = True
            print(f'For VLAN {which_vlan}, the configuration is already present on the trunk interface {a}')

        # If the VLAN is not in the trunk and the trunk is not allowed, send the commands to add the VLAN to the trunk
        if not vlan_in_trunk and trunk_is_allowed < 1:
            add_vlan_to_trunk = net_connect.send_config_set(add_new_vlan_to_trunk)
            print(f'new vlan {which_vlan} has been allowed on trunk interface {a}')

        # Increment the counter variable
        y += 1
