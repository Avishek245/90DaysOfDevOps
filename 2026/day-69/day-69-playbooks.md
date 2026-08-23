# Day 69 — Ansible Playbooks and Essential Modules

## Overview

Day 69 focused on building practical Ansible automation using AWS EC2 instances. Work covered:

- Ansible inventory and connectivity
- Ansible playbooks
- Essential Ansible modules
- Nginx installation and configuration
- File and directory management
- Services and package management
- Handlers
- Check mode, diff mode, verbose execution
- Multiple plays in a single playbook targeting different server groups

### Infrastructure

| Server | Ansible Group | Role |
|---|---|---|
| `web-server` | `web` | Web Server |
| `app-server` | `app` | Application Server |
| `db-server` | `db` | Database Server |

---

## Task 1 — Ansible Inventory and Connectivity

### Objective
Configure an Ansible inventory containing the web, app, and database servers, and verify connectivity from the control node.

### Inventory

```ini
[web]
web-server ansible_host=35.170.201.95 ansible_user=ec2-user ansible_ssh_private_key_file=/home/ec2-user/ansible-master-key.pem

[app]
app-server ansible_host=3.88.188.204 ansible_user=ec2-user ansible_connection=local

[db]
db-server ansible_host=54.210.130.62 ansible_user=ec2-user ansible_ssh_private_key_file=/home/ec2-user/ansible-master-key.pem
```

Verified with:
```bash
ansible-inventory -i inventory --list
```

Output confirmed three groups: `web`, `app`, `db`.

### Issue: SSH Host Key Verification
First connectivity attempt failed with:
```
Host key verification failed.
```
Resolved by accepting/trusting the EC2 host keys for the web and db servers.

### Connectivity Test
```bash
ansible all -m ping
```
All three servers eventually returned `SUCCESS` / `"ping": "pong"`.

### Key Learning
The inventory tells Ansible:
- Which servers to manage
- Which group each server belongs to
- Which SSH user and private key to use
- How the connection should be established (SSH vs local)

---

## Task 2 — Install and Start Nginx Using a Playbook

### Objective
Install Nginx, start it, enable it at boot, and deploy a custom index page — all via a playbook.

### Playbook: `install-nginx.yml`

```yaml
---
- name: Install and start Nginx on web servers
  hosts: web
  become: true

  tasks:
    - name: Install Nginx
      yum:
        name: nginx
        state: present

    - name: Start and enable Nginx
      service:
        name: nginx
        state: started
        enabled: true

    - name: Create a custom index page
      copy:
        content: "<h1>Deployed by Ansible - TerraWeek Server</h1>"
        dest: /usr/share/nginx/html/index.html
        mode: '0644'
```

### Annotated Structure

```yaml
---                                    # YAML document start
- name: Play name                      # PLAY — targets a group of hosts
  hosts: web                           # Which inventory group to run on
  become: true                         # Run tasks as root (sudo)

  tasks:                               # List of TASKS in this play
    - name: Task name                  # TASK — one unit of work
      module_name:                     # MODULE — what Ansible does
        key: value                     # Module arguments
```

**Q&A:**
1. **Play vs task** — A *play* maps a group of hosts to a set of things to do; a *task* is a single unit of work (one module call) inside a play.
2. **Multiple plays per playbook?** — Yes, a playbook is just a YAML list of plays; each can target a different host group.
3. **`become: true` at play vs task level** — At the play level it applies to every task in the play by default; at the task level it overrides that default for just that one task (e.g. one privileged task in an otherwise unprivileged play).
4. **If a task fails** — By default, Ansible stops running further tasks *for that host* (other hosts continue). Remaining tasks on the failed host are skipped unless you use `ignore_errors: true` or blocks/rescue.

### Issue: Nginx Package Not Found
```
No package matching 'nginx' found available
```
Amazon Linux 2 needed the Nginx repo enabled via Amazon Linux Extras:
```bash
ansible web -m shell -a "sudo amazon-linux-extras enable nginx1"
```
Output confirmed: `nginx1=latest enabled`. Playbook then ran successfully.

### Result
```
PLAY RECAP
web-server : ok=4  changed=0  unreachable=0  failed=0
```

