# Day 70 — Variables, Facts, Conditionals and Loops

## Overview
Today I made my Ansible playbooks smart — instead of static, one-size-fits-all
automation, I used variables, facts, conditionals, and loops so the same
playbook behaves differently depending on the host, the group, and the
environment it's running against.

Environment: 3 EC2 instances (Amazon Linux 2) — `web-server`, `db-server`, `app-server`.

---

## Task 1: Variables in Playbooks

`variables-demo.yml` defines `app_name`, `app_port`, `app_dir`, and a
`packages` list directly in the playbook `vars:` block, then uses them via
Jinja2 `{{ }}` interpolation in `debug`, `file`, and `yum` tasks.

**First run (default vars):**
```
TASK [Print app details]
ok: [web-server] => { "msg": "Deploying terraweek-app on port 8080 to /opt/terraweek-app" }
ok: [db-server]  => { "msg": "Deploying terraweek-app on port 8080 to /opt/terraweek-app" }
ok: [app-server] => { "msg": "Deploying terraweek-app on port 8080 to /opt/terraweek-app" }

PLAY RECAP
app-server : ok=4  changed=2  failed=0
db-server  : ok=4  changed=2  failed=0
web-server : ok=4  changed=2  failed=0
```

**Override from CLI with `-e`:**
```bash
ansible-playbook variables-demo.yml -i inventory.ini -e "app_name=my-custom-app app_port=9090"
```
```
TASK [Print app details]
ok: [web-server] => { "msg": "Deploying my-custom-app on port 9090 to /opt/my-custom-app" }
ok: [db-server]  => { "msg": "Deploying my-custom-app on port 9090 to /opt/my-custom-app" }
ok: [app-server] => { "msg": "Deploying my-custom-app on port 9090 to /opt/my-custom-app" }
```

**Verified:** Yes — the CLI `-e` variable completely overrode the playbook's
own `vars:` block. `app_name` and `app_port` both changed, and since `app_dir`
is templated from `app_name` (`"/opt/{{ app_name }}"`), it updated
automatically too.

---

## Task 2: group_vars and host_vars

**Directory structure created:**
```
ansible-practice/
├── inventory.ini
├── group_vars/
│   ├── all.yml
│   ├── web.yml
│   └── db.yml
├── host_vars/
│   └── web-server.yml
└── playbooks/
    └── site.yml
```

`group_vars/all.yml` (applies to every host):
```yaml
ntp_server: pool.ntp.org
app_env: development
common_packages:
  - vim
  - htop
  - tree
```

`group_vars/web.yml` (web group only):
```yaml
http_port: 80
max_connections: 1000
web_packages:
  - nginx
```

`group_vars/db.yml` (db group only):
```yaml
db_port: 3306
db_packages:
  - mysql-server
```

`host_vars/web-server.yml` (this specific host only):
```yaml
max_connections: 2000
custom_message: "This is the primary web server"
```

**Running `site.yml`:**
```
PLAY [Apply common config]
TASK [Show environment]
ok: [web-server] => { "msg": "Environment: development" }
ok: [db-server]  => { "msg": "Environment: development" }
ok: [app-server] => { "msg": "Environment: development" }

PLAY [Configure web servers]
TASK [Show web config]
ok: [web-server] => { "msg": "HTTP port: 80, Max connections: 2000" }

TASK [Show host-specific message]
ok: [web-server] => { "msg": "This is the primary web server" }

PLAY RECAP
app-server : ok=3  changed=1  failed=0
db-server  : ok=3  changed=1  failed=0
web-server : ok=6  changed=1  failed=0
```

**Variable precedence observed:**
`max_connections` was defined as `1000` in `group_vars/web.yml`, but the
report for `web-server` shows `2000` — the value from
`host_vars/web-server.yml`. This directly demonstrates:

```
host_vars > group_vars/<group> > group_vars/all > playbook vars
```
and (from Task 1) `-e` (extra vars) overrides everything, including
host_vars.

---

## Task 3: Ansible Facts

Ran `ansible web-server -m setup` and filtered specific facts:

```bash
ansible web-server -i inventory.ini -m setup -a "filter=ansible_os_family"
# → "ansible_os_family": "RedHat"

ansible web-server -i inventory.ini -m setup -a "filter=ansible_distribution*"
# → "ansible_distribution": "Amazon", "ansible_distribution_version": "2", "ansible_distribution_major_version": "2"

ansible web-server -i inventory.ini -m setup -a "filter=ansible_memtotal_mb"
# → "ansible_memtotal_mb": 966

ansible web-server -i inventory.ini -m setup -a "filter=ansible_default_ipv4"
# → address: 172.31.80.87, gateway: 172.31.80.1, network: 172.31.80.0, netmask: 255.255.240.0
```

