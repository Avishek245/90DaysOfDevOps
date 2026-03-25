# Day 44 – Secrets, Artifacts & Running Real Tests in CI

## 🚀 Objective
Today I implemented secure secret handling, artifact storage, real test execution, and caching inside GitHub Actions CI.

This is where CI starts doing real production-like work.

---

# 🔐 Task 1 – GitHub Secrets

## What I Did
- Created a repository secret: `MY_SECRET_MESSAGE`
- Accessed it using: `${{ secrets.MY_SECRET_MESSAGE }}`
- Verified that GitHub masks secret values in logs

## Important Observation
When trying to print the secret directly in logs, GitHub replaced it with:


## What I Learned
- Secrets are encrypted
- Secrets are automatically masked in logs
- Never print secrets in CI
- Logs may be visible to other collaborators
- Exposing secrets can leak tokens, passwords, API keys

---

# 🌍 Task 2 – Using Secrets as Environment Variables

## What I Did
- Passed secret as environment variable:
  ```yaml
  env:
    SECRET_MESSAGE: ${{ secrets.MY_SECRET_MESSAGE }}
Used it safely inside shell commands
Added:
DOCKER_USERNAME
DOCKER_TOKEN
What I Learned
Never hardcode credentials
Use Docker access tokens instead of passwords
Secure authentication is critical in CI/CD pipelines
📦 Task 3 – Upload Artifacts
What I Did
Generated a log file in workflow
Uploaded it using actions/upload-artifact@v4
Downloaded it from the Actions tab
Use Case of Artifacts

Artifacts are useful for:

Test reports
Build outputs
Compiled binaries
Logs for debugging
Passing files between jobs

📸 Screenshot: (Add artifact download screenshot here)

# 🔄 Task 4 – Download Artifacts Between Jobs
What I Did
Job 1: Created file and uploaded artifact
Job 2: Downloaded artifact and printed contents
Real-World Usage
Build job → produce artifact
Deploy job → download and deploy it
Separate test and release stages cleanly
🧪 Task 5 – Running Real Tests in CI
What I Did
Added health-check.sh script
Ran it in GitHub Actions
Intentionally broke the script (exit 1)
Observed pipeline failure (red)
Fixed it → pipeline turned green
What I Learned
CI fails automatically on non-zero exit code
CI enforces code quality
Testing inside pipeline prevents broken deployments


## ⚡ Task 6 – Caching
What I Did
Used actions/cache@v4
Cached dependency directories
Ran workflow twice
Observed faster second run
What Is Being Cached?
Dependency files (e.g., pip packages, node_modules)
Stored in GitHub's cache storage
Retrieved using cache key matching
Why It Matters
Reduces build time
Improves CI performance
Saves compute resources
🧠 Key Takeaways
Secrets must always be handled securely
Never expose sensitive values in logs
Artifacts allow job-to-job file sharing
CI enforces correctness via exit codes
Caching makes pipelines faster and more efficient
Real-world CI pipelines combine all these concepts
🏁 Final Result

✅ Secrets configured
✅ Artifacts uploaded & downloaded
✅ Real test executed
✅ Pipeline failure verified
✅ Pipeline success verified
✅ Caching implemented

## 📌 Reflection

Today was the first time my CI pipeline:

Handled secure credentials
Stored and transferred build outputs
Executed real validation logic
Failed and recovered intentionally

This feels like real DevOps engineering.

📸 Screenshot: 
![alt text](<Screenshot (440).png>) ![alt text](<Screenshot (434).png>) ![alt text](<Screenshot (435).png>) ![alt text](<Screenshot (436).png>) ![alt text](<Screenshot (437).png>) ![alt text](<Screenshot (438).png>) ![alt text](<Screenshot (439).png>)
