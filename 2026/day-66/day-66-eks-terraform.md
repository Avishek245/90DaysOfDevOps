# Day 66 — Provision an EKS Cluster with Terraform Modules

## Overview

Today I provisioned a complete **Amazon EKS cluster using Terraform Registry modules** instead of creating the Kubernetes cluster manually.

The infrastructure was created using Terraform modules for:

* AWS VPC
* Public and private subnets
* Internet Gateway
* NAT Gateway
* EKS Cluster
* EKS Managed Node Group
* IAM roles and policies
* Security groups
* KMS encryption
* EKS access entries

After provisioning the cluster, I connected `kubectl`, verified the worker nodes, deployed an Nginx workload, exposed it using an AWS LoadBalancer, accessed the Nginx welcome page, and finally destroyed the infrastructure cleanly.

---

## Objectives

The main objectives of this assignment were:

* Provision an AWS EKS cluster using Terraform.
* Use Terraform Registry modules instead of manually creating every resource.
* Create a highly available VPC with public and private subnets.
* Create an EKS managed node group.
* Connect `kubectl` to the Terraform-provisioned cluster.
* Deploy an Nginx application.
* Expose Nginx using an AWS LoadBalancer.
* Verify the application through the LoadBalancer.
* Destroy all resources cleanly after the exercise.

---

# 1. Project Structure

The project was created with the following structure:

```text
terraform-eks/
├── .terraform/
├── .terraform.lock.hcl
├── providers.tf
├── vpc.tf
├── eks.tf
├── variables.tf
├── outputs.tf
├── terraform.tfvars
└── k8s/
    └── nginx-deployment.yaml
```

### File Purpose

| File                        | Purpose                                   |
| --------------------------- | ----------------------------------------- |
| `providers.tf`              | Terraform providers and AWS configuration |
| `vpc.tf`                    | VPC Registry module configuration         |
| `eks.tf`                    | EKS Registry module configuration         |
| `variables.tf`              | Input variables                           |
| `outputs.tf`                | EKS cluster outputs                       |
| `terraform.tfvars`          | Environment-specific variable values      |
| `k8s/nginx-deployment.yaml` | Nginx Deployment and LoadBalancer Service |

---

# 2. Terraform Providers

The AWS provider was pinned to the `5.x` version range and the Kubernetes provider was added for Kubernetes-related operations.

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }

    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.region
}
```

The configuration was initialized successfully using:

```bash
terraform init
```

Terraform validation completed successfully:

```bash
terraform validate
```

Result:

```text
Success! The configuration is valid.
```

---

# 3. Input Variables

The following variables were defined:

```hcl
variable "region" {
  description = "AWS region"
  type        = string
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "terraweek-eks"
}

variable "cluster_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.31"
}

variable "node_instance_type" {
  description = "EC2 instance type for EKS nodes"
  type        = string
  default     = "t3.medium"
}

variable "node_desired_count" {
  description = "Desired number of EKS worker nodes"
  type        = number
  default     = 2
}

variable "vpc_cidr" {
  description = "CIDR block for the EKS VPC"
  type        = string
  default     = "10.0.0.0/16"
}
```

The region was configured in `terraform.tfvars`:

```hcl
region = "us-east-1"
```

---

# 4. VPC Using Terraform Registry Module

The VPC was created using:

```text
terraform-aws-modules/vpc/aws
```

Configuration:

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.cluster_name}-vpc"
  cidr = var.vpc_cidr

  azs = [
    "${var.region}a",
    "${var.region}b"
  ]

  public_subnets = [
    "10.0.1.0/24",
    "10.0.2.0/24"
  ]

  private_subnets = [
    "10.0.101.0/24",
    "10.0.102.0/24"
  ]

  enable_nat_gateway = true
  single_nat_gateway = true

  enable_dns_hostnames = true

  public_subnet_tags = {
    "kubernetes.io/role/elb" = 1
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = 1
  }
}
```

## VPC Design

```text
VPC: 10.0.0.0/16
│
├── us-east-1a
│   ├── Public Subnet  → 10.0.1.0/24
│   └── Private Subnet → 10.0.101.0/24
│
└── us-east-1b
    ├── Public Subnet  → 10.0.2.0/24
    └── Private Subnet → 10.0.102.0/24
```

A single NAT Gateway was enabled to reduce costs during the exercise.

The initial VPC-only Terraform plan showed:

```text
Plan: 19 to add, 0 to change, 0 to destroy.
```

---

# 5. Why Public and Private Subnets?

EKS requires a suitable network architecture for the cluster and its workloads.

### Public Subnets

The public subnets can be used for internet-facing resources such as AWS LoadBalancers.

They were tagged with:

```hcl
"kubernetes.io/role/elb" = 1
```

### Private Subnets

The EKS worker nodes were placed in private subnets.

The private subnets were tagged with:

```hcl
"kubernetes.io/role/internal-elb" = 1
```

The private subnets can access the internet through the NAT Gateway without directly exposing worker nodes to the public internet.

---

# 6. EKS Cluster Using Terraform Registry Module

The EKS cluster was created using:

```text
terraform-aws-modules/eks/aws
```

Configuration:

```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = var.cluster_name
  cluster_version = var.cluster_version

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  cluster_endpoint_public_access = true

  enable_cluster_creator_admin_permissions = true

  eks_managed_node_groups = {
    terraweek_nodes = {
      ami_type       = "AL2_x86_64"
      instance_types = [var.node_instance_type]

      min_size     = 1
      max_size     = 3
      desired_size = var.node_desired_count
    }
  }

  tags = {
    Environment = "dev"
    Project     = "TerraWeek"
    ManagedBy   = "Terraform"
  }
}
```

---

# 7. Terraform Plan

After adding the EKS module, Terraform planned:

```text
Plan: 55 to add, 0 to change, 0 to destroy.
```

The plan included resources such as:

* EKS Cluster
* EKS Managed Node Group
* IAM Roles
* IAM Policy Attachments
* Security Groups
* Launch Template
* KMS Key
* KMS Alias
* VPC resources
* NAT Gateway
* Subnets
* Route Tables
* Internet Gateway

---

# 8. Terraform Apply

The infrastructure was provisioned using:

```bash
terraform apply
```

Terraform successfully completed the initial deployment:

```text
Apply complete! Resources: 55 added, 0 changed, 0 destroyed.
```

The EKS outputs included:

```text
cluster_name   = "terraweek-eks"
cluster_region = "us-east-1"
cluster_endpoint = "https://....eks.amazonaws.com"
```

---

# 9. EKS Access Configuration

After the initial cluster creation, AWS authentication through the AWS CLI was working, but `kubectl` initially returned:

```text
You must be logged in to the server
```

The AWS identity was verified using:

```bash
aws sts get-caller-identity
```

The EKS authentication token was also successfully generated:

```bash
aws eks get-token --cluster-name terraweek-eks --region us-east-1
```

The issue was that the IAM user did not yet have Kubernetes administrative access to the EKS cluster.

To fix this through Terraform, the following configuration was added:

```hcl
enable_cluster_creator_admin_permissions = true
```

Terraform then planned:

```text
Plan: 2 to add, 0 to change, 0 to destroy.
```

The access entry and policy association were successfully created:

```text
Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
```

This brought the total Terraform-created resources during the exercise to:

```text
57 resources
```

---

# 10. Connect kubectl

The kubeconfig was updated using:

```bash
aws eks update-kubeconfig \
  --name terraweek-eks \
  --region us-east-1
```

The Kubernetes context was:

```text
arn:aws:eks:us-east-1:123877604025:cluster/terraweek-eks
```

---

# 11. Verify EKS Nodes

The cluster was verified using:

```bash
kubectl get nodes
```

The result showed **2 worker nodes in Ready state**.

Both nodes were running Kubernetes version:

```text
v1.31.13-eks-ecaa3a6
```

This confirmed that the EKS managed node group was successfully provisioned.

---

# 12. Verify Kubernetes System Pods

The cluster was checked using:

```bash
kubectl get pods -A
```

Important Kubernetes system components were running successfully, including:

* `aws-node`
* `coredns`
* `kube-proxy`

The cluster was also verified with:

```bash
kubectl cluster-info
```

The Kubernetes control plane and CoreDNS were successfully running.

---

# 13. Deploy Nginx

A Kubernetes manifest was created:

```text
k8s/nginx-deployment.yaml
```

The deployment used 3 replicas:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-terraweek
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx:latest
          ports:
            - containerPort: 80
```

A LoadBalancer service was also created:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
    - port: 80
      targetPort: 80
```

The workload was deployed using:

```bash
kubectl apply -f k8s/nginx-deployment.yaml
```

---

