# Day 28 Notes

## Self‑Assessment Results (selected items)

### Linux Networking
- [x] Check network connectivity — ping, curl, netstat, ss, dig, nslookup – **confident now**
- [x] Explain DNS resolution, IP addressing, subnets, and common ports – **confident now**

I spent extra time on Day 14–15 material and re‑ran the hands‑on exercises. The weak spot was networking, but after revisiting the notes and playing with `ip addr`, `ip route`, `ping`, `traceroute`, `ss -tulpn`, `dig`, and `nslookup`, everything feels solid.

### What I Re‑learned
- **IP addressing & subnets:** Practice calculating network and broadcast addresses with CIDR notation (e.g. 192.168.1.0/24 has hosts 1–254, netmask 255.255.255.0).
- **DNS resolution:** How a resolver queries recursive servers, the role of root and TLD servers, and using `dig +short` vs `nslookup` for quick lookups.
- **Common ports:** Remember HTTP (80), HTTPS (443), SSH (22), DNS (53), SMTP (25) – used ` `ss` and `netstat` to see listening ports.
- **Connectivity tools:** `ping` and `curl` for basic reachability, `traceroute` to trace path, and `mtr` for continuous route testing.

### Quick-Fire Answers (reviewed)
1. `chmod 755 script.sh` sets owner to rwx and group/others to r-x (executable by everyone).
2. A *process* is an instance of a running program; a *service* is a background process managed by init/systemd with start/stop controls.
3. `ss -tulpn | grep 8080` or `lsof -i :8080` shows the process using port 8080.
4. `set -euo pipefail` makes a script exit on any error, treat unset variables as errors, and fail if any command in a pipeline fails.
5. `git reset --hard` moves the HEAD and working tree to a commit, discarding changes; `git revert` creates a new commit that undoes a previous commit without rewriting history.
6. For a 5‑dev team shipping weekly, **GitHub Flow** (short-lived feature branches, merged into main via PR) works well.
7. `git stash` temporarily shelves uncommitted changes so you can switch branches; useful when you need to work on something else quickly.
8. Add `0 3 * * * /path/to/script.sh` to crontab (`crontab -e`).
9. `git fetch` downloads remote commits but doesn’t merge; `git pull` does `fetch` + `merge` (or rebase).
10. LVM (Logical Volume Manager) lets you create flexible, resizable volumes on top of physical disks, making resizing and snapshotting easier than fixed partitions.

### Teach‑Back Snippet
**Explaining DNS to a newcomer:** DNS is like the internet's phonebook. When you type `example.com` your computer asks a DNS resolver to translate that name into an IP address. The resolver may query a sequence of servers—root, TLD, then authoritative—until it gets the answer. This allows humans to use easy names while machines speak with numeric addresses.



