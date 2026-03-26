### 🚀 Day 45 – Docker Build & Push using GitHub Actions
### 📌 Objective

Build a complete CI/CD pipeline where:

Code pushed to main
Docker image builds automatically
Image is tagged (latest + commit SHA)
Image is pushed to Docker Hub
Image can be pulled and run locally
🛠 Workflow File

Location:

.github/workflows/docker-publish.yml
name: Docker build & push

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set short SHA
        run: echo "SHORT_SHA=$(echo $GITHUB_SHA | cut -c1-7)" >> $GITHUB_ENV

      - name: Log in to DockerHub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_TOKEN }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKER_USERNAME }}/github-actions-practice:latest
            ${{ secrets.DOCKER_USERNAME }}/github-actions-practice:sha-${{ env.SHORT_SHA }}
### 🐳 Dockerfile Used
FROM nginx:alpine
COPY . /usr/share/nginx/html
🔐 Secrets Used

Configured in GitHub Repository → Settings → Secrets:

DOCKER_USERNAME
DOCKER_TOKEN
🏷 Image Tags Generated

When pushing to main, two tags are created:

latest
sha-<short-commit-hash>

### Example:

avigho/github-actions-practice:latest
avigho/github-actions-practice:sha-abc1234
📦 Docker Hub Repository

👉 https://hub.docker.com/repository/docker/avigho/github-actions-practice/general

🧪 Pull and Run Locally
Pull Image
docker pull avigho/github-actions-practice:latest
Run Container
docker run -d -p 9090:80 avigho/github-actions-practice:latest
Access in Browser
http://localhost:9090

Application runs successfully ✅

### 🔁 Full Journey: git push → Running Container
Developer writes code locally
git push origin main
GitHub Actions workflow triggers
Runner checks out repository
Docker image builds using Dockerfile
Image tagged with:
latest
sha-<commit>
Docker login happens securely using secrets
Image pushed to Docker Hub
On local machine:
docker pull
docker run
Container starts and serves application
📊 Architecture Flow
Developer → GitHub → GitHub Actions → Docker Build → Docker Hub
                                                     ↓
                                               docker pull
                                                     ↓
                                                docker run
                                                     ↓
                                               Running Container
### 🎯 Key Learnings
Automating Docker builds using GitHub Actions
Secure authentication using GitHub Secrets
Image versioning with commit-based SHA tagging
Real-world CI/CD workflow design
Handling local port conflicts (Jenkins on 8080)
### ✅ Status Badge

Added workflow badge in README to show pipeline status.

🔥 This completes Day 45 – Production-Style Docker CI/CD Pipeline.

### Sreenshot
![alt text](<Screenshot (443).png>) ![alt text](<Screenshot (444).png>) ![alt text](<Screenshot (445).png>) ![alt text](<Screenshot (446).png>) ![alt text](<Screenshot (447).png>) ![alt text](<Screenshot (448).png>) ![alt text](<Screenshot (449).png>)