### Verification
```bash
curl --max-time 10 http://35.170.201.95
```
```
<h1>Deployed by Ansible - TerraWeek Server</h1>
```

### Idempotency Check
Ran the playbook a second time — all tasks reported `ok` instead of `changed`, confirming idempotency: Ansible checks current state and only acts when something needs to change.

*(Screenshot: first run showing `changed`, second run showing `ok` — attach to submission.)*

### Key Learning
`yum` manages packages; `service` manages whether they're running/enabled. Neither re-applies work that's already done.

---

## Task 3 — Essential Ansible Modules

### Objective
Practice the core modules used in almost every playbook.

### Sample config file: `files/app.conf`
```
# Ansible Practice Application Configuration
APP_NAME=TerraWeek
APP_ENV=dev
APP_PORT=8080
```

### Module Reference

| Module | Purpose | Example |
|---|---|---|
| `yum` / `apt` | Install/remove packages | `state: present` installs, `state: absent` removes |
| `service` | Start/stop/enable services | `state: started`, `enabled: true` |
| `copy` | Copy files (or inline content) to managed nodes | `src`/`content` + `dest` |
| `file` | Create directories, set ownership/permissions | `state: directory`, `mode` |
| `command` | Run a command — **no shell features** (no pipes, redirects, `&&`) | `command: df -h` |
| `shell` | Run a command **through a shell** — pipes, redirects, env vars work | `shell: ps aux \| wc -l` |
| `lineinfile` | Ensure a specific line exists/is set in a file | `path`, `line`, `create: true` |

```yaml
- name: Install multiple packages
  yum:
    name: [git, curl, wget, tree]
    state: present

- name: Check disk space
  command: df -h
  register: disk_output

- name: Print disk space
  debug:
    var: disk_output.stdout_lines

- name: Count running processes
  shell: ps aux | wc -l
  register: process_count

- name: Show process count
  debug:
    msg: "Total processes: {{ process_count.stdout }}"

- name: Set timezone in environment
  lineinfile:
    path: /etc/environment
    line: 'TZ=Asia/Kolkata'
    create: true
```

### `command` vs `shell`
- **`command`**: runs the binary directly, no shell involved. Safer (no injection risk, no accidental shell expansion), but **cannot** use pipes (`|`), redirects (`>`), environment variable expansion, or chaining (`&&`).
- **`shell`**: runs the command through `/bin/sh`, so pipes/redirects/chaining work. Use it *only* when you actually need shell features — prefer `command` (or a proper module) otherwise, since `shell` is harder to make idempotent and is a minor security consideration.

### Issue: Nginx Task on Non-Web Hosts
Running Nginx-related tasks against `app` and `db` groups failed:
```
Could not find the requested service nginx: host
```
Fixed by scoping Nginx-specific tasks to the `web` group only (via play `hosts:` targeting, not by attempting it on all hosts).

### Result
```
app-server : ok=9   changed=5  failed=0  skipped=1
db-server  : ok=9   changed=5  failed=0  skipped=1
web-server : ok=10  changed=2  failed=0  skipped=0
```

### Key Learning
Each module has a narrow job: `yum`/`service` for system state, `copy`/`file` for filesystem state, `command`/`shell` for one-off operations, `lineinfile` for surgical edits to existing files, `debug` for inspecting registered variables.

---

## Task 4 — Handlers: Restart Services Only When Needed

### Objective
Trigger a service restart only when configuration actually changes — not on every run.

### Playbook: `nginx-config.yml`

```yaml
---
- name: Configure Nginx with a custom config
  hosts: web
  become: true

  tasks:
    - name: Install Nginx
      yum:
        name: nginx
        state: present

    - name: Deploy Nginx config
      copy:
        src: files/nginx.conf
        dest: /etc/nginx/nginx.conf
        owner: root
        mode: '0644'
      notify: Restart Nginx

    - name: Deploy custom index page
      copy:
        content: "<h1>Managed by Ansible</h1><p>Server: {{ inventory_hostname }}</p>"
        dest: /usr/share/nginx/html/index.html

    - name: Ensure Nginx is running
      service:
        name: nginx
        state: started
        enabled: true

  handlers:
    - name: Restart Nginx
      service:
        name: nginx
        state: restarted
```

