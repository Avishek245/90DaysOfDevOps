# Day 71 -- Roles, Galaxy, Templates and Vault

## Overview
Today's lab covered structuring Ansible automation using **Roles**, generating dynamic configs with **Jinja2 Templates**, pulling community automation from **Ansible Galaxy**, and protecting sensitive data with **Ansible Vault**.

Infrastructure was re-provisioned via `terraform apply` at the start of the day (previous day's EC2 instances had been destroyed). Since WSL/Ansible wasn't available locally on Windows, one EC2 instance (the `app` server) was used as the Ansible control node -- Ansible was installed on it directly and used to manage itself and the other two nodes (`web`, `db`) over SSH.

**Environment:**
- Control node: `app-server` (3.88.66.77) -- Ansible 2.9.23 on Amazon Linux 2
- Managed nodes: `web-server` (3.84.72.138), `db-server` (44.201.201.45)
- Inventory: `inventory.ini` with `[web]`, `[app]`, `[db]` groups

---

## Task 1: Jinja2 Templates

Created `templates/nginx-vhost.conf.j2`, a Jinja2 template rendering an Nginx server block using variables (`app_name`, `http_port`) and Ansible facts (`ansible_hostname`).

Ran `template-demo.yml` with `--diff` against the `web` host. Since Amazon Linux 2 doesn't ship Nginx in its base repos, an extra task was needed to enable the extras repo first:

```yaml
- name: Enable nginx extras repo
  command: amazon-linux-extras enable nginx1
```

**Rendered output** (verified via `curl http://3.84.72.138`):
```
<h1>terraweek-app</h1><p>Host: ip-172-31-84-153 | IP: 172.31.84.153</p>
```

The `--diff` flag showed the template rendering `{{ ansible_hostname }}`, `{{ app_name }}`, and `{{ http_port | default(80) }}` into real values -- confirming Jinja2 variable substitution worked correctly end-to-end.

---

## Task 2: Role Structure

Generated a role skeleton with:
```bash
ansible-galaxy init roles/webserver
```

This created the standard role directory layout:
```
roles/webserver/
  tasks/main.yml
  handlers/main.yml
  templates/
  files/
  vars/main.yml
  defaults/main.yml
  meta/main.yml
  README.md
  tests/
```

### `vars/main.yml` vs `defaults/main.yml`

- **`defaults/main.yml`** -- **lowest priority** in Ansible's variable precedence chain. Meant to be easily overridden by the playbook calling the role, inventory variables, or `-e` extra vars. Used for sensible defaults a caller might reasonably want to change (e.g. `http_port: 80`).
- **`vars/main.yml`** -- **much higher priority**, near the top of the precedence chain. Meant for constants the role author does *not* want casually overridden -- internal values the role depends on to function correctly.

**Rule of thumb:** if a caller should reasonably override it → `defaults/`. If it's an internal constant → `vars/`.

---

## Task 3: Custom Webserver Role

Built a full `webserver` role from scratch:

- **`defaults/main.yml`** -- `http_port`, `app_name`, `max_connections`
- **`tasks/main.yml`** -- enables the nginx extras repo, installs Nginx, deploys `nginx.conf` and vhost config from templates, creates the web root, deploys the index page, starts/enables the service
- **`handlers/main.yml`** -- restarts Nginx on config change
- **`templates/`** -- `nginx.conf.j2`, `vhost.conf.j2`, `index.html.j2`

Called the role from `site.yml`:
```yaml
- name: Configure web servers
  hosts: web
  become: true
  roles:
    - role: webserver
      vars:
        app_name: terraweek
        http_port: 80
```

**Result:** `ok=9 changed=7 failed=0`

One gotcha hit: both Task 1's standalone vhost config and the role's vhost config used the same `server_name` (`{{ ansible_hostname }}`), so Nginx picked whichever config file sorted first alphabetically. Removed the stale Task 1 config (`terraweek-app.conf`) and restarted Nginx.

**Verified rendered page:**
```
<h1>terraweek</h1>
<p>Server: ip-172-31-84-153</p>
<p>IP: 172.31.84.153</p>
<p>Environment: development</p>
<p>Managed by Ansible</p>
```

---

## Task 4: Ansible Galaxy -- Community Roles

1. **Searched** Galaxy: `ansible-galaxy search nginx --platforms EL` → 809 matching roles found, confirming search functionality.
2. **Installed** a role: `ansible-galaxy install geerlingguy.docker` → installed version 8.0.0 successfully.
3. **Listed** installed roles: `ansible-galaxy list` → confirmed `geerlingguy.docker` present.
4. **Used `requirements.yml`** to pin versions and install multiple roles at once:
   ```yaml
   roles:
     - name: geerlingguy.docker
       version: "7.4.1"
     - name: geerlingguy.ntp
   ```
   Installed with `ansible-galaxy install -r requirements.yml --force`, which downgraded Docker to the pinned 7.4.1 and added `geerlingguy.ntp` 4.0.0.

### Why `requirements.yml` over manual installs?
`requirements.yml` makes role dependencies **declarative, versioned, and reproducible**. Instead of remembering (or documenting separately) which roles and versions a project needs, the file itself is the source of truth -- anyone cloning the repo runs one command (`ansible-galaxy install -r requirements.yml`) to get an identical, pinned set of roles. This avoids "works on my machine" drift, supports CI/CD pipelines cleanly, and lets you lock a specific tested version instead of silently picking up breaking changes from a role's latest release.

### Known limitation encountered
Running `geerlingguy.docker` (both v8.0.0 and v7.4.1) against Amazon Linux 2 failed at the "Install Docker packages" step:
```
Failure talking to yum: ... download.docker.com/linux/centos/2/x86_64/stable/repodata/repomd.xml:
[Errno 14] HTTPS Error 404 - Not Found
```
The role's CentOS/RHEL-targeted logic builds a Docker CE repo URL assuming CentOS, but Amazon Linux 2 isn't CentOS despite being RPM-based -- so the URL 404s. A direct `amazon-linux-extras install docker` attempt also failed, because the broken `docker-ce-stable` repo file left behind by the role blocked all subsequent yum operations until it was manually removed (`rm /etc/yum.repos.d/docker-ce.repo && yum clean all`).

**Takeaway:** this is a real-world illustration of why community roles built for one OS family don't always translate cleanly to another, even within the same package-manager ecosystem (RPM/yum). The Galaxy search → install → requirements.yml → playbook workflow itself worked correctly at every step; only the role's internal OS-detection logic was incompatible with Amazon Linux 2.

---

## Task 5: Ansible Vault -- Encrypt Secrets

1. **Created** an encrypted vault file:
   ```bash
   ansible-vault create group_vars/db/vault.yml
   ```
   containing `vault_db_password`, `vault_db_root_password`, `vault_api_key`. Confirmed encrypted at rest with `cat` (showed `$ANSIBLE_VAULT;1.1;AES256` ciphertext, not plaintext).

2. **Viewed** without editing:
   ```bash
   ansible-vault view group_vars/db/vault.yml
   ```
   Correctly decrypted and displayed the plaintext YAML after entering the vault password.

3. **Edited** the encrypted file:
   ```bash
   ansible-vault edit group_vars/db/vault.yml
   ```

4. **Encrypted an existing plaintext file:**
   ```bash
   ansible-vault encrypt group_vars/db/secrets.yml
   ```
   Confirmed with "Encryption successful" and verified ciphertext via `cat`.

5. **Used vault variables in a playbook** (`db-setup.yml`), run two ways:
   - `--ask-vault-pass` (interactive prompt) -- worked, returned `"DB password is set: True"`.
   - `--vault-password-file .vault_pass` (password stored in a file, chmod 600, added to `.gitignore`) -- also worked once the password file's contents were confirmed to exactly match the vault's actual password.

### Lesson learned: password file mismatches
The most time-consuming part of today was **not** a technical Ansible problem -- it was a mismatch between the password typed interactively at `ansible-vault create`/`rekey` prompts (invisible while typing, easy to mistype) and the string saved into `.vault_pass`. The fix was to bypass interactive typing entirely by creating/viewing the vault using `--vault-password-file` from the start, so the password was only ever "entered" once, into a file, and never re-typed at a masked prompt.

### Why `--vault-password-file` is better than `--ask-vault-pass` for CI/CD
`--ask-vault-pass` requires an interactive human to type the password at a prompt -- in an automated pipeline there is no human present, so the pipeline would hang indefinitely waiting for input. `--vault-password-file` lets Ansible read the password programmatically from a file (often itself populated from a secrets manager or CI secret store), enabling fully unattended, automated runs. The password file is excluded from version control via `.gitignore` so the vault's key is never committed alongside the encrypted data it protects.

---

## Task 6: Combine Roles, Templates, and Vault

Final `site.yml` combining everything from today:

```yaml
- name: Configure web servers
  hosts: web
  become: true
  roles:
    - role: webserver
      vars:
        app_name: terraweek
        http_port: 80

- name: Configure app servers with Docker
  hosts: app
  become: true
  roles:
    - geerlingguy.docker

- name: Configure database servers
  hosts: db
  become: true
  tasks:
    - name: Create DB config with secrets
      template:
        src: templates/db-config.j2
        dest: /etc/db-config.env
        owner: root
        mode: '0600'
```

`templates/db-config.j2` renders a `.env` file combining an Ansible fact, a default-filtered variable, and two Vault-encrypted secrets:
```jinja2
DB_HOST={{ ansible_default_ipv4.address }}
DB_PORT={{ db_port | default(3306) }}
DB_PASSWORD={{ vault_db_password }}
DB_ROOT_PASSWORD={{ vault_db_root_password }}
```

**Run:** `ansible-playbook -i inventory.ini site.yml --vault-password-file .vault_pass`

- **web play:** `ok=8, failed=0` ✅
- **app/Docker play:** failed at package install (documented OS-compat issue above)
- **db play:** `ok=2, changed=1, failed=0` ✅

**Verified on db-server:**
```
$ sudo cat /etc/db-config.env
# Database Configuration -- Managed by Ansible
DB_HOST=172.31.90.121
DB_PORT=3306
DB_PASSWORD=SuperSecretP@ssw0rd
DB_ROOT_PASSWORD=R00tP@ssw0rd123

$ sudo ls -l /etc/db-config.env
-rw------- 1 root root 147 Aug 26 19:22 /etc/db-config.env
```

Secrets decrypted correctly and the file permission is exactly `600` as required -- confirming the Vault → Template → Playbook pipeline works end-to-end.

---

## When to Use Roles vs Playbooks vs Ad-hoc Commands

| Approach | Best for |
|---|---|
| **Ad-hoc commands** (`ansible <host> -m <module>`) | One-off, throwaway tasks -- checking a service status, restarting something once, quick fact-gathering. Nothing reusable or version-controlled. |
| **Plain playbooks** | Small, self-contained automation for a specific one-time or lightly-repeated job -- a single deployment script, a migration, a demo. Fine when there's no need to share logic across projects. |
| **Roles** | Any automation you expect to reuse, share, or scale across multiple projects/servers -- installing and configuring a service (web server, database, monitoring agent) in a structured, testable, composable way. Roles separate tasks, handlers, templates, and variables into predictable locations, making large automation codebases maintainable as they grow. |

---

### Screenshot
![alt text](<Screenshot (980).png>) ![alt text](<Screenshot (981).png>) ![alt text](<Screenshot (982).png>) ![alt text](<Screenshot (984).png>) ![alt text](<Screenshot (985).png>) ![alt text](<Screenshot (986).png>) ![alt text](<Screenshot (989).png>) ![alt text](<Screenshot (990).png>) ![alt text](<Screenshot (991).png>) ![alt text](<Screenshot (992).png>) ![alt text](<Screenshot (996).png>) ![alt text](<Screenshot (997).png>) ![alt text](<Screenshot (998).png>)

## Summary

Today's work demonstrated the full lifecycle of production-style Ansible automation: structuring reusable roles, generating dynamic configuration with Jinja2, consuming (and troubleshooting) community roles via Galaxy, and protecting secrets with Vault -- then tying all four together in a single playbook that correctly provisioned a web server, attempted a Docker install, and rendered a secrets-backed config file with correct permissions on a database server.