`facts-demo.yml` output:
```
TASK [Show OS info]
ok: [web-server] => { "msg": "Hostname: ip-172-31-80-87, OS: Amazon 2, RAM: 966MB, IP: 172.31.80.87\n" }
ok: [db-server]  => { "msg": "Hostname: ip-172-31-83-34, OS: Amazon 2, RAM: 966MB, IP: 172.31.83.34\n" }
ok: [app-server] => { "msg": "Hostname: ip-172-31-80-91, OS: Amazon 2, RAM: 966MB, IP: 172.31.80.91\n" }

TASK [Show all network interfaces]
ok: [web-server] => { "ansible_interfaces": ["lo", "eth0"] }
```

**Five useful facts and where I'd use them in real playbooks:**

| Fact | Real-world use |
|---|---|
| `ansible_distribution` / `ansible_distribution_major_version` | Branch package-manager logic (`yum` vs `apt`) and pick correct package names per OS |
| `ansible_memtotal_mb` | Decide whether to install memory-heavy services (e.g. skip Elasticsearch on small nodes) or trigger low-memory alerts |
| `ansible_default_ipv4.address` | Auto-populate config files (nginx, app configs) with the host's real IP without hardcoding |
| `ansible_hostname` / `inventory_hostname` | Tag logs, reports, and monitoring dashboards per-server |
| `ansible_os_family` | Broad conditionals across many distros at once (`RedHat` vs `Debian`) instead of checking each distro name individually |

---

## Task 4: Conditionals with `when`

`conditional-demo.yml` ran with `when` conditions gating each task by group
membership, OS, memory, and environment.

**Note on package names:** the original demo used `nginx` and `mysql-server`,
which aren't available in Amazon Linux 2's default repos (`amazon-linux-extras`
territory). I swapped these for `httpd` and `mariadb`, which install cleanly
on Amazon Linux 2 — the conditional logic itself is unaffected either way.

**Final run — clean, `failed=0` across all hosts:**
```
TASK [Install Apache (only on web servers)]
skipping: [db-server]
skipping: [app-server]
changed: [web-server]

TASK [Install MariaDB (only on db servers)]
skipping: [web-server]
skipping: [app-server]
changed: [db-server]

TASK [Show warning on low memory hosts]
ok: [web-server] => "WARNING: This host has less than 1GB RAM"
ok: [db-server]  => "WARNING: This host has less than 1GB RAM"
ok: [app-server] => "WARNING: This host has less than 1GB RAM"

TASK [Run only on Amazon Linux]
ok: [web-server] / ok: [db-server] / ok: [app-server]  → all matched

TASK [Run only on Ubuntu]
skipping: [web-server] / skipping: [db-server] / skipping: [app-server]

TASK [Run only in production]
skipping: [web-server] / skipping: [db-server] / skipping: [app-server]

TASK [Multiple conditions (AND)]
ok: [web-server] => "Web server with enough memory"
skipping: [db-server] / skipping: [app-server]

TASK [OR condition]
ok: [web-server] => "Either web or app server"
ok: [app-server] => "Either web or app server"
skipping: [db-server]

PLAY RECAP
app-server : ok=4  changed=0  failed=0  skipped=5
db-server  : ok=4  changed=1  failed=0  skipped=5
web-server : ok=6  changed=1  failed=0  skipped=3
```

**Verified:** Yes — every task skipped or executed exactly on the hosts it
should have, based on group membership, distro, memory, and combined
AND/OR logic.

---

## Task 5: Loops

`loops-demo.yml` used `loop` to create multiple users, directories, and
install multiple packages in a single task block each, instead of writing
one task per item.

```
TASK [Create multiple users]
changed: [web-server] => (item=deploy)
changed: [web-server] => (item=monitor)
changed: [web-server] => (item=appuser)
... (same for db-server, app-server)

TASK [Create multiple directories]
changed: [web-server] => (item=/opt/app/logs)
changed: [web-server] => (item=/opt/app/config)
changed: [web-server] => (item=/opt/app/data)
changed: [web-server] => (item=/opt/app/tmp)

TASK [Install multiple packages]
ok: [web-server] => (item=git)
ok: [web-server] => (item=curl)
ok: [web-server] => (item=unzip)
changed: [web-server] => (item=jq)

TASK [Print each user created]
ok: [web-server] => (item={'name': 'deploy', 'groups': 'wheel'})  => "Created user deploy in group wheel"
ok: [web-server] => (item={'name': 'monitor', 'groups': 'wheel'}) => "Created user monitor in group wheel"
ok: [web-server] => (item={'name': 'appuser', 'groups': 'users'}) => "Created user appuser in group users"

PLAY RECAP
app-server : ok=5  changed=3  failed=0
db-server  : ok=5  changed=3  failed=0
web-server : ok=5  changed=3  failed=0
```

