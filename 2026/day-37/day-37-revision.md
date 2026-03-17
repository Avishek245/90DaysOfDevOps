# Day 37 – Docker Revision & Self Assessment

## ✅ Self-Assessment Checklist

- [x] Run a container from Docker Hub (interactive + detached) – CAN DO
- [x] List, stop, remove containers and images – CAN DO
- [x] Explain image layers and caching – CAN DO
- [x] Write Dockerfile from scratch – CAN DO
- [x] Explain CMD vs ENTRYPOINT – CAN DO
- [x] Build and tag custom image – CAN DO
- [x] Create and use named volumes – CAN DO
- [x] Use bind mounts – CAN DO
- [x] Create custom networks and connect containers – CAN DO
- [x] Write docker-compose.yml for multi-container app – CAN DO
- [x] Use environment variables and .env in Compose – CAN DO
- [x] Write multi-stage Dockerfile – CAN DO
- [x] Push image to Docker Hub – CAN DO
- [x] Use healthchecks and depends_on – CAN DO

---

# 🔥 Quick-Fire Answers

### 1. Difference between image and container?
Image is a blueprint (read-only template).  
Container is a running instance of that image.

---

### 2. What happens to data when container is removed?
Data inside container is lost unless stored in a volume or bind mount.

---

### 3. How do two containers on same custom network communicate?
They communicate using container names as DNS hostnames.

Example:
host="postgres-db"

---

### 4. docker compose down vs docker compose down -v?
down → Stops and removes containers  
down -v → Also removes volumes (data deleted)

---

### 5. Why are multi-stage builds useful?
They reduce image size by separating build dependencies from runtime image.

---

### 6. Difference between COPY and ADD?
COPY → Simple file copy  
ADD → Can extract tar files and fetch URLs (less predictable)

---

### 7. What does -p 8080:80 mean?
Maps host port 8080 → container port 80.

---

### 8. How to check Docker disk usage?
docker system df

---

# 🎯 Weak Spots Revisited

Re-practiced:
1. Custom networks with Flask + Postgres
2. Multi-stage Dockerfile optimization

---

# 🧠 Reflection

Today reinforced:
- Networking concepts
- Volumes vs bind mounts
- Compose orchestration
- Image optimization

Feeling confident with Docker fundamentals and production-level workflows.

### Screenshot

![alt text](<Screenshot (384).png>) ![alt text](<Screenshot (378).png>) ![alt text](<Screenshot (379).png>)  ![alt text](<Screenshot (381).png>) ![alt text](<Screenshot (382).png>) ![alt text](<Screenshot (383).png>)