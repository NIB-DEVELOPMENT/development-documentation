# NIB Online Portal — Executive Overview

**Audience:** Anyone joining the project — technical leader, manager, new developer, succession-planning stakeholder. **Read this first.**
**Last reviewed:** 2026-05-19

---

## What This System Does

The **NIB Online Portal** is the digital services platform for the **National Insurance Board of The Bahamas**. It lets Bahamian citizens apply for government insurance benefits and services online, and lets NIB staff process those applications.

The portal replaces — and in some cases continues to coexist with — in-person paperwork at NIB branch offices. Every claim or card application submitted online is one less line at a counter.

---

## Who It Serves

| User group | Numbers | What they do here |
|---|---|---|
| **Bahamian citizens** | Tens of thousands of registered users (all working-age Bahamians are eligible) | Apply for benefits and NIB cards, upload supporting documents, check status |
| **NIB staff** | Hundreds of Customer Service / Cards / Claims officers across multiple Bahamian local offices | Review applications, request additional documents, approve/reject, generate forms |

It is a **government-scale system**. Outages, data loss, or misrouted citizen data have real reputational and policy consequences. Production changes are made deliberately and with operator authorization for risky actions.

---

## What Citizens Can Do

Two product pillars:

### 1. Benefit Claims (7 types)

- **Unemployment Benefit** — when a citizen loses their job
- **Sickness Benefit** — short-term illness compensation
- **Maternity Benefit** — paid leave around childbirth
- **Funeral Benefit** — bereavement support
- **Retirement Benefit** — pension claim
- **Disability Benefit** — long-term medical
- **Surviving Spouse Benefit** — bereavement income support

Each claim flow gathers structured data (employment dates, dependents, medical details), supporting documents (B80, B81 forms, passport, banking proof), and produces a submission an NIB Claims Officer can review.

### 2. NIB Cards

- **New card** — first-time NIB card issuance
- **Renewal** — card past its expiry
- **Replacement** — lost, damaged, or stolen card

---

## What Staff Can Do

Through the **Admin Portal**:

- **List & filter applications** by status, claim type, local office, and routed-to officer
- **Review** the full submission — citizen profile, banking details, every uploaded document
- **Request reupload** when a document is unreadable or incomplete (triggers an email + citizen prompt)
- **Approve or reject** with documented reasoning
- **Generate official forms** (B80 Employer's Certificate, B81 Medical Certificate, etc.) as PDFs
- **Assign** an application to a specific officer for routing/ownership

---

## How It's Built (at 30,000 ft)

The system is a **polyrepo microservices platform** — 20 independent code repositories that together form one running product.

```
┌─────────────────────────────┐         ┌─────────────────────────────┐
│   Customer Portal (Web)     │         │    Admin Portal (Web)       │
│   nibonline.nib-bahamas.com │         │ nibonline-admin.nib-bahamas │
│                             │         │ .com                        │
│   Vue 3 single-page app     │         │   Vue 3 single-page app     │
└──────────────┬──────────────┘         └──────────────┬──────────────┘
               │                                       │
               │  REST API calls                       │  REST API calls
               ▼                                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Backend microservices (Python Flask, one per concern)               │
│                                                                      │
│   Customer side: user-service, demographic-service, online-claims,   │
│                  online-cards                                        │
│                                                                      │
│   Admin side:    admin-auth, online-cards-admin, online-claims-admin │
│                                                                      │
│   Shared:        nib-email-service (used by both portals)            │
│                  4 background workers (scheduled jobs)               │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Data layer                                                          │
│                                                                      │
│   Oracle Database (system of record — applications, users, files     │
│                    metadata)                                         │
│                                                                      │
│   File storage (uploaded docs, shared between customer-write and     │
│                 admin-read services)                                 │
│                                                                      │
│   Redis (rate limiting), MinIO (future object storage)               │
└──────────────────────────────────────────────────────────────────────┘
```

**Tech foundations:**

- **Backend:** Python 3.11, Flask 2.2, SQLAlchemy 2.0, Oracle Database
- **Frontend:** Vue 3 + TypeScript + Vite + TailwindCSS
- **Auth:** JWT (citizens), LDAP + JWT (staff)
- **Containers:** Docker, orchestrated by Docker Compose
- **CI/CD:** Jenkins pipelines per service
- **Observability:** Sentry (errors), Loki + Grafana (logs), in-house healthchecks

---

## Operational Status

**As of May 2026:** Production. Live. Serving citizens daily.

| Environment | Server | Status |
|---|---|---|
| **Production** | `192.168.100.139` (frontend) + `172.16.1.139` (backend) | Live, post-LB-cutover (2026-05-10) |
| **Legacy production** | `192.168.100.117` / `.125` / `172.16.1.117` / `.116` | Being drained from the load balancer; not yet decommissioned |
| **Staging** | `192.168.100.123` | Test environment with prod-shaped configuration |

The 2026-05-10 cutover moved customer traffic to a new server tier (`.139`). The legacy tier (`.117`) is staying warm for rollback safety until "Cutover P4" formally removes it from the load balancer.

---

## Key Risks & How They're Managed

| Risk | Mitigation |
|---|---|
| **Database connection poisoning** (Oracle 10h idle-timeout drops connections, then SQLAlchemy pool returns dead connections on every request — full outage until container restart) | Every Flask service has a `SQLAlchemyError` handler that invalidates poisoned connections and lets the pool re-establish on next checkout. This was a hard-won 2026-05-18 incident; the pattern is now in 8 services. |
| **File storage divergence between customer write and admin read** | Customer-write and admin-read services share the same Docker volume. The shared mount is the only thing keeping admin able to read what citizens uploaded. |
| **Citizen credential exposure / leakage** | No secrets in git. Config files rendered at deploy time from templates + operator's local environment. SSL wildcard cert mounted into nginx, not individual containers. |
| **Government-scale outages** | Sentry alerts on every service. Loki centralized logs across 3 hosts. Independent staging environment for testing. Operator-authorized production write discipline (explicit "Authorize prod-write" phrasing). |
| **Lossy deploys** (Docker volume vs bind-mount confusion has caused data ghosting in the past) | Production uses **bind-mounts** to `/Data_Repository/`. Documented critical-gotcha in workspace `CLAUDE.md`. |
| **Image tag drift** (Jenkins building one tag, compose pinning another) | Documented; under remediation. Tag-pinning policy now: compose explicitly pins the deployed tag rather than `:latest`. |

---

## Where Things Stand (Active Initiatives)

These are the threads currently being worked on or recently shipped:

- **Log aggregation rollout** (Loki + Grafana) — staging stack live; prod stack replicated; alerting in progress
- **Banking-doc storage topology** — recently fixed; all banking docs now persist to `/Data_Repository/BankingDocs/` (previously some writes went to ephemeral container layer)
- **Cross-portal reupload flow** — admin can now request a citizen reupload; citizen sees a prompt; documents flow back through customer service to admin review
- **Sentry environment tagging** — staging and prod events now distinguished in Sentry UI
- **`nib-user-service-v2`** — FastAPI replacement for the legacy customer user service; partial production traffic
- **Legacy server decommission** — Cutover P4 will remove `.117` from the load balancer pool

---

## What Makes This System Distinctive

1. **Polyrepo, not monorepo.** Each service has its own git repository. Orchestration lives centrally in `deploy-nib-online`. This trades onboarding cost (new dev clones 20 repos) for service independence (each team owns their service end-to-end).

2. **Shared file volumes between customer and admin services.** Most microservice systems move files via HTTP between services. This one mounts the same volume into both. Simpler. Faster. Tightly coupled.

3. **Auto-discovery of routes.** Each Flask service runs a glob at startup that loads every `*_controller.py` file. Adding an endpoint is "create a file in the right directory."

4. **Auto-migration on startup.** Each Flask service runs Alembic migrations on every container start. Convenient and risky in equal measure — migrations must be tiny and idempotent.

5. **Government compliance posture.** No third-party SaaS for citizen data. Oracle Database on-prem. SMTP via internal relay. SSL via wildcard cert managed by NIB infra.

---

## Onboarding Checklist for a New Developer

1. **Read `02-ARCHITECTURE.md`** — understand how the apps work together.
2. **Read `03-SERVICES.md`** — get a feel for what each repo does. You don't need to memorize, but know where to look.
3. **Clone the workspace** — get all 20 repos under one parent directory (the polyrepo layout).
4. **Check out `master`** on each repo as a starting baseline. Read what's stable. When ready to make changes, switch to `staging`.
5. **Read the workspace-level `CLAUDE.md`** at the polyrepo root — it has the quick-reference tables (image tag map, port map, branching policy).
6. **Get a deployment walkthrough from the current maintainer** — Jenkins access, SSH tunnels to production, the operator-authorization protocol for risky actions.
7. **Spin up the customer portal locally with Docker Compose** — `cd deploy-nib-online/customer-portal && docker compose up`. Verify you can log in as a test citizen.
8. **Read one service end-to-end** — pick `online-claims-submission-api`. Trace one endpoint from `app.py` → `src/__init__.py` → a `*_controller.py` → service → repo → model. That's the pattern everywhere.

---

## Glossary

| Term | Meaning |
|---|---|
| **NIB** | National Insurance Board (of The Bahamas) — the governmental body this system serves |
| **EENI** | Citizen identifier (functionally, the NIB number) |
| **LB / NetScaler** | Load balancer in front of customer-facing services |
| **Polyrepo** | Architecture pattern where each service lives in its own git repository (contrast: monorepo) |
| **B80 / B81** | Government claim forms — Employer's Certificate of Termination / Medical Certificate |
| **`v3train` / `v3prod`** | Oracle service names — staging uses `v3train`, production uses `v3prod` |
| **`.123` / `.139` / `.117`** | Server shorthand by IP last-octet (staging / current-prod / legacy-prod) |
| **`:preprod` tag** | Despite the name, this is the **live production** image tag post-2026-05-10. The label is a historical holdover. |
| **Routed-to** | The CS officer or department head assigned to handle a specific application |
| **Reupload request** | Admin asking a citizen to re-upload a specific document that was illegible or missing |

---

## Quick-Reference: Where Things Live

- **All 20 repos** → `nib-online-portal/` (polyrepo workspace root)
- **Orchestration / Docker Compose** → `deploy-nib-online/`
- **CI/CD pipelines** → `deployments-jenkins/`
- **This documentation** → `development-documentation/onboarding/` (versioned in the `NIB-DEVELOPMENT/development-documentation` GitHub repo)
- **Architecture reference + incident notes** → `nib-online-docs/reference/` (still in the local docs dir on workstations)
- **Live production** → `192.168.100.139` (workstation reaches via VPN + SSH tunnel)
- **Sentry organization** → `the-national-insurance-board-242` at `https://o4506667039326208.sentry.io/`
- **Log dashboards** → `https://192.168.100.123:8080/grafana/`

---

**Next:** Read `02-ARCHITECTURE.md`.
