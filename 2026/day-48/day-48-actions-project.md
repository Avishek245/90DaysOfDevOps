# 🚀 Day 48 – GitHub Actions Capstone Project

## 📌 Project Overview

This project demonstrates a production-style CI/CD pipeline using GitHub Actions with:

* Reusable workflows
* Pull Request validation pipeline
* Main branch CI/CD pipeline
* Docker image build & push
* Environment protection
* Scheduled health checks

The application used is a simple **Node.js Express app** with a `/health` endpoint.

---

# 🏗️ Project Architecture

```
Pull Request → PR Pipeline → Build & Test

Push to Main → Main Pipeline
              ├── Build & Test
              ├── Docker Build & Push
              └── Deploy (Production Environment)

Scheduled Job → Health Check → Container Test
```

---

# 📂 Repository Structure

```
.github/
 └── workflows/
      ├── reusable-build-test.yml
      ├── reusable-docker.yml
      ├── pr-pipeline.yml
      ├── main-pipeline.yml
      └── health-check.yml

app.js
package.json
Dockerfile
README.md
```

---

# 🔁 Reusable Workflows

## 1️⃣ Reusable Build & Test

**File:** `.github/workflows/reusable-build-test.yml`

Purpose:

* Setup Node.js
* Install dependencies
* Run tests
* Return test result as output

Trigger:

```
on:
  workflow_call:
```

This workflow is not triggered directly.
It is called from other workflows.

---

## 2️⃣ Reusable Docker Workflow

**File:** `.github/workflows/reusable-docker.yml`

Purpose:

* Login to Docker Hub
* Build Docker image
* Push image
* Return image URL as output

Secrets used:

* `DOCKER_USERNAME`
* `DOCKER_TOKEN`

Trigger:

```
on:
  workflow_call:
```

---

# 🔎 PR Pipeline

**File:** `.github/workflows/pr-pipeline.yml`

Trigger:

```
on:
  pull_request:
    branches:
      - main
```

Purpose:

* Validate code before merging
* Run reusable build & test
* Prevent broken code from entering main

What it does:
✔ Runs tests
❌ Does NOT build Docker
❌ Does NOT deploy

---

# 🚀 Main Pipeline (CI/CD)

**File:** `.github/workflows/main-pipeline.yml`

Trigger:

```
on:
  push:
    branches:
      - main
```

Execution Flow:

1. Run Build & Test
2. Build Docker image
3. Push image to Docker Hub
4. Deploy to Production environment

Deploy step uses:

```
environment: production
```

Production environment has:
✔ Required reviewers
✔ Deployment protection

---

# ⏱️ Scheduled Health Check

**File:** `.github/workflows/health-check.yml`

Triggers:

```
on:
  schedule:
    - cron: '0 */12 * * *'
  workflow_dispatch:
```

Purpose:

* Pull latest Docker image
* Run container
* Call `/health`
* Report result in workflow summary

---

# 🔐 Secrets Management

Configured in:

```
Repo → Settings → Secrets → Actions
```

Secrets Used:

* DOCKER_USERNAME
* DOCKER_TOKEN

---

# 🐳 Docker Configuration

**Dockerfile**

```dockerfile
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["node", "app.js"]
```

Docker image pushed to:

```
docker.io/<your-username>/github-actions-practice:latest
```

---

# 🎯 Key Concepts Practiced

* Reusable workflows (`workflow_call`)
* Workflow outputs
* Job dependencies (`needs`)
* Secrets handling
* Branch-based triggers
* Environment protection rules
* Scheduled workflows (cron)
* CI vs CD separation

---

# 🧠 Learning Outcome

This capstone project simulates a real-world production pipeline where:

* PRs validate code before merge
* Main branch triggers full CI/CD
* Docker images are versioned and pushed
* Deployments require approval
* Health checks monitor application stability

This structure follows modern DevOps best practices.

---

# 📈 Future Improvements

* Add Trivy security scan
* Add semantic version tagging
* Use GitHub Container Registry
* Add Slack notification
* Add test coverage reporting
* Deploy to real cloud (AWS / Azure / GCP)

---

# 🏁 Conclusion

This project demonstrates end-to-end CI/CD automation using GitHub Actions with production-style structure and best practices.

It showcases readiness for real-world DevOps pipelines.

---

**Author:** Avishek
**Day:** 48
**Topic:** GitHub Actions Capstone


# Screenshot
![alt text](<Screenshot (478).png>) ![alt text](<Screenshot (477).png>)