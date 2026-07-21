# 🚀 Day 60 – Kubernetes Capstone: Deploy WordPress + MySQL on Kubernetes

**Date:** 22 July 2026

## 📌 Objective

The objective of this capstone project was to combine all the Kubernetes concepts learned over the last ten days into one real-world deployment by hosting a **WordPress application backed by a MySQL database** on a Kubernetes cluster.

This project covered storage, networking, configuration management, security, health monitoring, scaling, and application deployment using Kubernetes best practices.

---

# 🏗️ Architecture

```
                    +-----------------------+
                    |      Browser          |
                    | localhost:8080        |
                    +-----------+-----------+
                                |
                        kubectl port-forward
                                |
                     +----------v----------+
                     |  WordPress Service  |
                     |     ClusterIP       |
                     +----------+----------+
                                |
                    +-----------+------------+
                    |                        |
          +---------v---------+    +---------v---------+
          | WordPress Pod 1   |    | WordPress Pod 2   |
          | Deployment        |    | Deployment        |
          +---------+---------+    +---------+---------+
                    |                        |
                    +-----------+------------+
                                |
                    ConfigMap + Secret
                                |
                     +----------v-----------+
                     |  MySQL Headless SVC  |
                     +----------+-----------+
                                |
                     +----------v-----------+
                     |   MySQL StatefulSet  |
                     |      mysql-0         |
                     +----------+-----------+
                                |
                         Persistent Volume
                       (VolumeClaimTemplate)
```

---

# 📚 Kubernetes Concepts Used

| Concept | Purpose |
|----------|---------|
| Namespace | Isolated the application resources |
| Secret | Stored MySQL credentials securely |
| ConfigMap | Stored WordPress configuration |
| StatefulSet | Deployed MySQL with stable identity |
| Headless Service | Enabled StatefulSet DNS |
| Deployment | Managed WordPress replicas |
| ClusterIP Service | Exposed WordPress internally |
| Persistent Volume Claim | Persisted MySQL data |
| Resource Requests & Limits | Controlled CPU and Memory usage |
| Liveness Probe | Restarted unhealthy containers |
| Readiness Probe | Allowed traffic only when ready |
| Port Forward | Accessed the application locally |
| HPA | Practiced Horizontal Pod Autoscaler |
| Helm | Compared manual deployment with Helm charts |

---

# 📁 Project Structure

```
day-60/
│
├── mysql-secret.yaml
├── mysql-headless-service.yaml
├── mysql-statefulset.yaml
├── wordpress-configmap.yaml
├── wordpress-deployment.yaml
├── wordpress-service.yaml
├── wordpress-hpa.yaml
└── day-60-capstone.md
```

---

# ✅ Task 1 – Create Namespace

Created a dedicated namespace for the project.

```bash
kubectl create namespace capstone
```

Set it as the default namespace.

```bash
kubectl config set-context --current --namespace=capstone
```

### Verification

```bash
kubectl get ns
```

**Result**

- Namespace `capstone` created successfully.

---

# ✅ Task 2 – Deploy MySQL

## Created Secret

Created a Kubernetes Secret using `stringData`.

Stored:

- MYSQL_ROOT_PASSWORD
- MYSQL_DATABASE
- MYSQL_USER
- MYSQL_PASSWORD

Verified Secret.

```bash
kubectl get secret
```

---

## Created Headless Service

Created a Headless Service.

```yaml
clusterIP: None
```

Purpose:

- Stable DNS
- Required for StatefulSet

Verified.

```bash
kubectl get svc
```

---

## Created StatefulSet

Used:

- mysql:8.0
- envFrom
- VolumeClaimTemplate
- Resource Requests
- Resource Limits

Storage

```
1Gi
```

Mounted at

```
/var/lib/mysql
```

Verified.

```bash
kubectl get statefulset
```

---

## Verified Database

Executed

```bash
kubectl exec -it mysql-0 -- mysql -u wordpress -p
```

Ran

```sql
SHOW DATABASES;
```

Successfully confirmed the **wordpress** database existed.

---

# ✅ Task 3 – Deploy WordPress

Created ConfigMap.

Stored

```
WORDPRESS_DB_HOST
WORDPRESS_DB_NAME
```

Verified.

```bash
kubectl get configmap
```

---

Created Deployment

Features:

- 2 Replicas
- wordpress:latest
- envFrom ConfigMap
- secretKeyRef
- Resource Requests
- Resource Limits
- Readiness Probe
- Liveness Probe

Verified

```bash
kubectl get deploy
```

Output

```
2/2 Ready
```

---

# ✅ Task 4 – Expose WordPress

Created ClusterIP Service.

Accessed application using

```bash
kubectl port-forward svc/wordpress 8080:80
```

Opened

```
http://localhost:8080
```

Successfully reached the WordPress installation page.

Completed the installation wizard by providing:

- Site Title
- Username
- Password
- Email

Successfully logged into the WordPress Dashboard.

---

# ⚠️ Issue Faced During Deployment

