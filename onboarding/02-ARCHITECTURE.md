# NIB Online Portal — Architecture & Integration

**Audience:** Developers and AI assistants joining the project. Read this **after** `01-EXECUTIVE-OVERVIEW.md` and **before** `03-SERVICES.md`.
**Branch reference:** All paths/commits cite the **`master`** branch of each repo. Branch policy is at the bottom of this doc.
**Last reviewed:** 2026-05-19

---

## 1. The Big Picture

The NIB Online Portal is **two public portals sharing one backend ecosystem**:

| Portal | Audience | Domain | Tech |
|---|---|---|---|
| **Customer Portal** | Bahamian citizens | `nibonline.nib-bahamas.com` | Vue 3 SPA + 5 Flask APIs |
| **Admin Portal** | NIB staff (Customer Service / Cards / Claims teams) | `nibonline-admin.nib-bahamas.com` | Vue 3 SPA + 4 Flask APIs |

Behind these two portals sit:

- **1 shared email service** (Flask) bridging both portals
- **4 scheduled background workers** (APScheduler) doing cleanup / sync
- **1 shared Oracle Database** (the system of record)
- **2 Redis instances** (one per portal)
- **1 MinIO cluster** (admin portal object storage)
- **Shared file volumes** linking customer uploads to admin review

The whole thing is **a polyrepo**: 20 sibling git repositories coordinated by `deploy-nib-online`, which holds the Docker Compose orchestration that wires services together.

---

## 2. Repository Topology

```
nib-online-portal/                          # workspace root (NOT a git repo itself)
│
│── ── DEPLOYMENT (3 repos) ─────────────────────────────────────────────
│
├── deploy-nib-online/                       # 🔑 Orchestration source of truth
│   ├── customer-portal/compose.yml          #   wires 5 customer APIs + redis + frontend
│   ├── admin-portal/compose.yml             #   wires 4 admin APIs + redis + minio + frontend
│   ├── shared-services/shared-services.yml  #   email-service + redis base definitions
│   ├── background-job/compose.yml           #   4 scheduled workers
│   ├── config-templates/                    #   per-environment .env templates
│   ├── generate-configs.sh                  #   renders .env files for staging/preprod
│   └── monitoring/                          #   Loki + Promtail + Grafana stack
│
├── deploy-background-job/                   # (legacy, mostly placeholder)
└── deployments-jenkins/                     # Jenkins pipelines for ALL deploys (P2 jobs)
    └── nib-online-portal/
        ├── preprod/<portal>/<service>/Jenkinsfile  # builds :preprod, deploys to .139
        └── <portal>/<service>/Jenkinsfile          # builds :prod (legacy .117 lane)
│
│── ── CUSTOMER PORTAL (5 repos) ────────────────────────────────────────
│
├── nib_user_service/                        # Customer auth, account create/activate (Flask)
├── demographic-service/                     # Profile + banking-detail uploads (Flask)
├── online-claims-submission-api/            # Claims submit + reupload (Flask)
├── online-cards-api/                        # Card applications (Flask)
├── online-claims-submissions-frontend/      # Customer SPA (Vue 3 + TS)
│
│── ── ADMIN PORTAL (4 repos) ───────────────────────────────────────────
│
├── admin-auth/                              # LDAP login + JWT issue (Flask)
├── online-cards-admin-api/                  # Admin card review (Flask)
├── online-claims-administrative-api/        # Admin claims review (Flask)
├── online-submissions-admin-frontend/       # Admin SPA (Vue 3 + TS)
│
│── ── SHARED SERVICES (2 repos) ────────────────────────────────────────
│
├── nib-email-service/                       # SMTP relay (Flask) — runs in BOTH portals
├── nib-user-service-v2/                     # Next-gen user service (FastAPI, partial)
│
│── ── BACKGROUND JOBS (4 repos) ────────────────────────────────────────
│
├── email-service-background-job/            # email queue → SMTP (every minute)
├── users-refresh-job/                       # daily sync from legacy user DB
├── online-claims-submission-pending-app-removal/   # clean expired pending claims (daily)
├── online-cards-expired-pending-app-background-job/# clean expired pending cards (daily)
│
│── ── UTILITIES (2 repos) ──────────────────────────────────────────────
│
├── audit-user-service/                      # CSV audit + date-of-death updates
└── development-documentation/               # cross-team dev docs (also hosts onboarding/)

(plus a local-only docs dir: nib-online-docs/ — holds reference/ point-in-time docs)
```

