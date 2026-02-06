# Day 12 – Revision & Consolidation (Days 01–11)

## Review Summary

Today I took a breather to consolidate everything learned from Days 01–11. As a frontend engineer transitioning to DevOps, this revision helped reinforce fundamental Linux commands and system management concepts.

---

## Commands Practiced

### 1. File Permissions (`chmod`)
**Screenshot Reference:** Screenshot 1

- Created a file: `echo "Hello Linux" > day6_demo.txt`
- Initially attempted incorrect syntax: `chmod day6_demo.txt` (missing permission mode)
- Correctly applied permissions: `chmod 775 day6_demo.txt`
- Verified with: `ls -l day6_demo.txt`
  - Result: `-rwxrwxr-x` (owner: rwx, group: rwx, others: r-x)
  - Owner: `avigho`, Group: `avigho`, Size: 12 bytes

**Key Learning:** Always specify permission mode (numeric or symbolic) before the filename in `chmod`.

---

### 2. File Ownership (`chown`)
**Screenshot Reference:** Screenshot 2 & Screenshot 4

**Single File Practice:**
- Attempted: `sudo chown berlin:planner day6_demo.txt` ❌ (invalid user/group)
- Successfully changed: `sudo chown nairobi:vault-team day6_demo.txt` ✅
- Verified: `ls -l day6_demo.txt` showed owner `nairobi` and group `vault-team`

**Multiple Files Practice (bank-heist directory):**
- `sudo chown Tokyo:vault-team bank-heist/access-codes.txt` ✅
- `sudo chown Berlin:tech-team bank-heist/blueprints.pdf` ✅
- `sudo chown nairobi:vault-team bank-heist/escape-plan.txt` ✅
- Verified with: `ls -l bank-heist/`

**Key Learning:** User and group names are case-sensitive. Use lowercase consistently (`nairobi` not `Nairobi`).

---

### 3. Directory Creation (`mkdir`)
**Screenshot Reference:** Screenshot 3

