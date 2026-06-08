# Onboarding Documentation Sweep — Audit Report

**Date:** 2026-06-08 · **Scope:** all 11 prose docs under `development-documentation/onboarding/` · **Method:** per-doc review with claims verified against live code, plus a cross-doc repetition pass (12-agent workflow). **Mode:** findings only — no docs edited.

**Goal context:** these docs are headed for (a) external send-out and (b) embedding in the admin portal SPA as in-app help for NIB admin staff.

---

## Headline

- **0 of 11 docs are send-out ready as-is.** Every one has at least one blocker — most commonly internal/security exposure or a code-contradicting factual error.
- **2 docs should be cut entirely** as redundant: `05-CITIZEN-GUIDE.md` (≈ duplicate of `USER-MANUAL.md`) and `06-ADMIN-GUIDE.md` (superset duplicating `ADMIN-MANUAL.md` + `SUPERVISOR-MANUAL.md`).
- **Admin-SPA in-app bundle = `ADMIN-MANUAL` + `SUPERVISOR-MANUAL` only**, and only after an "adapt" pass. Everything else is dev-only or citizen-facing.
- A **recurring family of factual errors** (benefit types, B80/B81 form naming, card types, admin filter/reason lists) appears across multiple docs — fix once at the canonical source.

## Per-document verdict

| Doc | Audience | Admin-SPA | Send-out | Top issue |
|---|---|---|---|---|
| README.md | developer | exclude | ❌ | Stale "three docs" (six exist); internal task refs |
| 01-EXECUTIVE-OVERVIEW.md | mixed | adapt | ❌ | **Invented benefit types** "Disability"/"Surviving Spouse"; IPs/incident detail |
| 02-ARCHITECTURE.md | developer | exclude | ❌ | Email job misdescribed (RabbitMQ consumer, not 60s poller); B81 mislabel; unresolved JWT TODO |
| 03-SERVICES.md | developer | exclude | ❌ | **Security disclosure**: hardcoded-secret notes, named personal Oracle cred, SECURITY_FIXES pointer |
| 04-DEPLOYMENT.md | developer | exclude | ❌ | **Live Grafana password in plaintext**; prod IPs; unresolved prod-data incident |
| 05-CITIZEN-GUIDE.md | citizen | exclude | ❌ | Near-duplicate of USER-MANUAL; "Replacement" card type doesn't exist; dev screenshot block |
| 06-ADMIN-GUIDE.md | admin-staff | adapt | ❌ | Superset duplicate of the two manuals; PII (LDAP user, named colleague); "choose form type" step is fictional |
| ADMIN-MANUAL.md | admin-staff | **adapt → include** | ❌ | **Status filter values wrong** (UI has only Pending/Approved/Denied); **reupload reason list fabricated**; cites non-existent composable |
| SUPERVISOR-MANUAL.md | admin-staff | **adapt → include** | ❌ | **Form mapping wrong** (Sickness=MED 1, Maternity=MED 2, not "B81"); **"SUPERVISOR CS can reassign" contradicts code** |
| USER-MANUAL.md | citizen | exclude (citizen-portal, not admin) | ❌ | **Claims first-time "New Card" online works — it doesn't** (renewal/replacement only) |
| DESIGN-SYSTEM.md | developer | exclude | ❌ | Wrong file path; "Montserrat" vs config typo "Monsterrat"; brand-asset clearance |

## CRITICAL send-out blockers (security / PII) — fix before ANY distribution

These are not stylistic; they leak credentials, infrastructure, and personal data:

1. **`04-DEPLOYMENT.md` — live Grafana credential in plaintext** (admin password, appears twice in §9.1 and §14). Redact + **rotate**.
2. **Production infrastructure exposure** (04, 03, 02, 01): private IPs (`192.168.100.139`, `172.16.1.139`, `.117`, `.123`, NetScaler VIPs), hostnames, SSH jumphost topology, Sentry org IDs, Oracle schema/SID names.
3. **Named personal/credential leaks**: `03-SERVICES` references a personal Oracle credential ("lionels@"); `06-ADMIN-GUIDE` names the "LDAP user lionels" test account and a colleague "Adena Minus" with internal policy attribution; `SUPERVISOR-MANUAL` repeats "Adena Minus, 2026".
4. **Security-posture disclosure**: `03-SERVICES` references hardcoded-secret notes, `verify=False` rationale, and points to `SECURITY_FIXES_REQUIRED.md` (19 open security items).
5. **Unresolved incidents stated as current**: `04` documents a possible prod-data-integrity issue (staging cards-cleanup job defaulting to prod Oracle) and a 98%-full prod disk — distributing these is risky.