**Mental model:** each square bracket above = independent git repo. Each maps to **one Docker image**. The mapping is documented in the workspace `CLAUDE.md` (repo → image table).

---

## 3. Docker Network Architecture

Three Docker networks shape the topology. **Network membership defines who can talk to whom.**

```
┌────────────────────────────────────────────────────────────────────┐
│  NIB-ONLINE  (customer portal — bridge network)                    │
│                                                                    │
│   user-service ──┐                                                 │
│   demographic-service ──┐                                          │
│   online-claims-service ──┐  ◄── ALSO on NIB-ONLINE-ADMIN          │
│   online-cards-service ──┤                                         │
│   nib-email-service ──┐  │                                         │
│   customer-redis ─────┤  │                                         │
│   online-portal-frontend (nginx 80/443/5000-5004) ◄── public edge  │
│                       │  │                                         │
│                       │  └──► (bridges to admin via claims-svc)    │
│                       └──► (bridges to NIB-QUERY-TOOL via email)   │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│  NIB-ONLINE-ADMIN  (admin portal — bridge network)                 │
│                                                                    │
│   admin-auth-service                                               │
│   online-cards-admin-service                                       │
│   online-claims-admin-service                                      │
│   nib-email-service (separate container, same image)               │
│   admin-redis                                                      │
│   minio (x2 replicas, ports 9004/9005)                             │
│   online-portal-admin-frontend (nginx 8080/9000-9005) ◄── public   │
│   online-claims-service (bridged-in from customer network)         │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│  NIB-QUERY-TOOL  (external bridge — owned by a different system)   │
│                                                                    │
│   email-service bridges here so emails sent from the NIB Query     │
│   Tool platform can be relayed through the same SMTP machinery.    │
└────────────────────────────────────────────────────────────────────┘
```

**Two cross-network bridges worth remembering:**

1. **`online-claims-service` is on BOTH** `NIB-ONLINE` and `NIB-ONLINE-ADMIN`. This is the **reupload-request bridge**: an admin requests a reupload, the customer-side claims API must learn about it. Without this dual-membership, the customer SPA never sees the prompt.
2. **`nib-email-service` is on `NIB-ONLINE` (or `NIB-ONLINE-ADMIN`) + `NIB-QUERY-TOOL`**. Lets the legacy NIB Query Tool also send email through this service.

> Gotcha: on `.123` (staging), the customer-claims container loses its `NIB-ONLINE-ADMIN` membership on every Jenkins rebuild and must be re-attached with `docker network connect`. The compose `networks:` block fixes this — see memory `customer-claims-admin-network-reconnect`.

---

## 4. The Two Request Lifecycles

### 4.1 Customer Journey — Submitting a Claim

```
Citizen browser
    │
    ▼  HTTPS (443)
┌──────────────────────────────────────────────────────────────┐
│  online-portal-frontend  (nginx, customer SPA + reverse proxy)│
│                                                              │
│   /                       → Vue SPA (static)                 │
│   /api/user/...           → user-service:5000                │
│   /api/demographic/...    → demographic-service:5000         │
│   /api/online-claims/...  → online-claims-service:5000       │
│   /api/cards/...          → online-cards-service:5000        │
│   /api/email/...          → nib-email-service:5000           │
└──────────────────────────────────────────────────────────────┘
    │
    │  1. POST /api/user/login            (JWT issued)
    │  2. GET  /api/demographic/user      (profile loaded)
    │  3. POST /api/online-claims/application/sickness  (submit)
    │     ├── Service inserts application_header + applications row
    │     ├── File upload writes to /Data_Repository/online-claims-applications/Submitted/{user}/{type}/{id}/{file}
    │     │   (Docker volume customer-portal_online-claims-applications — bound to host /Data_Repository on .139)
    │     ├── application_docs row created (file_path = relative, /Submitted/... stripped)
    │     └── Async: POST /api/email/send (background thread, non-blocking)
    │
    ▼
Oracle DB        +    Shared file volume    +    Email service
(application_header,  (customer-portal_      (logs into email_queue
 applications,         online-claims-         table → picked up by
 application_docs,     applications)          email-service-bg every 60s)
 banking_details)
```

