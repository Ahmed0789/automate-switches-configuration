#!/usr/bin/env python3
import json
import subprocess
import os
import logging

# File paths
DEVICES_FILE = "/devices/devices.json"
INVENTORY_FILE = "/tmp/ansible_inventory.ini"
PLAYBOOK_FILE = "/switch_template.yml"
LOG_FILE = "/var/log/switch_config.log"

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def load_switches():
    """Read devices.json, validate data, and extract switches."""
    if not os.path.exists(DEVICES_FILE):
        logging.error(f"Devices file '{DEVICES_FILE}' not found.")
        return {}

    try:
        with open(DEVICES_FILE, "r") as file:
            data = json.load(file)
        switches = data.get("switches", {})
        if not switches:
            logging.warning("No switches found in devices.json.")
        return switches
    except json.JSONDecodeError:
        logging.error("Error decoding JSON file.")
        return {}

def create_inventory(switches):
    """Generate an Ansible inventory file."""
    if not switches:
        logging.error("No valid switches to configure.")
        return None

    with open(INVENTORY_FILE, "w") as file:
        file.write("[cisco_switches]\n")
        for name, ip in switches.items():
            file.write(f"{ip}\n")
    
    logging.info(f"Inventory created successfully: {INVENTORY_FILE}")
    return INVENTORY_FILE

def run_ansible_playbook(inventory):
    """Execute Ansible playbook with generated inventory."""
    if not inventory:
        logging.error("Skipping playbook execution due to inventory errors.")
        return
    
    cmd = f"ansible-playbook -i {inventory} {PLAYBOOK_FILE}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        logging.info("Ansible playbook executed successfully.")
    else:
        logging.error(f"Error running playbook: {result.stderr}")

def retrieve_vlans(switches):
    """Retrieve VLAN information from configured switches."""
    vlan_data = {}

    for name, ip in switches.items():
        logging.info(f"Retrieving VLAN info from {name} ({ip})...")
        cmd = f"ansible {ip} -m cisco.ios.ios_command -a 'show vlan brief'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            vlan_data[name] = result.stdout
            logging.info(f"VLANs retrieved for {name}: {result.stdout}")
        else:
            logging.error(f"Error retrieving VLANs from {name}: {result.stderr}")

    return vlan_data

def store_vlans_in_core(vlan_data, core_ip):
    """Store VLAN data in the core switch."""
    if not vlan_data:
        logging.error("No VLAN data to store.")
        return

    logging.info(f"Storing VLANs in core switch ({core_ip})...")
    for switch, vlans in vlan_data.items():
        cmd = f"ansible {core_ip} -m cisco.ios.ios_config -a 'banner motd VLANs from {switch}: {vlans}'"
        result = subprocess.run(cmd, shell=True)

        if result.returncode == 0:
            logging.info(f"Successfully stored VLANs for {switch} in core switch.")
        else:
            logging.error(f"Failed to store VLANs from {switch} in core switch.")

def main():
    switches = load_switches()
    inventory = create_inventory(switches)
    run_ansible_playbook(inventory)
    
    vlan_data = retrieve_vlans(switches)
    core_switch_ip = "192.168.1.1"  # Replace with actual core switch IP
    store_vlans_in_core(vlan_data, core_switch_ip)

if __name__ == "__main__":
    main()