## Recurring factual errors (verified against code) — fix at canonical source

- **Benefit types** (`01`): lists non-existent "Disability Benefit" and "Surviving Spouse Benefit"; omits Injury, Sickness Extension, Maternity Extension. Actual: Unemployment, Sickness (+Ext), Maternity (+Ext), Funeral, Retirement, Injury.
- **B80 / B81 form naming** (`01`, `02`, `06`, `SUPERVISOR`): B81 is the **Department of Labour Unemployment Card**, NOT a "Medical Certificate". Generated forms are per claim type — `med_1.html` (Sickness/Injury), `med_2.html` (Maternity), `unemployment_benefit.html`, etc. B80/B81 are citizen **uploads**, not admin-generated forms.
- **Card types** (`05`, `USER-MANUAL`): no first-time "New Card" and no "Replacement" online flow in practice — the system supports **Renewal** (and Replacement in the enum); first-time applicants are routed to the paper R4 form.
- **Admin claims queue Status filter** (`ADMIN-MANUAL`): UI offers only **Pending / Approved / Denied**, not the 6 listed.
- **Reupload reason list** (`ADMIN-MANUAL`): the real list is 5 fixed NIB-specific reasons with **no free-text "Other"** — doc invents generic ones.
- **SUPERVISOR CS reassign** (`SUPERVISOR-MANUAL §7.3`): contradicts code — reassign is gated on the `canEdit`/manager tier; SUPERVISOR CS cannot reassign.
- **Email background job** (`02 §8`): it's an always-on RabbitMQ consumer, not a 60-second DB poller.
- **Currency gap (all admin docs):** none mention the new read-only **Payment card**, **MED 2 payment rendering**, or the **NibDetailCard** unification (this sprint's work).

## Repetition → consolidation plan

**Cut 2 documents:**
- **`05-CITIZEN-GUIDE.md` → merge into `USER-MANUAL.md`** (near-duplicates: same Quick Map, sign-in tree, benefit cards, account pages, status table, FAQ). Keep USER-MANUAL (versioned, has Document Information footer). Fix the shared inaccuracies while porting.
- **`06-ADMIN-GUIDE.md` → split into `ADMIN-MANUAL.md` + `SUPERVISOR-MANUAL.md`** (06 is a superset of both). Discard 06's inaccurate variants (e.g. "choose the form type").

**Canonical homes for the dev docs (cross-link, don't duplicate):**
- `03-SERVICES.md` owns: the 20-repo Service Index, Verified Oracle Schema Map, service-to-service URL table, Sentry/Redis coverage, per-background-job detail.
- `04-DEPLOYMENT.md` owns: server inventory/IP-DNS, image-tag matrix, branch→tag→server flow, Jenkins, config/secrets workflow, monitoring config, operational gotchas catalog.
- `02-ARCHITECTURE.md` owns: conceptual models (networks, request lifecycles, patterns) — trimmed to summaries that cross-link 03/04.
- `01-EXECUTIVE-OVERVIEW.md` owns: the single glossary + executive-altitude environment list.
- `README.md` owns: the reading-order index + the single "Refreshing Screenshots" devops block (pull the Playwright/test-credential blocks out of 05 and 06).
- `SUPERVISOR-MANUAL.md §7` owns: the single authoritative admin role reference (02 §5.2 and 03 admin-auth keep only "roles sourced from Oracle, not LDAP" and cross-link).

## Admin-SPA in-app help bundle (recommendation)

Surface **only** `ADMIN-MANUAL.md` + `SUPERVISOR-MANUAL.md`, after an "adapt" pass that:
- fixes the high-severity accuracy errors above,
- strips dev/internal jargon (Oracle table names, composable names, source file names, bug codes),
- removes PII and the screenshot-regeneration appendices,
- adds the new **Payment card** explanation (incl. "Payment Collection Office" vs processing office) and updates the claim-detail section list.

Exclude from the admin SPA: README, 01–04, DESIGN-SYSTEM (dev), and 05/USER-MANUAL (citizen — belongs in the *citizen* portal's help instead).

## Suggested execution order

1. **Security/PII redaction pass** (04, 03, 01, 06) — blocks everything; pair with credential rotation.
2. **Cut 05 and 06** (merge into USER-MANUAL / the two manuals).
3. **Fix the recurring factual errors** at canonical source (benefit types, B80/B81, card types, filter/reason lists, SUPERVISOR CS reassign, email job).
4. **Currency update** — add Payment card / MED 2 payment / NibDetailCard to the admin docs.
5. **Canonical-home consolidation + cross-links** for the dev docs.
6. **Adapt the two admin manuals** for in-app embedding; re-verify fixes against live code.