# 14. Verify Nginx Deployment

The deployment was checked using:

```bash
kubectl get deployments
```

The result showed:

```text
nginx-terraweek    3/3    3    3
```

This confirmed that all three Nginx replicas were available.

The pods were also verified using:

```bash
kubectl get pods
```

All three Nginx pods were in:

```text
Running
```

state.

---

# 15. AWS LoadBalancer

The service was checked using:

```bash
kubectl get svc nginx-service
```

The service received an AWS LoadBalancer hostname.

The Nginx application was accessed through the LoadBalancer URL and the **Nginx Welcome Page** was successfully displayed.

This confirmed the complete flow:

```text
Internet
   ↓
AWS LoadBalancer
   ↓
Kubernetes Service
   ↓
Nginx Deployment
   ↓
3 Nginx Pods
   ↓
EKS Worker Nodes
```

---

# 16. Cleanup

Before destroying the infrastructure, the Kubernetes resources were removed:

```bash
kubectl delete -f k8s/nginx-deployment.yaml
```

The Nginx deployment and service were successfully deleted.

Verification:

```bash
kubectl get svc
```

Only the default Kubernetes service remained.

The AWS LoadBalancer was also verified using:

```bash
aws elb describe-load-balancers --region us-east-1
```

Result:

```json
{
    "LoadBalancerDescriptions": []
}
```

This confirmed that the Nginx LoadBalancer had been completely removed before destroying the Terraform infrastructure.

---

# 17. Terraform Destroy

After removing the Kubernetes LoadBalancer, the complete AWS infrastructure was destroyed using:

```bash
terraform destroy
```

The EKS cluster, managed node group, VPC, NAT Gateway, IAM resources, security groups, and other Terraform-managed resources were removed.

The purpose of destroying everything was to avoid unnecessary AWS charges, especially from resources such as:

* EKS
* NAT Gateway
* EC2 worker nodes
* Elastic IP
* LoadBalancer

---

# 18. Key Commands Used

```bash
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
terraform destroy
```

AWS:

```bash
aws sts get-caller-identity

aws eks update-kubeconfig \
  --name terraweek-eks \
  --region us-east-1

aws eks get-token \
  --cluster-name terraweek-eks \
  --region us-east-1
```

Kubernetes:

```bash
kubectl get nodes
kubectl get pods -A
kubectl cluster-info

kubectl apply -f k8s/nginx-deployment.yaml

kubectl get deployments
kubectl get pods
kubectl get svc nginx-service

kubectl delete -f k8s/nginx-deployment.yaml
```

---

# 19. Screenshots

## Terraform Apply Completed

> Add screenshot here showing:

```text
Apply complete! Resources: 55 added, 0 changed, 0 destroyed.
```

---

## EKS Nodes

> Add screenshot here showing:

```text
2 nodes in Ready state
```

---

## Kubernetes System Pods

> Add screenshot here showing:

```text
aws-node
coredns
kube-proxy
```

running successfully.

---

## Nginx Deployment

> Add screenshot here showing:

```text
nginx-terraweek    3/3    3    3
```

---

## Nginx LoadBalancer

> Add screenshot here showing:

```text
nginx-service    LoadBalancer
```

with an AWS external hostname.

---

## Nginx Welcome Page

> Add screenshot here showing the Nginx Welcome Page accessed through the AWS LoadBalancer.

---

## Terraform Destroy

> Add screenshot here showing the final `terraform destroy` completion.

---

# 20. Terraform Resources Created

The initial Terraform deployment created:

```text
55 resources
```

After fixing EKS cluster access, Terraform created 2 additional resources:

```text
EKS Access Entry
EKS Access Policy Association
```

Therefore, the total number of resources created during the complete exercise was:

```text
57 resources
```

---

# 21. What I Learned

### Terraform Modules

Terraform Registry modules make it possible to provision complex infrastructure without manually defining every AWS resource.

Instead of creating individual resources for the VPC and EKS cluster, I used:

```text
terraform-aws-modules/vpc/aws
terraform-aws-modules/eks/aws
```

This made the infrastructure configuration more reusable and maintainable.

### EKS Networking

I learned why EKS commonly uses public and private subnets:

* Public subnets can support internet-facing load balancers.
* Private subnets can host worker nodes.
* NAT Gateway provides outbound internet connectivity for private resources.

### Managed Node Groups

Instead of manually creating EC2 instances, the EKS module created a managed node group.