### 4.2 Admin Journey — Reviewing a Claim

```
NIB staff browser
    │
    ▼  HTTPS (8080)
┌──────────────────────────────────────────────────────────────┐
│  online-portal-admin-frontend  (nginx, admin SPA + proxy)    │
│                                                              │
│   /                              → Vue admin SPA             │
│   /api/admin-auth/...            → admin-auth-service:5000   │
│   /api/cards-admin/...           → online-cards-admin:5000   │
│   /api/claims-admin/...          → online-claims-admin:5000  │
│   /api/email/...                 → nib-email-service:5000    │
└──────────────────────────────────────────────────────────────┘
    │
    │  1. POST /api/admin-auth/login                (LDAP creds → JWT)
    │  2. GET  /api/claims-admin/application/list   (paginated, filtered by office)
    │  3. GET  /api/claims-admin/application/{id}   (full detail + uploads + banking)
    │  4. GET  /api/claims-admin/application/file/{file_id}
    │     │  ├── Reads application_docs.file_path from DB
    │     │  ├── Builds abs path: /Data_Repository/online-claims-applications/<file_path>
    │     │  ├── ApplicationFileUploadsService.base_path_for(document_type)
    │     │  │   resolves either to online-claims-applications/ or BankingDocs/
    │     │  └── Returns file bytes (or 400 "File does not exist")
    │     ▼
    │  Reads from SAME shared volume the customer wrote to
    │  (customer-portal_online-claims-applications) ─────────────┐
    │                                                             │
    │  5. POST /api/claims-admin/application/{id}/reupload        │
    │     ├── reupload_request_repo.save() → reupload_requests row│
    │     ├── ApplicationFileUploadsRepo.update_doc_status(       │
    │     │       app_file_upload_id, REUPLOAD_REQUESTED)         │
    │     ├── Calls customer-claims-service (cross-network bridge)│
    │     │   via AdminService.root_url — internal Docker DNS     │
    │     └── Async email to citizen via nib-email-service        │
    ▼
Oracle DB                  Shared file volume     Email service
(reupload_requests,       (R-only, same as       (same machinery)
 application_assignment,   customer side)
 application_docs.status updated)
```

> The two journeys **share the Oracle DB and the file volume**. That sharing is the whole point — it lets admin act on data citizens submitted without any network round trip to fetch files.

---

## 5. Authentication

Two completely separate auth flows.

### 5.1 Customer Auth (citizen-facing)

- **Library:** `flask-jwt-extended`
- **Token format:** JWT, identity = NIB number (also called `EENI`)
- **Issuance:** `nib_user_service` validates Oracle user credentials, returns JWT
- **Token lifetime:** 1 day (`JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)`)
- **Storage:** localStorage in customer SPA
- **Forwarding:** Every customer Flask service runs `@app.before_request` that captures the `Authorization` header into Flask `g.token`, used for service-to-service calls

### 5.2 Admin Auth (staff-facing)

- **Library:** `ldap3` + `flask-jwt-extended`
- **Identity source:** corporate LDAP
- **Role source:** Oracle table `dbo.security_role_user` (LDAP only authenticates the password — *roles* come from this DB table)
- **Roles that grant admin write access:** `SUPERVISOR R`, `DEPARTMENT HEAD R`, `MANAGER FIU`, `SUB OFFICE MANAGER FIU`
- **Token identity:** the JWT `identity` is a user-role dict (not just a username), set in `admin-auth/src/auth/auth_service.py:47`
- **Enforcement:** `@admin_required` / `@user_required` / `@read_only` decorators in `<service>/src/nib_user/decorators/` plus frontend `canEdit` computed in `useCards.ts` / `useClaims.ts`

> Gotcha: front- and back-end role lists must stay in sync. There was a 2026-03-24 incident where `useCards.ts` was missing `MANAGER FIU` and `SUB OFFICE MANAGER FIU` — backend allowed the action but the UI hid the button.

### 5.3 JWT secret sharing within a portal domain (CRITICAL)

Two JWT domains exist and must each have **identical** secrets across all services that validate them:

