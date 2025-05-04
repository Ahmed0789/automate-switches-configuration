#!/usr/bin/env python3
import json
import subprocess
import os
import logging

# File paths
DISCOVERED_SWITCHES_FILE = "/devices/discovered_switches.json"
INVENTORY_FILE = "/inventory.yml"
LOG_FILE = "/var/log/switch_auto_config.log"
PLAYBOOK_FILE = "/switch_template.yml"

# Core switch details (controller)
CORE_SWITCH = "192.168.1.1"

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def discover_switches():
    """Run Ansible to discover switches from core switch."""
    cmd = f"ansible-playbook -i {CORE_SWITCH}, discover_switches.yml"
    subprocess.run(cmd, shell=True)

def load_discovered_switches():
    """Load discovered switches from stored JSON."""
    if not os.path.exists(DISCOVERED_SWITCHES_FILE):
        logging.error("Switch discovery file missing.")
        return {}

    try:
        with open(DISCOVERED_SWITCHES_FILE, "r") as file:
            switches = json.load(file)
        return switches
    except json.JSONDecodeError:
        logging.error("Invalid JSON data in discovered switches file.")
        return {}

def create_inventory(switches):
    """Generate dynamic inventory file."""
    if not switches:
        logging.error("No switches detected, skipping inventory creation.")
        return None

    inventory = {
        "all": {
            "hosts": {f"switch{index+1}": {"ansible_host": ip} for index, ip in enumerate(switches)},
            "children": {
                "switches": {
                    "hosts": {f"switch{index+1}": {} for index, ip in enumerate(switches)}
                }
            }
        }
    }

    with open(INVENTORY_FILE, "w") as file:
        json.dump(inventory, file, indent=2)
    
    logging.info(f"Dynamic inventory created: {INVENTORY_FILE}")
    return INVENTORY_FILE

def run_ansible_playbook(inventory):
    """Execute configuration template on discovered switches."""
    if not inventory:
        logging.error("Skipping playbook execution due to missing inventory.")
        return
    
    cmd = f"ansible-playbook -i {inventory} {PLAYBOOK_FILE}"
    subprocess.run(cmd, shell=True)

def retrieve_vlans(switches):
    """Get VLANs from each configured switch."""
    vlan_data = {}

    for index, ip in enumerate(switches):
        switch_name = f"switch{index+1}"
        logging.info(f"Retrieving VLAN info from {switch_name} ({ip})...")
        cmd = f"ansible {ip} -m cisco.ios.ios_command -a 'show vlan brief'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            vlan_data[switch_name] = result.stdout
        else:
            logging.error(f"Error retrieving VLANs from {switch_name}: {result.stderr}")

    return vlan_data

def store_vlans_in_core(vlan_data):
    """Store VLAN details into the core switch (controller)."""
    if not vlan_data:
        logging.error("No VLAN data available for storing.")
        return

    logging.info(f"Storing VLAN data in core switch ({CORE_SWITCH})...")
    for switch, vlans in vlan_data.items():
        cmd = f"ansible {CORE_SWITCH} -m cisco.ios.ios_config -a 'banner motd VLANs from {switch}: {vlans}'"
        subprocess.run(cmd, shell=True)

def main():
    discover_switches()
    switches = load_discovered_switches()
    inventory = create_inventory(switches)
    
    run_ansible_playbook(inventory)
    
    vlan_data = retrieve_vlans(switches)
    store_vlans_in_core(vlan_data)

if __name__ == "__main__":
    main()
