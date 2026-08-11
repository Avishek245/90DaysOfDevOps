# 🚀 Day 63 — Terraform State Management

## 📌 Overview
Learned how Terraform tracks, stores, imports, moves, and reconciles infrastructure state.

**Topics:** State inspection, Remote state (S3), Versioning, Locking, Migration, Import, Move, Remove, Drift detection & reconciliation.

---

## 🎯 1. Inspect State
```bash
terraform state list
terraform state show aws_instance.main
terraform state show aws_vpc.main
```
Shows tracked resources and their attributes (IDs, tags, config, etc.). State also has a `serial` (version number).

---

## ☁️ 2. Remote State (S3)
- **Bucket:** `terraweek-state-avishek-2026`
- **Path:** `dev/terraform.tfstate`

**Versioning check:**
```bash
aws s3api get-bucket-versioning --bucket terraweek-state-avishek-2026
# "Status": "Enabled"
```

**Locking check:**
```bash
aws dynamodb describe-table --table-name terraweek-state-lock --region ap-south-1
# Status: ACTIVE, Key: LockID
```
⚠️ `dynamodb_table` is deprecated → use `use_lockfile = true`.

---

## 🔄 3. Migrate Local → S3
```bash
terraform fmt
terraform init -migrate-state   # confirm with "yes"
terraform plan                  # → No changes.
```

---

## 📥 4. Import Existing Resource
```bash
aws s3api create-bucket --bucket terraweek-import-test-avishek-2026 --region us-east-1
terraform import aws_s3_bucket.imported terraweek-import-test-avishek-2026
# → Import successful!
```

---

## 🔀 5. Move & Remove State
```bash
terraform state mv aws_s3_bucket.imported aws_s3_bucket.logs_bucket
# → Successfully moved 1 object(s).

terraform state rm aws_s3_bucket.logs_bucket
# → Successfully removed 1 resource instance(s).
```
📝 `state rm` untracks the resource — doesn't delete it. `terraform destroy` actually deletes it.

---

## 🧪 6. Drift Detection & Fix
Changed EC2 `Name` tag manually outside Terraform (`control` vs expected `TerraWeek-Server`).

```bash
terraform plan
# "Name" = "control" -> "TerraWeek-Server"
# Plan: 0 to add, 1 to change, 0 to destroy.

terraform apply   # confirm "yes"
# Apply complete! Resources: 0 added, 1 changed, 0 destroyed.

terraform plan
# → No changes.
```

---

## 🧠 Key Learnings
| Concept | Takeaway |
|---|---|
| State | Links Terraform config to real infra |
| Remote State (S3) | Centralized, persistent storage |
| Versioning | Recover previous state files |
| Locking | Prevents concurrent state changes |
| Import | `terraform import <addr> <id>` |
| Move | `terraform state mv <src> <dest>` |
| Remove | `terraform state rm <addr>` (no deletion) |
| Drift | `terraform plan` detects out-of-band changes |
| Reconciliation | `terraform apply` restores desired state |

---

## 🏆 Final Result
✅ State inspected → Remote backend set up → Versioning & locking verified → Migrated → Imported → Moved/Removed → Drift detected & fixed → Final `terraform plan` = **No changes**.

SCREENSHOT
![alt text](<Screenshot (785).png>) ![alt text](<Screenshot (786).png>) ![alt text](<Screenshot (787).png>) ![alt text](<Screenshot (788).png>) ![alt text](<Screenshot (789).png>) ![alt text](<Screenshot (790).png>) ![alt text](<Screenshot (791).png>) ![alt text](<Screenshot (792).png>) ![alt text](<Screenshot (793).png>) ![alt text](<Screenshot (794).png>) ![alt text](<Screenshot (795).png>) ![alt text](<Screenshot (796).png>) ![alt text](<Screenshot (797).png>) ![alt text](<Screenshot (798).png>) ![alt text](<Screenshot (799).png>) ![alt text](<Screenshot (800).png>) ![alt text](<Screenshot (801).png>) ![alt text](<Screenshot (802).png>) ![alt text](<Screenshot (803).png>) ![alt text](<Screenshot (776).png>) ![alt text](<Screenshot (777).png>) ![alt text](<Screenshot (778).png>) ![alt text](<Screenshot (779).png>) ![alt text](<Screenshot (780).png>) ![alt text](<Screenshot (781).png>) ![alt text](<Screenshot (782).png>) ![alt text](<Screenshot (783).png>) ![alt text](<Screenshot (784).png>)