#Day 4:
## Process checks
- ps -ef  
  Output: shows all running processes

- pgrep sshd  
  Output: shows PID of sshd process

## Service checks
- systemctl status ssh  
  Output: SSH service is active and running

- systemctl list-units --type=service  
  Output: list of active services

## Log checks
- journalctl -u ssh -n 20  
  Output: recent SSH logs

- tail -n 20 /var/log/syslog  
  Output: recent system logs

## Mini troubleshooting steps
1. Check if process is running using ps or pgrep
2. Check service status using systemctl
3. Inspect logs using journalctl
4. Restart service if needed

<img width="1920" height="1080" alt="Screenshot (88)" src="https://github.com/user-attachments/assets/479744e0-2410-4ba4-a965-455b11b5c8e6" />
