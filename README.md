# automate-switches-configuration

### **Step 1: Installing Ansible & Python on the Controller**
If your controller runs Linux (preferably a server distro like Unix / Debian), installing Ansible and Python is straightforward.

1. **Update Packages:**
   ```bash
   sudo apt update && sudo apt upgrade -y  # For Debian/Ubuntu
   sudo yum update -y  # For CentOS/RHEL
   ```
2. **Install Python (if not already installed):**
   ```bash
   sudo apt install python3 -y  # Debian/Ubuntu
   sudo yum install python3 -y  # CentOS/RHEL
   ```
3. **Install Pip (for Python package management):**
   ```bash
   sudo apt install python3-pip -y
   sudo yum install python3-pip -y
   ```
4. **Install Ansible:**
   ```bash
   pip install ansible
   ```
5. **Verify Installation:**
   ```bash
   ansible --version
   ```
6. **Check & Confirm prerequisites:**
   ```
   sudo apt install python3
   sudo apt install python3-pip
   pip3 install Netmiko
   pip3 install paramiko
   ```

### **Step 2: Setting Up the Ansible Inventory File**
Since you have **30-40 switches**, the inventory file should be structured efficiently. Here’s how you can start with just **2 switches** and scale later.

1. Create an inventory file (`inventory.yml`) inside your Ansible project folder:

   ```yaml
   all:
     hosts:
       switch1:
         ansible_host: 192.168.1.101
         ansible_user: admin
         ansible_password: password_here
         ansible_network_os: cisco_ios
       switch2:
         ansible_host: 192.168.1.102
         ansible_user: admin
         ansible_password: password_here
         ansible_network_os: cisco_ios
     children:
       switches:
         hosts:
           switch1:
           switch2:
   ```

2. Ensure SSH access to switches:
   - You should **enable SSH** on all switches to allow remote automation.
   - Confirm **Ansible can connect** using:
     ```bash
     ansible -i inventory.yml all -m ping
     ```

### **Step 3: Running a Test Playbook**
To test if Ansible can communicate properly with the switches, create a basic playbook (`test-playbook.yml`):

```yaml
- name: Test Switch Connectivity
  hosts: switches
  gather_facts: no
  tasks:
    - name: Check switch status
      ansible.builtin.ping:
```

Run the playbook:
```bash
ansible-playbook -i inventory.yml test-playbook.yml
```