### Before / After Comparison

**First run** (config file is new → handler fires):
```
TASK [Deploy Nginx config]        changed: [web-server]
TASK [Deploy custom index page]   changed: [web-server]
TASK [Ensure Nginx is running]    ok: [web-server]
RUNNING HANDLER [Restart Nginx]   changed: [web-server]

web-server : ok=6  changed=3  failed=0
```

**Second run** (nothing changed → handler does NOT fire):
```
TASK [Deploy Nginx config]        ok: [web-server]
TASK [Deploy custom index page]   ok: [web-server]
TASK [Ensure Nginx is running]    ok: [web-server]
(no handler runs)

web-server : ok=5  changed=0  failed=0
```

*(Screenshot: both runs side by side — attach to submission.)*

### Key Learning
Handlers are only triggered by `notify` and only run if the notifying task actually reports `changed`. Even if multiple tasks notify the same handler, it runs once, at the end of the play — this avoids unnecessary restarts (and the brief downtime that comes with them).

---

## Task 5 — Check Mode, Diff Mode, and Verbosity

### Check Mode (dry run — no changes applied)
```bash
ansible-playbook install-nginx.yml --check
```
```
TASK [Install Nginx]              ok: [web-server]
TASK [Start and enable Nginx]     ok: [web-server]
TASK [Create a custom index page] changed: [web-server]
```
Shows what *would* happen without touching the system.

### Check + Diff Mode (shows the actual content/permission differences)
```bash
ansible-playbook nginx-config.yml --check --diff
```
```
web-server : ok=5  changed=0  failed=0
```
Confirms current state already matches desired state — no drift.

### Verbose Modes
```bash
ansible-playbook install-nginx.yml -v     # module results, config file used
ansible-playbook install-nginx.yml -vv    # + SSH connection, SFTP, module transfer, BECOME-SUCCESS details
```

### Other Useful Flags
```bash
ansible-playbook install-nginx.yml --limit web-server
ansible-playbook install-nginx.yml --list-hosts
ansible-playbook install-nginx.yml --list-tasks
ansible-playbook install-nginx.yml --syntax-check
```

### Why `--check --diff` matters most for production
`--check` prevents any real change from being applied, and `--diff` shows *exactly* what would change (file contents, permissions, etc.) — together they let you review a playbook's impact on production hosts before committing to it, catching unintended changes (wrong file, wrong permissions, wrong host group) with zero risk.

### `--check` vs `--diff` vs `-v`
| Flag | What it does |
|---|---|
| `--check` | Dry run — reports what *would* change, applies nothing |
| `--diff` | Shows before/after content differences for file-based tasks (usually paired with `--check`) |
| `-v` / `-vv` / `-vvv` | Increases output detail — module results → connection/transfer details → full connection debugging |

---

## Task 6 — Multiple Plays in One Playbook

### Objective
Manage web, app, and database tiers from a single playbook using separate plays per group.

### Playbook: `multi-play.yml`

```yaml
---
- name: Configure web servers
  hosts: web
  become: true
  tasks:
    - name: Install Nginx
      yum:
        name: nginx
        state: present
    - name: Start Nginx
      service:
        name: nginx
        state: started
        enabled: true

- name: Configure app servers
  hosts: app
  become: true
  tasks:
    - name: Install Node.js dependencies
      yum:
        name: [gcc, make]
        state: present
    - name: Create app directory
      file:
        path: /opt/app
        state: directory
        mode: '0755'

- name: Configure database servers
  hosts: db
  become: true
  tasks:
    - name: Install MySQL client
      yum:
        name: mysql
        state: present
    - name: Create data directory
      file:
        path: /var/lib/appdata
        state: directory
        mode: '0700'
```

### Syntax Check
```bash
ansible-playbook multi-play.yml --syntax-check
```
```
playbook: multi-play.yml
```

### Run
```bash
ansible-playbook multi-play.yml
```

