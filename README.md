# DevSecOps
# DevSecOps Platform — End-to-End Project

> **Role:** Solo engineer | **Stack:** Python · Docker · Terraform · EKS · Helm · Ansible · GitHub Actions · AWS

---

## Architecture

```
Developer (Git Push)
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│                  GitHub Actions CI/CD                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │
│  │Lint+Test │→ │SAST Scan │→ │Build+Push│→ │Deploy  │  │
│  │ pytest   │  │Bandit    │  │Docker→ECR│  │EKS via │  │
│  │          │  │Checkov   │  │Trivy scan│  │Helm    │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘  │
└─────────────────────────────────────────────────────────┘
        │                               │
        ▼                               ▼
┌──────────────┐              ┌─────────────────────────┐
│  AWS ECR     │              │     AWS EKS Cluster      │
│  (Docker     │              │  ┌───────────────────┐   │
│   Registry)  │              │  │  devsecops-demo   │   │
└──────────────┘              │  │  Pod (FastAPI)    │   │
                              │  │  /health /metrics │   │
┌──────────────┐              │  └───────────────────┘   │
│  Terraform   │──provisions──│  ┌───────────────────┐   │
│  S3 Backend  │              │  │  Prometheus Stack │   │
│  DynamoDB    │              │  │  + Grafana        │   │
└──────────────┘              │  └───────────────────┘   │
                              └─────────────────────────┘
┌──────────────┐                          │
│  AWS Secrets │──────IRSA────────────────┘
│  Manager     │
└──────────────┘
┌──────────────┐
│  Ansible     │──── PostgreSQL provisioning (local/VM)
└──────────────┘
```

---

## Decisions Made

| Decision | Rationale |
|---|---|
| **FastAPI over Flask** | Built-in OpenAPI docs, async support, and native Pydantic validation — better for modern microservices |
| **Multi-stage Docker build** | Keeps final image small and free of build tools; reduces attack surface |
| **EKS over ECS** | Kubernetes is portable across clouds; ECS is AWS-only. Better long-term investment |
| **Terraform modules (VPC, EKS)** | Community-maintained modules reduce boilerplate and encode best practices |
| **Helm over raw kubectl** | Templating enables the same chart to deploy across dev/staging/prod with different values |
| **S3 + DynamoDB state backend** | Remote state with locking prevents concurrent apply conflicts in a team |
| **IRSA over node-level IAM** | Pod-level AWS permissions are more granular and follow least-privilege principle |
| **Bandit + Checkov over single tool** | Bandit targets Python code; Checkov targets IaC — two different threat surfaces |

---

## Security Controls at Each Stage

| Stage | Control | Tool |
|---|---|---|
| **Code** | Static analysis for insecure patterns | Bandit |
| **IaC** | Policy-as-code scan on Terraform files | Checkov |
| **Container Build** | Vulnerability scan of image layers | Trivy |
| **Container Runtime** | Non-root user, read-only filesystem, dropped Linux capabilities | Docker + K8s security context |
| **Network** | Restrict pod ingress/egress to required ports only | Kubernetes NetworkPolicy |
| **Secrets** | No secrets in code or environment files — sourced from vault | AWS Secrets Manager |
| **Access** | Pod assumes IAM role via service account — no long-lived keys on nodes | IRSA |
| **Deployment** | Staging and prod require peer review approval before apply | GitHub Environment gates |
| **Infrastructure** | State encrypted at rest, access logged | S3 SSE + CloudTrail |

---

## Trade-offs

**CSI Driver vs Manual Secret Sync** — The AWS Secrets Store CSI driver provides automatic secret rotation but requires careful OIDC and tokenRequests configuration. For this project I synced secrets manually via CLI to unblock delivery. In production I would fully implement the CSI driver with rotation enabled.

**Single Node Group** — Using one `t3.medium` node group keeps costs low for a demo environment. Production would use separate node groups for system and application workloads with auto-scaling policies.

**No Service Mesh** — Skipped Istio/Linkerd to reduce complexity. A service mesh would add mTLS between pods automatically, which is valuable in a multi-service environment but adds significant operational overhead for a single service.

**Terraform Workspaces vs Separate State Files** — Used workspaces for dev/staging/prod separation. Some teams prefer completely separate state files per environment for stronger blast radius isolation. Workspaces are simpler to manage for a single operator.

**kubectl deploy in CI vs GitOps** — The pipeline uses `kubectl set image` for deployments. In a production team environment I would replace this with ArgoCD for a fully declarative, auditable GitOps model where the cluster state always matches Git.

---

## Outcome

A fully automated DevSecOps pipeline where every `git push` to `main` triggers testing, security scanning, image building, and deployment to Kubernetes — with zero manual steps and no secrets ever touching the filesystem. Promotion to production requires a peer review approval gate. The entire infrastructure is defined as code and can be torn down and recreated in under 25 minutes.
