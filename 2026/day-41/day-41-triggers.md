Day 41 – Triggers & Matrix Builds
🎯 Objective

Today I learned how GitHub Actions workflows can be triggered in multiple ways and how to use matrix builds to test across different environments.

This included:

Pull Request trigger
Scheduled (cron) trigger
Manual trigger
Matrix strategy
Exclude combinations
Fail-fast behavior
✅ Task 1 – Pull Request Trigger
📁 File: .github/workflows/pr-check.yml
name: PR Check

on:
  pull_request:
    branches: [main]
    types: [opened, synchronize]

jobs:
  pr-job:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Print branch name
        run: echo "PR check running for branch: ${{ github.head_ref }}"
🔎 What I Verified
Workflow triggered automatically when PR was opened
It also triggered when new commits were pushed to the PR
Status appeared on the PR page
✅ Task 2 – Scheduled Trigger
Cron Configuration
on:
  schedule:
    - cron: '0 0 * * *'
🕒 Meaning

Runs every day at midnight (UTC).

❓ Cron for Every Monday at 9 AM (UTC)
0 9 * * 1
🧠 Important Notes
Cron time is in UTC
Workflow must exist in main
It does not run immediately after pushing
✅ Task 3 – Manual Trigger
📁 File: .github/workflows/manual.yml
name: Manual Trigger Workflow

on:
  workflow_dispatch:
    inputs:
      environment:
        description: "Enter environment (staging/production)"
        required: true
        default: "staging"

jobs:
  manual-job:
    runs-on: ubuntu-latest

    steps:
      - name: Print selected environment
        run: echo "Deploying to ${{ github.event.inputs.environment }}"
🔎 What I Verified
I was able to manually trigger from the Actions tab
I provided input (staging/production)
Input value printed correctly in logs
✅ Task 4 – Matrix Build
📁 File: .github/workflows/matrix.yml
name: Matrix Build

on:
  push:
    branches: [main]

jobs:
  matrix-build:
    runs-on: ${{ matrix.os }}

    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ["3.12","3.13","3.14"]

        exclude:
          - os: windows-latest
            python-version: "3.12"

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Print Python version
        run: python --version
🧠 Matrix Explanation

Matrix creates combinations of:

Operating Systems × Python Versions

Without exclude:

2 OS × 3 Python = 6 jobs

With exclude (removed Windows + 3.12):

6 - 1 = 5 jobs

Each Python version runs once per OS.

Example:

Python 3.14 runs on Ubuntu
Python 3.14 runs on Windows

That’s why some versions appear twice — it’s expected behavior.

✅ Task 5 – Fail-Fast Behavior
Default (true)

If one matrix job fails:

All other running jobs stop immediately.
With fail-fast: false

If one job fails:

Other matrix jobs continue running.

This helps when testing across multiple environments and you want complete results.

📸 Screenshots Added
PR workflow running
Manual workflow execution
Matrix parallel jobs
Exclude behavior demonstration
🚀 What I Learned
Different workflow triggers and when to use them
How cron scheduling works (UTC-based)
How to manually trigger workflows with inputs
How matrix builds expand combinations
How exclude works
Difference between fail-fast true vs false
🏁 Conclusion

Today I moved from basic CI to multi-environment testing strategy.

Matrix builds are extremely powerful and used in real-world production pipelines.

### Screenshot 

![alt text](<Screenshot (413).png>) ![alt text](<Screenshot (407).png>) ![alt text](<Screenshot (408).png>) ![alt text](<Screenshot (409).png>) ![alt text](<Screenshot (410).png>) ![alt text](<Screenshot (411).png>) ![alt text](<Screenshot (412).png>)