Each loop iteration was reported as its own line in the output (`item=...`),
confirming Ansible ran the task once per list element rather than treating
the list as a single unit.

**`loop` vs `with_items`:** `loop` is the modern, recommended keyword.
`with_items` is the older, legacy syntax and is now considered deprecated
style. Functionally they're similar for a plain list, but `loop` is more
consistent — it works the same way regardless of the input source (a list,
a dict via filters, etc.), whereas the old style needed a different
`with_*` keyword for each kind of source (`with_dict`, `with_file`,
`with_fileglob`, etc.), each backed by a different lookup plugin. Ansible's
official docs recommend `loop` for all new playbooks.

---

## Task 6: Register, Debug, and Combine Everything

`server-report.yml` combined `register`, facts, conditionals, and file output
into one real-world health report.

```
TASK [Generate report]
ok: [web-server] => {
  "msg": [
    "========== web-server ==========",
    "OS: Amazon 2",
    "IP: 172.31.80.87",
    "RAM: 966MB",
    "Disk: /dev/xvda1  8.0G  1.9G  6.2G  23% /",
    "Running services (first 20): 20"
  ]
}
... (same structure for db-server and app-server)

TASK [Flag if disk is critically low]
skipping: [web-server] / skipping: [db-server] / skipping: [app-server]
(disk usage was 23-25% on all hosts — well below the alert threshold, so
 skipping here is the correct/expected result)

TASK [Save report to file]
changed: [web-server] / changed: [db-server] / changed: [app-server]

PLAY RECAP
app-server : ok=6  changed=4  failed=0  skipped=1
db-server  : ok=6  changed=4  failed=0  skipped=1
web-server : ok=6  changed=4  failed=0  skipped=1
```

**Verified — report files read back from each server:**

`/tmp/server-report-web-server.txt`
```
Server: web-server
OS: Amazon 2
IP: 172.31.80.87
RAM: 966MB
Disk: /dev/xvda1  8.0G  1.9G  6.2G  23%  /
Checked at: 2026-08-24T18:08:24Z
```

`/tmp/server-report-app-server.txt`
```
Server: app-server
OS: Amazon 2
IP: 172.31.80.91
RAM: 966MB
Disk: /dev/xvda1  8.0G  2.0G  6.1G  25%  /
Checked at: 2026-08-24T18:08:24Z
```

`/tmp/server-report-db-server.txt`
```
Server: db-server
OS: Amazon 2
IP: 172.31.83.34
RAM: 966MB
Disk: /dev/xvda1  8.0G  1.9G  6.2G  24%  /
Checked at: 2026-08-24T18:08:24Z
```

All three files matched the live playbook output exactly, confirming
`register` correctly captured command output and `copy` wrote it to disk
per-host using `inventory_hostname`.

---

## Key Takeaways

- Variables can come from playbook `vars:`, `group_vars/`, `host_vars/`, or
  the CLI (`-e`) — and Ansible resolves conflicts using a strict precedence
  order, with `-e` always winning.
- Facts (`ansible_*`) are auto-gathered from every managed host and let a
  single playbook adapt itself per-host without manual configuration.
- `when` conditionals let tasks selectively run based on group membership,
  OS, resource levels, or custom variables — including AND/OR logic.
- `loop` replaces repetitive copy-pasted tasks with a single reusable block
  driven by a list or list-of-dicts.
- `register` + `debug` + `copy` together turn ad-hoc checks into a
  structured, saved report — the foundation of real infrastructure
  auditing and monitoring playbooks.

---

## Screenshots

Screenshots below are in the order the tasks were completed (Task 1 → Task 6).
![alt text](<screenshots/Screenshot (940).png>) ![alt text](<screenshots/Screenshot (941).png>) ![alt text](<screenshots/Screenshot (942).png>) ![alt text](<screenshots/Screenshot (943).png>) ![alt text](<screenshots/Screenshot (944).png>) ![alt text](<screenshots/Screenshot (945).png>) ![alt text](<screenshots/Screenshot (946).png>) ![alt text](<screenshots/Screenshot (947).png>) ![alt text](<screenshots/Screenshot (948).png>) ![alt text](<screenshots/Screenshot (949).png>) ![alt text](<screenshots/Screenshot (950).png>) ![alt text](<screenshots/Screenshot (951).png>) ![alt text](<screenshots/Screenshot (952).png>) ![alt text](<screenshots/Screenshot (953).png>) ![alt text](<screenshots/Screenshot (958).png>) ![alt text](<screenshots/Screenshot (959).png>) ![alt text](<screenshots/Screenshot (960).png>) ![alt text](<screenshots/Screenshot (961).png>) ![alt text](<screenshots/Screenshot (962).png>) ![alt text](<screenshots/Screenshot (963).png>) ![alt text](<screenshots/Screenshot (965).png>) ![alt text](<screenshots/Screenshot (967).png>)