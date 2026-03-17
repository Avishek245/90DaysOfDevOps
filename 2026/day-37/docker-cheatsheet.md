# 🐳 Docker Cheat Sheet

A quick reference for daily DevOps work.

---

# 🔹 Container Commands

docker run -it nginx → Run container interactively  
docker run -d nginx → Run container in background  
docker ps → List running containers  
docker ps -a → List all containers  
docker stop <container> → Stop container  
docker rm <container> → Remove container  
docker exec -it <container> sh → Enter container  
docker logs <container> → View logs  

---

# 🔹 Image Commands

docker build -t image-name . → Build image  
docker images → List images  
docker rmi <image> → Remove image  
docker pull nginx → Pull image from Docker Hub  
docker push username/image:tag → Push image  
docker tag image newname:tag → Retag image  

---

# 🔹 Volume Commands

docker volume create vol-name → Create named volume  
docker volume ls → List volumes  
docker volume inspect vol-name → Inspect volume  
docker volume rm vol-name → Remove volume  

Bind mount example:  
docker run -v ${PWD}:/app image-name  

---

# 🔹 Network Commands

docker network create net-name → Create network  
docker network ls → List networks  
docker network inspect net-name → Inspect network  
docker network connect net-name container → Connect container  

Run with network:  
docker run --network net-name image-name  

---

# 🔹 Docker Compose Commands

docker compose up → Start services  
docker compose up --build → Rebuild and start  
docker compose down → Stop services  
docker compose down -v → Stop and remove volumes  
docker compose ps → List services  
docker compose logs → View logs  
docker compose build → Build services  

---

# 🔹 Cleanup Commands

docker system df → Check disk usage  
docker container prune → Remove stopped containers  
docker image prune → Remove unused images  
docker volume prune → Remove unused volumes  
docker system prune -a → Remove everything unused  

---

# 🔹 Dockerfile Instructions

FROM → Base image  
RUN → Execute command during build  
COPY → Copy files from host to container  
WORKDIR → Set working directory  
EXPOSE → Document container port  
CMD → Default command at runtime  
ENTRYPOINT → Fixed executable  
ENV → Set environment variables  