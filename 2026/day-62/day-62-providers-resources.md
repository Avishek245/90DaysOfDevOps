# Day 62 – Providers, Resources and Dependencies

## 📅 Date
25 July 2026

---

# Objective

The objective of this assignment was to build a complete AWS networking infrastructure using Terraform while understanding how Terraform manages providers, resources, and dependencies.

Unlike previous exercises where individual resources were created independently, this assignment focused on building interconnected infrastructure components such as a VPC, Subnet, Internet Gateway, Route Table, Security Group, EC2 Instance, and an S3 Bucket. Along the way, I explored how Terraform automatically determines the correct resource creation order through implicit dependencies and how explicit dependencies can be defined using the `depends_on` meta-argument.

---

# Prerequisites

- Terraform
- AWS CLI
- AWS Account
- Visual Studio Code
- Git & GitHub

---

# Task 1 – Explore the AWS Provider

## Configure the AWS Provider

I started by creating a `providers.tf` file to configure Terraform and specify the AWS provider.

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  required_version = ">= 1.5.0"
}

provider "aws" {
  region = "us-east-1"
}
```

After creating the configuration, I initialized the project using:

```bash
terraform init
```

Terraform downloaded the AWS provider plugin and created the `.terraform.lock.hcl` file.

The installed AWS provider version was:

```
5.100.0
```

### Understanding Version Constraints

#### `~> 5.0`

Allows Terraform to install any compatible **5.x** version while preventing upgrades to version **6.x**.

Examples:

- ✅ 5.10.0
- ✅ 5.50.1
- ❌ 6.0.0

#### `>= 5.0`

Allows Terraform to install version **5.0** or any later version, including future major releases.

Examples:

- ✅ 5.0
- ✅ 6.0
- ✅ 7.0

#### `= 5.0.0`

Pins Terraform to one exact provider version.

Only:

```
5.0.0
```

is allowed.

### Understanding `.terraform.lock.hcl`

The `.terraform.lock.hcl` file is automatically generated after running `terraform init`.

Its purpose is to:

- Lock the exact provider version.
- Ensure all team members use the same provider version.
- Make Terraform executions reproducible across different environments.
- Verify downloaded provider plugins using checksum hashes.

This file should always be committed to version control.

---

# Task 2 – Build a VPC from Scratch

I built a complete networking infrastructure by creating the following AWS resources.

## Virtual Private Cloud (VPC)

Created a VPC using the CIDR block:

```
10.0.0.0/16
```

Tag:

```
TerraWeek-VPC
```

---

## Public Subnet

Created a public subnet inside the VPC using:

```
10.0.1.0/24
```

The subnet was configured to automatically assign public IP addresses to newly launched instances.

Tag:

```
TerraWeek-Public-Subnet
```

---

## Internet Gateway

Created and attached an Internet Gateway to the VPC to enable internet connectivity.

Tag:

```
TerraWeek-IGW
```

---

## Route Table

Created a Route Table containing the default route:

```
0.0.0.0/0
```

pointing to the Internet Gateway.

Tag:

```
TerraWeek-Public-RT
```

---

## Route Table Association

Associated the Route Table with the Public Subnet.

Terraform Plan showed:

```text
Plan: 5 to add, 0 to change, 0 to destroy.
```

After running:

```bash
terraform apply
```

Terraform successfully provisioned all networking resources.

---

# Task 3 – Understanding Implicit Dependencies

Terraform automatically builds a dependency graph by analyzing resource references.

For example:

```hcl
vpc_id = aws_vpc.main.id
```

creates an implicit dependency because the subnet cannot exist until the VPC has been created.

Terraform automatically determined the following dependency chain:

- VPC → Subnet
- VPC → Internet Gateway
- Internet Gateway → Route Table
- Route Table + Subnet → Route Table Association

### Implicit Dependencies Found

| Resource | Depends On |
|-----------|------------|
| Public Subnet | VPC |
| Internet Gateway | VPC |
| Route Table | VPC & Internet Gateway |
| Route Table Association | Route Table & Subnet |

### How does Terraform know the order?

Terraform analyzes resource references inside the configuration. Whenever one resource references another resource attribute, Terraform automatically creates the dependency and provisions resources in the correct order.

### What happens if the subnet is created before the VPC?

AWS would reject the request because a subnet cannot be created without an existing VPC.

---

# Task 4 – Add Security Group and EC2 Instance

After completing the networking infrastructure, I added compute resources.

## Security Group

Created a Security Group inside the VPC.

### Inbound Rules

- SSH (Port 22)
- HTTP (Port 80)

Source:

```
0.0.0.0/0
```

### Outbound Rules

Allowed all outbound traffic.

Tag:

```
TerraWeek-SG
```

---

## EC2 Instance

Launched an EC2 instance using:

- Amazon Linux 2 AMI
- Instance Type: `t2.micro`
- Public Subnet
- Public IP Enabled
- Attached Security Group

Tag:

```
TerraWeek-Server
```

Terraform successfully launched the EC2 instance, which received a Public IPv4 address.

---

# Task 5 – Explicit Dependencies using depends_on

Terraform usually detects dependencies automatically.

However, there are situations where two resources do not directly reference each other but still need to be created in a specific order.

To demonstrate this, I created an S3 Bucket for application logs.

```hcl
depends_on = [
    aws_instance.main
]
```

Although the S3 bucket does not reference the EC2 instance, the `depends_on` meta-argument instructs Terraform to create the EC2 instance first.

This is known as an **explicit dependency**.

---

## Dependency Graph

I generated Terraform's dependency graph using:

```bash
terraform graph
```

The graph visually represents how Terraform connects resources and determines the correct creation order.

### When should depends_on be used?

**Example 1**

Create an S3 bucket only after an EC2 instance has been deployed.

**Example 2**

Deploy monitoring or backup infrastructure only after application servers become available.

---

# Task 6 – Lifecycle Rules and Destroy

Terraform lifecycle rules control how resources behave during updates and replacement.

## create_before_destroy

I added the following lifecycle rule to the EC2 instance:

```hcl
lifecycle {
    create_before_destroy = true
}
```

This instructs Terraform to create the replacement resource before destroying the existing one, helping reduce downtime.

---

## Other Lifecycle Meta Arguments

### prevent_destroy

Prevents Terraform from accidentally deleting important resources.

Example:

- Production databases
- Critical S3 buckets

---

### ignore_changes

Allows Terraform to ignore changes made outside Terraform for selected resource attributes.

Example:

Ignoring tags modified manually through the AWS Console.

---

## Destroy Infrastructure

After completing the assignment, I removed all created AWS resources using:

```bash
terraform destroy
```

Terraform deleted resources in reverse dependency order, ensuring that dependencies were handled correctly during cleanup.

Resources destroyed:

- S3 Bucket
- EC2 Instance
- Security Group
- Route Table Association
- Route Table
- Internet Gateway
- Public Subnet
- VPC

This ensured that no unnecessary AWS resources continued running, helping avoid additional cloud costs.

---

# Key Learnings

- Configured the AWS Provider using Terraform.
- Learned how Terraform manages provider version constraints.
- Understood the purpose of `.terraform.lock.hcl`.
- Built a complete AWS networking infrastructure from scratch.
- Created a VPC, Public Subnet, Internet Gateway, Route Table, Security Group, EC2 Instance, and S3 Bucket.
- Learned the difference between implicit and explicit dependencies.
- Used `depends_on` to create explicit dependencies.
- Generated and analyzed the Terraform dependency graph.
- Explored Terraform lifecycle meta-arguments.
- Successfully provisioned and destroyed AWS infrastructure using Terraform.

---

# Conclusion

This assignment provided practical experience in provisioning a complete AWS infrastructure using Terraform while understanding how resources are connected through dependencies. I learned how Terraform automatically resolves implicit dependencies, when explicit dependencies using `depends_on` are necessary, how lifecycle rules influence infrastructure updates, and how to safely clean up resources after deployment. These concepts are fundamental for building scalable, maintainable, and production-ready Infrastructure as Code (IaC) solutions.

---

# Screenshots
![alt text](<images/Screenshot (733).png>) ![alt text](<images/Screenshot (734).png>) ![alt text](<images/Screenshot (735).png>) ![alt text](<images/Screenshot (736).png>) ![alt text](<images/Screenshot (737).png>) ![alt text](<images/Screenshot (738).png>) ![alt text](<images/Screenshot (739).png>) ![alt text](<images/Screenshot (740).png>) ![alt text](<images/Screenshot (741).png>) ![alt text](<images/Screenshot (742).png>) ![alt text](<images/Screenshot (743).png>) ![alt text](<images/Screenshot (744).png>) ![alt text](<images/Screenshot (745).png>) ![alt text](<images/Screenshot (747).png>) ![alt text](<images/Screenshot (751).png>) ![alt text](<images/Screenshot (752).png>) ![alt text](<images/Screenshot (753).png>) ![alt text](images/Screenshot(754).PNG)