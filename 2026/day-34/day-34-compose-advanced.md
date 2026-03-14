
# Day 34 – Docker Compose Advanced

## What I Built
- Flask Web App
- PostgreSQL Database
- Redis Cache
- Custom Network
- Named Volume
- Healthchecks
- Restart Policies
- Scaling Test

---

## Key Learnings

### depends_on with healthcheck
Ensures app waits for DB to be fully ready.

### restart: always
Used for critical services like database.

### Named volumes
Data persists even if container is deleted.

### Custom networks
Improves isolation and service communication.

### Scaling limitation
Port binding prevents multiple replicas on same host port.
Need load balancer for proper scaling.

---

## Commands Used

docker compose up --build  
docker compose down  
docker compose up --scale web=3  
docker kill postgres-compose  

---

Run:

docker compose up --scale web=3


You’ll get error because:

ports: "5000:5000"


Only one container can bind to port 5000 on host.

📌 Why Scaling Breaks?

Because:

All replicas try to bind to same host port

Port conflicts happen

You need load balancer (like Nginx) in front

That’s how production works.
## Conclusion

Today I built a production-like 3-tier app stack using Docker Compose.

![alt text](<Screenshot (358).png>) ![alt text](<Screenshot (354).png>) ![alt text](<Screenshot (355).png>) ![alt text](<Screenshot (356).png>) ![alt text](<Screenshot (357).png>)