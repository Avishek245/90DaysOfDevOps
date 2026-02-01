# Linux Troubleshooting Runbook

**Target service / process:** <replace-with-service>

## Snapshot: Environment
- Command: `uname -a`
  - Output: <paste output>
  - Note: <short observation>
- Command: `cat /etc/os-release`
  - Output: <paste output>
  - Note: <short observation>

## Snapshot: CPU & Memory
- Command: `top -b -n 1 | head -n 15`
  - Output: <paste output>
  - Note: <e.g., CPU usage, runaway processes>
- Command: `free -h`
  - Output: <paste output>
  - Note: <memory pressure observations>

## Snapshot: Disk & IO
- Command: `df -h`
  - Output: <paste output>
  - Note: <disk usage, full partitions>
- Command: `du -sh /var/log` (or targeted dir)
  - Output: <paste output>
  - Note: <log bloat or normal>

## Snapshot: Network
- Command: `ss -tulpn` (or `netstat -tulpn`)
  - Output: <paste output>
  - Note: <listening services>
- Command: `curl -I <service-endpoint>` (or `ping`)
  - Output: <paste output>
  - Note: <latency or HTTP status>

## Logs reviewed
- Command: `journalctl -u <service> -n 50`
  - Output: <paste output or important lines>
  - Note: <errors, warnings, last restart>
- Command: `tail -n 50 /var/log/<file>.log`
  - Output: <paste output>
  - Note: <relevant log lines>

## Quick findings
- Finding 1: <short statement>
- Finding 2: <short statement>
- Findings should be 1–3 short bullet points summarizing the above evidence.

## If this worsens (next steps)
1. Restart strategy: `systemctl restart <service>` and watch for regressions. If repeated failures, escalate to deployment freeze.
2. Increase log verbosity and capture fresh logs (`journalctl -u <service> --since "5 minutes ago"`), collect `strace -p <pid>` if stuck.
3. Capture resource traces (e.g., `perf`, `iostat`, `vmstat`) and open an incident ticket with attachments.

---

> Notes: Replace all `<...>` placeholders with real outputs from your machine. Keep content concise (aim for ~1 page). Save this file in `2026/day-05/linux-troubleshooting-runbook.md` and commit your changes.
