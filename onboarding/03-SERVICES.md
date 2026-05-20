# NIB Online Portal — Service-by-Service Reference

**Audience:** Developers and AI assistants. Read this **after** `02-ARCHITECTURE.md`.
**Purpose:** Per-service deep dive verified against live `.123` (staging) and `.139` (prod) configs, plus repo source.
**Branch reference:** Paths cite the `master` branch. Live production runs `:preprod` images from `staging` — see `02-ARCHITECTURE.md` §11 and §14.
**Verified:** 2026-05-19 from live server configs + local repos. Schemas, endpoints, and config classes are source-truth.

---

## Service Index

| # | Repo | Image | Tier | Stack | Network |
|---|---|---|---|---|---|
| 1 | `nib_user_service` | `nibitdev/user-service` | Customer | Flask | NIB-ONLINE |
| 2 | `demographic-service` | `nibitdev/demographic-service` | Customer | Flask | NIB-ONLINE |
| 3 | `online-claims-submission-api` | `nibitdev/online-claims` | Customer | Flask | NIB-ONLINE + NIB-ONLINE-ADMIN |
| 4 | `online-cards-api` | `nibitdev/online-cards` | Customer | Flask | NIB-ONLINE |
| 5 | `online-claims-submissions-frontend` | `nibitdev/online-portal-frontend` | Customer | Vue 3 + nginx | NIB-ONLINE |
| 6 | `admin-auth` | `nibitdev/admin-auth` | Admin | Flask | NIB-ONLINE-ADMIN |
| 7 | `online-cards-admin-api` | `nibitdev/online-cards-admin` | Admin | Flask | NIB-ONLINE-ADMIN |
| 8 | `online-claims-administrative-api` | `nibitdev/online-claims-admin` | Admin | Flask | NIB-ONLINE-ADMIN |
| 9 | `online-submissions-admin-frontend` | `nibitdev/online-portal-admin-frontend` | Admin | Vue 3 + nginx | NIB-ONLINE-ADMIN |
| 10 | `nib-email-service` | `nibitdev/email-service` | Shared | Flask + pika | Both portals + NIB-QUERY-TOOL |
| 11 | `nib-user-service-v2` | (manual) | Shared (migration target) | **FastAPI** | partial deploy |
| 12 | `email-service-background-job` | `nibitdev/email-service-bg` | Background | Flask + APScheduler | NIB-QUERY-TOOL |
| 13 | `users-refresh-job` | `nibitdev/user-refresh-job` | Background | Flask + APScheduler | (job network) |
| 14 | `online-claims-submission-pending-app-removal` | `nibitdev/claims-pending-app-bg` | Background | Flask + APScheduler | (job network) |
| 15 | `online-cards-expired-pending-app-background-job` | `nibitdev/cards-background-job` | Background | Flask + APScheduler | (job network) |
| 16 | `audit-user-service` | (CLI) | Utility | Flask | — |
| 17 | `development-documentation` | (docs) | Utility | Markdown | — |
| 18 | `deploy-nib-online` | (orchestration) | Deployment | Compose + Bash | — |
| 19 | `deployments-jenkins` | (CI/CD) | Deployment | Jenkinsfile (Groovy) | — |
| 20 | `deploy-background-job` | (placeholder) | Deployment | — | — |

> All Flask services expose port 5000 internally. External ports map only on the two frontend nginx containers.

---

## Verified Oracle Schema Map

Verified 2026-05-19 from `.123` (`v3train`) and `.139` (`nib_v3prod`) config bind-mounts.

| Service | Staging schema (`v3train`) | Prod schema (`nib_v3prod`) | Reads from (cross-schema) |
|---|---|---|---|
| `demographic-service` | `demographic_service` | `demographic_service` | `client` |
| `online-claims-submission-api` | `ONLINE_CLAIMS` | `online_claims` | `client`, `demographic_service`, `nib_admin_auth` |
| `online-cards-api` | `online_nib_cards` | `online_nib_cards` | `client`, `demographic_service`, `nib_admin_auth`, `online_nib_cards_admin` |
| `admin-auth` | `nib_admin_auth` | `admin_auth_preprod` ⚠️ | own only |
| `online-cards-admin-api` | `online_nib_cards_admin` | `online_nib_cards_admin_preprod` ⚠️ | `client`, `nib_admin_auth`, `online_nib_cards`, `demographic_service` |
| `online-claims-administrative-api` | `online_claims_admin` | `online_claims_admin` | `client`, `nib_admin_auth`, `online_claims`, `demographic_service` |
| `nib-email-service` (customer) | `nib_email_service` | `nib_email_service_preprod` ⚠️ | own only |
| `nib-email-service` (admin) | `nib_email_service` | `nib_email_service_preprod` ⚠️ | own only |
| `claims-pending-bg` | `online_claims` | `online_claims` | `client`, `demographic_service` |
| `cards-pending-bg` | `online_nib_cards` (env-driven) | `online_nib_cards` | `client`, `demographic_service`, `nib_admin_auth`, `online_nib_cards_admin` |
| `email-service-bg` | `nib_email_service` | `nib_email_service_preprod` ⚠️ | own only |
| `user-refresh-job` | `nib_admin_auth` | `admin_auth_preprod` ⚠️ | own only |

**⚠️ Prod `_preprod`-suffix drift** — four schemas on prod still carry the `_preprod` suffix that survived the May 2026 LB cutover. Tracked as workspace task #45 (rename to production names). Until it's done, staging schema names are the *production-style* names and prod schema names are *temporary*.