Initially, the WordPress pods entered a **CrashLoopBackOff** state.

## Root Cause

The default health probes were too aggressive.

The application required more startup time before becoming healthy.

Additionally, port **8080** was already occupied by a Jenkins instance running inside WSL, causing the browser to open Jenkins instead of WordPress.

## Troubleshooting Performed

- Checked pod logs

```bash
kubectl logs <pod-name>
```

- Described pod

```bash
kubectl describe pod <pod-name>
```

- Verified MySQL connectivity

- Verified Secrets

- Verified ConfigMap

- Verified Deployment

- Increased

```
initialDelaySeconds

timeoutSeconds

failureThreshold
```

for the probes.

- Investigated port 8080 using

```bash
netstat -ano
```

- Found `wslrelay.exe` forwarding traffic.

- Identified Jenkins Java process inside WSL.

- Stopped Jenkins service.

- Restarted port forwarding.

After fixing the issues, WordPress became healthy and accessible.

---

# ✅ Task 5 – Self-Healing Test

Deleted a WordPress pod.

```bash
kubectl delete pod <wordpress-pod>
```

Result

Deployment automatically recreated the Pod.

Website remained available.

---

Deleted MySQL Pod

```bash
kubectl delete pod mysql-0
```

Result

StatefulSet recreated the Pod automatically.

Persistent Volume retained database data.

WordPress data remained intact after recovery.

---

# ✅ Task 6 – Horizontal Pod Autoscaler

Created an HPA.

Configuration

- CPU Target : 50%
- Minimum Replicas : 2
- Maximum Replicas : 10

Verified

```bash
kubectl get hpa
```

Successfully observed HPA configuration.

---

# ✅ Task 7 – Helm Comparison

Compared manual deployment with Helm.

Learned that Helm:

- Creates multiple resources automatically
- Simplifies deployments
- Reduces YAML management

Manual deployment provided:

- Better understanding
- Greater control
- Fine-grained customization

---

# ✅ Resource Verification

Verified every Kubernetes object.

```bash
kubectl get all
```

Verified

```bash
kubectl get pvc
```

Verified

```bash
kubectl get svc
```

Verified

```bash
kubectl get configmap
```

Verified

```bash
kubectl get secret
```

Verified

```bash
kubectl get statefulset
```

Verified

```bash
kubectl describe pod
```

Everything was functioning correctly.

---

# 🧪 Results

Successfully deployed

- WordPress
- MySQL
- Persistent Storage
- Networking
- Secrets
- ConfigMaps
- Health Checks
- Resource Limits

Verified

- Deployment
- StatefulSet
- Services
- ConfigMaps
- Secrets
- PVC
- Pods

Successfully accessed the WordPress dashboard through Kubernetes.

---

# 🧹 Cleanup

Deleted the complete application.

```bash
kubectl delete namespace capstone
```

Reset namespace.

```bash
kubectl config set-context --current --namespace=default
```

Verification

```bash
kubectl get ns
```

Confirmed that the **capstone** namespace and all associated resources were removed successfully.

---

# 📷 Screenshots

![alt text](<Screenshot (687).png>) ![alt text](<Screenshot (688).png>) ![alt text](<Screenshot (689).png>) ![alt text](<Screenshot (690).png>) ![alt text](<Screenshot (691).png>) ![alt text](<Screenshot (692).png>) ![alt text](<Screenshot (693).png>) ![alt text](<Screenshot (694).png>) ![alt text](<Screenshot (697).png>) ![alt text](<Screenshot (708).png>) ![alt text](<Screenshot (709).png>) ![alt text](<Screenshot (710).png>) ![alt text](<Screenshot (711).png>) ![alt text](<Screenshot (712).png>) ![alt text](<Screenshot (713).png>) ![alt text](<Screenshot (714).png>)

---

# 🎯 Learning Outcomes

Through this capstone project, I gained practical experience in deploying and managing a complete application stack on Kubernetes.

Key takeaways:

- Understanding the difference between Deployments and StatefulSets.
- Managing sensitive configuration using Secrets.
- Using ConfigMaps for application configuration.
- Implementing persistent storage with PVCs.
- Configuring Headless Services for StatefulSets.
- Applying CPU and memory resource management.
- Using Readiness and Liveness probes effectively.
- Troubleshooting CrashLoopBackOff issues.
- Investigating networking and port conflicts.
- Validating Kubernetes resources using kubectl.
- Understanding the benefits of Helm over manual YAML deployment.
- Cleaning up Kubernetes resources efficiently.

---

# 🎉 Conclusion

Day 60 marked the completion of the Kubernetes learning journey by bringing together all the concepts learned over the previous ten days into one production-style deployment.

Deploying WordPress with a MySQL backend demonstrated how Kubernetes manages application lifecycle, storage, networking, configuration, health monitoring, and scalability in a real-world scenario.

This capstone significantly strengthened my understanding of Kubernetes fundamentals and prepared me for more advanced topics such as Ingress Controllers, GitOps, CI/CD pipelines, and production-grade Kubernetes deployments.