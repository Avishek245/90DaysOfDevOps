# Day 63 — Variables, Outputs, Data Sources and Expressions

## TerraWeek Challenge — #TrainWithShubham

## Objective

Refactored my Day 62 Terraform configuration to make it dynamic, reusable, and environment-aware.

---

## Task 1 — Extract Variables

Created `variables.tf` with:

- `region` — string
- `vpc_cidr` — string
- `subnet_cidr` — string
- `instance_type` — string
- `project_name` — string
- `environment` — string
- `allowed_ports` — list(number)
- `extra_tags` — map(string)

### Variable Types

| Type | Purpose |
|---|---|
| string | Text |
| number | Numeric values |
| bool | True/False |
| list | Collection of values |
| map | Key/value pairs |

---

## Task 2 — Variable Files & Precedence

Created:

### `terraform.tfvars`

```hcl
project_name  = "terraweek"
environment   = "dev"
instance_type = "t2.micro"
```

### `prod.tfvars`

```hcl
project_name  = "terraweek"
environment   = "prod"
instance_type = "t3.small"
vpc_cidr      = "10.1.0.0/16"
subnet_cidr   = "10.1.1.0/24"
```

Tested:

```bash
terraform plan
terraform plan -var-file="prod.tfvars"
terraform plan -var="instance_type=t2.nano"
```

### Precedence

```text
Default → terraform.tfvars → *.auto.tfvars → -var-file → -var → TF_VAR_*
```

---

## Task 3 — Outputs

Created `outputs.tf` for:

- VPC ID
- Subnet ID
- EC2 Instance ID
- Public IP
- Public DNS
- Security Group ID

Used:

```bash
terraform apply
terraform output
terraform output instance_public_ip
terraform output -json
```

Verified the EC2 public IP successfully.

---

## Task 4 — Data Sources

Removed the hardcoded AMI ID and added an AWS AMI data source.

```hcl
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
}
```

Used:

```hcl
ami = data.aws_ami.amazon_linux.id
```

Also added:

```hcl
data "aws_availability_zones" "available" {}
```

Used the first available AZ:

```hcl
availability_zone = data.aws_availability_zones.available.names[0]
```

### Resource vs Data

`resource` creates/manages infrastructure.

`data` reads existing information.

---

## Task 5 — Locals

Added locals for reusable names and tags:

```hcl
locals {
  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
```

Used `merge()` for consistent tagging:

```hcl
tags = merge(local.common_tags, {
  Name = "${local.name_prefix}-server"
})
```

---

## Task 6 — Functions & Conditional Expressions

Practiced in:

```bash
terraform console
```

Functions tested:

```hcl
upper("terraweek")
join("-", ["terra", "week", "2026"])
format("arn:aws:s3:::%s", "my-bucket")
length(["a", "b", "c"])
lookup({dev = "t2.micro", prod = "t3.small"}, "dev")
toset(["a", "b", "a"])
cidrsubnet("10.0.0.0/16", 8, 1)
```

### Five Useful Functions

- `upper()` — converts text to uppercase
- `join()` — joins strings
- `length()` — returns collection size
- `merge()` — combines maps
- `cidrsubnet()` — calculates subnet CIDRs

### Conditional Expression

```hcl
var.environment == "prod" ? "t3.small" : "t2.micro"
```

This allows the instance type to change based on the environment.

---

## Commands Used

```bash
terraform fmt
terraform validate
terraform plan
terraform plan -var-file="prod.tfvars"
terraform apply
terraform output
terraform output instance_public_ip
terraform console
```

---

## Key Learnings

- Variables make Terraform reusable.
- `.tfvars` files support different environments.
- Outputs expose infrastructure information.
- Data sources dynamically retrieve AWS information.
- Locals reduce repetition.
- Functions make configurations dynamic.
- Conditional expressions support environment-specific configurations.

---

## Assignment Status

- Task 1 — Variables
- Task 2 — Variable Files
- Task 3 — Outputs
- Task 4 — Data Sources
- Task 5 — Locals
- Task 6 — Functions & Expressions
- Terraform Validate
- Terraform Plan
- Terraform Apply
- AWS Verification

---

## Screenshots

![alt text](<Screenshot (766).png>) ![alt text](<Screenshot (767).png>) ![alt text](<Screenshot (769).png>) ![alt text](<Screenshot (770).png>) ![alt text](<Screenshot (771).png>) ![alt text](<Screenshot (772).png>) ![alt text](<Screenshot (773).png>) ![alt text](screenhot(762).PNG) ![alt text](screenhot(771).PNG) ![alt text](<Screenshot (755).png>) ![alt text](<Screenshot (756).png>) ![alt text](<Screenshot (759).png>) ![alt text](<Screenshot (760).png>) ![alt text](<Screenshot (761).png>) ![alt text](<Screenshot (762).png>) ![alt text](<Screenshot (763).png>)

#90DaysOfDevOps #TerraWeek #DevOpsKaJosh #TrainWithShubham