**Cross-schema reads** use SQLAlchemy `__table_args__ = {"schema": "<name>", "autoload_with": db.engine}` — see e.g. `online-claims-administrative-api/src/applications/sickness/sickness_application_model.py:7` reading from `online_claims`. The full cross-schema read set was confirmed by grepping `__table_args__.*schema` across all `src/**/*_model.py` files.

---

# Customer Portal

## 1. `nib_user_service` → `nibitdev/user-service`

**One-liner:** Customer authentication, account creation, activation, validation. The front door to the customer portal.

| Concern | Detail |
|---|---|
| Network | `NIB-ONLINE` |
| Stack | Flask + Waitress + SQLAlchemy + Oracle |
| Internal port | 5000 |
| Public route | `/api/user/*` (proxied by `online-portal-frontend`) |
| Config bind | `.env` file (not config.py — exception to the pattern) |
| Redis dep | `customer-redis` (rate limiting) |
| Sentry | **None** (gap) |

**Key responsibilities:** citizen login (NIB number + password → JWT), account creation with email activation, password reset, profile update, JWT validation.

**Notes:**

- Source of customer JWTs used by **every** customer-side service. JWT secret must match across all customer services (see `02-ARCHITECTURE.md` §5.1).
- Endpoint surface is locked behind activation-token flows; specific routes live in `modules/application/controllers/user.py` (legacy module structure — pre-dates the `*_controller.py` auto-discovery pattern used everywhere else).
- **No Dockerfile in the local checkout.** Image must be pulled from Docker Hub (`nibitdev/user-service`).
- Local clone may appear empty in some workspaces; re-clone from origin to populate.
- Sentry was *never* added — one of the gaps in the Feb 2026 observability audit. Adding it is task post-launch backlog.

---

## 2. `demographic-service` → `nibitdev/demographic-service`

**One-liner:** Citizen profile, contacts, addresses, local-office assignment, banking details, **banking document upload/reupload**.

| Concern | Detail |
|---|---|
| Network | `NIB-ONLINE` |
| Stack | Flask 2.2.3 + SQLAlchemy 2.0.6 + oracledb 2.0.1 + Gunicorn/gevent |
| Internal port | 5000 |
| Public route | (deployed image serves at root; nginx rewrites `/api/demographic/*` → `/*`) |
| Schema (prod) | `demographic_service` |
| Reads | `client` (users, bank_branches) |
| Critical volume | `/Data_Repository:/Data_Repository` (banking doc writes) |
| Email API | `http://nib-email-service:5000` (Docker DNS) |
| Sentry | Basic (DSN-only, no PII scrubbing) |

**Verified endpoints (from `src/**/*_controller.py`):**

| Method | Path | Module |
|---|---|---|
| GET | `/user` | user |
| GET | `/user/<eeni>` | user |
| GET | `/user/<eeni>/legacy` | user |
| GET | `/local-offices` | local_office |
| GET | `/user/local-office` | user_local_office |
| POST | `/user/local-office` | user_local_office |
| GET | `/claimant-address` | claimant_address |
| POST | `/claimant-address` | claimant_address |
| GET | `/claimant-address/states` | claimant_address |
| GET | `/claimant-address/types` | claimant_address |
| GET | `/claimant-contact` | claimant_contact |
| POST | `/claimant-contact` | claimant_contact |
| GET | `/claimant-contact/countries` | claimant_contact |
| GET | `/claimant-contact/phone/types` | claimant_contact |
| PUT | `/claimant-contact/<id>/primary` | claimant_contact |
| GET | `/banking-details` | payment_details |
| POST | `/banking-details` | payment_details |
| PUT | `/banking-details/<id>/primary` | payment_details |
| DELETE | `/banking-details/<id>` | payment_details |
| GET | `/bank-branches` | bank_branches |
| POST | `/banking-details/<id>/documents` | document_upload (banking doc upload) |
| GET | `/banking-details/<id>/documents` | document_upload (list banking docs) |
| DELETE | `/banking-details/<id>/documents/<doc_id>` | document_upload |
| PUT | `/banking-docs/<id>/reupload` | document_upload (citizen replaces banking doc) |
| GET | `/banking-details/document-types` | document_upload |
| PUT | `/upload-docs/<app_type>/<app_id>` | document_upload (legacy app-doc upload) |

**Banking-doc file storage:** `/Data_Repository/BankingDocs/<user>/<banking_details_id>/<file>` — **sibling** of `online-claims-applications/`. Critical detail — admin reads via `ApplicationFileUploadsService.base_path_for(document_type)` and a misconfig will route to the wrong base path.

**Notes:**

- Uses `BaseService[T]` / `BaseRepository[T, DTO]` generic abstracts (richer base classes than the other Flask services).
- Validation framework: `@validate_path_params`, `@validate_json_request`, `@validate_form_request` decorators.
- NIB number pattern: `^[A-Z0-9]{8,15}$`.
- Profile changes trigger `UserAccountAlertsService.send_account_updated_alert()` → email via `nib-email-service`.

---

## 3. `online-claims-submission-api` → `nibitdev/online-claims`

**One-liner:** Citizen-facing claims submission API. 7 benefit types: Unemployment, Sickness, Maternity (+ extension), Funeral, Injury, Retirement, Surviving Spouse.

