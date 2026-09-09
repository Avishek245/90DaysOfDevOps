# 🚀 Day 72 — Ansible Docker Deployment Project

## 📌 Overview

This project combines the Ansible concepts learned across Days 68–72 into a complete application deployment.

The goal was to use Ansible to:

- Configure multiple EC2 servers
- Install common packages
- Install and configure Docker
- Pull and run a containerized application
- Install and configure Nginx
- Configure Nginx as a reverse proxy
- Secure Docker Hub credentials using Ansible Vault
- Use Ansible roles, variables, handlers, templates, tags, conditionals, and idempotency
- Verify the complete deployment

---

# 🏗️ Architecture

```text
                    Ansible Controller
                     (App Server)
                           |
                           | SSH
                           v
                  +-------------------+
                  |    Web Server     |
                  |                   |
                  |   Nginx :80       |
                  |       |           |
                  |       v           |
                  | Docker Container  |
                  |    myapp :8080    |
                  |       |           |
                  |    nginx :80      |
                  +-------------------+

        Ansible
           |
     +-----+-----+
     |     |     |
   Web    App    DB
```

## Request Flow

```text
Client
  |
  | HTTP :80
  v
Nginx
  |
  | Reverse Proxy
  v
127.0.0.1:8080
  |
  v
Docker Container (myapp)
  |
  v
nginx:latest :80
```

---

# 📁 Project Structure

```text
ansible-docker-project/
├── ansible.cfg
├── inventory.ini
├── site.yml
├── .gitignore
├── .vault_pass
│
├── group_vars/
│   ├── all.yml
│   └── web/
│       ├── vars.yml
│       └── vault.yml
│
└── roles/
    ├── common/
    │   └── tasks/
    │       └── main.yml
    │
    ├── docker/
    │   ├── defaults/
    │   │   └── main.yml
    │   ├── handlers/
    │   │   └── main.yml
    │   ├── tasks/
    │   │   └── main.yml
    │   └── templates/
    │       └── docker-compose.yml.j2
    │
    └── nginx/
        ├── defaults/
        │   └── main.yml
        ├── handlers/
        │   └── main.yml
        ├── tasks/
        │   └── main.yml
        └── templates/
            ├── nginx.conf.j2
            └── app-proxy.conf.j2
```

---

# 1️⃣ Ansible Configuration

## `ansible.cfg`

```ini
[defaults]
inventory = inventory.ini
host_key_checking = False
vault_password_file = .vault_pass
```

The configuration tells Ansible:

- Which inventory file to use
- Not to ask for SSH host-key confirmation
- Which password file to use for Ansible Vault

---

# 2️⃣ Inventory

## `inventory.ini`

```ini
[web]
web-server ansible_host=<WEB_SERVER_IP>

[app]
app-server ansible_host=<APP_SERVER_IP>

[db]
db-server ansible_host=<DB_SERVER_IP>

[all:vars]
ansible_user=ec2-user
ansible_ssh_private_key_file=~/.ssh/ansible-master-key.pem
```

The EC2 infrastructure was provisioned using Terraform and managed through the Ansible controller.

---

# 3️⃣ Common Role

The `common` role performs basic configuration on all servers.

## `roles/common/tasks/main.yml`

```yaml
---
- name: Update package cache
  yum:
    update_cache: yes

- name: Install common packages
  yum:
    name: "{{ common_packages }}"
    state: present

- name: Set hostname
  hostname:
    name: "{{ inventory_hostname }}"

- name: Set timezone
  timezone:
    name: "{{ timezone }}"

- name: Create deploy user
  user:
    name: deploy
    groups: wheel
    append: yes
    create_home: yes
    state: present
```

---

# 4️⃣ Global Variables

## `group_vars/all.yml`

```yaml
timezone: Asia/Kolkata
project_name: devops-app
app_env: development

common_packages:
  - vim
  - curl
  - wget
  - git
  - htop
  - tree
  - jq
  - unzip
```