- **Customer domain** — all five customer Flask services (user, demographic, online-claims, online-cards, email-customer) share the same `JWTConfig.secret`. Any mismatch = 401 on every protected endpoint.
- **Admin domain** — all four admin Flask services (admin-auth, cards-admin, claims-admin, email-admin) share the same (different) `JWTConfig.secret`.

**The cross-portal call** (`online-claims-submission-api` → `online-claims-administrative-api` via `AdminService.root_url`) forwards the **customer** JWT in the `Authorization` header. For these three specific endpoints to work — `/file/request/<id>` GET/PUT and `/application/<id>/assignment/active` GET — the admin claims service must accept customer JWTs. Implication: either the two domains share a secret for these endpoints, or the admin service has a separate auth path for service-to-service calls. **Verify this assumption before changing JWT secrets on either side.**

A local-deployment checklist:

- Set identical `JWTConfig.secret` in ALL customer Flask `config.py` files
- Set the same secret in `nib_user_service/.env` as `JWT_SECRET_KEY`
- Set identical `JWTConfig.secret` in ALL admin Flask `config.py` files
- Test the cross-portal call (claims customer → claims admin with customer JWT) before declaring environment ready

---

## 6. Data Stores

### 6.1 Oracle Database (system of record)

- **Driver:** `oracledb` (thin mode) — replaces older `cx-oracle`
- **ORM:** SQLAlchemy 2.0
- **Migration tool:** Alembic via Flask-Migrate
- **Migration trigger:** Each Flask service calls `flask_migrate.upgrade()` inside `src/__init__.py` **on every startup**. This is convenient but means migrations land the moment a container restarts — keep them idempotent and small.
- **Connection pool tuning** (identical on every Flask service):
  ```python
  app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
      "pool_pre_ping": True,       # check connection before checkout
      "pool_recycle": 1800,        # recycle after 30 minutes
      "pool_size": 5,              # baseline pool
      "max_overflow": 10,          # burst capacity
      "pool_timeout": 30,
  }
  ```

#### Verified schema map (2026-05-19, from live server configs)

