# Day 14 – Networking Fundamentals & Hands-on Checks

## Task
Get comfortable with core networking concepts and the commands you’ll actually run during troubleshooting.

---

## Quick Concepts

### OSI vs TCP/IP
- **OSI (L1–L7):** Conceptual model used for learning and troubleshooting (Physical → Application).
- **TCP/IP:** Practical stack used on the internet (Link → Internet → Transport → Application).

### Protocol Placement
- **IP:** Internet layer (routing packets).
- **TCP/UDP:** Transport layer (reliable vs fast delivery).
- **HTTP/HTTPS:** Application layer (web).
- **DNS:** Application layer (name → IP resolution).

### Real Example
- `curl https://example.com` = **Application (HTTP)** over **Transport (TCP)** over **Internet (IP)**.

---

## Hands-on Checklist

**Target used:** `google.com` (and `localhost` for local checks)

### Identity
- Command: `hostname -I` / `ip addr show`
- Observation: System has a private IP assigned (e.g., 192.168.x.x).

### Reachability
- Command: `ping google.com`
- Observation: Host reachable with low latency and 0% packet loss.

### Path
- Command: `traceroute google.com`
- Observation: Multiple hops via ISP; some hops may not reply (timeouts are normal).

### Ports
- Command: `ss -tulpn`
- Observation: SSH service listening on port 22.

### Name Resolution
- Command: `dig google.com`
- Observation: Domain resolves to multiple IPs (load-balanced).

### HTTP Check
- Command: `curl -I https://google.com`
- Observation: HTTP 200/301 received, confirming application-layer reachability.

### Connections Snapshot
- Command: `netstat -an | head`
- Observation: Few LISTEN sockets, some ESTABLISHED connections.

---

## Mini Task: Port Probe & Interpret

1) Identified listening port: **22 (SSH)**  
2) Test:
   ```bash
   nc -zv localhost 22
   ```
3) Result: Port reachable.  
   - If unreachable: next checks → service status, firewall rules, correct port.

---

## Reflection

- **Fastest signal:** `ping` (quick reachability check).
- **If DNS fails:** Inspect **Application layer (DNS)**.
- **If HTTP 500 occurs:** Inspect **Application layer**, then backend service logs.

### Follow-up Checks
- Verify firewall rules (`iptables` / `ufw`).
- Check service health and logs.

---
![alt text](<Screenshot (129).png>) ![alt text](<Screenshot (132).png>) ![alt text](<Screenshot (131).png>) ![alt text](<Screenshot (130).png>)S