| Play | Target | Tasks | Result |
|---|---|---|---|
| 1 — Web | `web-server` | Install + start Nginx | `ok=3 changed=0` (already configured from earlier tasks) |
| 2 — App | `app-server` | Install gcc/make, create `/opt/app` | `ok=3 changed=2` |
| 3 — DB | `db-server` | Install MySQL client, create `/var/lib/appdata` (0700) | `ok=3 changed=2` |

```
PLAY RECAP
app-server : ok=3  changed=2  unreachable=0  failed=0  skipped=0
db-server  : ok=3  changed=2  unreachable=0  failed=0  skipped=0
web-server : ok=3  changed=0  unreachable=0  failed=0  skipped=0
```

**Verification:** Nginx installed only on `web-server`, MySQL client only on `db-server` — confirmed each play only touched its own `hosts:` group.

### Key Learning
A playbook is just an ordered list of plays. Each play independently chooses its own target group via `hosts:`, so one file can describe and converge an entire multi-tier environment in one `ansible-playbook` invocation.

---

## Day 69 — Final Summary

| Task | Topic | Status |
|---|---|---|
| 1 | Inventory & connectivity | ✅ |
| 2 | Install/start Nginx via playbook | ✅ |
| 3 | Essential modules | ✅ |
| 4 | Handlers | ✅ |
| 5 | Check / diff / verbose modes | ✅ |
| 6 | Multiple plays, one playbook | ✅ |

### Architecture

```
                    Ansible Control Node
                           |
                    Static Inventory
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
     Web Group         App Group         DB Group
          |                |                |
          v                v                v
    web-server        app-server        db-server
          |                |                |
       Nginx          gcc + make       MySQL client
       HTTP           /opt/app         /var/lib/appdata
```

### Core Concepts Learned
1. **Inventory** — defines managed hosts, groups, SSH user/key, connection method
2. **Playbooks** — YAML description of desired state, made of one or more plays
3. **Modules** — the actual units of work (`yum`, `service`, `copy`, `file`, `command`, `shell`, `lineinfile`, `debug`)
4. **Idempotency** — re-running a playbook only changes what's actually out of state (`changed=0` on repeat runs)
5. **Handlers** — fire only on `notify` from a task that reported `changed`; run once, at end of play
6. **Check mode** (`--check`) — dry run, no changes applied
7. **Diff mode** (`--diff`) — shows exact file/content differences
8. **Verbose mode** (`-v`/`-vv`/`-vvv`) — increasing levels of execution/connection detail
9. **Multiple plays** — one playbook, many host groups, each with its own tasks

### Troubleshooting Log
| Issue | Cause | Fix |
|---|---|---|
| `Host key verification failed` | SSH hadn't trusted new EC2 host keys | Accepted host keys before first run |
| `No package matching 'nginx' found` | Amazon Linux 2 doesn't ship Nginx by default | `amazon-linux-extras enable nginx1`, then `yum clean metadata` |
| `Could not find the requested service nginx: host` | Nginx tasks run against non-web hosts | Scoped Nginx tasks to `hosts: web` only |

### Commands Practiced
```bash
ansible-inventory -i inventory --list
ansible all -m ping
ansible-playbook install-nginx.yml --syntax-check
ansible-playbook install-nginx.yml
ansible-playbook install-nginx.yml --check
ansible-playbook nginx-config.yml --check --diff
ansible-playbook install-nginx.yml -v
ansible-playbook install-nginx.yml -vv
ansible-playbook multi-play.yml
```

### Screenshots to Attach on Submission

![alt text](<Screenshot (904).png>) ![alt text](<Screenshot (905).png>) ![alt text](<Screenshot (906).png>) ![alt text](<Screenshot (907).png>) ![alt text](<Screenshot (908).png>) ![alt text](<Screenshot (910).png>) ![alt text](<Screenshot (911).png>) ![alt text](<Screenshot (913).png>) ![alt text](<Screenshot (914).png>) ![alt text](<Screenshot (915).png>) ![alt text](<Screenshot (916).png>) ![alt text](<Screenshot (917).png>) ![alt text](<Screenshot (919).png>) ![alt text](<Screenshot (920).png>) ![alt text](<Screenshot (921).png>) ![alt text](<Screenshot (922).png>) ![alt text](<Screenshot (923).png>)

---

**Day 69 Status: ✅ COMPLETED — Tasks 1–6**