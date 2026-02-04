# Day 09 Challenge — Linux User & Group Management 🧑‍💻

## Summary
Practice creating users and groups, assigning group membership, and setting up shared directories with proper group permissions. Add screenshots of your command outputs into `screenshots/` and reference them below.

---

## Users & Groups Created
- Users: `tokyo`, `berlin`, `professor`, `nairobi`
- Groups: `developers`, `admins`, `project-team`

---

## Group Assignments
- `tokyo`: developers, project-team
- `berlin`: developers, admins
- `professor`: admins
- `nairobi`: project-team

(Verify with `id username` or `groups username`.)

---

## Directories Created
- `/opt/dev-project` — group: `developers` — perms: `775` (rwxrwxr-x), setgid recommended (`chmod g+s`)
- `/opt/team-workspace` — group: `project-team` — perms: `775`, setgid recommended (`chmod g+s`)

(Verify with `ls -ld /opt/dev-project /opt/team-workspace`.)

---

## Commands Used (examples)

### Create users + set password
```
sudo useradd -m -s /bin/bash tokyo
sudo passwd tokyo

sudo useradd -m -s /bin/bash berlin
sudo passwd berlin

sudo useradd -m -s /bin/bash professor
sudo passwd professor

sudo useradd -m -s /bin/bash nairobi
sudo passwd nairobi
```

### Create groups
```
sudo groupadd developers
sudo groupadd admins
sudo groupadd project-team
```

### Add users to groups
```
sudo usermod -aG developers tokyo
sudo usermod -aG developers,admins berlin
sudo usermod -aG admins professor
sudo usermod -aG project-team nairobi
sudo usermod -aG project-team tokyo
```

### Create shared directories and set permissions
```
sudo mkdir -p /opt/dev-project
sudo chgrp developers /opt/dev-project
sudo chmod 775 /opt/dev-project
sudo chmod g+s /opt/dev-project    # optional: inherit group for new files

sudo mkdir -p /opt/team-workspace
sudo chgrp project-team /opt/team-workspace
sudo chmod 775 /opt/team-workspace
sudo chmod g+s /opt/team-workspace
```

### Test file creation as another user
```
sudo -u tokyo touch /opt/dev-project/tokyo.txt
sudo -u berlin touch /opt/dev-project/berlin.txt
sudo -u nairobi touch /opt/team-workspace/nairobi.txt
```

---

## Verification Commands (examples)
- `grep '^tokyo:' /etc/passwd` — user exists
- `ls -ld /home/tokyo /home/berlin /home/professor /home/nairobi` — home dirs exist
- `getent group developers admins project-team` — groups exist
- `id tokyo` / `id berlin` / `id professor` / `id nairobi` — check memberships
- `ls -ld /opt/dev-project /opt/team-workspace` — check group and perms
- `ls -l /opt/dev-project /opt/team-workspace` — check created files

---


---

## What I Learned
1. Creating users with `useradd -m` and setting passwords with `passwd` creates functioning accounts quickly.
2. Adding users to supplementary groups with `usermod -aG` is safer than editing `/etc/group` directly.
3. Setting the setgid bit (`chmod g+s`) on shared directories helps new files inherit the directory group.

---

## Troubleshooting Notes
- If a user doesn’t see new group membership, they may need to log out/log in or run `newgrp groupname`.
- If `touch` complains permission denied, re-check group owner (`ls -ld`) and permissions (`chmod`) and ensure user is in the correct group.

---
![alt text](<Screenshot (106).png>) ![alt text](<Screenshot (95).png>) ![alt text](<Screenshot (96).png>) ![alt text](<Screenshot (97).png>) ![alt text](<Screenshot (98).png>) ![alt text](<Screenshot (99).png>) ![alt text](<Screenshot (100).png>) ![alt text](<Screenshot (101).png>) ![alt text](<Screenshot (102).png>) ![alt text](<Screenshot (103).png>) ![alt text](<Screenshot (104).png>) ![alt text](<Screenshot (105).png>)