- Attempted: `mskdir team_devops/learninflow` ❌ (typo: `mskdir`)
- Attempted: `mkdir team_devops/learninflow` ❌ (parent directory doesn't exist)
- Successfully created nested directories: `mkdir -p team_devops/learninflow` ✅
- Verified with: `ls -l` showing `drwxr-xr-x 3 avigho avigho 4096 Feb 6 17:53 team_devops`

**Key Learning:** Use `-p` flag to create parent directories automatically if they don't exist.

---

### 4. Process Management (`ps`)
**Screenshot Reference:** Screenshot 4

- Checked running processes: `ps`
  - Output showed: `bash` (PID 527) and `ps` (PID 4280)
- Consulted manual: `man ps` for more options

**Key Learning:** Basic `ps` shows processes in current terminal. Use `ps aux` for all processes system-wide.

---

### 5. Service Management (`systemctl`)
**Screenshot Reference:** Screenshot 4

- Checked Nginx service status: `systemctl status nginx`
  - Status: `active (running)` since Feb 5, 2026
  - Service: enabled (starts on boot)
  - Main PID: 234 (master process)
  - Worker processes: 236, 237, 238, 239
  - Memory: 4.2M (peak: 5.3M)
- Consulted manual: `man systemctl`

**Key Learning:** `systemctl status <service>` provides comprehensive service health information including process IDs, memory usage, and uptime.

---

### 6. Log Management (`journalctl`)
**Screenshot Reference:** Screenshot 4

- Attempted: `journalctl nginx` ❌ (invalid argument)
- Successfully retrieved logs: `sudo journalctl -u nginx > systemlog-nginx.txt` ✅
- Viewed logs: `cat systemlog-nginx.txt`
  - Logs showed Nginx service starts/stops from September 23-24

**Key Learning:** Use `-u` flag to specify unit name. Always use `sudo` for `journalctl` when accessing system service logs.

---

## Mindset & Plan Review

**Revisited Day 01 Learning Plan:**
- ✅ Goals remain aligned: Dockerize frontend app, AWS infra with Terraform, ArgoCD for GitOps
- ✅ Schedule maintained: 6 days learning + 1 day revision per week
- ✅ Focus areas: File permissions, service management, and system monitoring are foundational for DevOps

**Adjustments:**
- Need more practice with `journalctl` flags and filtering options
- Should create a personal cheat sheet for common `chmod` numeric values

---

## Mini Self-Check Answers

### 1) Which 3 commands save you the most time right now, and why?

1. **`ls -l`** - Instantly shows file permissions, ownership, size, and timestamps. Essential for debugging permission issues.
2. **`systemctl status <service>`** - One command gives complete service health overview (status, PIDs, memory, uptime). Faster than checking multiple sources.
3. **`mkdir -p`** - Creates nested directory structures in one command instead of multiple `mkdir` calls. Saves time when setting up project structures.

---

### 2) How do you check if a service is healthy? List the exact 2–3 commands you'd run first.

1. **`systemctl status <service-name>`** - Primary check for service state, process IDs, and recent activity
2. **`sudo journalctl -u <service-name> -n 50`** - View last 50 log entries to identify any errors or warnings
3. **`ps aux | grep <service-name>`** - Verify processes are actually running (double-check if status shows running but something seems off)

---

### 3) How do you safely change ownership and permissions without breaking access? Give one example command.

**Safe approach:**
1. First verify current ownership: `ls -l <file>`
2. Check if the target user/group exists: `id <username>` or `getent group <groupname>`
3. Change ownership: `sudo chown <user>:<group> <file>`
4. Verify the change: `ls -l <file>`

**Example:**
```bash
# Verify current state
ls -l day6_demo.txt

# Check user/group exists
id nairobi
getent group vault-team

# Make the change
sudo chown nairobi:vault-team day6_demo.txt

# Verify
ls -l day6_demo.txt
```

**Why this is safe:** Verifying user/group existence prevents errors, and checking before/after ensures the change worked correctly without breaking access.

---

### 4) What will you focus on improving in the next 3 days?

1. **Advanced `journalctl` usage** - Learn filtering by time ranges, log levels, and combining with grep for better log analysis
2. **Process management** - Practice `ps aux`, `top`, `htop`, and understanding process trees
3. **File system navigation** - Master `find`, `grep`, and combining commands with pipes for efficient file operations
4. **Service troubleshooting workflow** - Build a systematic approach: check status → check logs → check processes → check dependencies

---

## Key Takeaways

### What I Reinforced Today:
- ✅ File permissions (`chmod`) require explicit mode specification
- ✅ File ownership (`chown`) is case-sensitive and requires valid user/group names
- ✅ Directory creation with `mkdir -p` handles nested structures elegantly
- ✅ Service health checks require multiple commands for complete picture
- ✅ Always verify changes with `ls -l` after permission/ownership modifications

### Commands I Now Remember Confidently:
- **`chmod 775 <file>`** - Sets rwx for owner/group, r-x for others
- **`sudo chown user:group <file>`** - Changes ownership (remember case sensitivity!)
- **`mkdir -p path/to/nested/dir`** - Creates parent directories automatically
- **`systemctl status <service>`** - Comprehensive service health check
- **`sudo journalctl -u <service> -n 50`** - View recent service logs

### Areas Needing More Practice:
- `journalctl` filtering and advanced options
- Process management with `ps aux` and understanding output
- Combining commands with pipes for efficient workflows

---

## Screenshots Documentation

1. **Screenshot 1:** File creation and `chmod` practice (day6_demo.txt with 775 permissions)
2. **Screenshot 2:** `chown` practice (changing ownership to nairobi:vault-team)
3. **Screenshot 3:** `mkdir -p` practice (creating nested directory structure)
4. **Screenshot 4:** Comprehensive practice session (chown, ps, systemctl status nginx, journalctl)

---

## Next Steps

- Continue with Day 13 content
- Practice `journalctl` filtering options
- Create a personal command cheat sheet
- Start thinking about how these Linux fundamentals apply to containerization (Docker)


Screenshot (118).png
Screenshot (115).png
Screenshot (116).png
Screenshot (117).png