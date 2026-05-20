# NIB Online Portal — Developer Onboarding

This directory contains the three onboarding documents for new developers (and AI assistants) joining the NIB Online Portal project. They are designed to be read in order.

## Reading Order

### For developers / AI assistants (technical onboarding)

1. **[`01-EXECUTIVE-OVERVIEW.md`](./01-EXECUTIVE-OVERVIEW.md)** — what the system is, who it serves, operational status, key risks. **Start here.** ~10 minutes.
2. **[`02-ARCHITECTURE.md`](./02-ARCHITECTURE.md)** — how the apps work together: networks, request lifecycles, auth, data stores, deployment topology, patterns to recognize. ~30 minutes.
3. **[`03-SERVICES.md`](./03-SERVICES.md)** — per-service deep dive. Reference doc; skim once, return as needed. ~30 minutes to skim.
4. **[`04-DEPLOYMENT.md`](./04-DEPLOYMENT.md)** — DevOps: server inventory, replica counts, network names per environment, CI/CD, configs, monitoring, backups, sync. Operational manual. ~30 minutes.

### For end users (citizens and NIB staff)

5. **[`05-CITIZEN-GUIDE.md`](./05-CITIZEN-GUIDE.md)** — how Bahamian citizens use the customer portal: register, submit claims, apply for cards, respond to reupload requests, manage banking details. With screenshots from staging. ~15 minutes.
6. **[`06-ADMIN-GUIDE.md`](./06-ADMIN-GUIDE.md)** — how NIB staff process applications: queue, detail review, reupload requests, approve/deny, form generation, plus the **authoritative role reference** (5 categories, 15 roles, canEdit matrix). ~25 minutes.

## How These Docs Are Used

- **For humans** — read in order. Each doc builds on the previous one. After reading all three, you'll know enough to clone the repos, find the right place to make a change, and understand the deployment path.
- **For AI assistants (e.g. Claude Code)** — load `02-ARCHITECTURE.md` and `03-SERVICES.md` as context for code-related questions. `01-EXECUTIVE-OVERVIEW.md` is helpful for setting the business framing on a new conversation.

## Branch Policy (Important)

These docs reference the **`master`** branch of each repo as the canonical baseline for the new developer to read. **But:**

- Live production runs the `:preprod` image tags, which are built from the **`staging`** branch.
- The `master` branch is the legacy lane for the `.117` server (being decommissioned).
- **New work should branch from `staging`, not `master`.**

Why we still point new readers at `master`: it's the stable, well-aged baseline. It's not where new work happens, but it's the right place to learn the codebase before adapting to active-development on `staging`.

See `02-ARCHITECTURE.md` §11 and §14 for the full branching policy.

## When to Update These Docs

- **Topology changes** (new service, new portal, new network) → update `02-ARCHITECTURE.md` §2-3 AND `04-DEPLOYMENT.md` §2-3
- **New service or major service refactor** → update or add an entry in `03-SERVICES.md`
- **New environment or server cutover** → update `01-EXECUTIVE-OVERVIEW.md` operational status, `02-ARCHITECTURE.md` §11, AND `04-DEPLOYMENT.md` §1
- **New deployment policy / branching change** → update `02-ARCHITECTURE.md` §11 + §14, `04-DEPLOYMENT.md` §7, and this README
- **Schema names change** (task #45 — `_preprod` suffix removal) → update `02-ARCHITECTURE.md` §6.1 + `03-SERVICES.md` schema map
- **Replica counts change** (scaling) → update `04-DEPLOYMENT.md` §3
- **Jenkins upgrade / replacement** → update `04-DEPLOYMENT.md` §7
- **SPA redesign / new UI screens** → re-run Playwright capture specs and refresh screenshots in `05-CITIZEN-GUIDE.md` / `06-ADMIN-GUIDE.md`
- **New role added to `user-roles.enums.ts` or `canEdit` change** → update the role matrix in `06-ADMIN-GUIDE.md` §7

## Refreshing Screenshots

The two user guides embed screenshots captured by Playwright against staging:

```bash
cd e2e

# Customer/citizen captures (creds already in .env)
npx playwright test specs/customer/screenshots/citizen-walkthrough.spec.ts --project=customer-portal

# Admin captures (requires TEST_ADMIN_PASSWORD in .env)
npx playwright test specs/admin/screenshots/admin-walkthrough.spec.ts --project=admin-portal
```

Screenshots land in `development-documentation/onboarding/images/citizen/` and `.../images/admin/`. They overwrite the existing files in place, so the markdown references stay stable.

## Related Documentation

- **Workspace root `CLAUDE.md`** — quick-reference tables (image tags, ports, branch→tag→server flows). The canonical "cheat sheet."
- **Each repo's own `CLAUDE.md`** — service-specific patterns and conventions. Read after the onboarding docs. Present in: `demographic-service`, `online-claims-submission-api`, `online-cards-api`, `online-cards-admin-api`, `online-claims-administrative-api`, `nib-email-service`. Not present (gap): `nib_user_service`, `admin-auth`, both frontends, `nib-user-service-v2`, all bg jobs.
- **`development-documentation/` repo** — older cross-team developer notes (predates these onboarding docs).

### Pre-existing reference docs in `nib-online-docs/reference/`

These were authored Feb-2026 and may have point-in-time staleness, but contain useful detail not duplicated here. Cross-reference rather than re-read in full:

| File | What it has that's still useful |
|---|---|
| `architecture.md` | Layered topology diagram; deployment pipeline diagram |
| `service-dependencies.md` | Service-startup-order checklist for `docker compose up` |
| `NIB_Online_Service_Configuration_Reference.md` | Full per-service config class breakdown (passwords stripped). Largest single doc. |
| `NIB_Online_Cohesiveness_Analysis.md` | The "8 critical findings" memo (cross-portal HTTP, Oracle 7 schemas, missing Dockerfiles, JWT secret consistency, etc.). The schema names in this doc reflect Feb-2026 state; trust `03-SERVICES.md` and `02-ARCHITECTURE.md` §6.1 for current (verified 2026-05-19) names. |
| `NIB_Online_Local_Deployment_Reference.md` | Local deployment instructions (hosts file, certs, schema setup) |
| `NIB_Online_Preprod_Deployment_Testing_Plan.md` | Pre-cutover smoke-test plan |
| `env-branching-strategy.md` | Earlier formulation of the branch→tag→server flow |
| `DNS_PRODUCTION_MIGRATION_PLAN.md` | LB cutover plan (now executed 2026-05-10) |
| `launch-image-provenance.md` | Why the customer frontend tag is `:claims` and how to recover the source commit |
| `banking-doc-reupload-option-b-plan.md` | Architectural design behind the banking-doc reupload feature (shipped 2026-05-18) |
| `ADENA_MEETING_FULL_STATUS.md` | CS team operational context (Adena Minus / FIU office scope) |

If a `reference/` doc and an onboarding doc disagree, the onboarding doc wins (it's more recent and verified). The `reference/` docs are kept for historical context and point-in-time detail.