These variables are automatically available to all hosts.

---

# 5️⃣ Docker Role

The Docker role installs Docker, pulls the application image, creates the container, and performs a health check.

## Docker Defaults

### `roles/docker/defaults/main.yml`

```yaml
---
docker_app_image: nginx
docker_app_tag: latest
docker_app_name: myapp
docker_app_port: 8080
docker_container_port: 80
```

---

## Docker Tasks

The Docker role performs the following:

1. Checks whether the Docker image exists
2. Pulls the image when required
3. Checks whether the container exists
4. Creates the container when required
5. Verifies running containers
6. Performs an application health check

Because the `community.docker` collection could not be installed with the available Ansible/Galaxy environment, standard Ansible `command` and `shell` modules were used as the fallback.

### Idempotent Docker Logic

```yaml
---
- name: Check if application Docker image exists
  command: docker image inspect {{ docker_app_image }}:{{ docker_app_tag }}
  register: docker_image_check
  failed_when: false
  changed_when: false

- name: Pull application Docker image
  command: docker pull {{ docker_app_image }}:{{ docker_app_tag }}
  when: docker_image_check.rc != 0

- name: Check if application container exists
  shell: docker ps -a --format '{{ "{{.Names}}" }}' | grep -w "{{ docker_app_name }}"
  register: docker_container_check
  failed_when: false
  changed_when: false

- name: Run application container
  command: >
    docker run -d
    --name {{ docker_app_name }}
    --restart always
    -p {{ docker_app_port }}:{{ docker_container_port }}
    {{ docker_app_image }}:{{ docker_app_tag }}
  when: docker_container_check.rc != 0

- name: Check application container
  command: docker ps
  register: docker_ps
  changed_when: false

- name: Display running containers
  debug:
    var: docker_ps.stdout_lines

- name: Check application health
  uri:
    url: "http://localhost:{{ docker_app_port }}"
    status_code: 200
  register: app_health
  retries: 5
  delay: 5
  until: app_health.status == 200
  when: not ansible_check_mode
```

---

# 6️⃣ Docker Container

The application container was successfully deployed.

```text
CONTAINER ID   IMAGE          PORTS
50649f87278c   nginx:latest   0.0.0.0:8080->80/tcp
```

Container name:

```text
myapp
```

Docker image:

```text
nginx:latest
```

Port mapping:

```text
8080:80
```

---

# 7️⃣ Nginx Role

The Nginx role:

- Enables the Amazon Linux Nginx repository
- Installs Nginx
- Removes the default configuration
- Deploys the main Nginx configuration
- Deploys the reverse-proxy configuration
- Tests the Nginx configuration
- Starts and enables Nginx

## Nginx Defaults

### `roles/nginx/defaults/main.yml`

```yaml
---
nginx_http_port: 80
nginx_upstream_port: 8080
nginx_server_name: "_"
```

---

# 8️⃣ Nginx Reverse Proxy

## `roles/nginx/templates/app-proxy.conf.j2`

```nginx
upstream app_backend {
    server 127.0.0.1:{{ nginx_upstream_port }};
}

server {
    listen {{ nginx_http_port }};
    server_name {{ nginx_server_name }};

    location / {
        proxy_pass http://app_backend;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://app_backend;
        proxy_set_header Host $host;
    }

    {% if app_env == "development" %}
    access_log /var/log/nginx/app_access.log;
    {% endif %}
}
```

Nginx listens on port `80` and forwards requests to the Docker application on port `8080`.

---

# 9️⃣ Nginx Configuration Validation

The configuration was tested using:

```bash
nginx -t
```

Result:

```text
syntax is ok
test is successful
```

This confirms that the generated Nginx configuration is valid.

---

# 🔐 10️⃣ Ansible Vault

Docker Hub credentials were protected using Ansible Vault.

The encrypted file:

```text
group_vars/web/vault.yml
```

was created using:

```bash
ansible-vault create group_vars/web/vault.yml
```

