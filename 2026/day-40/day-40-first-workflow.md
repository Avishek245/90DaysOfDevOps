Day 40 – My First GitHub Actions Workflow 🚀
Repository Name

github-actions-practice

📌 Workflow File

Location:

.github/workflows/hello.yml
✅ Final Workflow YAML
name: First Workflow

on:
  push:

jobs:
  greet:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Say Hello
        run: echo "Hello from GitHub Actions!"

      - name: Print Date
        run: date

      - name: Print Branch Name
        run: echo "Branch name is ${{ github.ref_name }}"

      - name: List Files
        run: ls -la

      - name: Print Runner OS
        run: echo "Running on $RUNNER_OS"
📷 Screenshot of Green Run

(Attach screenshot of your successful workflow run here)

🧠 Understanding the Workflow Anatomy
🔹 name:

Defines the name of the workflow shown in the Actions tab.

🔹 on:

Defines when the workflow will trigger.

In this case:

on:
  push:

This means the workflow runs every time code is pushed to the repository.

🔹 jobs:

Defines the tasks that will run in the workflow.

A workflow can have multiple jobs.

🔹 runs-on:

Specifies the virtual machine environment where the job runs.

Here:

runs-on: ubuntu-latest

This means GitHub provides a Linux virtual machine.

🔹 steps:

Defines the sequence of actions inside a job.

Each job executes steps one by one.

🔹 uses:

Runs a pre-built GitHub Action.

Example:

uses: actions/checkout@v4

This action checks out the repository code into the runner.

🔹 run:

Executes shell commands on the runner.

Example:

run: echo "Hello from GitHub Actions!"
🧪 Breaking the Pipeline (Intentional Failure)

I added this step to test failure behavior:

- name: Break the build
  run: exit 1
🔴 What Happened?

The workflow turned red.

The job stopped immediately.

The failed step showed an error.

Exit code 1 indicates failure.

📖 What I Learned

If any step fails, the job fails.

The logs clearly show where the failure occurred.

Debugging is done by reading step logs.

After removing the failing step and pushing again, the pipeline turned green again.

🚀 Key Learnings from Day 40

How to create a GitHub Actions workflow

How workflows trigger on push

How jobs and steps work

How to use built-in GitHub variables

How to debug a failed pipeline

How CI runs in the cloud automatically

💡 Reflection

Today CI/CD stopped being theory and became real.

I wrote my first workflow.
I saw it run in the cloud.
I broke it.
I fixed it.
I watched it turn green.

That green checkmark hits different. ✅


### Screnshots

![alt text](<Screenshot (401).png>) ![alt text](<Screenshot (395).png>) ![alt text](<Screenshot (396).png>) ![alt text](<Screenshot (397).png>) ![alt text](<Screenshot (398).png>) ![alt text](<Screenshot (399).png>) ![alt text](<Screenshot (400).png>)