| Concern | Detail |
|---|---|
| Network | `NIB-ONLINE` **and** `NIB-ONLINE-ADMIN` (cross-portal bridge) |
| Stack | Flask 2.2 + SQLAlchemy 2.0 + oracledb + Gunicorn (gevent, 4 workers, 120s timeout) |
| Internal port | 5000 |
| Public route | `/api/online-claims/*` (proxied) |
| Schema (prod) | `online_claims` |
| Reads | `client`, `demographic_service`, `nib_admin_auth` |
| Critical volume | `online-claims-applications:/app/uploads` (shared with admin-claims-admin) |
| Mem limit | 1024m (raised from 200m after F12 OOM) |
| Email API | `http://nib-email-service:5000` (prod) / `https://staging-customer-email-api.nib-bahamas.com` (staging) |
| AdminService URL | Docker DNS to admin-claims-admin container (cross-network) |
| Sentry | **Sophisticated** — `src/observability/` with PII scrubbing, integrations, context processors |

**Verified endpoints (from `src/**/*_controller.py`):**

| Method | Path | Module |
|---|---|---|
| GET | `/application` | applications.index |
| GET | `/application/<app_id>/<benefit_type>` | applications.index |
| GET | `/application/types` | applications.index |
| GET | `/application/payment-type` | applications.index |
| GET | `/application/validators/<app_type>` | applications.index |
| POST | `/application/sickness` | applications.sickness |
| GET | `/application/sickness` | applications.sickness |
| POST | `/application/unemployment` | applications.unemployment |
| GET | `/application/unemployment/eligibility` | applications.unemployment |
| POST | `/application/maternity` | applications.maternity |
| GET | `/application/maternity/claims` | applications.maternity |
| POST | `/application/maternity/extend` | applications.maternity_extension |
| POST | `/application/funeral` | applications.funeral |
| POST | `/application/funeral/validation` | applications.funeral |
| GET | `/application/funeral/beneficiary-type` | applications.funeral |
| POST | `/application/injury` | applications.injury |
| GET | `/application/injury/types` | applications.injury |
| POST | `/application/retirement` | applications.retirement |
| GET | `/application/retirement/date-types` | applications.retirement |
| GET | `/application/retirement/effective-dates` | applications.retirement |
| GET | `/application/<benefit_type>/documents` | application_documents |
| PATCH | `/application-docs/banking-doc-updated` | application_documents |
| PUT | `/upload-docs/<app_type>/<app_id>` | document_upload |
| GET | `/pending-app/<id>` | applications.pending |
| GET | `/pending-apps` | applications.pending |
| POST | `/pending-app` | applications.pending |
| PUT | `/pending-app/<id>` | applications.pending |
| DELETE | `/pending-app/<id>` | applications.pending |
| PUT/POST | `/pending-app/<id>/files` | applications.pending |
| GET | `/benefits` | benefits |
| GET | `/benefits-types` | benefits |
| GET | `/api/v1/benefit-config/<claim_type>` | benefit_config |
| GET | `/benefit/<app_id>/payments` | benefits_payments |
| GET | `/banking-details`, POST, PUT/DELETE variants | banking_details |
| GET | `/claimant-address`, `/claimant-contact` (mirrors of demographic, lots of dup) | claimant_address / claimant_contact |
| GET | `/user/<eeni>`, `/person/<eeni>` | user / person |
| GET | `/local-offices`, `/bank-branches`, `/funeral-homes`, `/third-party-institutions` | reference data |
| GET/POST | `/user/local-office` | user_local_office |

**Cross-portal call (the bridge):** customer-claims calls admin-claims-admin via `AdminService.root_url` (Docker DNS). Three specific call sites:

- `src/application_assignment/application_assignment_service.py` → `GET {admin}/application/<id>/assignment/active` (5s timeout, `verify=False`)
- `src/reupload_request/reupload_request_service.py` → `GET {admin}/file/request/<file_upload_id>` (5s timeout)
- `src/reupload_request/reupload_request_service.py` → `PUT {admin}/file/request/<file_upload_id>` (5s timeout)

All three forward the customer's JWT via `g.token` — admin side must accept it (JWT secrets shared across portal boundary for these calls — see `02-ARCHITECTURE.md` §5).

**File storage:**

- Submitted: `/Data_Repository/online-claims-applications/Submitted/<user>/<type>/<app_id>/<file>`
- Pending: `/Data_Repository/online-claims-applications/Pending/<user>/<app_id>/<file>`
- `FileRepo.path` MUST be absolute — relative paths historically caused CWD-dependent resolution bugs (cf. memory `bug-b2`).

**Known bug at `src/document_upload/document_upload_service.py:280`** — `.replace(self.sub_file_path, "")` is missing trailing `os.sep`, leaving leading `/` in `application_docs.file_path`. Corrupted 8 rows on `.139` in May 2026 (DB-fixed; code fix deferred).

**Notes:**

- Has the canonical, most-recently-updated repo `CLAUDE.md` (~400 lines). Read that for module-by-module detail.
- Read the global error handlers in `app.py` — they're the source for the SQLAlchemy-pool-poisoning fix (memory `pool-cascade-broken-handler-pattern`).

---

## 4. `online-cards-api` → `nibitdev/online-cards`

**One-liner:** Citizen-facing NIB card applications: new card, renewal, replacement.

| Concern | Detail |
|---|---|
| Network | `NIB-ONLINE` |
| Stack | Flask 2.2.3 + SQLAlchemy 2.0.5 + oracledb + Gunicorn/gevent |
| Internal port | 5000 |
| **API prefix** | `/api/cards` (routes ALL use `API_PREFIX + ...`) |
| Schema (prod) | `online_nib_cards` |
| Reads | `client`, `demographic_service`, `nib_admin_auth`, `online_nib_cards_admin` |
| Volume | `online-card-applications:/app/uploads` |
| Mem limit | 1024m (raised symmetric to claims after F14) |
| Email API | `http://nib-email-service:5000` (prod) / `jumvmapdevsrv01:3006` (staging — note divergence) |
| Sentry | **Sophisticated** — `src/observability/` |