The configuration used:

```text
Instance Type: t3.medium
Desired Nodes: 2
Minimum Nodes: 1
Maximum Nodes: 3
```

### EKS Authentication

I also learned that successfully generating an AWS authentication token does not automatically mean the IAM identity has Kubernetes permissions.

The EKS access entry and `AmazonEKSClusterAdminPolicy` association were required to allow my IAM user to administer the cluster through `kubectl`.

### Kubernetes Workloads

After provisioning the infrastructure, I used normal Kubernetes commands to deploy an Nginx workload.

This demonstrated how Terraform can provision the infrastructure while Kubernetes manages workloads running on top of that infrastructure.

---

# 22. Terraform EKS vs Kind/Minikube

During the Kubernetes learning week, I worked with local Kubernetes clusters such as Kind.

The major difference is the infrastructure environment.

### Kind/Minikube

```text
Local Machine
     ↓
Kind / Minikube
     ↓
Kubernetes Cluster
     ↓
Containers
```

These tools are excellent for:

* Learning Kubernetes
* Testing manifests
* Practicing kubectl
* Local development

They are lightweight and run on a local computer.

### Terraform + EKS

```text
AWS
 ↓
VPC
 ↓
EKS Control Plane
 ↓
Managed Node Group
 ↓
Kubernetes Workloads
 ↓
AWS LoadBalancer
```

EKS provides a real cloud-based Kubernetes environment with AWS networking, IAM, managed worker nodes, and AWS integrations.

Terraform makes the entire infrastructure repeatable.

### Main Difference

With Kind/Minikube, I was mainly learning how Kubernetes works.

With Terraform + EKS, I learned how **cloud infrastructure and Kubernetes can be provisioned together using Infrastructure as Code**.

---

# 23. Key Takeaways

* Terraform Registry modules simplify complex infrastructure provisioning.
* EKS requires proper VPC and subnet design.
* Private subnets are suitable for EKS worker nodes.
* Public subnets can be used for internet-facing load balancers.
* NAT Gateway provides outbound internet access from private subnets.
* EKS Managed Node Groups reduce the need to manually manage worker EC2 instances.
* EKS access entries can provide IAM-based Kubernetes access.
* Terraform can provision the infrastructure while Kubernetes manages application workloads.
* Kubernetes LoadBalancer services can integrate with AWS load balancing.
* Infrastructure should be destroyed after temporary exercises to avoid unnecessary cloud costs.
* A complete EKS environment can be provisioned and destroyed using Terraform.

---

# 24. Final Reflection

This exercise was a major step from local Kubernetes practice toward real cloud infrastructure.

Previously, I used Kind/Minikube to create Kubernetes clusters locally. With this task, I provisioned an actual AWS EKS cluster using Terraform modules, created the supporting VPC infrastructure, configured managed worker nodes, connected `kubectl`, deployed Nginx, exposed it through an AWS LoadBalancer, and finally destroyed the entire environment.

The most important lesson was understanding how **Terraform and Kubernetes work together**:

```text
Terraform
   ↓
Cloud Infrastructure
   ↓
AWS EKS
   ↓
Kubernetes
   ↓
Application Workloads
```

This is much closer to how Kubernetes infrastructure is managed in real DevOps and cloud environments.

---

# Day 66 Completed 🚀

# Screenshot
![alt text](<Screenshot (840).png>) ![alt text](<Screenshot (842).png>) ![alt text](<Screenshot (843).png>) ![alt text](<Screenshot (844).png>) ![alt text](<Screenshot (845).png>) ![alt text](<Screenshot (846).png>) ![alt text](<Screenshot (847).png>) ![alt text](<Screenshot (832).png>) ![alt text](<Screenshot (833).png>) ![alt text](<Screenshot (834).png>) ![alt text](<Screenshot (835).png>) ![alt text](<Screenshot (836).png>) ![alt text](<Screenshot (837).png>) ![alt text](<Screenshot (838).png>) ![alt text](<Screenshot (839).png>)

**AWS EKS Cluster → Terraform Modules → Managed Nodes → kubectl → Nginx → LoadBalancer → Clean Destroy**

Infrastructure was provisioned automatically, the workload was deployed successfully, the Nginx application was accessed through AWS, and the environment was cleaned up after the exercise.

**#90DaysOfDevOps #TerraWeek #DevOpsKaJosh #TrainWithShubham**
