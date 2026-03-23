# Day 42 – Runners: GitHub-Hosted & Self-Hosted

## Overview

Today I learned how GitHub Actions jobs actually execute — using **runners**.

A runner is the machine that executes workflow jobs.

There are two types:

* GitHub-hosted runners
* Self-hosted runners

Platform used: GitHub

---

# Task 1 – GitHub-Hosted Runners

I created a workflow that runs 3 jobs in parallel on:

* ubuntu-latest
* windows-latest
* macos-latest

Each job printed:

* OS information
* Hostname
* Current user

### What is a GitHub-hosted runner?

A GitHub-hosted runner is a temporary virtual machine provided and fully managed by GitHub.
It is automatically created when a workflow starts and destroyed after it completes.

### Who manages it?

GitHub manages:

* Infrastructure
* Security patches
* Pre-installed tools
* Scaling

---

# Task 2 – Pre-installed Software

On ubuntu-latest, I checked:

* Docker version
* Python version
* Node version
* Git version

### Why pre-installed tools matter?

* Faster builds
* No need to manually install dependencies
* Standardized environment
* Reduced setup time

This makes CI pipelines efficient and reliable.

---

# Task 3 – Self-Hosted Runner Setup

I configured a self-hosted runner on my Linux machine (EC2).

Steps followed:

1. Downloaded runner package
2. Extracted files
3. Configured using config.sh
4. Started runner using run.sh

After setup, the runner appeared as:

🟢 Idle

This confirmed successful registration.

---

# Task 4 – Running Workflow on Self-Hosted Runner

Created workflow:

```yaml
runs-on: [self-hosted, my-linux-runner]
```

The workflow:

* Printed hostname
* Printed working directory
* Created test-file.txt

After execution, I verified inside:

~/actions-runner/_work/<repo>/<repo>/

The file existed on my EC2 machine.

This proved:

* GitHub sent the job
* My machine executed it
* Self-hosted runner works correctly

---

# Task 5 – Labels

Added custom label:

my-linux-runner

Updated workflow:

```yaml
runs-on: [self-hosted, my-linux-runner]
```

### Why labels are useful?

Labels help when:

* Multiple self-hosted runners exist
* Different environments are used (staging, production, GPU, high-memory)
* Specific machines are required for specific jobs

Labels give precise control over job execution.

---

# Task 6 – GitHub-Hosted vs Self-Hosted Comparison

| Feature             | GitHub-Hosted          | Self-Hosted                                     |
| ------------------- | ---------------------- | ----------------------------------------------- |
| Who manages it?     | GitHub                 | Me                                              |
| Cost                | Free (limited minutes) | Server cost                                     |
| Pre-installed tools | Yes                    | I install manually                              |
| Good for            | Standard CI/CD         | Custom infra, internal network, heavy workloads |
| Security concern    | Code runs on GitHub VM | Code runs on my machine                         |
| Maintenance         | Zero                   | I manage updates & uptime                       |

---

# Key Learnings

* CI jobs require a machine (runner) to execute.
* GitHub-hosted runners are convenient and fast.
* Self-hosted runners provide full control.
* Labels help scale infrastructure.
* Infrastructure responsibility shifts when using self-hosted runners.

Today I moved from “using CI” to understanding the infrastructure behind it.

---

# Screenshots (To Add)

![alt text](<Screenshot (423).png>) ![alt text](<Screenshot (413).png>) ![alt text](<Screenshot (414).png>) ![alt text](<Screenshot (415).png>) ![alt text](<Screenshot (416).png>) ![alt text](<Screenshot (418).png>) ![alt text](<Screenshot (419).png>) ![alt text](<Screenshot (421).png>) ![alt text](<Screenshot (422).png>)

---

# Conclusion

This was a major milestone in understanding CI/CD infrastructure.

Running CI on my own machine demonstrated:

* Infrastructure ownership
* Runner lifecycle
* Workflow-machine communication

Real DevOps begins when you understand where your code actually runs.
