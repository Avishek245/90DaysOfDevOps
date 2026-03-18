# Day 38 – YAML Basics

## 🎯 Objective
Before writing CI/CD pipelines, I focused on mastering **YAML**, the language used in:

- Kubernetes manifests
- Docker Compose files
- GitHub Actions workflows
- CI/CD pipelines

---

# 🧪 Task 1 – Key-Value Pairs

Created `person.yaml`

```yaml
name: Avishek Ghosh
role: Software Engineer
experience_years: 3
learning: true

✅ Learned:

YAML uses key: value

Booleans are lowercase (true / false)

No tabs allowed

🧪 Task 2 – Lists

Updated person.yaml

name: Avishek Ghosh
role: Software Engineer
experience_years: 3
learning: true

tools:
  - Docker
  - Kubernetes
  - Git
  - GitHub
  - GitHub Actions
  - Linux

hobbies: ["reading", "Coding", "Gym"]

🧠 Two ways to write lists in YAML:

Block style (using -)

Inline style [item1, item2]

🧪 Task 3 – Nested Objects

Created server.yaml

server:
  name: app-server-01
  ip: 192.168.1.10
  port: 8080

database:
  host: localhost
  name: app_db
  credentials:
    user: admin
    password: secret123

🔥 Learned:

Indentation defines hierarchy

Tabs break YAML

Nested mappings are used in real DevOps configs

🧪 Task 4 – Multi-line Strings

Added multi-line scripts:

startup_script_literal: |
  #!/bin/bash
  echo "Starting server..."
  npm install
  npm start

startup_script_folded: >
  #!/bin/bash
  echo "Starting server..."
  npm install
  npm start

🧠 Difference:

| → preserves newlines

> → folds into a single line

Use | for scripts and config files.
Use > for long readable text.

🧪 Task 5 – Validation

Installed yamllint:

pip install yamllint
yamllint person.yaml
yamllint server.yaml

💥 Intentionally broke indentation → got:

syntax error: mapping values are not allowed here

Fixed indentation → validation passed ✅

🧪 Task 6 – Spot the Difference

Correct:

tools:
  - docker
  - kubernetes

Broken:

tools:
- docker
  - kubernetes

❌ First list item is not properly indented.

🚀 What I Learned Today

YAML is indentation-sensitive.

Tabs will break everything.

YAML validation is critical before pushing CI/CD configs.

### Screenshots

![alt text](<Screenshot (385).png>) ![alt text](<Screenshot (386).png>) ![alt text](<Screenshot (387).png>) ![alt text](<Screenshot (388).png>) ![alt text](<Screenshot (389).png>) ![alt text](<Screenshot (390).png>) ![alt text](<Screenshot (391).png>)