The encrypted file begins with:

```text
$ANSIBLE_VAULT;1.1;AES256
```

Example variables stored inside Vault:

```yaml
vault_docker_username: <dockerhub-username>
vault_docker_password: <dockerhub-token>
```

The Vault password was stored separately in:

```text
.vault_pass
```

Permissions were restricted using:

```bash
chmod 600 .vault_pass
```

The password file was also added to `.gitignore`.

---

# 🧪 11️⃣ Dry Run

Before the actual deployment, a check-mode run was performed:

```bash
ansible-playbook site.yml --check --diff
```

The dry run completed successfully without failures.

This helped identify configuration problems before making changes to the servers.

---

# 🚀 12️⃣ Full Deployment

The complete deployment was executed using:

```bash
ansible-playbook site.yml
```

Final result:

```text
app-server  : ok=6  changed=4 failed=0
db-server   : ok=6  changed=4 failed=0
web-server  : ok=20 changed=5 failed=0
```

The deployment completed successfully.

---

# ♻️ 13️⃣ Idempotency Test

The playbook was executed a second time to verify idempotency.

The Docker role was updated so that an existing image and container are not recreated unnecessarily.

Successful idempotent Docker result:

```text
web-server : ok=6 changed=0 failed=0 skipped=2
```

This confirms that the Docker tasks do not make unnecessary changes when the desired state already exists.

---

# 🏷️ 14️⃣ Ansible Tags

The project uses tags to execute specific parts of the deployment.

## Common

```bash
ansible-playbook site.yml --tags common
```

## Docker

```bash
ansible-playbook site.yml --tags docker
```

## Nginx

```bash
ansible-playbook site.yml --tags nginx
```

Tags make it possible to deploy or update only a specific component.

---

# 🔍 15️⃣ Verification

## Check Docker Container

```bash
ansible web -b -m shell -a "docker ps"
```

Result:

```text
CONTAINER ID   IMAGE          COMMAND                  CREATED          STATUS          PORTS                                   NAMES
50649f87278c   nginx:latest   "/docker-entrypoint.…"   50 minutes ago   Up 50 minutes   0.0.0.0:8080->80/tcp, :::8080->80/tcp   myapp
```

This confirms that the Docker container is running successfully.

---

## Test Docker Application Directly

```bash
ansible web -b -m shell -a "curl -I http://localhost:8080"
```

Result:

```text
HTTP/1.1 200 OK
Server: nginx/1.31.5
```

This confirms that the Docker container is responding on port `8080`.

---

## Test Nginx Reverse Proxy

```bash
ansible web -b -m shell -a "curl -I http://localhost"
```

Result:

```text
HTTP/1.1 200 OK
Server: nginx/1.30.4
```

This confirms that Nginx is successfully forwarding traffic from port `80` to the Docker application on port `8080`.

---

# 📸 16️⃣ Screenshots

Add the screenshots captured during the project below.

## Screenshot 1 — Docker Container

```text
[Insert screenshot: docker ps showing myapp and port 8080]
```

---

## Screenshot 2 — Nginx Deployment

```text
[Insert screenshot: Nginx installation and nginx -t successful]
```

---

## Screenshot 3 — Nginx Port 80 Verification

```text
[Insert screenshot: curl -I http://localhost returning HTTP 200]
```

---

## Screenshot 4 — Docker Port 8080 Verification

```text
[Insert screenshot: curl -I http://localhost:8080 returning HTTP 200]
```

---

## Screenshot 5 — Ansible Vault

```text
[Insert screenshot: encrypted group_vars/web/vault.yml]
```

---

## Screenshot 6 — Full Ansible Deployment

```text
[Insert screenshot: ansible-playbook site.yml successful]
```

---

## Screenshot 7 — Idempotency

```text
[Insert screenshot: second playbook run showing changed=0]
```

---

## Screenshot 8 — Ansible Tags

```text
[Insert screenshots: common, docker and nginx tag executions]
```

