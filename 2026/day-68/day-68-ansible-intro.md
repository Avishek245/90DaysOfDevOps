# Day 68 — Introduction to Ansible and Inventory Setup

## 🚀 90 Days of DevOps — Day 68

Today I started my Ansible journey by learning configuration management and how Ansible can manage multiple servers from a single control node.

For this lab, I used **Terraform to provision three Amazon EC2 instances** and then configured Ansible on the Web EC2 instance to manage all three servers.

The lab covered Ansible's **agentless architecture, inventory management, SSH connectivity, ad-hoc commands, inventory groups, patterns, and `ansible.cfg` configuration**.

---

## 1. What is Ansible?

Ansible is an open-source automation and configuration management tool used to automate tasks such as:

- Installing packages
- Managing services
- Creating and modifying files
- Managing users
- Configuring servers
- Deploying applications
- Running commands across multiple servers

Ansible is **agentless**, meaning no Ansible agent needs to be installed on the managed servers.

Ansible uses **SSH** to communicate with Linux servers.

---

## 2. What is Configuration Management?

Configuration management is the process of maintaining servers and systems in a consistent and desired state.

For example, instead of manually connecting to three servers and installing Git on each one, Ansible can perform the task from one control node:

```bash
ansible web -m yum -a "name=git state=present" --become
```

Configuration management makes infrastructure:

- Faster to manage
- Consistent
- Repeatable
- Less error-prone
- Easier to automate

---

## 3. Ansible vs Other Configuration Management Tools

| Tool | Main Characteristic |
|---|---|
| Ansible | Agentless, uses SSH, YAML-based |
| Chef | Uses agents and Ruby-based configuration |
| Puppet | Usually uses agents and declarative configuration |
| Salt | Supports agent-based and agentless communication |

### Why Ansible?

Ansible is simple to start with because managed Linux servers do not require an Ansible agent. SSH is enough for Ansible to communicate with them.

---

## 4. What Does Agentless Mean?

Agentless means Ansible does not require any special Ansible software or agent to be installed on the managed servers.

The architecture is:
             Control Node
          Ansible Installed
                 |
                 | SSH
      -------------------------
      |           |           |
      v           v           v
  Web Server   App Server   DB Server
    EC2          EC2          EC2

    
The control node sends commands and modules to the managed nodes over SSH.

---

## 5. Ansible Architecture

Ansible consists of several important components.

### Control Node

The machine where Ansible is installed and executed.

For this lab, I used the Web EC2 instance as the Ansible control node.

### Managed Nodes

The servers managed by Ansible.

I created three EC2 instances:

- Web Server
- App Server
- DB Server

### Inventory

The inventory contains the list of servers that Ansible manages.

Example:

```ini
[web]
web-server ansible_host=<WEB_PUBLIC_IP>

[app]
app-server ansible_host=<APP_PUBLIC_IP>

[db]
db-server ansible_host=<DB_PUBLIC_IP>
```

### Modules

Modules are reusable units of work that Ansible executes.

Examples used in this lab:

- `ping`
- `command`
- `yum`
- `copy`

### Playbooks

Playbooks are YAML files used to define repeatable automation tasks.

This lab focused mainly on ad-hoc commands. Playbooks will be used for more complex and repeatable automation.

---

## 6. Lab Environment

For the lab environment, I used:

### Option A — Terraform

Terraform was used to provision three EC2 instances.

### EC2 Instances

| Instance | Role | OS | Instance Type |
|---|---|---|---|
| ansible-web | Web / Control Node | Amazon Linux 2 | t2.micro |
| ansible-app | App Server | Amazon Linux 2 | t2.micro |
| ansible-db | DB Server | Amazon Linux 2 | t2.micro |

All three instances were created using Terraform.

A security group was also created to allow SSH access:

- Port: 22
- Protocol: TCP

The EC2 instances used the key pair:
ansible-master-key


---

## 7. Terraform Infrastructure

The Terraform configuration created:

- Default VPC
- Security Group
- 3 EC2 instances
- Amazon Linux 2 AMI
- SSH access
- Public IP outputs

Terraform provided the public IP addresses of the three instances.

The instances were labeled:

