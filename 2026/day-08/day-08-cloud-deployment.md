# Day 08 — Cloud Deployment (submitted file)

This is my Day 08 submission for: **Cloud Server Setup: Docker, Nginx & Web Deployment**.

---

## Commands Used

- Launch / SSH (example for AWS):
```bash
ssh -i ~/keys/my-key.pem ubuntu@<your-instance-ip>
```

- Update & install Nginx:
```bash
sudo apt update && sudo apt install -y nginx
sudo systemctl enable --now nginx
```

- Open firewall (Ubuntu UFW example):
```bash
sudo ufw allow 'Nginx HTTP'
sudo ufw status
```

- Save Nginx logs:
```bash
sudo tail -n 500 /var/log/nginx/access.log | sudo tee ~/nginx-logs.txt
```

- Copy log file to local machine (replace key and user):
```bash
scp -i ~/keys/my-key.pem ubuntu@<your-instance-ip>:~/nginx-logs.txt .
```

- Run official Nginx container (optional):
```bash
docker run --rm -p 8080:80 nginx
```

---

## Screenshots

Include the requested screenshots in this folder (relative paths):

- `assets/ssh-connection.png` — SSH session showing the server prompt
- `assets/nginx-webpage.png` — Browser showing the Nginx welcome page
- `assets/docker-nginx.png` — (Optional) Docker Nginx page if you used Docker

Example markdown to show images in this file:

![SSH connection](assets/ssh-connection.png)

![Nginx welcome page](assets/nginx-webpage.png)

---

## nginx-logs.txt (attached)

Attach `nginx-logs.txt` in this folder.

Example contents (first lines):
```
127.0.0.1 - - [03/Feb/2026:10:10:00 +0000] "GET / HTTP/1.1" 200 612 "-" "Mozilla/5.0"
54.236.23.34 - - [03/Feb/2026:10:12:43 +0000] "GET / HTTP/1.1" 200 612 "-" "Mozilla/5.0"
```

---

## Challenges Faced

- [ ] (Add any connection, security group, or permission issues you faced and how you fixed them)


## What I Learned

- How to provision a cloud instance and connect via SSH
- How to install and run Nginx and make it accessible via port 80
- How to collect server logs and copy them to my workstation
- How to run the nginx image via Docker for local testing

---
![alt text](<Screenshot (92).png>) ![alt text](<Screenshot (93).png>) ![alt text](<Screenshot (94).png>) ![alt text](<Screenshot (90).png>) ![alt text](<Screenshot (91).png>)