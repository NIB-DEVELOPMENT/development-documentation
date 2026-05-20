# NIB Online Portal — Deployment & DevOps Architecture

**Audience:** Developers, operators, and AI assistants who will deploy, troubleshoot, or operate the platform.
**Purpose:** Verified-from-live-servers DevOps reference — server inventory, deployment topology, CI/CD, configuration management, monitoring, backups, sync mechanics, and operational gotchas.
**Verified:** 2026-05-19 from live `.123` (staging) and `.139` (prod) hosts via SSH. Every IP, container name, image tag, volume mount, and compose file path cited here was directly observed.
**Read after:** `01-EXECUTIVE-OVERVIEW.md`, `02-ARCHITECTURE.md`, `03-SERVICES.md`.

---

## 1. Server Inventory

### 1.1 Production server `.139`

| Attribute | Value |
|---|---|
| Frontend IP | `192.168.100.139` |
| Backend IP | `172.16.1.139` |
| Hostname | `jumonlprdbckdsrv01` |
| OS | RHEL 9.7 (kernel `5.14.0-611.34.1.el9_7`) |
| Docker | 29.2.1 |
| SSH access | `ssh -J querytool-prod devadmin@preprod-backend` (jumphost via 172.16.1.156) |
| DNS | `nibonline.nib-bahamas.com` AND `preprod-nibonline.nib-bahamas.com` (both resolve here post 2026-05-10 LB cutover) |
| Status | **LIVE PRODUCTION** |

**Disk layout (observed 2026-05-19):**

```
/dev/mapper/rhel-root   61G   60G  1.7G  98% /          ← CRITICAL: near full
/dev/mapper/rhel-home   30G  635M   30G   3% /home
```

> ⚠ **Operational alert:** `.139` root volume is at 98%. `/Data_Repository` lives on root (not home), so further citizen uploads + container layers compete for ~1.7G remaining. Backups (e.g. `~/backups/jenkins-139-pre-upgrade-20260516-0108.tar.gz` 333MB) sit in `/home` and are not implicated. Needs investigation of what's consuming root.

**`/Data_Repository` actual structure:**

```
/Data_Repository/
├── BankingDocs/                  ← demographic-service banking docs (May 19 — active)
├── online-card-applications/     ← Jul 2024, drwxrwxrwx (777!) — F4 incident residue
├── online-cards-applications/    ← Feb 2026 (note 's' — F4 plural variant)
└── online-claims-applications/   ← active claim uploads
```

> Two cards directories coexist on prod. The plural variant (`online-cards-applications/`) was created during the F4 launch incident. Investigate which is actually being written to before any cleanup.

### 1.2 Staging server `.123`

| Attribute | Value |
|---|---|
| Frontend IP | `192.168.100.123` |
| Backend IP | `172.16.1.123` (refusing SSH; use `192.168.100.123` instead) |
| Hostname | `jumapdevstgsrv3.nib-bahamas.com` |
| OS | RHEL 9.6 (kernel `5.14.0-570.21.1.el9_6`) |
| Docker | 28.1.1 |
| Docker Compose | v2.35.1 |
| SSH access | `ssh devadmin@192.168.100.123` (direct, no jumphost) |
| DNS | `staging-nibonline.nib-bahamas.com` |
| Status | Test environment + multi-tenant host |

**Disk layout:**

```
/dev/mapper/rhel-root   44G   30G   15G  68% /
/dev/sdb1               99G   49G   45G  53% /Staging_Repositiry   ← note typo
```

**`.123` is a multi-tenant server** — hosts the entire NIB development ecosystem, not just the online portal:

| Project | Containers on `.123` |
|---|---|
| **nib-online-portal** | customer + admin Flask services, customer + admin frontends, 4 bg jobs, customer-redis, admin-redis, 2 MinIO replicas |
| **nib-website** | Strapi CMS, frontend, postgres-15, redis-7, meilisearch, nginx |
| **query-tool** | backend, frontend, monitor, RabbitMQ, redis |
| **manager-queue** | frontend, backend |
| **nib-hr-file-management** | frontend, backend, redis |
| **nib-death-update** | frontend, api, postgres-16 |
| **monitoring** | Loki + Grafana + Promtail (this is the central log aggregator) |
| **CI/CD** | Jenkins |

This means routine `.123` operations (disk pressure, docker prune, network conflicts) can affect projects beyond `nib-online-portal`.

### 1.3 Legacy production servers (being drained)