- Web Server
- App Server
- DB Server

The Web server was then used as the Ansible control node.

---

## 8. Installing Ansible

I connected to the Web EC2 instance using SSH.

I verified the operating system:

```bash
cat /etc/os-release
```

The instance was running:
Python 3.7.16

The standard `yum install ansible` command was not available because the Ansible package was not present in the configured Amazon Linux 2 repositories.

Therefore, I installed Ansible using pip3, which was also provided as an option in the assignment:

```bash
pip3 install ansible
```

After installation, I verified Ansible:

```bash
ansible --version
```

Ansible was successfully installed.

Installed version:
ansible [core 2.11.12]

The Ansible control node was:

Web EC2 instance

Ansible only needed to be installed on the control node because the managed nodes communicate with it through SSH and do not require an Ansible agent.

---

## 9. Creating the Ansible Project Directory

I created the Ansible project directory:

```bash
mkdir -p ansible-practice
cd ansible-practice
```

The project contained:
ansible-practice/
├── inventory.ini
├── hello.txt
└── ansible.cfg

---

## 10. Creating the Ansible Inventory

I created:inventory.ini

My inventory configuration was:

```ini
[web]
web-server ansible_host=<WEB_PUBLIC_IP>

[app]
app-server ansible_host=<APP_PUBLIC_IP>

[db]
db-server ansible_host=<DB_PUBLIC_IP>

[all:vars]
ansible_user=ec2-user
ansible_ssh_private_key_file=~/ansible-master-key.pem

[application:children]
web
app

[all_servers:children]
application
db
```

IP addresses are redacted in this documentation for security.

The inventory contains three main groups:

- web
- app
- db

It also contains two parent groups:

- application
- all_servers

---

## 11. Testing Ansible Connectivity

I tested connectivity to all managed nodes using:

```bash
ansible all -i inventory.ini -m ping
```

All three servers successfully responded with:
web-server | SUCCESS
"ping": "pong"

app-server | SUCCESS
"ping": "pong"

db-server | SUCCESS
"ping": "pong"

This confirmed that Ansible was successfully communicating with all three EC2 instances over SSH.

---

## 12. Ad-Hoc Commands

Ad-hoc commands allow Ansible to perform quick one-time tasks without creating a playbook.

### 12.1 Check Server Uptime

Command:

```bash
ansible all -i inventory.ini -m command -a "uptime"
```

The command successfully returned the uptime of:

- web-server
- app-server
- db-server

Example output:app-server | CHANGED | rc=0 >>
15:57:09 up 40 min, 1 user, load average: 0.00, 0.00, 0.00

db-server | CHANGED | rc=0 >>
15:57:09 up 40 min, 1 user, load average: 0.00, 0.00, 0.00

web-server | CHANGED | rc=0 >>
15:57:09 up 40 min, 2 users, load average: 0.02, 0.04, 0.01

---

## 13. Check Free Memory

I checked memory on the Web server using:

```bash
ansible web -i inventory.ini -m command -a "free -h"
```

This command targeted only the web group.

It displayed the available memory and memory usage of the Web server.

---

## 14. Check Disk Space

I checked disk usage on all servers:

```bash
ansible all -i inventory.ini -m command -a "df -h"
```

This displayed filesystem and disk usage information for:

- web-server
- app-server
- db-server

---

## 15. Install Git on the Web Server

I installed Git on the Web server using the Ansible yum module:

```bash
ansible web -i inventory.ini -m yum -a "name=git state=present" --become
```

Git was successfully installed.

The result showed:changed: true

and confirmed:
Installed:
git.x86_64

---

## 16. What Does `--become` Do?

The `--become` option is used for privilege escalation.

It allows Ansible to perform tasks with elevated privileges, similar to:
sudo

For example, installing packages usually requires root privileges.

Therefore, I used:
--become

with the package installation command.

---

## 17. Creating a File

I created a file on the Ansible control node:

```bash
echo "Hello from Ansible" > hello.txt
```

I verified the file:

```bash
cat hello.txt
```

Output:Hello from Ansible

---

## 18. Copying a File to All Servers

I used the Ansible copy module:

```bash
ansible all -i inventory.ini -m copy -a "src=hello.txt dest=/tmp/hello.txt"
```

The file was successfully copied to:/tmp/hello.txt

on all three managed servers.

The output showed:
web-server | CHANGED
app-server | CHANGED
db-server | CHANGED

This confirmed that the file was copied successfully.

---

## 19. Verifying the Copied File

I verified the file on all three servers:

```bash
ansible all -i inventory.ini -m command -a "cat /tmp/hello.txt"
```

All three servers returned:Hello from Ansible

This confirmed that the file was successfully copied to every managed node.

---

## 20. Inventory Groups

I created a group of groups using:

```ini
[application:children]
web
app

[all_servers:children]
application
db
```

This created the following structure:
application
├── web
└── app

all_servers
├── application
│ ├── web
│ └── app
└── db

---

## 21. Test the Application Group

I ran:

```bash
ansible application -i inventory.ini -m ping
```

The command successfully targeted:

- web-server
- app-server

Both returned:SUCCESS
"ping": "pong"

---

## 22. Test the DB Group

I ran:

```bash
ansible db -i inventory.ini -m ping
```

Only the DB server was targeted.

Output:db-server | SUCCESS
"ping": "pong"

---

## 23. Test the All Servers Group

I ran:

```bash
ansible all_servers -i inventory.ini -m ping
```

All three servers successfully responded:
db-server | SUCCESS
app-server | SUCCESS
web-server | SUCCESS

---

## 24. Ansible Host Patterns

I also practiced Ansible host patterns.

### OR Pattern

Command:

```bash
ansible 'web:app' -i inventory.ini -m ping
```

This targets:
web OR app

Therefore, the Web and App servers are selected while the DB server is excluded.

### NOT Pattern

Command:

```bash
ansible 'all:!db' -i inventory.ini -m ping
```

This means:all servers except db

Therefore, only:

- web-server
- app-server

are targeted.

---

## 25. Creating `ansible.cfg`

To avoid typing:-i inventory.ini

every time, I created:
ansible.cfg

Configuration:

```ini
[defaults]
inventory = inventory.ini
host_key_checking = False
remote_user = ec2-user
private_key_file = ~/ansible-master-key.pem
```

This configuration tells Ansible:

- Which inventory to use
- Which remote user to use
- Which SSH private key to use
- Not to prompt for host key verification during the lab

---

## 26. Final Ansible Configuration Test

After creating `ansible.cfg`, I ran:

```bash
ansible all -m ping
```

I no longer needed:-i inventory.ini

All three servers returned:
SUCCESS
"ping": "pong"

This confirmed that `ansible.cfg` was working correctly.

---

## 27. Command Module vs Shell Module

### Command Module

The command module executes commands directly without using a shell.

Example:

```bash
ansible all -m command -a "uptime"
```

It is preferred when shell functionality is not required.

### Shell Module

The shell module executes commands through the system shell.

It supports shell features such as:

- Pipes
- Redirects
- Environment variables
- Command chaining

Example:

```bash
ansible all -m shell -a "df -h | grep /"
```

### Difference

| Feature | command | shell |
|---|---|---|
| Uses shell | No | Yes |
| Supports pipes | No | Yes |
| Supports redirects | No | Yes |
| Simple commands | Recommended | Works |
| Shell-specific operations | Not suitable | Suitable |

---

## 28. Ansible Architecture — My Understanding

The architecture I implemented during this lab was:
                Terraform
                    |
                    v
           AWS EC2 Infrastructure
                    |
      -----------------------------
      |            |              |
      v            v              v
  Web EC2       App EC2        DB EC2
  Control       Managed        Managed
   Node          Node           Node
      |
      |
   Ansible
      |
      | SSH
      |
      +---------------------------+
      |             |             |
      v             v             v
   Web EC2       App EC2       DB EC2

   Terraform → Provision Infrastructure
Ansible → Configure Infrastructure

---

## 29. Important Concepts Learned

During Day 68, I learned:

- Ansible is a configuration management tool.
- Ansible is agentless.
- Ansible uses SSH to communicate with Linux servers.
- The control node runs Ansible.
- Managed nodes do not need an Ansible agent.
- Inventory defines managed hosts.
- Inventory can contain groups and child groups.
- Modules perform individual tasks.
- Ad-hoc commands are useful for quick tasks.
- `--become` provides privilege escalation.
- `command` runs simple commands.
- `shell` supports shell features.
- `copy` can transfer files to remote servers.
- `yum` can manage packages on Amazon Linux.
- Host patterns allow flexible server selection.
- `ansible.cfg` reduces repetitive command-line options.
- Playbooks are better for repeatable and complex automation.

---

## 30. Lab Cleanup

After completing the Day 68 exercises and capturing the required screenshots, I cleaned up the AWS infrastructure created by Terraform.

I used:

```bash
terraform destroy
```

This removed the Terraform-managed EC2 instances and supporting resources to avoid unnecessary AWS charges.

---

## 31. Screenshots
![alt text](<Screenshot (878).png>) ![alt text](<Screenshot (879).png>) ![alt text](<Screenshot (880).png>) ![alt text](<Screenshot (881).png>) ![alt text](<Screenshot (883).png>) ![alt text](<Screenshot (884).png>) ![alt text](<Screenshot (885).png>) ![alt text](<Screenshot (887).png>) ![alt text](<Screenshot (888).png>) ![alt text](<Screenshot (889).png>) ![alt text](<Screenshot (890).png>) ![alt text](<Screenshot (891).png>) ![alt text](<Screenshot (892).png>) ![alt text](<Screenshot (893).png>) ![alt text](<Screenshot (894).png>) ![alt text](<Screenshot (895).png>) ![alt text](<Screenshot (896).png>) ![alt text](<Screenshot (897).png>) ![alt text](<Screenshot (898).png>) ![alt text](<Screenshot (899).png>)

### Ad-Hoc Commands

Add screenshots showing the successful execution of:

```bash
ansible all -m command -a "uptime"
ansible web -m command -a "free -h"
ansible all -m command -a "df -h"
ansible web -m yum -a "name=git state=present" --become
ansible all -m copy -a "src=hello.txt dest=/tmp/hello.txt"
```

---

## 32. Final Result

The Day 68 Ansible lab was successfully completed.

### Completed Tasks

- [x] Learned configuration management
- [x] Learned Ansible architecture
- [x] Provisioned 3 EC2 instances using Terraform
- [x] Used Web EC2 as the Ansible control node
- [x] Installed Ansible
- [x] Created inventory.ini
- [x] Connected Ansible to all three EC2 instances
- [x] Tested Ansible ping
- [x] Checked server uptime
- [x] Checked memory
- [x] Checked disk usage
- [x] Installed Git using Ansible
- [x] Used `--become`
- [x] Copied a file to all servers
- [x] Verified the copied file
- [x] Created inventory groups
- [x] Tested group patterns
- [x] Created ansible.cfg
- [x] Verified `ansible all -m ping` without `-i inventory.ini`
- [x] Compared command and shell
- [x] Cleaned up the AWS infrastructure

---

## 33. Conclusion

Day 68 gave me my first practical experience with Ansible.

I used Terraform to provision the infrastructure and then used Ansible to manage the servers from a single control node.

The biggest concept I learned was that Ansible is agentless. The managed EC2 instances did not require an Ansible agent. Ansible communicated with them over SSH.

I also learned how inventory groups, modules, ad-hoc commands, privilege escalation, host patterns, and `ansible.cfg` work together.

The overall workflow was:
Terraform
↓
Provision EC2 Infrastructure
↓
Ansible Control Node
↓
Inventory
↓
SSH
↓
Managed EC2 Instances
↓
Run Configuration Tasks



This was a great introduction to configuration management and the next step toward automating infrastructure beyond provisioning.

**🚀 Day 68 Completed**

Introduction to Ansible and Inventory Setup

### Technologies Used

AWS EC2, Terraform, Ansible, Amazon Linux 2, SSH, Linux, YAML, INI

### Tags

#90DaysOfDevOps #DevOpsKaJosh #TrainWithShubham #Ansible #Terraform #AWS #DevOps #ConfigurationManagement #InfrastructureAsCode