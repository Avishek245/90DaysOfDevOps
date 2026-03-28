### Day 46 – Reusable Workflows & Composite Actions
Overview

Today I learned how to:

Create a Reusable Workflow
Call it from another workflow
Pass inputs and secrets
Define and use outputs
Create a Composite Action
Understand the difference between reusable workflows and composite actions
### Task 1 – Understanding Concepts
1️⃣ What is a Reusable Workflow?

A reusable workflow is a GitHub Actions workflow that can be called by another workflow using workflow_call.

It helps avoid duplication by centralizing CI/CD logic.

2️⃣ What is workflow_call?

workflow_call is a trigger that allows one workflow to be executed by another workflow.

Example:

on:
  workflow_call:
3️⃣ Difference Between Reusable Workflow and Regular Action
A reusable workflow runs as a full job.
A regular action runs as a step inside a job.
Reusable workflows can contain multiple jobs.
Actions (composite or marketplace) contain steps only.
4️⃣ Where Must Reusable Workflows Live?

They must be inside:

.github/workflows/

Otherwise GitHub will not detect them.

Task 2 – Reusable Workflow

File:

.github/workflows/reusable-build.yml
name: Reusable Build Workflow

on:
  workflow_call:
    inputs:
      app_name:
        description: "Application Name"
        required: true
        type: string
      environment:
        description: "Environment"
        required: true
        type: string
        default: staging
    secrets:
      docker_token:
        required: true

jobs:
  build:
    runs-on: ubuntu-latest

    outputs:
      build_version: ${{ steps.version.outputs.build_version }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Print build info
        run: |
          echo "Building ${{ inputs.app_name }} for ${{ inputs.environment }}"
          echo "Docker token is set: true"

      - name: Generate version
        id: version
        run: |
          SHORT_SHA=$(echo $GITHUB_SHA | cut -c1-7)
          VERSION="v1.0-$SHORT_SHA"
          echo "build_version=$VERSION" >> $GITHUB_OUTPUT
Task 3 – Caller Workflow

File:

.github/workflows/call-build.yml
name: Call Reusable Build

on:
  push:
    branches:
      - main

jobs:
  build:
    uses: ./.github/workflows/reusable-build.yml
    with:
      app_name: "my-web-app"
      environment: "production"
    secrets:
      docker_token: ${{ secrets.DOCKER_TOKEN }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Print build version
        run: echo "Build version is ${{ needs.build.outputs.build_version }}"
Task 4 – Outputs

The reusable workflow generates:

v1.0-<short-sha>

The caller workflow accesses it using:

${{ needs.build.outputs.build_version }}
Task 5 – Composite Action

Folder:

.github/actions/setup-and-greet/

File:

action.yml
name: Setup and Greet
description: Custom composite action

inputs:
  name:
    description: "Name of the person"
    required: true
  language:
    description: "Greeting language"
    required: false
    default: "en"

outputs:
  greeted:
    description: "Whether greeting happened"
    value: ${{ steps.set-output.outputs.greeted }}

runs:
  using: "composite"
  steps:
    - name: Print Greeting
      run: |
        if [ "${{ inputs.language }}" = "en" ]; then
          echo "Hello, ${{ inputs.name }}!"
        elif [ "${{ inputs.language }}" = "es" ]; then
          echo "Hola, ${{ inputs.name }}!"
        else
          echo "Hi, ${{ inputs.name }}!"
        fi
      shell: bash

    - name: Print Date and OS
      run: |
        echo "Date: $(date)"
        echo "Runner OS: $RUNNER_OS"
      shell: bash

    - name: Set output
      id: set-output
      run: echo "greeted=true" >> $GITHUB_OUTPUT
      shell: bash
Workflow Using Composite Action

File:

.github/workflows/use-composite.yml
name: Use Composite Action

on:
  push:
    branches:
      - main

jobs:
  greet:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Use custom action
        uses: ./.github/actions/setup-and-greet
        with:
          name: "Avishek"
          language: "en"

      - name: Done
        run: echo "Composite action executed"
### Task 6 – Comparison Table
| Feature                      | Reusable Workflow           | Composite Action                         |
| ---------------------------- | --------------------------- | ---------------------------------------- |
| Triggered by                 | `workflow_call`             | `uses:` inside step                      |
| Can contain jobs?            | Yes                         | No                                       |
| Can contain multiple steps?  | Yes                         | Yes                                      |
| Lives where?                 | `.github/workflows/`        | `.github/actions/` (or anywhere in repo) |
| Can accept secrets directly? | Yes                         | No (must pass as inputs)                 |
| Best for                     | Reusing entire CI pipelines | Reusing grouped steps                    |

### Screenshot
![alt text](<Screenshot (455).png>) ![alt text](<Screenshot (450).png>) ![alt text](<Screenshot (451).png>) ![alt text](<Screenshot (452).png>) ![alt text](<Screenshot (453).png>) ![alt text](<Screenshot (454).png>)