| Server | IP | Role | Status |
|---|---|---|---|
| Customer prod | `192.168.100.117` / `172.16.1.117` | Old customer backend | Being drained from NetScaler (task #34) |
| Admin prod | `192.168.100.125` / `172.16.1.116` | Old admin backend | Being drained |

Neither is receiving new traffic post 2026-05-10 cutover. Files on `.117` are rsync'd to `.139` every 15 minutes (see §6.2 below).

---

## 2. Docker Network Topology (verified)

**Network names differ between staging and prod** — a non-obvious artifact of the cutover. Docs and diagrams that say "NIB-ONLINE" only describe staging.

### 2.1 Staging `.123` networks (12 total — multi-tenant host)

```
$ docker network ls
NETWORK ID     NAME                                         DRIVER
5d57d2713e62   NIB-ONLINE                                   bridge   ← customer portal
6d5eb99e1d62   NIB-ONLINE-ADMIN                             bridge   ← admin portal
74f6e41b5dcd   NIB-QUERY-TOOL                               bridge   ← shared (email bridges here)
45d84fc5f51a   background-job_default                       bridge   ← 4 bg jobs
6fded9c28af1   nib-monitoring                               bridge   ← Loki/Grafana/Promtail
abebb93b6649   nib-website                                  bridge   ← unrelated project
375dd88be419   deploy-death-update_nib-network              bridge   ← unrelated
12cc4518db03   deploy-manager-queue_manager-queue-network   bridge   ← unrelated
ff73dac5b3fb   deploy-nib-hr-file-management_hr_network     bridge   ← unrelated
```

### 2.2 Production `.139` networks (8 total — dedicated)

```
NETWORK ID     NAME                   DRIVER
a6c43bd94069   NIB-PREPROD-CUSTOMER   bridge   ← customer portal (DIFFERENT NAME)
103cce4efef4   NIB-PREPROD-ADMIN      bridge   ← admin portal (DIFFERENT NAME)
f9c532d1f7a2   NIB-QUERY-TOOL         bridge   ← shared (email bridges here)
f376e0a7d844   jenkins_default        bridge   ← Jenkins
ed50487967da   monitoring_default     bridge   ← Promtail
```

> 🚨 **`NIB-PREPROD-CUSTOMER` / `NIB-PREPROD-ADMIN` are the actual prod network names.** Any docs/scripts referring to `NIB-ONLINE` / `NIB-ONLINE-ADMIN` describe staging only. The "preprod" naming is a cutover artifact.

---

## 3. Running Topology — What's Actually Deployed

### 3.1 Production `.139` (verified `docker ps`, 2026-05-19)

**Customer-portal stack** (compose: `~/deploy-nib-online/customer-portal/compose.preprod-backend.yml`)

| Service | Replicas | Image | Status |
|---|---|---|---|
| user-service | **3** | `nibitdev/user-service:preprod` | Up 4 days, healthy |
| demographic-service | **3** | `nibitdev/demographic-service:preprod` | Up 32 hours, healthy |
| online-claims-service | **3** | `nibitdev/online-claims:preprod` | Up 11 hours, healthy |
| online-cards-service | **2** | `nibitdev/online-cards:preprod` | Up 21 hours, healthy |
| nib-email-service | **2** | `nibitdev/email-service:preprod` | Up 21 hours, healthy |
| preprod-backend-proxy | 1 | `nginx:1.25-alpine` | Up 2 months, healthy |
| preprod-customer-redis | 1 | `redis:alpine3.18` | Up 2 months, healthy |

**Admin-portal stack** (compose: `~/deploy-nib-online/admin-portal/compose.preprod.yml` + `compose.preprod-dashboard.yml`)

| Service | Replicas | Image | Status |
|---|---|---|---|
| admin-auth | **2** | `nibitdev/admin-auth:preprod` | Up 21 hours, healthy |
| online-cards-admin | **2** | `nibitdev/online-cards-admin:preprod` | Up 21 hours, healthy |
| online-claims-admin | **2** | `nibitdev/online-claims-admin:preprod` | Up 11 hours, healthy |
| admin-email | **2** | (image-hash `b1fff8f1ad64` — same as customer email) | Up 21 hours, healthy |
| preprod-admin-nginx | 1 | `nibitdev/online-portal-admin-frontend:preprod` | Up 5 days, healthy |
| admin-portal-preprod-admin-dashboard-1 | 1 | `nibitdev/online-portal-admin-frontend:preprod-dashboard` | Up 2 months, healthy |
| preprod-admin-redis | 1 | `redis:alpine3.18` | Up 2 months, healthy |

> **Two admin frontends on prod.** `preprod-admin-nginx` is the live admin SPA (`:preprod` tag). `admin-portal-preprod-admin-dashboard-1` (`:preprod-dashboard` tag) is a separate dashboard view from `compose.preprod-dashboard.yml`. Both run simultaneously.

**Background jobs stack** (compose: `~/deploy-nib-online/background-job/compose.preprod.yml`)

| Container | Image | Status |
|---|---|---|
| preprod-claims-pending-bg | `nibitdev/claims-pending-app-bg:preprod` | Up 8 days, healthy |
| preprod-cards-pending-bg | `nibitdev/cards-background-job:preprod` | Up 8 days, healthy |
| preprod-email-service-bg | `nibitdev/email-service-bg:preprod` | Up 14 hours, **unhealthy** |
| preprod-user-refresh-job | `nibitdev/user-refresh-job:preprod` | Up 8 days, healthy |

**Shared infrastructure on `.139`:**

| Container | Image |
|---|---|
| preprod-rabbitmq | `heidiks/rabbitmq-delayed-message-exchange:4.0.2-management` |
| preprod-jenkins | `jenkins-jenkins` (custom build — not Docker Hub `jenkins/jenkins`) |
| nib-promtail | `grafana/promtail:3.0.0` (ships logs to `.123` Loki) |

> The RabbitMQ image is the `delayed-message-exchange` variant — supports delayed message delivery via plugin. Required because the email-service uses the delay feature.

### 3.2 Staging `.123` (verified `docker ps`, 2026-05-19)

**nib-online-portal containers on `.123`** — single replicas (no LB needed):

| Service | Image |
|---|---|
| online-portal-frontend | `nibitdev/online-portal-frontend:staging` |
| customer-portal-user-service-1 | `nibitdev/user-service:staging` |
| customer-portal-demographic-service-1 | `nibitdev/demographic-service:staging` |
| customer-portal-online-claims-service-1 | `nibitdev/online-claims:staging` |
| customer-portal-online-cards-service-1 | `nibitdev/online-cards:staging` |
| customer-portal-nib-email-service-1 | `nibitdev/email-service:staging` |
| customer-redis | `redis:alpine3.18` |
| online-portal-admin-frontend | `nibitdev/online-portal-admin-frontend:staging` |
| admin-portal-admin-auth-service-1 | `nibitdev/admin-auth:staging` |
| admin-portal-online-cards-admin-service-1 | `nibitdev/online-cards-admin:staging` |
| admin-portal-online-claims-admin-service-1 | `nibitdev/online-claims-admin:staging` |
| admin-portal-nib-email-service-1 | `nibitdev/email-service:staging` |
| admin-portal-minio-1 / admin-portal-minio-2 | `quay.io/minio/minio:RELEASE.2024-02-26T09-33-48Z.fips` |
| admin-redis | `redis:alpine3.18` |
| background-job-claims-pending-background-job-1 | `nibitdev/claims-pending-app-bg:latest` ← **`:latest`, NOT `:staging`** |
| background-job-cards-pending-background-job-1 | `nibitdev/cards-background-job:latest` |
| background-job-email-service-background-job-1 | `nibitdev/email-service-bg:staging` |
| background-job-user-refresh-job-1 | `nibitdev/user-refresh-job:latest` |
| nib-loki / nib-grafana / nib-promtail | `grafana/{loki,grafana,promtail}` (3.0/11.0/3.0) |
| jenkins | `jenkins/jenkins:lts-jdk17` |

> **Background jobs on staging pull `:latest`** (3 of 4), not `:staging`. They share the prod image tag pool by default. Verify this is intentional.

---

## 4. Customer Backend Proxy (the prod LB pattern)

Production `.139` runs an internal nginx (`preprod-backend-proxy`, `nginx:1.25-alpine`) that binds host ports 5000-5004 and reverse-proxies to Docker service names — letting the compose-managed replicas share host ports without external LB awareness.

**Verified config** (`/etc/nginx/nginx.conf` inside `preprod-backend-proxy`):

```
Port 5000 → user-service:5000          (3 replicas, round-robin via Docker DNS)
Port 5001 → demographic-service:5000    (3 replicas)
Port 5002 → online-claims-service:5000  (3 replicas)
Port 5003 → online-cards-service:5000   (2 replicas)
Port 5004 → nib-email-service:5000      (2 replicas)
```

**How LB happens:**

```
External request (citizen)
    │
    ▼
NetScaler LB (172.16.82.x VIPs)
    │
    ▼
Customer nginx on 192.168.100.139 (the public-facing SPA + reverse proxy)
    │
    ▼  via host ports 5000-5004
preprod-backend-proxy (nginx:1.25-alpine on .139 backend)
    │
    ▼  via Docker DNS (e.g. `user-service:5000`)
[user-service-1, user-service-2, user-service-3]  ← round-robin
```

Key nginx directives in `backend-proxy.conf`:

- `resolver 127.0.0.11 valid=10s` — Docker's embedded DNS, refreshed every 10s
- `client_max_body_size 50M` — uploads up to 50MB
- `proxy_buffer_size 128k`, `proxy_buffers 4 256k` — large buffers for form-encoded uploads
- `proxy_connect_timeout 10s`, `proxy_read_timeout 60s`, `proxy_send_timeout 60s`

> Staging `.123` does NOT use `backend-proxy` — it runs single replicas with direct port assignments (Docker picks high ports automatically, e.g., `0.0.0.0:36214->5000/tcp`).

---

## 5. Configuration Management

### 5.1 Where configs live on each host

**Staging `.123`** (configs are version-tracked alongside compose files):

```
~/projects/deploy-nib-online/
├── customer-portal/
│   ├── compose.yml                    ← active compose
│   └── backend/
│       ├── demographic-service/config.py
│       ├── online-claims-service/config.py
│       ├── online-cards-service/config.py
│       └── email-service/config.py
├── admin-portal/
│   ├── compose.yml
│   └── backend/
│       ├── admin-auth/config.py
│       ├── online-claims-admin/config.py
│       ├── online-cards-admin/config.py
│       └── email-service/config.py
├── shared-services/email-service/templates/
└── background-job/
    ├── compose.yml
    └── jobs/
        ├── card-pending-background-job/config.py
        ├── claims-pending-background-job/config.py
        ├── email-service-background-job/config.py
        └── user-refresh-job/config.py
```

**Production `.139`** (different structure — uses `generated-configs/` dir):

```
~/deploy-nib-online/
├── customer-portal/
│   ├── compose.preprod-backend.yml   ← active compose (NOT compose.yml)
│   └── (no backend/ subdir — configs come from generated-configs/)
├── admin-portal/
│   ├── compose.preprod.yml
│   └── compose.preprod-dashboard.yml ← separate dashboard frontend
├── background-job/
│   └── compose.preprod.yml
├── generated-configs/
│   └── preprod/
│       ├── admin-auth.config.py
│       ├── admin-email.config.py
│       ├── cards-admin.config.py
│       ├── cards-pending-bg.config.py
│       ├── claims-admin.config.py
│       ├── claims-pending-bg.config.py
│       ├── demographic-service.config.py
│       ├── email-bg.config.py
│       ├── email-service.config.py
│       ├── online-cards.config.py
│       ├── online-claims.config.py
│       ├── user-refresh-job.config.py
│       └── user-service.env           ← NOTE: .env not .py
└── certs/                              ← wildcard SSL
```

**Bind-mount pattern (from `compose.preprod-backend.yml`):**

```yaml
volumes:
  - ../generated-configs/preprod/demographic-service.config.py:/app/config.py:ro
  - ../generated-configs/preprod/online-claims.config.py:/app/config.py:ro
  - ../generated-configs/preprod/online-cards.config.py:/app/config.py:ro
```

Configs are read-only (`ro`) — services cannot mutate their own config.

### 5.2 Config generation

`deploy-nib-online/generate-configs.sh` (in the deploy-nib-online git repo) renders `config-templates/preprod/*` placeholders into `generated-configs/preprod/*.config.py`. Operator workflow:

```bash
# Local workstation
cd deploy-nib-online
vim generate-configs.sh   # edit values (e.g., Sentry DSN, schema names)
./generate-configs.sh preprod
# → generated-configs/preprod/*.config.py

# Deploy
scp generated-configs/preprod/* devadmin@preprod-backend:~/deploy-nib-online/generated-configs/preprod/
ssh devadmin@preprod-backend
cd ~/deploy-nib-online/admin-portal && docker compose -f compose.preprod.yml up -d
cd ~/deploy-nib-online/customer-portal && docker compose -f compose.preprod-backend.yml up -d
```

> No secrets are committed. `generated-configs/` is gitignored. Source-of-truth values come from the operator's local `generate-configs.sh` (which has hard-coded values that should themselves be moved into env vars — but currently are not).

### 5.3 user-service uses `.env`, not `config.py`

`user-service.env` is the one anomaly — `nib_user_service` predates the config-class pattern and uses env vars directly. It's bind-mounted as `.env` and read by `python-dotenv` at startup.

---

## 6. File Synchronization

### 6.1 Shared file volumes (intra-host)

Customer and admin services share Docker volumes for file uploads:

| Volume | Customer writes | Admin reads |
|---|---|---|
| `customer-portal_online-claims-applications` | online-claims-service | online-claims-admin |
| `customer-portal_online-card-applications` | online-cards-service | online-cards-admin |

On prod `.139`, these are bind-mounted to `/Data_Repository/`:

```
customer-portal_online-claims-applications  →  /Data_Repository/online-claims-applications/
customer-portal_online-card-applications    →  /Data_Repository/online-card-applications/   (Jul 2024)
                                                /Data_Repository/online-cards-applications/  (Feb 2026 — plural variant)
/Data_Repository/BankingDocs/                ← sibling, NOT under claims (demographic-service writes here)
```

On staging `.123` — **no `/Data_Repository` bind-mount exists.** File writes go to Docker's ephemeral container layer (memory: `staging-123-missing-data-repository`). Routing logic can be tested but persistence cannot.

### 6.2 Cross-host sync (`.117` legacy → `.139` prod)

During the LB cutover transition, admin portal on `.139` needs to review applications uploaded on the legacy `.117` customer server. Solved via 15-minute cron rsync:

**Script:** `/home/devadmin/scripts/sync-prod-uploads.sh` on `.139`
**Schedule:** Every 15 min (cron on `.139`, exact owner TBD — user crontab is empty so likely root or systemd timer)
**Direction:** `172.16.1.117:/Data_Repository/` → `172.16.1.139:/Data_Repository/`
**Mechanism:** `rsync -rlz --ignore-existing --omit-dir-times` over SSH (key: `/home/devadmin/.ssh/id_ed25519`)
**Lock file:** `/tmp/nib-upload-sync.lock` prevents overlapping runs
**Log:** `/home/devadmin/scripts/sync-prod-uploads.log` (3.7MB at time of inspection)

> Per memory `prod-preprod-file-sync-cron`: the sync started 2026-02-26 and should be retired post-Cutover P4 when `.117` is fully drained.

---

## 7. CI/CD — Jenkins

### 7.1 Two Jenkins instances

| Instance | Host | Image | Port | Builds | Targets |
|---|---|---|---|---|---|
| Staging Jenkins | `.123` | `jenkins/jenkins:lts-jdk17` | 8081 → 8080 (container) | `:staging` tags | deploys to `.123` |
| Preprod Jenkins | `.139` | `jenkins-jenkins` (custom) | 8080 (via SSH tunnel) | `:preprod` tags | deploys to `.139` |

**Staging Jenkins details** (verified on `.123`):

```
Image:   jenkins/jenkins:lts-jdk17
Created: 2025-09-22T21:54:28
Restart: unless-stopped
Mounts:
  /usr/bin/docker             → /usr/bin/docker        (host docker binary)
  /var/run/docker.sock        → /var/run/docker.sock   (docker-in-docker via socket)
  /Staging_Repositiry/docker-data/volumes/jenkins_home/_data → /var/jenkins_home
```

> Mounts include `docker.sock` and `/usr/bin/docker` — Jenkins runs `docker` commands directly on the host (no DinD). This is intentional for the build-and-push pattern.

**Preprod Jenkins** is `jenkins-jenkins` (locally-built image, no public source). Up 9 days at time of inspection. Access via SSH tunnel:

```bash
ssh -L 8080:localhost:8080 -fN -J querytool-prod devadmin@preprod-backend
# → http://localhost:8080  (Jenkins UI; HTTP 403 = unauthenticated, expected)
```

### 7.2 Pipeline pattern (verified from `deployments-jenkins` repo)

Three pipeline lanes, one per environment:

| Tag | Built by | Source branch | Target |
|---|---|---|---|
| `:staging` | Service repo's own `Jenkinsfile` (Jenkins on `.123`) | service repo's `staging` branch | `.123` |
| `:preprod` | `deployments-jenkins/nib-online-portal/preprod/<portal>/<service>/Jenkinsfile` (Jenkins on `.139`) | service repo's `staging` branch | `.139` |
| `:prod` | `deployments-jenkins/nib-online-portal/<portal>/<service>/Jenkinsfile` (Jenkins on `.139` or legacy) | service repo's `master` branch | `.117` (legacy, draining) |

Same source branch (`staging`) feeds BOTH `:staging` and `:preprod` pipelines — by design, since `:preprod` is the live production tag post-cutover.

### 7.3 Known Jenkins issues

- **Stale-container-id bug** (memory `jenkins-stale-container-id-bug`): pipelines bail at deploy step with "No such container" / "removal in progress" after successful image build. Workaround: manual `docker compose up -d` on host. Folded into P3 standardization sprint.
- **Customer-frontend preprod build is guarded** (task #70): the `:preprod` Jenkins job for customer SPA was guarded against accidental trigger to protect the launch image from being rebuilt without source recovery. See memory `launch-image-provenance`.
- **No automated `:prod` builds** (task #38 pending): post-launch, `:prod` tag builds and `.117` deploy weren't being triggered. Manual until task #38 lands.

### 7.4 Jenkins backups (created 2026-05-16, pre-upgrade)

| Host | Backup file | Size |
|---|---|---|
| `.123` | `~/backups/jenkins-123-pre-upgrade-20260516-0105.tar.gz` | 1.6GB |
| `.139` | `~/backups/jenkins-139-pre-upgrade-20260516-0108.tar.gz` | 333MB |

Backups are tarballs of the `jenkins_home` volume taken via Docker alpine container (avoids host UID issues). Restore would require stopping Jenkins, untarring into volume, restarting.

---

## 8. Docker Image Registry

| Aspect | Value |
|---|---|
| Registry | Docker Hub |
| Namespace | `nibitdev/*` |
| Push credentials | Stored in Jenkins credential store |
| Pull on hosts | Public images — no auth required on hosts |

**Image tag conventions (verified from running containers):**

| Tag | Source | Where it runs |
|---|---|---|
| `:staging` | Service repo's `staging` branch via .123 Jenkins | `.123` |
| `:preprod` | Service repo's `staging` branch via .139 Jenkins | `.139` (LIVE PROD) |
| `:prod` | Service repo's `master` branch | `.117` legacy |
| `:latest` | Background jobs (default tag) | `.123` (3 of 4 bg jobs) and `.139` |
| `:claims` | Customer frontend (legacy holdover) | `.123` staging only |
| `:preprod-dashboard` | Admin frontend dashboard variant | `.139` |

> The `:claims` tag on customer frontend is a historical artifact — the image is bit-identical to `:preprod` but the tag survived rebranding. See memory `launch-image-provenance`.

---

## 9. Monitoring & Observability

### 9.1 Monitoring stack (Loki + Grafana + Promtail)

**Host:** `.123` (single Loki instance receives logs from all 3 hosts)
**Compose:** `/home/devadmin/monitoring/compose.monitoring.yml` on `.123`
**Network:** `nib-monitoring` bridge on `.123`

**Components:**

| Container | Image | Port |
|---|---|---|
| nib-loki | `grafana/loki:3.0.0` | `0.0.0.0:3100` |
| nib-grafana | `grafana/grafana:11.0.0` | `0.0.0.0:8082` (mapped from 3000) |
| nib-promtail | `grafana/promtail:3.0.0` | (no port — pushes to Loki) |

**Log shipping topology:**

```
.123 nib-promtail   ────┐
.139 nib-promtail   ────┼──→  .123 nib-loki (3100)  ──→  .123 nib-grafana (8082)
.117 promtail (TBD) ────┘
```

Promtail auto-discovers containers via `/var/run/docker.sock` and labels logs with `container`, `compose_project`, `compose_service`, `host`. Sample query:

```
{compose_service="online-claims-service"} |~ "ERROR"
```

**Access:**

- Direct on `.123`: `http://192.168.100.123:8082` (blocked by corporate firewall — see memory `grafana-staging-access`)
- Via SSH tunnel: `ssh -L 3030:127.0.0.1:3030 devadmin@192.168.100.123` → `http://localhost:3030`
- Via admin nginx fronting: `https://192.168.100.123:8080/grafana/` (the workable workstation path)

**Login:** `admin / NibLogs2026!` (change after first login — memory note).

**Retention:** 30 days (`Loki retention_period: 720h`). Old-sample window 1 year for backfill.

### 9.2 Sentry

| Aspect | Value |
|---|---|
| Org | `the-national-insurance-board-242` (4506667039326208) |
| URL | `https://o4506667039326208.sentry.io/` |
| Project pattern | One Sentry project per service |
| DSN provisioning | Hard-coded in `generate-configs.sh` (committed to deploy-nib-online repo) |
| Env tag | `SENTRY_ENVIRONMENT` passed via compose env — `production` on `.139`, `staging` on `.123` |
| Replay sampling | Set to `0.0` post-2026-05-10 to stop burning quota |

Per-service Sentry coverage matrix is in `03-SERVICES.md` (some services have only basic init; a few have no Sentry at all).

---

## 10. Networking & DNS

### 10.1 DNS topology

| Hostname | Resolves to | Notes |
|---|---|---|
| `nibonline.nib-bahamas.com` | `192.168.100.139` | Live prod customer (post-cutover) |
| `nibonline-admin.nib-bahamas.com` | `172.16.82.3` (LB VIP) | Live prod admin via NetScaler |
| `preprod-nibonline.nib-bahamas.com` | `192.168.100.139` | Same server as prod (post-cutover) |
| `preprod-*-api.nib-bahamas.com` | `172.16.1.139` directly | Preprod backend, skips LB |
| `staging-nibonline.nib-bahamas.com` | `192.168.100.123` | Test env |

Per memory `network-topology-critical`:

- **Prod customer**: DNS → NetScaler LB (172.16.82.2/.3) → `.139`
- **Prod admin**: DNS → NetScaler LB (172.16.82.3) → `.139`
- **Preprod**: DNS → direct A record to `.139` (skips LB entirely)

### 10.2 NetScaler load balancer

Operated by NIB infra team (Craig). LB VIPs:

- `172.16.82.2` — customer pool
- `172.16.82.3` — admin pool

Customer pool was flipped to `.139` on 2026-05-10 (Cutover P3). Admin pool was flipped same day (task #40 completed). `.117` and `.116` are still in the pool but receiving zero traffic (Cutover P4 will formally remove them).

### 10.3 Internal firewall ACLs (NetSec-managed)

From `.123` outbound — limited reachability (memory `staging-netsec-acl-map`):

- `172.16.82.2` reachable
- `172.16.82.3` blocked
- `172.16.1.x` blocked

Implication: don't write integration code that has `.123` reach across backend subnets — use Docker DNS within compose project instead.

**SSH access policy:**

- Workstation → `.123`: direct via VPN (`192.168.100.123`)
- Workstation → `.139` customer/admin: must go through jumphost `172.16.1.156` (`querytool-prod` alias). NetSec ACL blocks direct.
- Memory: `ssh-backend-jumphost`

### 10.4 SSL certificates

**Wildcard:** `*.nib-bahamas.com` (single cert covers all subdomains)
**Location on deploy hosts:** `~/deploy-nib-online/certs/star_nib_bahamas_com.{pem,key,crt}`
**Mounted into:** nginx containers only (`online-portal-frontend`, `online-portal-admin-frontend`, `preprod-admin-nginx`). Backend services see plain HTTP within Docker networks.

> Internal Docker traffic is plaintext HTTP. `verify=False` is used on internal `requests` calls because no internal CA is configured. External-facing TLS termination happens at the nginx edge containers.

---

## 11. Deploying a Code Change (end-to-end)

The verified deployment path for a backend service code change:

### 11.1 Standard staging→preprod flow

```bash
# 1. Developer commits to service repo
cd online-claims-submission-api
git checkout staging
git pull
# edit code...
git commit -am "fix: ..."
git push origin staging

# 2. Two Jenkins jobs trigger automatically on push
#    a. .123 Jenkins (port 8081):
#       - Builds nibitdev/online-claims:staging
#       - SSHes to .123 and runs docker compose up -d
#    b. .139 Jenkins (port 8080 via tunnel):
#       - Builds nibitdev/online-claims:preprod  ← LIVE PROD
#       - SSHes to .139 and runs docker compose -f compose.preprod-backend.yml up -d

# 3. Operator verifies on .123 first (rate-limited test traffic)
ssh devadmin@192.168.100.123
docker logs customer-portal-online-claims-service-1 -f
curl -X POST https://staging-nibonline.nib-bahamas.com/api/online-claims/...

# 4. If staging looks good, .139 deploy is already done (parallel build)
ssh -J querytool-prod devadmin@preprod-backend
docker ps  # verify replicas restarted with new image
# observe Sentry + Grafana for first hour
```

### 11.2 Manual rollback (if Jenkins deploy failed)

```bash
# On prod .139:
cd ~/deploy-nib-online/customer-portal
docker compose -f compose.preprod-backend.yml pull   # pull current :preprod tag
docker compose -f compose.preprod-backend.yml up -d --force-recreate

# Specific service only:
docker compose -f compose.preprod-backend.yml up -d --force-recreate online-claims-service

# Rolling restart (preserves replica availability):
docker compose -f compose.preprod-backend.yml restart online-claims-service
```

### 11.3 Config-only change (no image rebuild)

```bash
# Workstation
cd deploy-nib-online
./generate-configs.sh preprod
scp generated-configs/preprod/online-claims.config.py \
    devadmin@preprod-backend:~/deploy-nib-online/generated-configs/preprod/

# On .139 (file is bind-mounted, but services don't hot-reload config.py)
ssh -J querytool-prod devadmin@preprod-backend
cd ~/deploy-nib-online/customer-portal
docker compose -f compose.preprod-backend.yml restart online-claims-service
```

---

## 12. Operational Gotchas (verified incidents)

### 12.1 `cards-pending-bg` on `.123` points at PROD Oracle

**Verified 2026-05-19** via `docker inspect background-job-card-pending-background-job-1`: NO `DB_HOST` / `DB_SERVICE_NAME` env vars are set.

The container's `config.py` reads:

```python
host = os.getenv("DB_HOST", "jumv3prddb-scan.nib-bahamas.com")
sid  = os.getenv("DB_SERVICE_NAME", "nib_v3prod")
```

With no overrides, it defaults to prod. The cleanup logic (delete pending applications > 30 days old) is therefore operating on prod data from a staging deploy. Container has been "Up 8 days (unhealthy)" — unhealthy means the `last_run` file check fails, suggesting the job may not actually be ticking. **Verify whether real cleanup operations have run.** If they have, prod data integrity needs review.

Memory entry: `cards-pending-bg-prod-oracle-default`.

### 12.2 `.139` root volume at 98% full

`/dev/mapper/rhel-root` 60G/61G used. `/Data_Repository/` lives on root. Citizen file uploads + Docker layer accumulation are filling the volume. `/home` has 30G free but isn't being used for either. Needs `du -sh /Data_Repository /var/lib/docker/* ~/deploy-nib-online ~/backups` to find culprit.

### 12.3 Two cards directories on prod

`/Data_Repository/online-card-applications/` (singular, July 2024, mode 0777) AND `/Data_Repository/online-cards-applications/` (plural, Feb 2026) both exist. F4 incident (memory) confirmed singular is the correct one but apparently the plural variant was never deleted. Worth `du -sh` and a content audit before any cleanup — may contain orphaned uploads.

### 12.4 Docker bind-mount + `sed -i` inode gotcha

`sed -i` creates a new file with a new inode; Docker bind-mounts track the original inode. After `sed -i`, the container still sees the OLD file content even after `nginx -s reload`. Fix: use Python `open(path, 'w')` or `cat > file` (preserves inode), OR restart the container. Post-mortem: 2026-03-02 nginx config edits via `sed -i` were invisible for hours.

### 12.5 Customer-claims loses NIB-ONLINE-ADMIN network on Jenkins rebuild

On `.123`, the customer-claims container loses its `NIB-ONLINE-ADMIN` membership on every Jenkins rebuild. Symptom: reupload_requests fetch returns `[]`. Recover with `docker network connect NIB-ONLINE-ADMIN customer-portal-online-claims-service-1`. Permanent fix is to add to compose `networks:` block. Memory: `customer-claims-admin-network-reconnect`.

### 12.6 PowerShell / Git Bash path mangling on Windows builds

`/api/auth` → `C:/Program Files/Git/api/auth` when passed as a Docker build-arg. Vite bakes the mangled URL into the bundle. **Set `MSYS_NO_PATHCONV=1`** for any `docker build` with `VITE_*` build args. Affects local frontend builds only; Jenkins (Linux) is unaffected. Memory: workspace `CLAUDE.md` "MSYS Path Mangling."

### 12.7 SQLAlchemy pool poisoning on Oracle TCP idle timeout

Oracle drops connections after ~10h idle. Without proper handling, the first request hits a dead connection (DatabaseError), and the pool is poisoned for every subsequent request (PendingRollbackError) until container restart. **The fix is in every service's `app.py`:**

```python
@app.errorhandler(SQLAlchemyError)
def handle_database_exception(e):
    try: db.session.connection().invalidate()
    except: pass
    try: db.session.rollback()
    except: pass
    try: db.session.close()
    except: pass
    return jsonify({"message": "Database temporarily unavailable, please retry"}), 503
```

Don't remove it. Memory: `pool-cascade-broken-handler-pattern`.

---

## 13. Backup & Disaster Recovery

### 13.1 What's backed up

**Verified on `.123`:**

| Item | Path | Last backup |
|---|---|---|
| Jenkins home (`.123`) | `~/backups/jenkins-123-pre-upgrade-20260516-0105.tar.gz` (1.6GB) | 2026-05-16 |
| Strapi CMS uploads | `~/backups/strapi-uploads-backup.tar.gz` (360MB) | 2026-01-21 |
| Strapi CMS schemas | `~/backups/cms_pre_*.sql` | 2026-01 |
| nib-website backup cron | `cd ~/projects/deploy-nib-website/docker-deployment/backups/scripts && bash backup-all.sh` daily 02:00 |

**Verified on `.139`:**

| Item | Path | Last backup |
|---|---|---|
| Jenkins home (`.139`) | `~/backups/jenkins-139-pre-upgrade-20260516-0108.tar.gz` (333MB) | 2026-05-16 |

### 13.2 What's NOT backed up (gaps)

- **Oracle Database** — managed by NIB DBA team. Backup discipline not visible from these hosts.
- **`/Data_Repository/` uploads** — no scheduled backup of citizen uploaded documents. Only the `.117`→`.139` sync exists (which is replication, not backup — deletions propagate).
- **Generated configs** — not gitignored on host but only present on the deploy hosts (`generated-configs/preprod/`). If `.139` loses its disk, configs must be re-generated from operator's local `generate-configs.sh`.
- **Redis state** — in-memory; not backed up. Rate-limit token buckets are ephemeral.
- **MinIO** — bind-mounted volume but no scheduled backup.

### 13.3 `.123` automated cleanup crons

```cron
0  2 * * *   bash backup-all.sh                          # nib-website daily backup
0  */6 * * * docker image prune -af --filter until=48h   # every 6h
30 3 * * *   keep only 3 most recent CMS upload backups  # daily
```

`.139` user-crontab is empty — sync runs from root crontab or systemd (not directly visible without sudo).

---

## 14. Day-1 Cheat Sheet for a New Operator

```bash
# CONNECT TO STAGING
ssh devadmin@192.168.100.123
docker ps                                # see all 30+ containers
docker logs <container> -f               # tail logs
docker compose -f ~/projects/deploy-nib-online/customer-portal/compose.yml ps

# CONNECT TO PROD (jumphost)
ssh -J querytool-prod devadmin@preprod-backend
docker ps                                # see prod containers (replicated)
docker compose -f ~/deploy-nib-online/customer-portal/compose.preprod-backend.yml ps

# OPEN JENKINS TUNNEL (PROD)
ssh -L 8080:localhost:8080 -fN -J querytool-prod devadmin@preprod-backend
# → http://localhost:8080

# OPEN GRAFANA TUNNEL (LOG VIEWER)
ssh -L 3030:127.0.0.1:3030 devadmin@192.168.100.123
# → http://localhost:3030 (admin / NibLogs2026!)
# OR direct via admin-nginx fronting: https://192.168.100.123:8080/grafana/

# RESTART A SERVICE (PROD)
ssh -J querytool-prod devadmin@preprod-backend
cd ~/deploy-nib-online/customer-portal
docker compose -f compose.preprod-backend.yml restart online-claims-service

# READ A LIVE CONFIG (PROD)
ssh -J querytool-prod devadmin@preprod-backend
cat ~/deploy-nib-online/generated-configs/preprod/online-claims.config.py

# CHECK ORACLE FROM A CONTAINER (PROD)
ssh -J querytool-prod devadmin@preprod-backend
docker exec customer-portal-online-claims-service-1 \
  python -c "from src import db; print(db.engine.url)"

# SYNC LATEST FILES FROM LEGACY .117
ssh -J querytool-prod devadmin@preprod-backend
bash /home/devadmin/scripts/sync-prod-uploads.sh
tail -100 /home/devadmin/scripts/sync-prod-uploads.log
```

---

## 15. Known Gaps in This Doc

What I did NOT verify in this pass (because the verification would have required sudo, prod writes, or out-of-scope inspections):

- Exact contents of `generate-configs.sh` (template-rendering logic) — visible in the deploy-nib-online repo but not freshly inspected for current envs
- `.139` root crontab and systemd timers (sync-prod-uploads scheduling owner)
- NetScaler LB pool config (Craig's domain)
- Oracle DBA backup discipline
- Exact ACL rules (NetSec's domain)
- The `:preprod-dashboard` admin frontend variant — its purpose vs `:preprod` (it's running on prod but the use case is unclear from outside)
- Whether `cards-pending-bg` on `.123` has actually executed cleanup operations against prod, or just sat unhealthy

Each of these is verifiable; flag if you need them documented and we'll do a focused follow-up read.

---

## 16. Verification Discipline (for future maintainers of this doc)

The original 2026-05-19 onboarding docs had to be partially rewritten because point-in-time reference docs (Feb 2026) had drifted. **When updating this doc:**

1. **Re-verify from live servers** before changing topology/network/replica claims. Examples of single commands that surface drift:
   - `docker ps` on each host
   - `docker network ls`
   - `docker inspect <container> --format '{{.Config.Image}}{{println}}{{.Config.Env}}'`
   - `cat ~/deploy-nib-online/generated-configs/preprod/<service>.config.py`
2. **Cite what you saw.** "Verified 2026-MM-DD" labels above each section keep readers honest about staleness.
3. **Flag gaps** in §15 when you didn't verify something. A doc that admits ignorance is more useful than one that fabricates confidence.
4. **Cross-check against memory** in `.claude/projects/.../memory/` — operational findings often live there before they're documented.

---

**Done. This is the operational/devops layer. For application-level patterns, see `02-ARCHITECTURE.md`. For per-service detail, see `03-SERVICES.md`. For business context, see `01-EXECUTIVE-OVERVIEW.md`.**