The platform uses **7 distinct Oracle schemas**. Each Flask service connects as one schema and SELECTs across others via `__table_args__ = {"schema": "<other>", "autoload_with": db.engine}`. **Schema names differ between staging and prod** — prod still carries `_preprod`-suffixed names from the May 2026 LB cutover (task #45 pending).

| Service | Staging schema (`v3train`) | Prod schema (`nib_v3prod`) | Reads from |
|---|---|---|---|
| demographic-service | `demographic_service` | `demographic_service` | `client` |
| online-claims | `ONLINE_CLAIMS` | `online_claims` | `client`, `demographic_service`, `nib_admin_auth` |
| online-cards | `online_nib_cards` | `online_nib_cards` | `client`, `demographic_service`, `nib_admin_auth`, `online_nib_cards_admin` |
| admin-auth | `nib_admin_auth` | `admin_auth_preprod` ⚠ | own only |
| online-cards-admin | `online_nib_cards_admin` | `online_nib_cards_admin_preprod` ⚠ | `client`, `nib_admin_auth`, `online_nib_cards`, `demographic_service` |
| online-claims-admin | `online_claims_admin` | `online_claims_admin` | `client`, `nib_admin_auth`, `online_claims`, `demographic_service` |
| nib-email-service | `nib_email_service` | `nib_email_service_preprod` ⚠ | own only |
| claims-pending-bg | `online_claims` | `online_claims` | `client`, `demographic_service` |
| cards-pending-bg | `online_nib_cards` | `online_nib_cards` | `client`, `demographic_service`, `nib_admin_auth`, `online_nib_cards_admin` |
| email-bg | `nib_email_service` | `nib_email_service_preprod` ⚠ | own only |
| user-refresh-job | `nib_admin_auth` | `admin_auth_preprod` ⚠ | own only |

**Oracle hosts:**

- **Prod:** `jumv3prddb-scan.nib-bahamas.com:1521`, SID `nib_v3prod`
- **Staging:** `JUMV3TSTDBSRV01.nib-bahamas.com:1531`, SID `v3train`

**The `client` schema** holds reference data read by nearly every service: `users` (legacy identity) and `bank_branches`. Cross-schema SELECT grants are required.

> ⚠ Schema-name drift: prod-named schemas (e.g. `nib_admin_auth`) exist on staging. The same logical role on prod uses `_preprod`-suffixed names. Task #45 will rename prod schemas to the production-style names. **Until then, schema names are environment-specific** — staging cannot be used as a "what's the prod schema name" cheat sheet for those 4 affected schemas.

### 6.2 Redis (per-portal, two instances)

- `customer-redis` — rate-limit token bucket for customer portal (Flask-Limiter)
- `admin-redis` — rate-limit token bucket for admin portal
- **Health-gated:** API services declare `depends_on: { redis: { condition: service_healthy } }`. Redis must be reachable before any Flask service starts.
- Not used for application caching today — pure rate-limit backend.

### 6.3 MinIO (admin portal only)

- 2 replicas, ports 9004 (API) + 9005 (console)
- Configured but **not actively used** for file storage. Files still go to the shared bind-mount volume. MinIO is here as a future migration target.

### 6.4 Shared File Volumes (the critical glue)

| Volume | Mounted in | Host path (`.139` prod) |
|---|---|---|
| `customer-portal_online-claims-applications` | `online-claims-service`, `online-claims-admin-service` | `/Data_Repository/online-claims-applications/` |
| `customer-portal_online-card-applications` | `online-cards-service`, `online-cards-admin-service` | `/Data_Repository/online-card-applications/` |

Banking docs live **alongside** these volumes (not under them): `/Data_Repository/BankingDocs/{user}/{banking_details_id}/{file}`. The demographic-service mounts `/Data_Repository:/Data_Repository` to reach that path.

> Gotcha: on `.123` (staging) there is **no bind-mount to `/Data_Repository`** — file writes are ephemeral. Routing logic can be verified but persistence cannot. Always test persistence on `.139`.

---

## 7. Service-to-Service Communication

All cross-service calls are **HTTP REST** with `requests` library. There is no message bus, no gRPC, no GraphQL.

Pattern (canonical, every service follows it):

```python
import requests, urllib3
from flask import g
from config import AdminService

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
req = requests.get(
    url=f"{AdminService.root_url}/endpoint",
    headers={"Content-Type": "application/json", "Authorization": g.token},
    verify=False,
    timeout=5,         # ALWAYS include
)
```

**Hard rules:**

1. Every `requests.get/post/put` **must** specify `timeout`. A 2026 incident had a service hang indefinitely because timeout was omitted.
2. Internal calls use Docker DNS (`http://nib-email-service:5000`), **not** the public load-balancer hostname. The LB hostname only works from outside the Docker network and adds an extra hop.
3. `verify=False` is used because the wildcard cert is mounted into nginx, not into individual containers. Internal traffic stays inside the Docker network so TLS isn't required for it.

**Common cross-service edges (verified 2026-05-19):**

| From | To | URL (prod) | Purpose |
|---|---|---|---|
| customer-claims | claims-admin (cross-network) | Docker DNS to admin container | Get reupload requests + assignments for a citizen's app |
| claims-admin | customer-claims | (via shared `application_docs.status` flip + bg notify) | Trigger citizen reupload prompt |
| Any customer service | email | `http://nib-email-service:5000` | Send transactional email (enqueue to RabbitMQ) |
| Any admin service | email | `http://admin-email:5000` | Same — note **different container name** in admin compose |
| customer-cards | cards-admin | (NO HTTP — reads `online_nib_cards_admin.reupload_request` via cross-schema autoload) | DB-level integration |
| email-service | RabbitMQ | `preprod-rabbitmq:5672` (prod) / `queueservice:5672` (staging) | Enqueue outbound emails |
| email-bg | RabbitMQ | Same | Consume + send via SMTP |

> Note: the email service runs in **both portals** as separate containers but uses the **same image**. Customer-side container is named `nib-email-service`; admin-side is `admin-email`. Both bind-mount different config.py files for different API keys but resolve via Docker DNS within their respective networks.

**RabbitMQ note:** Email is async. The HTTP `POST /email` doesn't wait for SMTP — it inserts a row in the email_request DB table and publishes a message to the `Email Queue` exchange on RabbitMQ. The `email-service-background-job` container consumes that queue and hits SMTP. If you see emails not arriving, check (1) `email_request` rows in Oracle for recent inserts, (2) RabbitMQ queue depth, (3) bg job logs for SMTP failures.

---

## 8. Background Jobs

Four standalone Flask + APScheduler workers, all running in the **separate** `background-job/compose.yml` stack.

| Job | Schedule | What it does |
|---|---|---|
| `email-service-background-job` | every 60s | Drains email_queue rows, hits SMTP, marks sent |
| `card-pending-background-job` | daily | Removes expired pending card applications (older than 30 days, never submitted) |
| `claims-pending-background-job` | daily | Same, for pending claim applications |
| `user-refresh-job` | daily | Syncs portal users from legacy identity tables |

**Two things to know:**

1. Every job declares `PYTHONUNBUFFERED=1` — without it, Python block-buffers stdout under Docker and `docker logs` shows nothing for hours. A 2026-03-17 incident silently broke logging for ~2 months.
2. Healthcheck pattern: each job touches `/app/last_run` on every tick. Docker checks "is `last_run` mtime within N seconds of now?" — if not, container is unhealthy. Simple and effective.

---

## 9. Frontend Architecture

Both SPAs follow the same pattern.

```
src/
├── components/        # shared UI primitives (Headless UI, Hero Icons)
├── views/             # page-level components (mounted by router)
├── router/            # Vue Router 4 routes + guards
├── stores/            # Pinia / composables (auth, user, application state)
├── services/          # Axios clients per-API (one file per backend service)
├── composables/       # Vue 3 Composition API helpers (useClaims, useCards, ...)
├── plugins/           # sentry.ts, axios.ts, validation.ts
├── utils/             # formatters, validators
├── App.vue
└── main.ts            # bootstrap
```

**Build & deploy:**

```
Node 18-alpine          ──►  vite build  ──►  dist/   ──►   nginx 1.15-alpine
(yarn install,                                                serves dist/ +
 vite dev-only)                                               proxies /api/* to
                                                              backend services
```

Multi-stage Dockerfile pattern (both SPAs):

```dockerfile
# Stage 1: build
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json yarn.lock ./
RUN yarn install --frozen-lockfile
COPY . .
ARG VITE_USER_SERVICE_URL    # ← baked at build time
ARG VITE_CLAIMS_SERVICE_URL
# ... more VITE_* ARGs
RUN yarn build

# Stage 2: serve
FROM nginx:1.15-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
```

> Gotcha: Vite bakes `VITE_*` env vars into the JS bundle at build time. They are **not** runtime-configurable. Changing an API URL requires a rebuild. This is the root cause of the **MSYS path-mangling** issue documented in workspace `CLAUDE.md` — Git Bash on Windows converts `/api/auth` → `C:/Program Files/Git/api/auth`, baking the wrong URL into prod bundles. Always set `MSYS_NO_PATHCONV=1` for local Docker builds.

---

## 10. Error Handling & Observability

### 10.1 Error Handler Stack (every Flask service)

The customer-claims service's `app.py` is the canonical example. Order matters — Flask routes more-specific handlers first:

```python
@app.errorhandler(SQLAlchemyError)        # 1. DB cascade (DatabaseError + PendingRollbackError)
@app.errorhandler(RateLimitExceeded)      # 2. 429
@app.errorhandler(405)                    # 3. method not allowed (custom message)
@app.errorhandler(HTTPException)          # 4. all other HTTP errors → JSON
@app.errorhandler(Exception)              # 5. last-resort 500
```

**The DB handler is the most load-bearing piece** and exists because Oracle has a ~10h TCP idle timeout. Without it, a single dropped connection poisons the SQLAlchemy pool and every subsequent request 500s until the container restarts. The fix:

```python
try: db.session.connection().invalidate()  # evict from pool, lets pool_pre_ping re-establish
except Exception: pass
try: db.session.rollback()
except Exception: pass
try: db.session.close()
except Exception: pass
return jsonify({"message": "Database temporarily unavailable, please retry"}), 503
```

> This pattern is duplicated across all 8 Flask services. Don't remove it.

### 10.2 Sentry (org `the-national-insurance-board-242`)

- One Sentry project per service
- DSNs shared between staging and prod; environments differentiated by `SENTRY_ENVIRONMENT` tag passed in compose env
- Generator: `deploy-nib-online/generate-configs.sh` emits `customer-portal.env`, `admin-portal.env`, `background-job.env`
- JWT user context auto-attached via `@app.before_request` — Sentry events carry NIB number, email, name
- Frontend SPA has its own Sentry project (source maps uploaded to symbolicator)

### 10.3 Loki + Grafana (post 2026-05-10)

- Stack on `192.168.100.123` (staging server)
- Grafana: `https://192.168.100.123:8080/grafana/` (fronted by admin nginx — direct `:3030` blocked by corp firewall)
- Promtail auto-discovers all containers via `/var/run/docker.sock`
- Three hosts ship logs into the same Loki instance — distinguished by `host` label (`staging-123`, `prod-139`, `prod-backend-139`)
- Sample query: `{compose_service="online-claims-service"} |~ "ERROR"`

---

## 11. Deployment Topology

### 11.1 Servers

| Role | IP | DNS | Status |
|---|---|---|---|
| **Staging frontend + backend** | `192.168.100.123` / `172.16.1.123` | `staging-nibonline.nib-bahamas.com` | Test environment |
| **Prod frontend (current)** | `192.168.100.139` | `nibonline.nib-bahamas.com` AND `preprod-nibonline.nib-bahamas.com` (both resolve here post-2026-05-10) | LIVE PRODUCTION |
| **Prod backend** | `172.16.1.139` | (internal only) | LIVE PRODUCTION |
| **Legacy prod** | `192.168.100.117/.125`, `172.16.1.117/.116` | (drained) | Being removed from LB |

### 11.2 Image Tags (per environment)

| Tag | Built by | Deployed to |
|---|---|---|
| `:staging` | Service's own `Jenkinsfile` (in service repo) | `.123` staging |
| `:preprod` | `deployments-jenkins/.../preprod/.../Jenkinsfile` | `.139` (LIVE) |
| `:prod` | `deployments-jenkins/.../.../Jenkinsfile` (no preprod prefix) | `.117` (legacy, draining) |
| `:latest` | various (mostly background jobs) | `.117` / `.139` |

> Critical distinction: **`:preprod` is what's actually live in production** as of the 2026-05-10 LB cutover. The `:prod` tag is the legacy lane being drained.

### 11.3 Branch → Tag → Server Flow

```
   Source branch    →    Built image tag    →    Target server
─────────────────────────────────────────────────────────────────
   staging branch   →    :staging           →    .123  (test env)
                              ↓ (validate)
   staging branch   →    :preprod           →    .139  (LIVE PROD)
   master branch    →    :prod              →    .117  (legacy, draining)
```

**What this means:**

- Developers should branch from and push to **`staging`** on each service repo
- The `staging` branch flows through TWO Jenkins jobs: first builds `:staging` (deploys to test on `.123`), then a separate **preprod-target** Jenkins job rebuilds the same source into `:preprod` (deploys to live `.139`)
- The `master` branch is the **archival lane** for the legacy `.117` server until cutover P4 fully drains it from NetScaler
- **New work should NOT branch from master.** Always branch from `staging`.

### 11.4 CI/CD (Jenkins)

Two Jenkins instances:

- `.123:8081` — staging Jenkins, builds `:staging` images, deploys to `.123`
- `.139:8080` — preprod/prod Jenkins, builds `:preprod` images, deploys to `.139`. Tunnel from workstation: `ssh -L 8080:localhost:8080 -fN -J querytool-prod devadmin@preprod-backend`

Pipelines push to Docker Hub registry `nibitdev/*`.

---

## 12. Configuration & Secrets

```
deploy-nib-online/
├── config-templates/                # source-controlled templates with placeholders
│   ├── customer-portal/
│   │   └── backend/<service>/config.py
│   └── admin-portal/
│       └── backend/<service>/config.py
├── generate-configs.sh              # renders templates → generated-configs/
└── generated-configs/                # gitignored, deployed by SCP

Each environment (staging/preprod/prod) generates its own:
- backend/<service>/config.py   # bind-mounted into container at /app/config.py
- backend/<service>/.env         # for env-driven values (Sentry DSN, GIT_COMMIT)
```

**No secrets in git.** The `config-templates` have placeholders like `{ORACLE_PASSWORD}` resolved by `generate-configs.sh` from the operator's local environment.

**Per-service config classes** (uniform across all Flask services):

- `OracleDB` — host, port, sid, userName, password
- `Flask` — host, port, env
- `FileRepo` — path to file storage (CRITICAL: must be absolute, e.g. `/Data_Repository/online-claims-applications`, not relative `uploads`)
- `NIBEmailService` — root_url
- `AdminService` — root_url (for cross-portal calls)
- `RedisDB` — host, port, password
- `Sentry` — DSN, environment
- `JWTConfig` — secret, expiry
- `RateLimiter` — defaults

---

## 13. The Five Patterns You'll See Everywhere

### 13.1 Controller / Service / Repository (3-tier)

```
src/<feature>/
├── <feature>_controller.py    # @app.route handlers, request parsing, calls service
├── <feature>_service.py       # business logic, calls repo, calls other services
├── <feature>_repo.py          # all DB queries, returns DTOs
├── <feature>_model.py         # SQLAlchemy model
├── dto/
│   └── <feature>_dto.py       # dataclass DTOs (controller ↔ service ↔ repo)
├── enums/                     # status enums
└── sql/                       # raw SQL files for complex queries
```

Controllers are thin. Services hold the rules. Repos own the DB.

### 13.2 Auto-Discovery of Controllers

Every `src/__init__.py` ends with this glob:

```python
import glob, importlib.util, os
for f in glob.glob(os.path.dirname(__file__) + "/**/*_controller.py", recursive=True):
    spec = importlib.util.spec_from_file_location(os.path.basename(f)[:-3], f)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
```

Result: **adding a new endpoint = create a new `*_controller.py` file**. No central registration. The file is discovered and its routes are registered with `@app.route(...)`.

### 13.3 DTO Pattern

```python
@dataclass
class ApplicationDTO:
    id: int
    nib_user_id: int
    status: str
    uploads: List[DocsUploadDTO] = field(default_factory=list)
```

DTOs are **always returned from services and repos** — never raw SQLAlchemy models. This insulates layers from each other and prevents lazy-load surprises after the session closes.

### 13.4 Auto-Migration on Startup

Every Flask service runs `flask_migrate.upgrade()` in `src/__init__.py`:

```python
with app.app_context():
    upgrade(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "migrations"),
            revision="head")
```

**Implications:** keep migrations tiny, idempotent, and never destructive. They run every time a container starts.

### 13.5 Gevent Monkeypatching (gunicorn workers)

The customer-claims `src/__init__.py` starts with:

```python
if "gevent" in sys.modules or os.getenv("GUNICORN_CMD_ARGS"):
    from gevent import monkey
    monkey.patch_all()
```

Production runs `gunicorn --worker-class gevent --workers 4 --timeout 120`. Gevent gives concurrency without async/await. **The monkeypatch must happen before any other imports**, otherwise things like `oracledb`'s TCP socket isn't patched and the worker blocks.

---

## 14. Master-Branch Reading Guide (this doc's branch policy)

The new developer should:

1. **Clone each repo and check out `master`** to read the "stable, deployed-elsewhere" source.
2. Understand `master` is the **legacy `.117` lane** for customer/admin services. Live production runs `:preprod` images built from `staging`.
3. Before making changes: `git checkout staging && git pull origin staging`, then branch from there.

This split exists because the 2026-05-10 LB cutover moved live traffic to `.139` but the team chose not to immediately re-point `master`. It will be reconciled in cutover P4.

---

## 15. Next Reading

- **`03-SERVICES.md`** — per-service deep dive (purpose, key files, endpoints, deps)
- **`../reference/`** — point-in-time architecture/incident reference docs
- Workspace `CLAUDE.md` — quick-reference tables (image tags, ports, branching)

---

**Glossary**

- **NIB** — National Insurance Board (of The Bahamas)
- **EENI** — citizen identifier (essentially the NIB number)
- **B80 / B81** — government claim forms (Employer Certificate of Termination / Medical Certificate)
- **Polyrepo** — multiple coordinated repos vs monorepo
- **`.123` / `.139` / `.117`** — IP last-octet shorthand for staging / prod / legacy-prod servers
- **`v3train` / `v3prod`** — Oracle service names (staging shares `v3train`, prod uses `v3prod`)
