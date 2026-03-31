🚀 Day 47 – Advanced Triggers: PR Events, Cron & Event-Driven Pipelines
📌 Overview

Today I explored advanced GitHub Actions triggers including:

Pull Request lifecycle events
PR validation gates
Scheduled cron workflows
Path & branch filters
Chained workflows using workflow_run
External triggers using repository_dispatch

This is real-world DevOps automation.

🔹 Task 1 – PR Lifecycle Workflow

File: .github/workflows/pr-lifecycle.yml

name: PR Lifecycle

on:
  pull_request:
    types: [opened, synchronize, reopened, closed]

jobs:
  pr-info:
    runs-on: ubuntu-latest

    steps:
      - name: Print Event Type
        run: echo "Event Type: ${{ github.event.action }}"

      - name: Print PR Title
        run: echo "PR Title: ${{ github.event.pull_request.title }}"

      - name: Print PR Author
        run: echo "PR Author: ${{ github.event.pull_request.user.login }}"

      - name: Print Branch Info
        run: |
          echo "Source Branch: ${{ github.head_ref }}"
          echo "Target Branch: ${{ github.base_ref }}"

      - name: Run Only If PR Merged
        if: github.event.pull_request.merged == true
        run: echo "This PR was merged 🎉"
✅ What I Observed
Workflow triggered when PR was opened
Triggered again when commits were pushed
Triggered when PR was merged
Conditional step ran only when merged
🔹 Task 2 – PR Validation Workflow

File: .github/workflows/pr-checks.yml

name: PR Checks

on:
  pull_request:
    branches:
      - main

jobs:

  file-size-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check file sizes
        run: |
          for file in $(find . -type f -size +1M); do
            echo "File too large: $file"
            exit 1
          done

  branch-name-check:
    runs-on: ubuntu-latest
    steps:
      - name: Validate branch name
        run: |
          echo "Branch: ${{ github.head_ref }}"
          if [[ ! "${{ github.head_ref }}" =~ ^(feature|fix|docs)/ ]]; then
            echo "Invalid branch name!"
            exit 1
          fi

  pr-body-check:
    runs-on: ubuntu-latest
    steps:
      - name: Check PR Body
        run: |
          if [ -z "${{ github.event.pull_request.body }}" ]; then
            echo "⚠️ PR description is empty"
          else
            echo "PR description provided"
          fi
✅ What I Verified
PR from bad branch name → workflow failed
Empty PR description → warning shown
Large file → workflow failed

This acts as an automated PR gate.

🔹 Task 3 – Scheduled Workflows (Cron)

File: .github/workflows/scheduled-tasks.yml

name: Scheduled Tasks

on:
  schedule:
    - cron: '30 2 * * 1'
    - cron: '0 */6 * * *'
  workflow_dispatch:

jobs:
  scheduled-job:
    runs-on: ubuntu-latest
    steps:
      - name: Print Triggered Schedule
        run: echo "Triggered by schedule: ${{ github.event.schedule }}"

      - name: Health Check
        run: |
          STATUS=$(curl -o /dev/null -s -w "%{http_code}" https://example.com)
          echo "Response Code: $STATUS"
          if [ "$STATUS" -ne 200 ]; then
            exit 1
          fi
🧠 Cron Expressions
Every weekday at 9 AM IST

IST = UTC +5:30
9:00 AM IST = 3:30 AM UTC

30 3 * * 1-5
First day of every month at midnight
0 0 1 * *
Why Scheduled Workflows May Be Delayed
They only run on the default branch
Inactive repositories disable scheduled workflows
GitHub load balancing may delay execution
🔹 Task 4 – Path & Branch Filters

File: .github/workflows/smart-triggers.yml

name: Smart Trigger

on:
  push:
    branches:
      - main
      - release/*
    paths:
      - 'src/**'
      - 'app/**'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Code changed in src or app"

File: .github/workflows/ignore-docs.yml

name: Ignore Docs

on:
  push:
    paths-ignore:
      - '*.md'
      - 'docs/**'

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Not triggered by docs only change"
🧠 When to Use
paths → Trigger only when specific folders change
paths-ignore → Skip workflow when only certain files change
🔹 Task 5 – workflow_run (Chained Pipelines)
tests.yml
name: Run Tests

on:
  push:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Running tests..."
deploy-after-tests.yml
name: Deploy After Tests

on:
  workflow_run:
    workflows: ["Run Tests"]
    types: [completed]

jobs:
  deploy:
    if: github.event.workflow_run.conclusion == 'success'
    runs-on: ubuntu-latest
    steps:
      - run: echo "Tests passed. Deploying..."
🧠 workflow_run vs workflow_call
workflow_run	workflow_call
Triggers after another workflow completes	Reusable workflow called like a function
Used for pipeline chaining	Used for DRY reusable workflow logic
Event-based	Direct invocation
🔹 Task 6 – repository_dispatch (External Trigger)

File: .github/workflows/external-trigger.yml

name: External Trigger

on:
  repository_dispatch:
    types: [deploy-request]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Print Environment
        run: echo "Environment: ${{ github.event.client_payload.environment }}"
Trigger Command Used
gh api repos/<owner>/<repo>/dispatches \
  --method POST \
  --input payload.json
🧠 When repository_dispatch Is Used
Slack bot triggers deployment
Monitoring system detects outage
External CI/CD system triggers pipeline
Manual production approval system
🎯 Final Learnings

Today I learned:

PR lifecycle automation
Building real PR validation gates
Writing cron schedules
Smart workflow filtering
Chaining CI/CD pipelines
Triggering workflows externally via API

This is production-level GitHub Actions engineering.

Screenshots:-
![alt text](<Screenshot (472).png>) ![alt text](<Screenshot (456).png>) ![alt text](<Screenshot (457).png>) ![alt text](<Screenshot (458).png>) ![alt text](<Screenshot (460).png>) ![alt text](<Screenshot (461).png>) ![alt text](<Screenshot (462).png>) ![alt text](<Screenshot (463).png>) ![alt text](<Screenshot (465).png>) ![alt text](<Screenshot (466).png>) ![alt text](<Screenshot (467).png>) ![alt text](<Screenshot (468).png>) ![alt text](<Screenshot (469).png>) ![alt text](<Screenshot (471).png>)