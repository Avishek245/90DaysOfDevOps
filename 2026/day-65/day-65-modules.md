# Day 65 — Terraform Modules: Build Reusable Infrastructure

## Overview

On Day 65 of #90DaysOfDevOps, I focused on **Terraform Modules** and learned how modules make Infrastructure as Code reusable, organized, and scalable.

Instead of keeping all Terraform resources inside one large `main.tf`, I separated reusable infrastructure into custom child modules and also used a public module from the Terraform Registry.

### What I Built

- A custom reusable **EC2 module**
- A custom reusable **Security Group module**
- Reused the EC2 module twice for two different servers
- Used a `dynamic` block to generate Security Group ingress rules
- Replaced the hand-written VPC configuration with the official `terraform-aws-modules/vpc/aws` module
- Used module inputs and outputs to connect resources
- Inspected how modules appear in Terraform state
- Practiced module versioning
- Successfully destroyed the infrastructure after completing the practical

---

# Task 1 — Understand Module Structure

The project was organized using a root module and two custom child modules:

```text
terraform-modules/
├── main.tf
├── variables.tf
├── outputs.tf
├── providers.tf
└── modules/
    ├── ec2-instance/
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    │
    └── security-group/
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

## Root Module vs Child Module

### Root Module

The root module is the main Terraform project where Terraform commands such as:

```bash
terraform init
terraform plan
terraform apply
```

are executed.

It is responsible for:

- Calling child modules
- Passing input variables
- Connecting module outputs to other resources
- Managing the overall infrastructure configuration

### Child Module

A child module is a reusable collection of Terraform configuration.

For this assignment I created:

```text
modules/ec2-instance/
modules/security-group/
```

The child modules contain the actual resource definitions and expose variables and outputs.

A simple way to think about it:

```text
Child Module = Reusable Function
Root Module  = Code Calling the Function
```

---

# Task 2 — Build a Custom EC2 Module

The EC2 module was created under:

```text
modules/ec2-instance/
```

The goal was to make the EC2 configuration reusable so that the same module could create multiple instances with different values.

## EC2 Module — `variables.tf`

```hcl
variable "ami_id" {
  description = "AMI ID for the EC2 instance"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}

variable "subnet_id" {
  description = "Subnet ID where the EC2 instance will be launched"
  type        = string
}

variable "security_group_ids" {
  description = "List of security group IDs"
  type        = list(string)
}

variable "instance_name" {
  description = "Name tag for the EC2 instance"
  type        = string
}

variable "tags" {
  description = "Additional tags for the EC2 instance"
  type        = map(string)
  default     = {}
}
```

These variables make the module flexible.

Instead of hardcoding the AMI, subnet, security groups, instance type, and name, the root module passes these values into the child module.

---

## EC2 Module — `main.tf`

```hcl
resource "aws_instance" "this" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = var.security_group_ids

  tags = merge(
    var.tags,
    {
      Name = var.instance_name
    }
  )
}
```

The `merge()` function combines the common tags with the instance-specific `Name` tag.

This allowed both servers to share common tags while having different names.

---

## EC2 Module — `outputs.tf`

```hcl
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.this.id
}

output "public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.this.public_ip
}

output "private_ip" {
  description = "Private IP address of the EC2 instance"
  value       = aws_instance.this.private_ip
}
```

The outputs allow the root module to retrieve information from the child module.

For example:

```hcl
module.web_server.public_ip
```

---

# Task 3 — Build a Custom Security Group Module

The second custom module was:

```text
modules/security-group/
```

This module creates a Security Group and generates ingress rules dynamically.

## Security Group Module — `variables.tf`

```hcl
variable "vpc_id" {
  description = "VPC ID where the security group will be created"
  type        = string
}

variable "sg_name" {
  description = "Name of the security group"
  type        = string
}

variable "ingress_ports" {
  description = "List of ports to allow for inbound traffic"
  type        = list(number)
  default     = [22, 80]
}