---

# 📚 17️⃣ Concepts Covered — Days 68–72

| Day | Concepts |
|---|---|
| Day 68 | Ansible installation, inventory, ad-hoc commands, SSH connectivity |
| Day 69 | Playbooks, modules, tasks, handlers |
| Day 70 | Variables, facts, conditionals, loops |
| Day 71 | Roles, templates, handlers, reusable automation |
| Day 72 | Docker, Nginx reverse proxy, Vault, tags, idempotency, complete deployment |

---

# 🧠 18️⃣ Key DevOps Concepts Learned

## Ansible Roles

Roles organize automation into reusable components:

```text
common
docker
nginx
```

## Variables

Variables make playbooks configurable and reusable.

## Templates

Jinja2 templates dynamically generate configuration files.

## Handlers

Handlers reload Nginx when configuration changes.

## Ansible Vault

Vault protects sensitive credentials from being stored in plain text.

## Tags

Tags allow selective execution of Ansible tasks.

## Idempotency

Running the same playbook multiple times should result in no unnecessary changes.

## Reverse Proxy

Nginx accepts requests on port `80` and forwards them to the application running on port `8080`.

---

# 🔄 19️⃣ End-to-End Flow

```text
Terraform
    |
    v
AWS EC2 Infrastructure
    |
    v
Ansible Controller
    |
    +-------------------+
    |                   |
    v                   v
Common Role          Web Server
                         |
                    Docker Role
                         |
                         v
                    Docker :8080
                         |
                    Nginx Role
                         |
                         v
                      Nginx :80
                         |
                         v
                     Application
```

---

# 🧹 20️⃣ Cleanup

After completing the assignment, AWS infrastructure can be removed using Terraform:

```bash
terraform destroy
```

Review the resources carefully before confirming destruction.

---

# ✅ 21️⃣ Project Completion Checklist

- [x] Ansible controller configured
- [x] Inventory configured
- [x] Common role created
- [x] Docker role created
- [x] Nginx role created
- [x] Docker installed
- [x] Docker container running
- [x] Nginx installed
- [x] Nginx reverse proxy configured
- [x] Nginx configuration validated
- [x] Ansible Vault configured
- [x] Dry run completed
- [x] Full deployment completed
- [x] Idempotency verified
- [x] Ansible tags tested
- [x] Docker port 8080 verified
- [x] Nginx port 80 verified

---

# 🎯 Final Result

The Day 72 Ansible project successfully automated a complete containerized application deployment.

The final setup provides:

```text
Ansible
   ↓
EC2 Web Server
   ↓
Nginx :80
   ↓
Docker Container :8080
   ↓
nginx:latest
```

The project demonstrates practical DevOps automation using:

- AWS EC2
- Ansible
- Docker
- Nginx
- Ansible Vault
- Jinja2 templates
- Roles
- Handlers
- Variables
- Tags
- Idempotency
- Terraform

---
# screenshot

![alt text](<Screenshot (1040).png>) ![alt text](<Screenshot (1042).png>) ![alt text](<Screenshot (1043).png>) ![alt text](<Screenshot (1044).png>) ![alt text](<Screenshot (1045).png>) ![alt text](<Screenshot (1046).png>) ![alt text](<Screenshot (1047).png>) ![alt text](<Screenshot (1048).png>) ![alt text](<Screenshot (1049).png>) ![alt text](<Screenshot (1050).png>) ![alt text](<Screenshot (1051).png>) ![alt text](<Screenshot (1053).png>) ![alt text](<Screenshot (1054).png>) ![alt text](<Screenshot (1055).png>) ![alt text](<Screenshot (1058).png>) ![alt text](<Screenshot (1059).png>) ![alt text](<Screenshot (1039).png>)

# 🚀 Day 72 Completed


**Technologies:**

`AWS EC2` • `Ansible` • `Docker` • `Nginx` • `Ansible Vault` • `Jinja2` • `Terraform` • `Linux`