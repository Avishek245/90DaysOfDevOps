# DevSecOps Capstone – Secure CI/CD Pipeline Implementation

## 📌 Overview

This project demonstrates the implementation of a secure CI/CD pipeline using GitHub Actions with integrated security best practices (DevSecOps).

The pipeline includes:

* Build & Test automation
* Dependency vulnerability scanning
* Container image security scanning
* Secure Docker image publishing
* Workflow permission hardening
* GitHub secret protection features

---

# ✅ Task 2 – GitHub Secret Scanning

## Difference Between Secret Scanning and Push Protection

**Secret Scanning** detects exposed secrets (API keys, tokens, passwords) in a repository after they are pushed and generates a security alert.

**Push Protection** prevents secrets from being pushed to the repository by blocking the commit before it is completed.

### Key Difference:

* Secret scanning = Detection after push
* Push protection = Prevention before push

## What Happens If GitHub Detects a Leaked AWS Key?

If GitHub detects a leaked AWS access key:

1. A security alert is generated in the repository.
2. GitHub may notify AWS automatically.
3. AWS may deactivate the compromised key.
4. The repository owner must:

   * Remove the key from the code
   * Rotate (regenerate) AWS credentials
   * Clean the secret from Git history

If push protection is enabled, the push is blocked immediately and the secret never reaches the repository.

---

# ✅ Task 3 – Dependency Vulnerability Scanning (PR Pipeline)

A dependency review step was added to the PR pipeline:

```yaml
- name: Check Dependencies for Vulnerabilities
  uses: actions/dependency-review-action@v4
  with:
    fail-on-severity: critical
```

### Purpose

* Scans newly added dependencies in Pull Requests
* Checks against known vulnerability databases
* Fails the PR if a CRITICAL vulnerability is detected

### Verification

* Opened a new branch
* Added a dependency
* Created a Pull Request
* Verified that "dependency-review" appears as a check in the PR

---

# ✅ Task 4 – Restrict Workflow Permissions

To follow the Principle of Least Privilege, workflow permissions were restricted.

Added this block to multiple workflow files:

```yaml
permissions:
  contents: read
```

If a workflow needs to comment on PRs:

```yaml
permissions:
  contents: read
  pull-requests: write
```

## Why Is It Good Practice to Limit Workflow Permissions?

Limiting workflow permissions reduces security risks by ensuring workflows only have the minimum access required.

This prevents potential damage if:

* A GitHub Action is compromised
* A third-party action contains malicious code
* A token is exposed

## What Could Go Wrong If a Compromised Action Has Write Access?

If write access is granted and the action is compromised, it could:

* Modify repository code
* Inject malicious code
* Push unauthorized commits
* Delete branches or tags
* Leak sensitive information
* Introduce backdoors into production

Restricting permissions minimizes these risks.

---

# ✅ Task 5 – Full Secure Pipeline Architecture

## Pull Request Flow

```
PR opened
  → Build & Test
  → Dependency vulnerability check
  → PR checks pass or fail
```

Security Benefits:

* Prevents vulnerable dependencies from being merged
* Ensures code quality before integration

---

## Main Branch Flow

```
Merge to main
  → Build & Test
  → Docker Build
  → Trivy image scan (fail on CRITICAL)
  → Docker Push (only if scan passes)
  → Deploy
```

Security Benefits:

* Vulnerable container images are blocked
* Docker images are pushed only if secure
* Deployment occurs only after security validation

---

## Always Active Security

* GitHub Secret Scanning
* Push Protection for secrets

These features protect against accidental leakage of:

* API keys
* AWS credentials
* Access tokens
* Passwords

---

# 🏆 Final Outcome

The final CI/CD pipeline includes:

✔ Automated build and testing
✔ Pull request validation
✔ Dependency vulnerability scanning
✔ Container image vulnerability scanning
✔ Fail-on-critical security enforcement
✔ Restricted workflow permissions
✔ Secure Docker image publishing
✔ Secret detection and prevention

This implementation demonstrates a real-world DevSecOps pipeline with integrated security at multiple stages of the software delivery lifecycle.

### Screenshot 
![alt text](<Screenshot (491).png>) ![alt text](<Screenshot (486).png>) ![alt text](<Screenshot (487).png>) ![alt text](<Screenshot (490).png>)