**Verified endpoints (all under `/api/cards` prefix):**

| Method | Path | Module |
|---|---|---|
| GET | `/api/cards/application` | application |
| POST | `/api/cards/application` | application |
| GET | `/api/cards/application/<id>` | application |
| PUT | `/api/cards/application/<id>/files` | application |
| DELETE | `/api/cards/application/<id>` | application |
| POST | `/api/cards/application/applicant` | application |
| GET | `/api/cards/documents` | application_documents |
| GET | `/api/cards/pending/application` | pending_applications |
| POST | `/api/cards/pending/application` | pending_applications |
| GET/PUT/DELETE | `/api/cards/pending/application/<id>` | pending_applications |
| POST/PUT | `/api/cards/pending/application/<id>/files` | pending_applications |
| GET | `/api/cards/file/request/reasons` | reupload_request |
| GET | `/api/cards/person/<nib_number>` | person |
| GET | `/api/cards/status` | status |
| GET | `/api/cards/user` | user |

**Reads `online_nib_cards_admin.reupload_request`** — see `src/reupload_request/reupload_request_model.py:6`. The customer-cards service reads the admin-side reupload requests table via cross-schema autoload. There is no HTTP call to admin-cards-admin; the integration is DB-only.

**File storage:** `/Data_Repository/online-card-applications/Submitted/<user>/<type>/<app_id>/<file>`

**Notes:**

- F7 launch incident: `--worker-class` Gunicorn flag was malformed and fell back to sync workers. Fixed.
- F14 OOM: mem_limit raised 200m→1024m after photo uploads stressed memory.

---

## 5. `online-claims-submissions-frontend` → `nibitdev/online-portal-frontend`

**One-liner:** Customer-facing Vue 3 SPA. The thing citizens actually see.

| Concern | Detail |
|---|---|
| Network | `NIB-ONLINE` |
| Stack | Vue 3.2 + TypeScript + Vite + TailwindCSS + Axios + Vuelidate + Pinia |
| Production server | nginx 1.15-alpine |
| Public ports | 80, 443 + 5000-5004 (5000-5004 proxy backend) |
| Container | `online-portal-frontend` |
| Image tag in production | `:claims` (legacy holdover) |
| Sentry | **Comprehensive** (browser tracing + replay + PII regex scrubbing) |

**`src/` layout (verified):**

```
src/
├── App.vue, main.ts, shims-vue.d.ts
├── assets/
├── components/
├── composables/
├── enums/
├── formatters/
├── plugins/             # axios.ts, sentry.ts, validation.ts
├── router/
├── services/            # one file per backend service (API clients)
├── store/               # Pinia stores
├── types/
├── utils/
└── views/               # page-level components
```

**Build-time env vars (baked into bundle by Vite):**

```
VITE_API_URL                  # → online-claims-submission-api
VITE_USER_SERVICE_URL         # → nib_user_service
VITE_CARD_SERVICE_URL         # → online-cards-api (includes /api/cards prefix)
VITE_DEMOGRAPHIC_SERVICE_URL  # → demographic-service (singular, no 's')
VITE_SENTRY_DSN
VITE_APP_ENV
```

**Axios baseURL:** `VITE_API_URL` (the claims service is the "default" backend). All non-claims requests use explicit per-service Axios clients in `src/services/*.ts`.

**Notes:**

- Production image tag is `:claims` (legacy from rebrand). The image is bit-identical to what should be `:preprod` — see memory `launch-image-provenance`.
- Tag-drift gotcha: Jenkins builds `:claims` but staging compose pinned `:preprod` for ~2 months. Always cross-check.
- Sentry replay sampling was set to `0.0` post-May-2026 to stop quota burn.
- **MSYS path-mangling** is a real footgun on Windows local builds — set `MSYS_NO_PATHCONV=1` (see workspace `CLAUDE.md`).

---

# Admin Portal

## 6. `admin-auth` → `nibitdev/admin-auth`

**One-liner:** Staff authentication via LDAP + role enrichment from Oracle + JWT issuance.

