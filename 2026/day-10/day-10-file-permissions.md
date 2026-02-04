# Day 10 Challenge ✅

## Files Created
- `devops.txt` — created with `touch devops.txt`
- `notes.txt` — created with `echo "Notes about permissions" > notes.txt`
- `script.sh` — created with `vim script.sh` and contents:

```bash
#!/bin/bash
echo "Hello DevOps"
```

---

## Permission Changes (before / after)

### script.sh
- **Before:** `-rw-r--r--` (no execute)
- **Command:** `chmod +x script.sh`
- **After:** `-rwxr-xr-x`
- **Verify:** `./script.sh` → outputs: `Hello DevOps`

### devops.txt
- **Before:** `-r---w---x` (as observed in `ls -l` output)
- **Command:** `chmod a-w devops.txt`  (or `chmod 444 devops.txt`)
- **After:** `-r--r--r--`
- **Test:** `echo hi >> devops.txt` → `bash: devops.txt: Permission denied`

### notes.txt
- **Before:** `-rw-r--r--`
- **Command:** `chmod 640 notes.txt`
- **After:** `-rw-r-----`
- **Note:** owner can read/write, group can read, others none

### project/ (directory)
- **Command (create + set perms):** `mkdir -m 755 project` (or `mkdir project && chmod 755 project`)
- **Verify:** `ls -ld project` → `drwxr-xr-x`

---

## Commands Used
```
# create files
touch devops.txt
echo "Notes about permissions" > notes.txt
cat > script.sh <<'EOF'
#!/bin/bash
echo "Hello DevOps"
EOF

# set permissions
chmod +x script.sh
chmod a-w devops.txt   # or: chmod 444 devops.txt
chmod 640 notes.txt
mkdir -m 755 project

# verify
ls -l devops.txt notes.txt script.sh
ls -ld project
./script.sh
```

---

## Tests & Notes
- Ran `./script.sh` → printed `Hello DevOps` (execute bit working). ✅
- Attempt to append to `devops.txt` after removing write produced `Permission denied`. ✅
- If `./script.sh` fails with `Permission denied` before chmod, use `chmod +x script.sh` or run with `sh script.sh`.
- If file shows Windows CRLF line endings, run `dos2unix script.sh` to fix.

---

## What I Learned ✨
- File mode bits control owner/group/others access (r=4, w=2, x=1).
- `chmod` can change permissions symbolically (`u+x`, `a-w`) or numerically (`640`, `755`).
- Directories need the execute bit to be `cd`'able; `755` gives read/execute to group/others for listing/access.

---

## Screenshots (attach here)
![alt text](<Screenshot (107).png>) ![alt text](<Screenshot (108).png>) ![alt text](<Screenshot (109).png>)
