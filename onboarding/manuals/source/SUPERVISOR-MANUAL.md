---
title: Supervisor Manual
subtitle: NIB Online Portal
audience: For Department Heads, Managers, and Supervisors
version: 1.0
date: 2026-05-20
---

## About This Manual

This manual covers the supervisor-tier actions on the **Admin Portal** — the workflows that are reserved for roles with approval authority and office-management responsibility.

**Portal address:** [https://nibonline-admin.nib-bahamas.com](https://nibonline-admin.nib-bahamas.com)

**Who should read this:**

- Customer Service Department Head (`DEPARTMENT HEAD CS`)
- Family Island Unit Manager (`MANAGER FIU`)
- Family Island Unit Sub-Office Manager (`SUB OFFICE MANAGER FIU`)
- Family Island Unit Supervisor (`SUPERVISOR FIU`)
- Customer Service Supervisor (`SUPERVISOR CS`)
- OHSU Department Head (`DEPARTMENT HEAD OHSU`)
- Registration Supervisor and Department Head (`SUPERVISOR R`, `DEPARTMENT HEAD R`)

**What you'll learn:**

- Everything in the **Admin Manual** is a prerequisite — please skim that first if you haven't.
- How to **approve** an application
- How to **deny** an application with the correct reason
- How to **reassign** an application from one officer to another
- How to change the **local office** handling an application
- How to **generate official forms** (the MED 1 / MED 2 medical forms and the other benefit forms) as PDFs
- The complete **role reference** showing which roles can do what
- How the office-scoping model affects what each role sees

**Prerequisite reading:** If you've never used the admin portal before, read the Admin Manual first. This document assumes you can already sign in, find an application, open the detail page, download documents, and request re-uploads.

---

## 1. Quick Reference — What You Can Do

Your role determines exactly which buttons show up on an application's detail page. The table below summarizes:

| Action | Cards roles that can do it | Claims roles that can do it |
|---|---|---|
| **Route To Me** | All roles with cards access | All roles with claims access |
| **Reassign / Re-route** | `MANAGER FIU`, `SUB OFFICE MANAGER FIU`, `SUPERVISOR R`, `DEPARTMENT HEAD R` | `DEPARTMENT HEAD CS`, `MANAGER FIU`, `SUB OFFICE MANAGER FIU`, `DEPARTMENT HEAD OHSU` |
| **Request Reupload** | All roles with cards access | All roles with claims access |
| **Approve** | `SUPERVISOR R`, `DEPARTMENT HEAD R`, `MANAGER FIU`, `SUB OFFICE MANAGER FIU` | `DEPARTMENT HEAD CS`, `MANAGER FIU`, `SUB OFFICE MANAGER FIU`, `DEPARTMENT HEAD OHSU` |
| **Deny** | (Same as Approve) | (Same as Approve) |
| **Change Local Office** | (Same as Approve) — and only while application is **un-routed** and **status=Pending** | (Same as Approve) — and only while application is **un-routed** and **status=Pending** |
| **Generate Pdf** | All roles with cards access (the system produces the appropriate PDF for that application's type) | All roles with claims access |
| **View Dashboard Statistics** | (varies by deployment) | (varies by deployment) |

> Notice: **claims and cards have different supervisor matrices.** For example, `DEPARTMENT HEAD CS` can approve claims but cannot approve cards (because cards live in the Registration department). `MANAGER FIU` can approve both. This is intentional — see §6 for the full role reference.

If a button you expect to see is missing, it's almost always because your role doesn't include that permission. Double-check the role table before assuming there's a bug.

---

## 2. Approving an Application

Before you can approve, the application must be **routed to you** (or to someone you have authority to act on behalf of). If it isn't, see §4 (Reassignment).

![A claim detail page. For supervisor-tier roles, the **Approve** and **Deny** buttons appear at the top-right next to the status badge.](images/admin/06-claims-application-detail.png)

To approve:

1. Open the application detail page from the queue
2. Confirm the **Routed To** field shows your name
3. Review all the claimant's details — including the **Payment** section (how and where the benefit will be paid) — plus the documents and contact information one more time
4. Click the **Approve** button (top right of the detail page)
5. A browser confirmation prompt appears ("Are you sure you want to approve this application?")
6. Click **OK** to confirm

What happens next:

- The application status changes to **Approved**
- The activity log records your approval with a timestamp
- The citizen receives an automatic approval email
- For **claims**, downstream payment scheduling picks up the approval (handled outside this portal)
- For **cards**, the next status is typically **Ready for Pickup** — the card is printed at the central registration office and shipped to the citizen's local office for collection

> **Approve is final.** There is no undo button. If you approve in error, contact NIB IT — the database state can be amended but the action will be visible in the audit log permanently.

### When NOT to approve

- The Routed To officer is someone else who's still working on the application
- A document is unreadable or expired (request a re-upload first)
- The claimant's banking details don't match what was uploaded (request a re-upload of the banking doc)
- The application has a **Reupload Requested** status (the citizen still needs to respond)
- You're uncertain about eligibility — escalate to your department head

---

## 3. Denying an Application

To deny:

1. Open the application detail page
2. Confirm Routed To = your name
3. Click **Deny** (next to the Approve button)
4. A menu of **denial reasons** (loaded from the system) appears — click the appropriate reason
5. A browser confirmation prompt then appears — click **OK** to confirm

> The claims deny flow has no separate free-text notes field; the reason you pick from the menu is what's recorded in the audit log and emailed to the citizen.

What happens next:

- Status changes to **Denied**
- Activity log records your denial + reason + timestamp
- Citizen receives an automatic denial email that includes the reason from the dropdown
- The citizen can contact NIB if they want to challenge the denial

### Denial reasons

The actual reasons are loaded from the system and vary by application type; you pick one from the menu. Typical examples:

| Reason | When to use |
|---|---|
| Insufficient contributions | Claimant doesn't meet the contribution requirements for the benefit |
| Eligibility period not met | Claim filed too early or too late relative to the qualifying event |
| Missing or invalid documents | Required documents are still missing or fundamentally wrong (after re-upload attempts) |
| Duplicate application | This citizen has already submitted (and possibly received) the same benefit |
| Not currently employed | (Unemployment) Claimant doesn't appear to have ceased employment |
| Self-employed | (Some benefits) — self-employed claimants may require in-person processing at their local office; confirm current policy with NIB Customer Service before denying on this basis |
| Other | A reason specific to the case |

---

## 4. Reassigning an Application

Use reassignment when an application is routed to the wrong officer — for example, the officer is out of office, the workload needs balancing, or the application should belong to a different department.

To reassign:

1. Open the application detail page
2. Click **Reassign** (or the "Routed To" field, if the button is named differently in your portal version)
3. Choose the new officer from the dropdown
4. Confirm

What happens:

- The Routed To field updates immediately
- Activity log records who reassigned, from whom, to whom, when
- The previous routed-to officer may receive a notification (depending on environment configuration)

### Removing an assignment

If you want to "un-claim" an application (return it to the unrouted pool):

1. Open the application detail page
2. Click **Remove Assignment** (the icon next to the Routed To field)
3. Confirm

> The **Remove Assignment** control only appears for **manager-tier (canEdit) roles** and only while the application's status is **Pending**. A non-manager officer who routed an application to themselves will not see it — a department head / manager has to remove the assignment for them.

The application now has no Routed To and any officer in the appropriate scope can claim it via Route To Me.

> Reassigning DOES NOT remove the original officer's audit history. Their prior actions (re-upload requests, document downloads, etc.) remain in the activity log. You're just changing who currently owns the work.

---

## 5. Changing the Local Office

If an application landed on the wrong office (e.g., the citizen entered the wrong office during registration, or they've since moved), this *may* be possible to fix from the application detail page — but the feature is narrowly gated.

**Important — when this is available:** the Local Office dropdown is **only enabled** when ALL three conditions are true:

1. You hold a `canEdit` role (manager-tier — see §7.3)
2. The application has **not** yet been routed to any officer (Routed To is empty)
3. The application's status is **Pending** (brand-new submission, not yet in review)

In practice, that means you can change the local office on a freshly-submitted application before anyone claims it, but **once an officer routes the application to themselves, the dropdown becomes read-only**. This is by design — once review has started, an office change would orphan the activity log.

If you find an application that needs to move offices *after* someone has routed it, the workflow is:

1. A manager-tier (canEdit) user clicks **Remove Assignment** to un-route it (the control isn't available to non-manager officers, so a department head / manager does this)
2. Once the application is back in the unrouted pool with status Pending, the Local Office dropdown will enable
3. Choose the correct office and confirm
4. The application moves to the new office's queue

If you expect to see the dropdown enabled and it isn't, check the three conditions above first. If all three are met and the dropdown is still greyed out, contact NIB IT — there may be a role/permission mismatch.

> Changing the local office DOES NOT automatically reassign the Routed To officer. The previous officer's audit history remains in the log; the application simply moves to the new office's queue.

---

## 6. Generating an Official Form (PDF)

Both **claims** and **card** applications have a **Generate Pdf** action on the application detail page (in the Application Documents section header, next to **Request Reuploads**).

**How it works:**

1. Open the application detail page
2. Click **Generate Pdf**
3. The system automatically produces the appropriate official PDF(s) for that application type — pre-filled with the citizen's submitted data plus reference data from Oracle
4. The file downloads to your computer

You do **not** choose the form — the system selects the right one based on the application's type:

| Application type | What the PDF contains |
|---|---|
| **Sickness** / **Injury** claim | The **MED 1** form, pre-filled |
| **Maternity** (and Maternity Extension) claim | The **MED 2** form, pre-filled |
| **Unemployment** claim | The unemployment benefit form, pre-filled (it references the citizen-uploaded **B80** Employer's Certificate of Termination where applicable) |
| **Retirement** claim | The retirement claim form, pre-filled |
| **Funeral** claim | The funeral benefit form, pre-filled |
| **Card** application | A printable application summary suitable for the registration office workflow |

> **B80 / B81 are citizen *uploads*, not generated forms.** B80 is the Employer's Certificate of Termination and B81 is the Department of Labour Unemployment Card — both are documents the citizen attaches to an unemployment claim. The PDFs *you* generate here are the MED / benefit forms listed above.

You can print, attach, or save the generated PDF as needed.

> **Empty fields are not errors.** If the citizen didn't provide a required field (e.g., "last employer NIB number" on Unemployment), the form displays a fallback like *"See attached B80 — Employer's Certificate of Termination"*. This is per NIB Customer Service policy (Adena Minus, 2026) — the B80 in the uploaded documents already carries that information so we don't ask the citizen to repeat it on the in-app form.

> The PDFs are generated by the system from the application's submitted data. If a generation fails, take a screenshot, note the application ID, and report it to NIB IT — it may be a template or data issue.

---

## 7. Role Reference (Authoritative)

The admin portal uses **5 role categories** organized by department. **A user can have multiple roles** (e.g., an officer may carry both Cards and Claims roles).

Your roles are assigned in the admin role directory, **not** from your LDAP groups — LDAP only validates your password.

### 7.1 The Five Categories

| Category | Suffix | What they do |
|---|---|---|
| **Registration (`R`)** | "...R" | Process NIB card applications |
| **Customer Service (`CS`)** | "...CS" | Process claims applications |
| **Family Island Unit (`FIU`)** | "...FIU" | Process applications from non-Nassau islands (geographic) |
| **IT** | "...IT" | View access for support; security manager has elevated access |
| **OHSU** | "...OHSU" | Occupational Health and Safety Unit — Injury Benefit claims |

### 7.2 Verified Role Inventory

```
Registration (Cards):
  NON SUPERVISOR R
  SUPERVISOR R
  DEPARTMENT HEAD R

Customer Service (Claims):
  NON SUPERVISOR CS
  SUPERVISOR CS
  DEPARTMENT HEAD CS

Family Island Unit (cross-domain):
  NON SUPERVISOR  FIU      (note: two spaces between SUPERVISOR and FIU)
  SUPERVISOR FIU
  MANAGER FIU
  SUB OFFICE MANAGER FIU

IT (cross-domain):
  NON SUPERVISOR IT
  SUPERVISOR IT
  SECURITY MANAGER IT

OHSU (Claims — Injury Benefit only):
  NON SUPERVISOR  OHSU     (note: two spaces between SUPERVISOR and OHSU)
  DEPARTMENT HEAD  OHSU    (note: two spaces between HEAD and OHSU)
```

> The double-space in "`NON SUPERVISOR  FIU`" and the OHSU roles is intentional — it matches the legacy Oracle data and must be preserved exactly when assigning roles. Do not "fix" the spacing.

### 7.3 What Each Role Can Do — Full Matrix

| Role | Cards: view | Cards: approve/deny | Claims: view | Claims: approve/deny | Notes |
|---|---|---|---|---|---|
| `NON SUPERVISOR R` | yes | no | no | no | Cards-only junior officer (Registration office) |
| `SUPERVISOR R` | yes | **yes** | no | no | Cards supervisor |
| `DEPARTMENT HEAD R` | yes | **yes** | no | no | Cards department head |
| `NON SUPERVISOR CS` | no | no | yes | no | Claims CS officer (read + route, no approve) |
| `SUPERVISOR CS` | no | no | yes | **no** | Claims supervisor — can route an application to **themselves** only; cannot reassign to others and cannot approve/deny |
| `DEPARTMENT HEAD CS` | no | no | yes | **yes** | Claims department head — full approve/deny |
| `NON SUPERVISOR FIU` | yes | no | yes | no | Family Island junior officer — both domains, read+route only |
| `SUPERVISOR FIU` | yes | no | yes | no | Family Island supervisor — read+route, no approve |
| `MANAGER FIU` | yes | **yes** | yes | **yes** | Family Island manager — full approve/deny on both |
| `SUB OFFICE MANAGER FIU` | yes | **yes** | yes | **yes** | Sub-office manager — full approve/deny on both |
| `NON SUPERVISOR IT` | yes | no | yes | no | IT support — view-only |
| `SUPERVISOR IT` | yes | no | yes | no | IT supervisor — view-only |
| `SECURITY MANAGER IT` | yes | no | yes | no | IT security — view-only |
| `NON SUPERVISOR OHSU` | no | no | yes | no | OHSU staff — claims read+route for injury benefits |
| `DEPARTMENT HEAD OHSU` | no | no | yes | **yes** | OHSU dept head — full approve/deny |

> Important: `SUPERVISOR CS` does **not** have approve/deny rights for claims. Only `DEPARTMENT HEAD CS` does. If your team needs a supervisor to be able to approve claims, request the `DEPARTMENT HEAD CS` role from NIB IT.

### 7.4 Office Scoping

Your role also determines which offices' applications you can see:

| Role | Office scope |
|---|---|
| CS Non-Supervisor | Their local office only |
| CS Supervisor | Their local office only (cannot approve, but full visibility within office) |
| Department Head CS | All offices (nationwide for claims) |
| FIU Non-Supervisor | Their Family Island office only |
| FIU Supervisor | Their Family Island office only |
| Manager FIU | All Family Island offices |
| Sub Office Manager FIU | Their sub-office only |
| Registration roles | All Registration offices (cards are centrally processed) |

> CS visibility is scoped per the table above. If your team needs wider cross-office visibility, request it from NIB IT through your department head.

---

## 8. The Dashboard / Statistics

![The Dashboard tab — aggregate statistics for the signed-in role's scope.](images/admin/03-dashboard.png)

The **Dashboard** tab in the top nav is where aggregate statistics for your scope render. Depending on your role and current deployment, you may see widgets such as:

- Pending review count (in your scope)
- Applications routed to you
- Approval / denial counts for the current period
- Average processing time

Department Heads see office-wide stats. Managers see Family Island Unit stats. CS Officers see their own caseload.

> The dashboard statistics view is being expanded as part of the post-launch initiatives. If you need specific reports that aren't visible, contact NIB IT to request them.

---

## 9. The Activity Log — Audit Trail

Every action you take (approval, denial, reassignment, local-office change, etc.) is logged with a timestamp and your username. The activity log on each application's detail page is the **regulatory audit trail** — not just a UI convenience.

When acting:

- Be deliberate. Every action is permanently recorded.
- Use notes fields where available — your reasoning can help others (including future you) understand the action months later.
- If you take an action you regret, do NOT try to hide it. Contact NIB IT to amend the database state if needed; the original action remains in the log.

When reviewing:

- Always read the activity log before approving or denying.
- The log may show that a previous officer requested a re-upload that the citizen is still working on.
- The log may show that a different department head previously denied — escalate to determine if anything has changed.

---

## 10. Common Issues

| Issue | What to do |
|---|---|
| **The Approve button isn't showing** | Either you're not the Routed To officer, OR your role doesn't include approve rights for this application's domain. Cross-check the role matrix in §7.3. |
| **I approved by mistake** | Contact NIB IT. The action is permanent in the log; the database state may be amendable but not the audit trail. |
| **The denial reason dropdown is empty** | Refresh the page. If it's still empty, contact NIB IT. |
| **Reassign dropdown doesn't show the officer I want** | The officer may not have the appropriate role for this domain, OR they're in a different local office than this application. |
| **I want to see ALL offices' applications, not just mine** | Your role's office scope (see §7.4) limits visibility. If you should have nationwide access, request a role upgrade through your department head. |
| **PDF form generation returns an error** | Take a screenshot, note the application ID, and report to NIB IT. Corrupt or missing data in the citizen's submission can also cause a generation to fail. |

---

## 11. Need Help?

- **Role assignment requests** (e.g., "I should be able to approve cards but I'm getting Route To Me only"): submit through your department head, who can request changes to your admin role assignment from NIB IT.
- **Policy questions** (e.g., "Can self-employed claimants apply?"): contact NIB Customer Service leadership or OHSU. Some policies are still being worked out and the portal will be updated to reflect them.
- **A bug in the admin portal**: report to NIB IT engineering. Include the application ID, your role, your action, and a screenshot if possible.
- **Compliance / audit questions**: the Activity Log on each application is your starting point. NIB IT can extract activity-log reports across applications if needed for compliance review.

---

## Document Information

**Title:** NIB Online Portal — Supervisor Manual
**Audience:** Department Heads, Managers, and Supervisors (canEdit-tier roles)
**Version:** 1.0
**Issued:** 2026-05-20
**Published by:** National Insurance Board of The Bahamas

This manual covers the supervisor-tier workflows. For basic admin operations (sign-in, queue, review, route, document download, re-upload requests, activity log), please refer to the **Admin Manual**.

The role matrix and office scoping in §7 are derived from the live system configuration as of the issue date. If new roles are added or canEdit policies change, this manual will be re-issued.
