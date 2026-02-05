# Day 11 Challenge - File Ownership & Permissions

## Files & Directories Created

### Task 1 - Understanding Ownership
- Files examined in home directory
- Analyzed permission format: `-rw-r--r-- 1 owner group size date filename`

### Task 2 - Basic chown Operations
- `devops-file.txt` - Created and ownership changed

### Task 3 - Basic chgrp Operations
- `team-notes.txt` - Created and group changed

### Task 4 - Combined Owner & Group Change
- `project-config.yaml` - Created with combined ownership
- `app-logs/` - Directory created with combined ownership

### Task 5 - Recursive Ownership
```
heist-project/
├── vault/
│   └── gold.txt
└── plans/
    └── strategy.conf
```

### Task 6 - Practice Challenge
```
bank-heist/
├── access-codes.txt
├── blueprints.pdf
└── escape-plan.txt
```

---

## Ownership Changes

| File/Directory | Before | After | Task |
|---|---|---|---|
| devops-file.txt | avigho:avigho | berlin:avigho | Task 2 |
| team-notes.txt | avigho:avigho | avigho:team-heist | Task 3 |
| project-config.yaml | avigho:avigho | professor:team-heist | Task 4 |
| app-logs/ | avigho:avigho | berlin:team-heist | Task 4 |
| heist-project/ (recursive) | avigho:avigho | professor:planners | Task 5 |
| access-codes.txt | avigho:avigho | tokyo:vault-team | Task 6 |
| blueprints.pdf | avigho:avigho | berlin:tech-team | Task 6 |
| escape-plan.txt | avigho:avigho | nairobi:vault-team | Task 6 |

---

## Commands Used

### User & Group Creation
```bash
# Create users
sudo useradd tokyo
sudo useradd berlin
sudo useradd nairobi
sudo useradd professor

# Create groups
sudo groupadd team-heist
sudo groupadd planners
sudo groupadd vault-team
sudo groupadd tech-team
```

### Task 2: Basic chown
```bash
touch devops-file.txt
ls -l devops-file.txt
sudo chown tokyo devops-file.txt
sudo chown berlin devops-file.txt
ls -l devops-file.txt
```

### Task 3: Basic chgrp
```bash
touch team-notes.txt
ls -l team-notes.txt
sudo groupadd team-heist
sudo chgrp team-heist team-notes.txt
ls -l team-notes.txt
```

### Task 4: Combined chown
```bash
touch project-config.yaml
sudo chown professor:team-heist project-config.yaml
mkdir app-logs
sudo chown berlin:team-heist app-logs/
ls -l project-config.yaml app-logs/
```

### Task 5: Recursive chown
```bash
mkdir -p heist-project/vault
mkdir -p heist-project/plans
touch heist-project/vault/gold.txt
touch heist-project/plans/strategy.conf
sudo groupadd planners
sudo chown -R professor:planners heist-project/
ls -lR heist-project/
```

### Task 6: Practice Challenge
```bash
# Create directory and files
mkdir bank-heist
touch bank-heist/access-codes.txt
touch bank-heist/blueprints.pdf
touch bank-heist/escape-plan.txt

# Create users and groups (if not already created)
sudo useradd tokyo
sudo useradd berlin
sudo useradd nairobi
sudo groupadd vault-team
sudo groupadd tech-team

# Change ownership for each file
sudo chown tokyo:vault-team bank-heist/access-codes.txt
sudo chown berlin:tech-team bank-heist/blueprints.pdf
sudo chown nairobi:vault-team bank-heist/escape-plan.txt

# Verify
ls -l bank-heist/
```

---

## Key Concepts Learned

### 1. File Ownership Structure
- **Owner (User)**: The individual who created the file or owns it
- **Group**: A collection of users with shared permissions
- **Format**: `-rw-r--r-- 1 owner group size date filename`
- First column after count shows: user permissions, group permissions, other permissions

### 2. chown vs chgrp vs Combined
- **chown**: Changes the owner of a file/directory
  - `sudo chown newowner filename`
  - Can also change group: `sudo chown newowner:newgroup filename`
- **chgrp**: Changes only the group of a file/directory
  - `sudo chgrp newgroup filename`
- **Combined**: Most efficient when changing both
  - `sudo chown owner:group filename`

### 3. Recursive Operations (-R flag)
- **Critical for DevOps**: When managing directories with multiple files
- `-R` flag applies changes to directory AND all contents recursively
- Example: `sudo chown -R owner:group directory/`
- Useful for:
  - Container file permissions
  - Application deployment directories
  - CI/CD artifact management
  - Shared team directories

---

Screen-shot added:-
![alt text](<Screenshot (114).png>) ![alt text](<Screenshot (110).png>) ![alt text](<Screenshot (111).png>) ![alt text](<Screenshot (112).png>) ![alt text](<Screenshot (113).png>)