variable "tags" {
  description = "Additional tags for the security group"
  type        = map(string)
  default     = {}
}
```

---

## Security Group Module — `main.tf`

```hcl
resource "aws_security_group" "this" {
  name        = var.sg_name
  description = "Security group created by Terraform module"
  vpc_id      = var.vpc_id

  dynamic "ingress" {
    for_each = var.ingress_ports

    content {
      description = "Allow inbound traffic on port ${ingress.value}"
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.tags,
    {
      Name = var.sg_name
    }
  )
}
```

## Understanding the `dynamic` Block

Instead of manually writing separate ingress blocks for:

```text
22
80
443
```

I passed:

```hcl
ingress_ports = [22, 80, 443]
```

The `dynamic` block loops through the list and creates the required ingress blocks automatically.

Conceptually:

```text
[22, 80, 443]
      ↓
 dynamic "ingress"
      ↓
┌──────────────┐
│ TCP 22       │
│ TCP 80       │
│ TCP 443      │
└──────────────┘
```

This makes the module reusable and avoids repeated configuration.

---

## Security Group Module — `outputs.tf`

```hcl
output "sg_id" {
  description = "ID of the security group"
  value       = aws_security_group.this.id
}
```

The root module uses this output when attaching the Security Group to the EC2 instances.

---

# Task 4 — Call the Custom Modules from Root

The root module called the Security Group module:

```hcl
module "web_sg" {
  source = "./modules/security-group"

  vpc_id        = module.vpc.vpc_id
  sg_name       = "terraweek-web-sg"
  ingress_ports = [22, 80, 443]

  tags = local.common_tags
}
```

The important part is:

```hcl
source = "./modules/security-group"
```

This tells Terraform that the module is a local module.

---

# Reusing the EC2 Module

The same custom EC2 module was called twice.

## Web Server

```hcl
module "web_server" {
  source = "./modules/ec2-instance"

  ami_id             = data.aws_ami.amazon_linux.id
  instance_type      = "t2.micro"
  subnet_id          = module.vpc.public_subnets[0]
  security_group_ids = [module.web_sg.sg_id]
  instance_name      = "terraweek-web"

  tags = local.common_tags
}
```

## API Server

```hcl
module "api_server" {
  source = "./modules/ec2-instance"

  ami_id             = data.aws_ami.amazon_linux.id
  instance_type      = "t2.micro"
  subnet_id          = module.vpc.public_subnets[0]
  security_group_ids = [module.web_sg.sg_id]
  instance_name      = "terraweek-api"

  tags = local.common_tags
}
```

The important learning here is that I did **not** create two separate EC2 resource definitions.

Instead:

```text
             EC2 Module
                 │
        ┌────────┴────────┐
        ▼                 ▼
 terraweek-web       terraweek-api
```

One module was reused with different inputs.

---

# Root Outputs

The root module exposed outputs from the child modules:

```hcl
output "web_server_ip" {
  description = "Public IP of the web server"
  value       = module.web_server.public_ip
}

output "api_server_ip" {
  description = "Public IP of the API server"
  value       = module.api_server.public_ip
}

output "web_server_instance_id" {
  description = "Instance ID of the web server"
  value       = module.web_server.instance_id
}

output "api_server_instance_id" {
  description = "Instance ID of the API server"
  value       = module.api_server.instance_id
}

output "security_group_id" {
  description = "Web security group ID"
  value       = module.web_sg.sg_id
}
```

This demonstrates how outputs flow from:

```text
Resource
   ↓
Child Module Output
   ↓
Root Module Output
```

---

# Task 5 — Use a Public Registry Module

After testing the custom VPC configuration, I replaced the hand-written VPC resources with the public Terraform Registry module:

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "terraweek-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["ap-south-1a", "ap-south-1b"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.3.0/24", "10.0.4.0/24"]

  map_public_ip_on_launch = true

  enable_nat_gateway   = false
  enable_dns_hostnames = true

  tags = local.common_tags
}
```

Terraform downloaded version:

```text
5.21.0
```

The registry module was downloaded into:

```text
.terraform/modules/vpc/
```

The downloaded directory contained files such as:

```text
main.tf
variables.tf
outputs.tf
versions.tf
README.md
CHANGELOG.md
```

This demonstrated that registry modules are reusable packages containing their own Terraform configuration.

---

# Updating Module References

After switching to the VPC registry module, the custom modules were updated to consume its outputs.

## Security Group

```hcl
vpc_id = module.vpc.vpc_id
```

## EC2 Modules

```hcl
subnet_id = module.vpc.public_subnets[0]
```

This created a dependency chain:

```text
Registry VPC Module
        │
        ├── vpc_id
        │      ↓
        │  Security Group Module
        │
        └── public_subnets[0]
               ↓
          EC2 Modules
```

---

# Terraform Initialization

After adding the registry module, I ran:

```bash
terraform init
```

Terraform successfully initialized the project and downloaded the VPC module:

```text
Downloading registry.terraform.io/terraform-aws-modules/vpc/aws 5.21.0
```

Terraform also reused the previously installed AWS provider:

```text
hashicorp/aws v5.100.0
```

The configuration was then validated:

```bash
terraform validate
```

Result:

```text
Success! The configuration is valid.
```

---

# Registry Module Migration

Replacing the hand-written VPC with the registry module resulted in:

```text
Plan: 20 to add, 0 to change, 8 to destroy.
```

The old VPC resources were removed and the new registry-module infrastructure was created.

The final apply completed successfully:

```text
Apply complete! Resources: 20 added, 0 changed, 8 destroyed.
```

The new VPC was:

```text
vpc-020a48aa1f210e6fe
```

The new Security Group was:

```text
sg-06453b0a11136fc10
```

The new EC2 instances were:

```text
Web → i-038cbccd37b11f15f
API → i-0c06bac9aae041284
```

---

# Public IP Configuration

Initially, the registry module created public subnets with:

```text
map_public_ip_on_launch = false
```

The EC2 instances therefore had private IP addresses but no public IPv4 addresses.

AWS CLI verification showed:

```text
| Instance ID          | State   | Subnet ID                 | Public IP | Private IP |
|----------------------|---------|---------------------------|-----------|------------|
| i-038cbccd37b11f15f  | running | subnet-0288addb8aa7b6feb | None      | 10.0.1.97  |
| i-0c06bac9aae041284  | running | subnet-0288addb8aa7b6feb | None      | 10.0.1.67  |
```

I then added:

```hcl
map_public_ip_on_launch = true
```

to the VPC module.

Terraform correctly planned:

```text
Plan: 0 to add, 2 to change, 0 to destroy.
```

Only the two public subnets were updated:

```text
map_public_ip_on_launch = false → true
```

The change was successfully applied:

```text
Apply complete! Resources: 0 added, 2 changed, 0 destroyed.
```

### Important Observation

The existing EC2 instances still had no public IP because they were launched **before** `map_public_ip_on_launch` was enabled.

The subnet setting applies automatically to **new instances**, but does not retroactively attach public IP addresses to existing EC2 instances.

This was an important practical learning about AWS subnet configuration and existing resources.

---

# Terraform State and Modules

I inspected the Terraform state using:

```bash
terraform state list
```

The state showed module prefixes such as:

```text
module.api_server.aws_instance.this

module.vpc.aws_default_network_acl.this[0]
module.vpc.aws_default_route_table.default[0]
module.vpc.aws_default_security_group.this[0]
module.vpc.aws_internet_gateway.this[0]
module.vpc.aws_route.public_internet_gateway[0]
module.vpc.aws_route_table.private[0]
module.vpc.aws_route_table.private[1]
module.vpc.aws_route_table.public[0]
module.vpc.aws_route_table_association.private[0]
module.vpc.aws_route_table_association.private[1]
module.vpc.aws_route_table_association.public[0]
module.vpc.aws_route_table_association.public[1]
module.vpc.aws_subnet.private[0]
module.vpc.aws_subnet.private[1]
module.vpc.aws_subnet.public[0]
module.vpc.aws_subnet.public[1]
module.vpc.aws_vpc.this[0]

module.web_server.aws_instance.this

module.web_sg.aws_security_group.this
```

This demonstrates Terraform's module addressing format:

```text
module.<module_name>.<resource_type>.<resource_name>
```

For example:

```text
module.web_server.aws_instance.this
```

means the `aws_instance.this` resource inside the `web_server` module.

---

# Module Reuse Demonstrated in State

The state clearly shows that the same EC2 module was used twice:

```text
module.web_server.aws_instance.this
module.api_server.aws_instance.this
```

This proves that one reusable module can create multiple resources with different configurations.

The Security Group was managed through:

```text
module.web_sg.aws_security_group.this
```

The VPC resources were managed through:

```text
module.vpc.*
```

---

# Hand-Written VPC vs Registry VPC Module

## Hand-Written VPC

The original Day 62 configuration required individual resources such as:

```text
aws_vpc
aws_internet_gateway
aws_subnet
aws_route_table
aws_route_table_association
```

The VPC was manually assembled by defining each resource and its relationships.

## Registry VPC Module

The registry module automatically managed a larger set of networking resources, including:

```text
VPC
Internet Gateway
Public Subnets
Private Subnets
Public Route Tables
Private Route Tables
Route Associations
Default Network ACL
Default Route Table
Default Security Group
Internet Gateway Route
```

The Terraform state showed the registry module managing **17 VPC-related resources** in this configuration.

The final migration created:

```text
20 resources
```

and destroyed:

```text
8 resources
```

from the previous hand-written configuration.

### Key Comparison

The important difference is not simply the number of resources.

The registry module encapsulates the networking logic so that I don't have to manually maintain every resource and relationship.

Instead of managing a large number of networking resources directly, I can configure the VPC using a smaller and cleaner module block.

---

# Task 6 — Module Versioning

The registry module was configured with:

```hcl
version = "~> 5.0"
```

This allows compatible 5.x versions.

Examples of Terraform module version constraints:

### Exact Version

```hcl
version = "5.1.0"
```

Uses exactly version 5.1.0.

### Compatible 5.x Version

```hcl
version = "~> 5.0"
```

Allows compatible releases within the 5.x series.

### Version Range

```hcl
version = ">= 5.0, < 6.0"
```

Allows versions from 5.0 up to, but not including, 6.0.

I also used:

```bash
terraform init -upgrade
```

to check for newer compatible module versions.

---

# Terraform State Module Prefixes

The following module prefixes were observed:

```text
module.vpc.
module.web_sg.
module.web_server.
module.api_server.
```

This makes it easier to identify which module owns a particular resource.

For example:

```text
module.vpc.aws_subnet.public[0]
```

belongs to the VPC module.

```text
module.web_sg.aws_security_group.this
```

belongs to the custom Security Group module.

```text
module.web_server.aws_instance.this
```

belongs to the custom EC2 module called `web_server`.

---

# Five Terraform Module Best Practices

## 1. Pin Module Versions

Always specify a version for public registry modules.

For example:

```hcl
version = "~> 5.0"
```

Version pinning helps prevent unexpected changes when a module is updated.

---

## 2. Keep Modules Focused

A module should have a clear responsibility.

For example:

```text
ec2-instance → EC2 infrastructure
security-group → Security Group configuration
```

Keeping modules focused makes them easier to understand, test, maintain, and reuse.

---

## 3. Use Variables Instead of Hardcoding

Inputs such as:

```text
AMI
instance type
subnet
security groups
instance name
ports
```

should be configurable through variables.

This makes the same module reusable across different environments and projects.

---

## 4. Define Useful Outputs

Modules should expose important information that callers may need.

For example:

```text
instance_id
public_ip
private_ip
sg_id
```

This allows the root module and other modules to consume resources cleanly.

---

## 5. Document Custom Modules

Every reusable custom module should have a `README.md` explaining:

- Purpose
- Inputs
- Outputs
- Usage
- Examples
- Requirements

Good documentation makes modules easier for other engineers to understand and reuse.

---

# Commands Practiced

During the assignment I used:

```bash
terraform fmt
terraform init
terraform init -upgrade
terraform validate
terraform plan
terraform apply
terraform output
terraform state list
terraform destroy
```

I also used AWS CLI to verify the EC2 instances:

```bash
aws ec2 describe-instances
```

For example:

```bash
aws ec2 describe-instances \
  --region ap-south-1 \
  --instance-ids i-038cbccd37b11f15f i-0c06bac9aae041284 \
  --query "Reservations[].Instances[].[InstanceId,State.Name,SubnetId,PublicIpAddress,PrivateIpAddress]" \
  --output table
```

---

# Final Cleanup

After completing the practical work and verification, I destroyed the infrastructure using:

```bash
terraform destroy
```

This was done to avoid leaving unnecessary AWS resources running and generating costs.

---

# Key Learnings

### Before Modules

```text
Large main.tf
     ↓
Repeated resources
     ↓
Harder maintenance
     ↓
Difficult reuse
```

### After Modules

```text
Reusable Modules
       ↓
Variables + Outputs
       ↓
Multiple Module Calls
       ↓
Cleaner Infrastructure
       ↓
Easier Maintenance
```

The biggest takeaway is:

> **Terraform modules allow infrastructure code to be written once and reused many times with different inputs.**

I also learned that modules can be:

- Built locally
- Reused multiple times
- Connected through outputs
- Downloaded from the Terraform Registry
- Version-pinned
- Tracked in Terraform state

---

# Verification

The final infrastructure was successfully verified during the practical.

The custom EC2 module was reused to create:

```text
terraweek-web
terraweek-api
```

Both instances used the same Security Group module output and were created from the same EC2 module.

The VPC was successfully migrated from hand-written Terraform resources to the public Terraform Registry module.

Terraform state confirmed the module structure through:

```text
module.vpc.*
module.web_sg.*
module.web_server.*
module.api_server.*
```

---

# Screenshots
![alt text](<Screenshot (827).png>) ![alt text](<Screenshot (829).png>) ![alt text](<Screenshot (830).png>) ![alt text](<Screenshot (831).png>) ![alt text](<Screenshot (805).png>) ![alt text](<Screenshot (807).png>) ![alt text](<Screenshot (808).png>) ![alt text](<Screenshot (809).png>) ![alt text](<Screenshot (810).png>) ![alt text](<Screenshot (811).png>) ![alt text](<Screenshot (812).png>) ![alt text](<Screenshot (813).png>) ![alt text](<Screenshot (814).png>) ![alt text](<Screenshot (815).png>) ![alt text](<Screenshot (816).png>) ![alt text](<Screenshot (817).png>) ![alt text](<Screenshot (820).png>) ![alt text](<Screenshot (822).png>) ![alt text](<Screenshot (823).png>) ![alt text](<Screenshot (826).png>)
---

# Conclusion

Day 65 helped me understand how Terraform modules are used to build **reusable and scalable Infrastructure as Code**.

I built custom EC2 and Security Group modules, reused the EC2 module multiple times, used dynamic blocks for Security Group rules, and then replaced my hand-written VPC configuration with a public Terraform Registry module.

The main lesson from today:

> **Write infrastructure once, parameterize it with variables, expose useful outputs, and reuse it through modules.**

---

## Day 65 Completed 🚀

**#90DaysOfDevOps #TerraWeek #DevOpsKaJosh #TrainWithShubham**