| Concern | Detail |
|---|---|
| Network | `NIB-ONLINE-ADMIN` |
| Stack | Flask + ldap3 + flask-jwt-extended + Pycryptodome |
| Internal port | 5000 |
| Public route | `/api/admin-auth/*` |
| Schema (prod) | `admin_auth_preprod` ⚠️ (drift; task #45) |
| **Redis** | **None** (anomaly — only admin service without rate limiting) |
| Sentry | None until 2026; added in task #14 |
| Dockerfile entry | `bash -c ./start_up.sh` → runs `flask db upgrade head` then gunicorn |

**Verified endpoints:**

| Method | Path |
|---|---|
| POST | `/auth/login` |
| GET | `/user/info` |
| GET | `/user` |
| GET | `/user/<user_id>/role` |

That's it — 4 routes. Smallest service surface in the platform.

**Notes:**

- LDAP only validates the password. **Roles come from `dbo.security_role_user`** in Oracle, not from LDAP groups. The service issues a JWT whose `identity` is the user-role dict.
- Admin write-access roles: `SUPERVISOR R`, `DEPARTMENT HEAD R`, `MANAGER FIU`, `SUB OFFICE MANAGER FIU` — must be kept in sync with frontend `useCards.ts` / `useClaims.ts` `canEdit` lists.
- Config classes: `OracleDB`, `JWTConfig`, `Flask`, `FileRepo`, `Credentials`, `LDAPServer`, `Sentry`. **No `RedisDB`, no `RateLimiter`.**
- Token creation site: `src/auth/auth_service.py:47`.

---

## 7. `online-cards-admin-api` → `nibitdev/online-cards-admin`

**One-liner:** Admin-side card application review, approval, document download, reupload request.

| Concern | Detail |
|---|---|
| Network | `NIB-ONLINE-ADMIN` |
| Stack | Flask 2.2.3 + SQLAlchemy 2.0.7 + WeasyPrint 54.0 + ldap3 |
| Internal port | 5000 |
| Public route | `/api/cards-admin/*` |
| Schema (prod) | `online_nib_cards_admin_preprod` ⚠️ |
| Reads | `client`, `nib_admin_auth`, `online_nib_cards` (customer cards tables), `demographic_service` |
| Shared volume | `customer-portal_online-card-applications:/app/uploads` |
| Email API | `http://admin-email:5000` (Docker DNS — DIFFERENT name from customer-side `nib-email-service`) |
| Sentry | Added in task #14 (env-based sampling: 0% dev, 10% staging, 100% prod) |
| MinIO | Configured but **not actively used** for storage |

**Verified endpoints:**

| Method | Path | Module |
|---|---|---|
| GET | `/dashboard/statistics` | dashboard |
| GET | `/application` | application |
| GET | `/application/<id>` | application |
| POST | `/application/<id>/file/<upload_file_id>/request` | application (reupload one file) |
| POST | `/application/<id>/file/request` | application (reupload all) |
| PUT | `/application/<id>/approval` | application |
| PUT | `/application/<id>/denial` | application |
| GET | `/application/denial/reasons` | application |
| PUT | `/application/<id>/ready` | application (ready for pickup) |
| GET | `/application/file/<path:file_name>` | application (download) |
| PUT | `/application/<id>/local-office` | application (reassign office) |
| GET | `/application/<id>/activity-logs` | application |
| POST | `/application/<id>/r4` | application |
| POST | `/application/<id>/assignment` | application_assignment |
| POST | `/application/<id>/reassignment` | application_assignment |
| PUT | `/application/<id>/assignment/inactive` | application_assignment |
| GET | `/user` | user |
| GET | `/file/request/reasons` | reupload_request |

**Custom decorators (`src/nib_user/decorators/`):** `@admin_required`, `@user_required`, `@read_only`.

**Activity logging** via Builder Pattern (`src/activity_logger/activity_builder.py`) — every significant action is logged with searchable criteria DTO.

**Email Factory** (`src/email/email_factory.py`) — dynamically loads templates per `EmailTemplates` enum.

---

## 8. `online-claims-administrative-api` → `nibitdev/online-claims-admin`

**One-liner:** Admin-side claims review. The densest admin service. 7 claim types + form generation + reupload + assignment.

| Concern | Detail |
|---|---|
| Network | `NIB-ONLINE-ADMIN` |
| Stack | Flask 2.2.3 + SQLAlchemy 2.0.7 + WeasyPrint + Pydantic 2.10.5 |
| Internal port | 5000 |
| Public route | `/api/claims-admin/*` |
| Schema (prod) | `online_claims_admin` (clean, no preprod suffix) |
| Reads | `client`, `nib_admin_auth`, `online_claims` (customer claims), `demographic_service` |
| Shared volume | `customer-portal_online-claims-applications:/app/uploads` |
| Email API | `http://admin-email:5000` |
| Sentry | Added in task #14 |
| Validation framework | **Pydantic 2.10.5** — `BaseValidationSchema` (extra="forbid") + `@validate_json(Schema)` decorator |

**Verified endpoints:**

| Method | Path | Module |
|---|---|---|
| GET | `/dashboard/statistics` | dashboard |
| GET | `/application` | applications.index |
| GET | `/application/<id>/<benefit_type>` | applications.index |
| GET | `/application/types` | applications.index |
| GET | `/application/status` | applications.index |
| POST | `/application/<id>/file/request` | applications.index (reupload request) |
| PUT | `/application/<id>/approval` | applications.index |
| PUT | `/application/<id>/denial` | applications.index |
| GET | `/application/denial/reasons` | applications.index |
| GET | `/application/file/<file_upload_id>` | applications.index (download by DB id — path-traversal-safe) |
| PUT | `/application/<id>/local-office` | applications.index |
| GET | `/application/<id>/activity-logs` | applications.index |
| POST | `/application/<id>/<benefit_type>/form` | applications.index (generate PDF form) |
| GET | `/application/form-types` | applications.index |
| GET | `/application/<benefit_type>/documents` | application_documents |
| POST | `/application/<id>/assignment` | application_assignment |
| POST | `/application/<id>/reassignment` | application_assignment |
| PUT | `/application/<id>/assignment/inactive` | application_assignment |
| GET | `/application/<id>/assignment/active` | application_assignment (← called cross-portal by customer-claims) |
| GET | `/file/request/<file_upload_id>` | reupload_request (← called cross-portal by customer-claims) |
| PUT | `/file/request/<file_upload_id>` | reupload_request (← called cross-portal by customer-claims) |
| DELETE | `/file/request/<file_upload_id>` | reupload_request |
| GET | `/file/request/reasons` | reupload_request |

**Application factory** (`src/applications/index/application_factory.py`) — maps benefit type strings to service handlers (Funeral, Sickness, Maternity, Unemployment, Injury, Retirement + extensions).

**File handling:** `ApplicationFileUploadsService.base_path_for(document_type)` resolves to one of:
- `/Data_Repository/online-claims-applications/` (claim doc)
- `/Data_Repository/BankingDocs/` (banking doc — sibling, not subpath)

Banking-doc base path was added in commit `f658ddc`.

**Form templates:** `src/application_templates/form_templates/*.html` — Jinja2 rendered with WeasyPrint to PDF. Forms include B80, B81, etc. Templates use `{% if last_employer %}...{% else %}<em>See attached B80...</em>{% endif %}` patterns for optional fields (per Adena's policy).

**Recent security:** path-traversal fixed via DB-id-based download (`/file/<file_upload_id>` not `/file/<path>`). `validate_safe_file_path()` enforces.

**Known open issues:** `SECURITY_FIXES_REQUIRED.md` in repo lists 19 priorities including hardcoded secrets, SSL `verify=False` on email calls, missing CORS origin allowlist.

---

## 9. `online-submissions-admin-frontend` → `nibitdev/online-portal-admin-frontend`

**One-liner:** Vue 3 admin SPA. Different audience, similar stack.

| Concern | Detail |
|---|---|
| Network | `NIB-ONLINE-ADMIN` |
| Stack | Vue 3.2 + TypeScript + Vite + TailwindCSS |
| Production server | nginx 1.15-alpine |
| Public ports | 8080, 9000-9005 |
| Healthcheck | `GET /login` returns 200 |
| Sentry | None |

**`src/` layout (verified):**

```
src/
├── App.vue, main.ts, env.d.ts
├── assets/
├── components/
├── composables/         # useCards.ts, useClaims.ts, useDownload.ts, useAssignment.ts
├── enums/
├── pages/               # page-level components (note: pages/, NOT views/)
├── plugins/
├── router/
├── store/
├── styles/
├── types/
└── utils/
```

**Build-time env vars (`.env.example`):**

```
VITE_API_URL                  # → online-claims-administrative-api
VITE_ADMIN_AUTH_SERVICE       # → admin-auth
VITE_CARD_SERVICE_URL         # → online-cards-admin-api
# Plus VITE_EMAIL_URL, VITE_MINIO_URL
```

**Notes:**

- Several open tasks: routed-to search broken (#56), claims filter shortcuts broken (#57), dark mode white panels (#60).
- `.env.example` historically hardcoded IPs (`http://172.16.1.172:3xxx`) — must rebuild with env-specific URLs for any other environment.
- Has `DOCKER_IMPROVEMENTS.md`, `IMPROVEMENTS_SUMMARY.md`, `SECURITY.md`, `QUICK_START.md` in repo (historical change logs).

---

# Shared Services

## 10. `nib-email-service` → `nibitdev/email-service`

**One-liner:** Single email relay used by both portals AND the NIB Query Tool. **Uses RabbitMQ for async delivery.**

| Concern | Detail |
|---|---|
| Network | Both portals + `NIB-QUERY-TOOL` (lives on all three) |
| Stack | Flask 2.2 + pika 1.3.2 (RabbitMQ) + SQLAlchemy + WeasyPrint + Jinja2 |
| Internal port | 5000 (Gunicorn) / 3006 (legacy via wfastcgi.py for IIS) |
| Container name (customer compose) | `nib-email-service` |
| Container name (admin compose) | `admin-email` (different — note for cross-service config) |
| Schema (prod) | `nib_email_service_preprod` ⚠️ |
| Auth | **API key** (X-API-Key header) — NOT JWT |
| RabbitMQ | `preprod-rabbitmq:5672` (prod) / `queueservice:5672` (staging) |

**Verified endpoints:**

| Method | Path | Auth |
|---|---|---|
| POST | `/email` | API key |
| POST | `/templates` | API key |
| GET | `/templates` | API key |
| GET | `/templates/<id>` | API key |
| POST | `/api-key` | None |
| PUT | `/api-key` | None (regenerate) |
| DELETE | `/api-key` | None (revoke) |
| GET | `/api-key` | None |

**Flow:**

```
1. Client service POST /email with X-API-Key
2. Email service validates key, saves email_request row to DB
3. Publishes request to RabbitMQ ("Email Queue" / "NIB QUEUE EXCHANGE")
4. email-service-background-job (separate container) consumes queue, hits SMTP
5. Updates email_request.sent_at / retry_count
```

**Registered application names (API key consumers):**

- `ONLINE_CARDS`, `ONLINE_CARDS_ADMIN`, `ONLINE_CLAIMS`, `ONLINE_CLAIMS_ADMIN`, `USER_SERVICE`, `DEMOGRAPHICS_SERVICE`

Each consumer's `config.py` declares `app_name` and references the email API URL via `NIBEmailService.root_url`.

**Template ID mappings (from CLAUDE.md, table in DB):**

| ID | Name | User |
|---|---|---|
| 1 | Account Activation | user-service |
| 2 | Password Reset | user-service |
| 3 | Email Change | user-service |
| 4 | Claims Confirmation | claims-service |
| 5 | Card Application | cards-service |
| 6 | Reupload Request | cards-admin |
| 7 | Profile Updated | demographic |
| 8 | Application Approved | claims-admin |
| 9 | Application Denied | claims-admin |
| 97 | OHSU Injury Benefit Submitted | claims-service (added 2026-05-15) |

**Notes:**

- API key regeneration: `ApiKeyService().regenerate_api_key('ONLINE_CLAIMS_ADMIN')` — required if a config rotates the key. See memory `staging-email-config-fix-pattern`.
- Different DNS names per portal: `nib-email-service` for customer, `admin-email` for admin — both same image, both in same Sentry project.

---

## 11. `nib-user-service-v2`

**One-liner:** FastAPI replacement for the legacy customer user service. Partial production traffic.

| Concern | Detail |
|---|---|
| Stack | **FastAPI** + uvicorn + SQLAlchemy 2.0 async + Oracle |
| Internal port | 5000 |
| Routing | Mounted at `/api/auth` prefix |
| Deployment | Has Jenkinsfile but currently manual deploy |
| Sentry | Added in task #13 |
| Open task | #28 (migrate off `lionels@` Oracle creds), #77 (rebuild via Jenkins properly) |

**Critical implementation detail** (`app.py:39-48`): forces `loop="asyncio"` instead of uvloop. uvloop's TCP transport marks connections closed before SQLAlchemy's pool reset-on-return rollback can fire, surfacing as `RuntimeError("TCPTransport closed=True")` and 500s. F6 launch blocker; fixed before launch.

---

# Background Jobs

All 4 jobs share the skeleton: APScheduler, touch `/app/last_run` per tick for healthcheck, `PYTHONUNBUFFERED=1` mandatory.

---

## 12. `email-service-background-job` → `nibitdev/email-service-bg`

| Concern | Detail |
|---|---|
| Network | `NIB-QUERY-TOOL` (reaches RabbitMQ) |
| Schedule | Every 60s (healthcheck = `last_run` within 60s) |
| Schema (prod) | `nib_email_service_preprod` |
| RabbitMQ host | `preprod-rabbitmq:5672` (prod) / `queueservice:5672` (staging) |
| Volume | `../shared-services/email-service/templates:/app/email-templates` |
| Sentry | Basic (task #16) |

**Flow:** consume RabbitMQ `Email Queue` → render Jinja2 template → SMTP → UPDATE `email_request.sent_at` / retry.

---

## 13. `users-refresh-job` → `nibitdev/user-refresh-job`

| Concern | Detail |
|---|---|
| Schedule | Daily (cron, 24h healthcheck) |
| Schema (prod) | `admin_auth_preprod` |
| Sentry | Basic |

**Flow:** compare `dbo.person` snapshot with `CREATED_CLIENT.users` (or equivalent — actual schema usage TBD via deeper inspection); apply additions/updates; date-of-death triggers deactivation.

**Minimal local src tree** — most logic lives in `app.py` and a single `src/__init__.py`.

---

## 14. `online-claims-submission-pending-app-removal` → `nibitdev/claims-pending-app-bg`

| Concern | Detail |
|---|---|
| Schedule | Daily midnight |
| Schema (prod) | `online_claims` |
| Reads | `client`, `demographic_service` |
| Email API | `http://nib-email-service:5000` |

**Flow:** SELECT `pending_applications` where `created_date < SYSDATE - 30 AND status = 'PENDING'` → delete uploaded files from `/Data_Repository/online-claims-applications/Pending/` → delete `application_docs` and `pending_applications` rows → email citizen.

**Rich src tree** — replicates application/banking/contacts/etc models because it needs to JOIN across the customer-claims domain.

---

## 15. `online-cards-expired-pending-app-background-job` → `nibitdev/cards-background-job`

| Concern | Detail |
|---|---|
| Schedule | Daily |
| Schema | `online_nib_cards` (config is env-var driven; defaults point at **prod** Oracle on `.123` staging too — flag for review) |
| Reads | `client`, `demographic_service`, `nib_admin_auth`, `online_nib_cards_admin` |

**Same cleanup pattern as claims-pending-removal.** Also has rich src tree replicating the customer-cards domain models.

> Heads-up: this job's `config.py` uses `os.getenv("DB_HOST", "jumv3prddb-scan.nib-bahamas.com")` — defaulting to prod Oracle. If env vars aren't set on staging, the job points at prod data. Worth verifying compose env passes the right values.

---

# Utilities

## 16. `audit-user-service`

**One-liner:** Internal CSV-driven tool for bulk operations (audit, date-of-death updates).

Stack: Flask used as CLI. Has `FACTORY_IMPLEMENTATION.md` documenting its factory pattern.

Not deployed as a long-running service. Used ad-hoc by ops.

---

## 17. `development-documentation`

Cross-team developer documentation predating `nib-online-docs/`. Loose grab-bag — runbooks, architecture notes. Not deployed.

---

# Deployment / CI/CD

## 18. `deploy-nib-online`

**The orchestration source of truth.** Docker Compose, config generation, monitoring stack.

```
deploy-nib-online/
├── customer-portal/
│   ├── compose.yml                     # default (staging)
│   └── compose.preprod-backend.yml     # prod .139 overrides
├── admin-portal/
│   ├── compose.yml
│   ├── compose.preprod.yml             # prod .139
│   └── compose.preprod-dashboard.yml
├── background-job/
│   ├── compose.yml
│   └── compose.preprod.yml
├── shared-services/
│   ├── shared-services.yml             # email-service + redis base
│   └── email-service/templates/        # Jinja2 templates (shared)
├── config-templates/                    # env-templated config.py + .env
├── generated-configs/preprod/           # rendered configs deployed to .139
├── monitoring/                          # Loki + Promtail + Grafana
├── certs/                               # wildcard *.nib-bahamas.com
├── generate-configs.sh                  # template renderer
└── scripts/                             # deploy helpers
```

**Tag swaps per environment:**

- Staging compose: `:staging` tags (customer frontend pinned at `:claims`)
- Prod `.139` compose.preprod-*.yml: `:preprod` tags
- Legacy `.117` compose: `:prod` tags

**Config generation:** `./generate-configs.sh preprod` renders `config-templates/preprod/*` → `generated-configs/preprod/*.config.py`, SCP'd to `.139:~/deploy-nib-online/generated-configs/preprod/`, bind-mounted into containers via `compose.preprod-*.yml`.

**Prod `.139` bind-mount pattern** (from `compose.preprod-backend.yml`):

```yaml
volumes:
  - ../generated-configs/preprod/demographic-service.config.py:/app/config.py:ro
  - ../generated-configs/preprod/online-claims.config.py:/app/config.py:ro
  - ../generated-configs/preprod/online-cards.config.py:/app/config.py:ro
```

Configs are RO bind-mounts — services cannot mutate their own config.

---

## 19. `deployments-jenkins`

Jenkins pipelines for everything.

```
deployments-jenkins/
└── nib-online-portal/
    ├── customer-portal/<service>/Jenkinsfile     # :prod   ← master   → .117 (legacy)
    ├── preprod/customer-portal/<service>/Jenkinsfile  # :preprod ← staging → .139 (LIVE)
    ├── preprod/admin-portal/<service>/Jenkinsfile
    └── background-job/<job>/Jenkinsfile
```

**Branch convention:**

- `:prod` ← `master` branch ← target `.117`
- `:preprod` ← `staging` branch ← target `.139` (LIVE)
- `:staging` ← service repo's own `Jenkinsfile` ← target `.123`

Known **stale-container-id bug**: pipelines bail with "No such container" / "removal in progress" at deploy step. Workaround: manual `docker compose up -d` on host.

---

## 20. `deploy-background-job`

Placeholder (one README). Job orchestration lives in `deploy-nib-online/background-job/`. Effectively retired.

---

# Cross-Cutting Reference

## Verified service-to-service URLs (prod)

| Caller | Callee | URL | Mechanism |
|---|---|---|---|
| demographic | email | `http://nib-email-service:5000` | Docker DNS |
| online-claims | email | `http://nib-email-service:5000` | Docker DNS |
| online-claims | claims-admin (CROSS-PORTAL) | Docker DNS to admin container | network bridge |
| online-cards | email | `http://nib-email-service:5000` | Docker DNS |
| online-cards | (cards-admin) | NO HTTP — reads `online_nib_cards_admin` schema directly | DB |
| cards-admin | email | `http://admin-email:5000` | Docker DNS |
| claims-admin | email | `http://admin-email:5000` | Docker DNS |
| claims-pending-bg | email | `http://nib-email-service:5000` | Docker DNS |
| cards-pending-bg | email | `http://nib-email-service:5000` | Docker DNS |
| user-refresh | — | None | — |
| email-service | RabbitMQ | `preprod-rabbitmq:5672` | Docker DNS |
| email-bg | RabbitMQ | `preprod-rabbitmq:5672` | Docker DNS |

> Internal calls use Docker DNS, not the public LB hostname. `verify=False` on cross-service HTTPS is intentional — internal traffic stays inside the Docker network.

## Sentry coverage (verified)

| Service | Level |
|---|---|
| online-claims-submission-api | **Sophisticated** (PII scrubbing, integrations, context processors) |
| online-cards-api | **Sophisticated** (same pattern) |
| online-claims-submissions-frontend | **Comprehensive** (browser tracing + replay + regex PII) |
| demographic-service | Basic (DSN init, error sampling) |
| nib-email-service | Basic |
| email-service-background-job | Basic |
| users-refresh-job | Basic |
| admin-auth | Added 2026 (task #14) — env-based sampling |
| online-cards-admin-api | Added 2026 (task #14) |
| online-claims-administrative-api | Added 2026 (task #14) |
| nib-user-service-v2 | Added 2026 (task #13) |
| nib_user_service | **None** (gap) |
| online-submissions-admin-frontend | **None** (gap) |
| claims-pending-bg | Added 2026 (task #16) |
| cards-pending-bg | Added 2026 (task #16) |

## Redis usage (verified)

| Service | Redis container | Rate limit pattern |
|---|---|---|
| demographic-service | customer-redis | Modern (Redis-backed Flask-Limiter) |
| online-claims-submission-api | customer-redis | Modern |
| online-cards-api | customer-redis | Modern |
| nib-email-service (customer) | customer-redis | Modern |
| online-claims-admin | admin-redis | Modern |
| online-cards-admin | admin-redis | Modern |
| nib-email-service (admin) | admin-redis | Modern |
| nib_user_service | None | In-memory (legacy) |
| admin-auth | **None** | No rate limiting at all |
| All bg jobs | None | N/A |

## How to read code in a new service (5-minute orientation)

1. Open `app.py` — WSGI entry + global error handlers
2. Open `src/__init__.py` — Flask init, config loads, auto-discovery glob
3. Open `config.py.example` (if local repo) or live config from server (see below)
4. Open `requirements.txt` for actual versions
5. List `src/` — each subdir is a feature module (controller/service/repo trio)
6. Open one feature's `*_controller.py` — endpoint shapes
7. Open its `*_service.py` — business logic
8. Open its `*_repo.py` — DB queries
9. Open repo `CLAUDE.md` if present — usually current and authoritative

## How to verify a config on the live server

```bash
# Staging (.123)
ssh devadmin@192.168.100.123 \
  cat ~/projects/deploy-nib-online/<customer-portal|admin-portal>/backend/<service>/config.py

# Prod (.139, via jump host)
ssh -J querytool-prod devadmin@preprod-backend \
  cat ~/deploy-nib-online/generated-configs/preprod/<service>.config.py
```

(Prod configs live in `generated-configs/preprod/`, NOT under `backend/`. They're bind-mounted into containers via `compose.preprod-*.yml`.)

---

**Done. Next: review the `nib-online-docs/reference/` directory for older but useful detail (architecture.md, service-dependencies.md, NIB_Online_Service_Configuration_Reference.md, NIB_Online_Cohesiveness_Analysis.md).**
