# Day 43 – Jobs, Steps, Environment Variables & Conditionals

## 🚀 Objective

Today I learned how to control the execution flow of GitHub Actions workflows using:

- Multiple jobs
- Job dependencies (`needs`)
- Environment variables (workflow, job, step level)
- Job outputs
- Conditional execution (`if`)
- Parallel vs sequential execution

This is where CI/CD pipelines become powerful and production-ready.

---

# 🔹 1. Multi-Job Workflow

## Concept

- A workflow can contain multiple jobs.
- By default, jobs run in **parallel**.
- To control execution order, use `needs:`.

## Example: Sequential Dependency

```yaml
name: Multi Job Pipeline

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Building the app"

  test:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - run: echo "Running tests"

  deploy:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - run: echo "Deploying"



What needs: Does

needs: creates a dependency between jobs.

Execution order:
build → test → deploy

Without needs, jobs run in parallel.


🔹 2. Environment Variables

Environment variables can be defined at three levels:

Level	Scope
Workflow	Available in all jobs
Job	Available inside that job only
Step	Available only in that step
Example


🔹 2. Environment Variables

🔹 2. Environment Variables

Environment variables can be defined at three levels:

Level	Scope
Workflow	Available in all jobs
Job	Available inside that job only
Step	Available only in that step
Example
name: Environment Variables Demo

on: push

env:
  APP_NAME: MyApp   # Workflow level

jobs:
  demo:
    runs-on: ubuntu-latest
    env:
      ENVIRONMENT: staging   # Job level

    steps:
      - name: Print Variables
        env:
          VERSION: 1.0.0   # Step level
        run: |
          echo "Application Name: $APP_NAME"
          echo "Environment: $ENVIRONMENT"
          echo "Version: $VERSION"
          echo "Commit SHA: $GITHUB_SHA"
          echo "Triggered by: $GITHUB_ACTOR"
Key Learning
Variables cascade from workflow → job → step.
GitHub provides built-in variables like:
github.sha
github.actor
github.ref
🔹 3. Job Outputs
Problem

Each job runs on a separate runner (machine).
Variables do NOT automatically transfer between jobs.

Solution

Use job outputs.

Example
name: Job Output Example

on: push

jobs:
  generate-date:
    runs-on: ubuntu-latest
    outputs:
      today: ${{ steps.date_step.outputs.date }}

    steps:
      - name: Generate Date
        id: date_step
        run: echo "date=$(date)" >> $GITHUB_OUTPUT

  use-date:
    runs-on: ubuntu-latest
    needs: generate-date

    steps:
      - name: Print Date
        run: echo "Today's date is ${{ needs.generate-date.outputs.today }}"
How It Works
Step writes output using $GITHUB_OUTPUT
Job exposes that output using outputs:
Next job accesses it using:
needs.<job-name>.outputs.<output-name>
Real-World Use Cases
Passing Docker image tags
Passing version numbers
Passing Terraform outputs
Sharing artifact paths
🔹 4. Conditionals

Conditionals allow selective execution of jobs or steps.

Example
name: Conditional Demo

on:
  push:
  pull_request:

jobs:
  conditional-job:
    runs-on: ubuntu-latest
    if: github.event_name == 'push'

    steps:
      - name: Run only on main
        if: github.ref == 'refs/heads/main'
        run: echo "Main branch push"

      - name: Force failure
        id: fail_step
        run: exit 1
        continue-on-error: true

      - name: Run if previous step failed
        if: failure()
        run: echo "Previous step failed"
Key Concepts
if: controls execution.
failure() runs only if previous step failed.
continue-on-error: true allows workflow to continue even if a step fails.
🔹 5. Smart Pipeline (Putting It All Together)
Requirements
Trigger on push to any branch
lint and test run in parallel
summary runs after both
Detect main branch vs feature branch
Print commit message
Example
name: Smart Pipeline

on:
  push:
    branches:
      - '**'

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Linting code..."

  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Running tests..."

  summary:
    runs-on: ubuntu-latest
    needs: [lint, test]

    steps:
      - name: Branch Info
        run: |
          if [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
            echo "Main branch push"
          else
            echo "Feature branch push"
          fi

      - name: Print Commit Message
        run: echo "Commit message: ${{ github.event.commits[0].message }}"
Execution Flow
lint      test
   \      /
    summary
🔥 Final Understanding

Today I learned how to:

Control job order using needs
Run jobs in parallel
Scope environment variables properly
Pass data between jobs using outputs
Apply conditional logic in workflows
Build dynamic, production-style pipelines

This is real CI/CD orchestration.

Screenshots: 
c:\Users\USER\OneDrive\Pictures\Screenshots\Screenshot (426).png c:\Users\USER\OneDrive\Pictures\Screenshots\Screenshot (427).png c:\Users\USER\OneDrive\Pictures\Screenshots\Screenshot (428).png c:\Users\USER\OneDrive\Pictures\Screenshots\Screenshot (429).png c:\Users\USER\OneDrive\Pictures\Screenshots\Screenshot (430).png c:\Users\USER\OneDrive\Pictures\Screenshots\Screenshot (431).png c:\Users\USER\OneDrive\Pictures\Screenshots\Screenshot (432).png c:\Users\USER\OneDrive\Pictures\Screenshots\Screenshot (433).png c:\Users\USER\OneDrive\Pictures\Screenshots\Screenshot (424).png c:\Users\USER\OneDrive\Pictures\Screenshots\Screenshot (425).png