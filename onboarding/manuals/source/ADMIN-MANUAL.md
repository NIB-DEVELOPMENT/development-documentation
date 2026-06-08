---
title: Admin Manual
subtitle: NIB Online Portal
audience: For NIB Customer Service Officers and Staff
version: 1.0
date: 2026-05-20
---

## About This Manual

This manual covers how NIB staff use the **Admin Portal** to review and process the applications citizens submit through the online portal.

**Portal address:** [https://nibonline-admin.nib-bahamas.com](https://nibonline-admin.nib-bahamas.com)

**Who should read this:**

- Customer Service Officers (`NON SUPERVISOR CS`)
- Family Island Unit non-supervisor staff (`NON SUPERVISOR FIU`)
- IT support staff (`NON SUPERVISOR IT`, `SUPERVISOR IT`, `SECURITY MANAGER IT`)
- OHSU non-supervisor staff (`NON SUPERVISOR OHSU`)
- Anyone who needs to route applications, review documents, and request re-uploads

> **If you can approve or deny applications**, you have a supervisor-tier role. Please read the **Supervisor Manual** instead, which covers the additional approve / deny / reassignment workflows.

**What you'll learn:**

- How to sign in with your LDAP credentials
- How to navigate the application queue
- How to open and review an application's details
- How to download supporting documents
- How to **route an application to yourself** so you can work on it
- How to **request a document re-upload** when something is missing or unreadable
- How to read the activity log for any application

**What this manual does NOT cover** (those are in the Supervisor Manual):

- Approving applications
- Denying applications (with denial reasons)
- Re-assigning applications to other officers
- Changing the local office handling an application
- Generating official PDF forms (the MED 1 / MED 2 medical forms, the unemployment and retirement forms, etc.)
- Office-wide / department-wide statistics

If you have questions this manual doesn't cover, ask your supervisor or contact NIB IT.

---

## 1. Signing In

Open [nibonline-admin.nib-bahamas.com](https://nibonline-admin.nib-bahamas.com) in your browser. You'll land on the admin login screen.

![Admin login page](images/admin/01-admin-login.png)

**What you need:**

- Your **LDAP username** (the same one you use for other NIB internal systems)
- Your **LDAP password**

The admin portal authenticates against the corporate LDAP directory. After your password is verified, the system looks up your assigned **admin roles** to determine what you're allowed to do.

If your LDAP password works but you receive a "no permission" toast on the page, that means your account doesn't yet have an admin role assigned. Ask your department head to request the appropriate role from NIB IT.

If your LDAP password doesn't work, contact NIB IT — the admin portal does NOT have a self-service password reset.

---

## 2. The Applications Hub

After signing in, you land on the **Applications hub** — a chooser for the two application domains you can work in.

![Applications hub](images/admin/02-applications-hub.png)

Two large cards represent the two domains:

- **Online Card Renewals** — Search and manage online card renewal applications.
- **Claims** — Search and manage online claim applications.

Click whichever card matches the work you need to do. The top nav has **Dashboard** and **Applications** tabs; you can also click your name in the top right to sign out.

> Your hub may show the Cards card, the Claims card, both, or neither depending on which roles you have. For example, OHSU staff only see Claims (they handle Injury Benefit claims). Cards Registration staff only see Cards.

---

## 3. Finding an Application

### 3.1 The Claim Applications queue

If your role gives you access to Claims, click **Claims** from the hub. You'll see the queue.

![Claim applications queue](images/admin/04-claims-queue.png)

The queue shows applications matching your filter. The header shows the result count (e.g., **"Results found: 71"**) and the table lists:

| Column | Meaning |
|---|---|
| **Application ID** | Internal unique number for the application |
| **NI Number** | The citizen's NIB number |
| **First Name / Last Name** | The citizen who submitted the application |
| **Application Type** | The benefit type (Sickness, Unemployment, Maternity, etc.) |
| **Status** | Where the application is in the workflow |
| **Local Office** | Which NIB office is handling it |
| **Inserted Date** | When the citizen submitted it |

Click any row to open that application's detail page.

### 3.2 The Card Applications queue

If your role gives you access to Cards, click **Online Card Renewals** from the hub.

![Card applications queue](images/admin/05-cards-queue.png)

Same filter form, different result columns. Application Type values will be **Renewal** or **Replacement**.

### 3.3 Using filters

Both queues share the same filter form at the top:

| Filter | What it does |
|---|---|
| **Application ID** | Find one specific application by its internal number |
| **NI Number** | Find all applications from one citizen |
| **First Name / Last Name** | Search by claimant name |
| **Application Type** | Limit to one benefit / card type |
| **Status** | Pending, Approved, or Denied (these are the only three filter options) |
| **Routed To** | Filter by which officer owns it (see §4.3 about routing) |
| **Local Office** | Filter to one office (your access may be limited to your own office) |
| **From / To Inserted Date** | Date range when the citizen submitted |

Click **Search** to apply your filters, or **Clear** to reset.

### 3.4 What you see depends on your role

By default:

- **NON SUPERVISOR CS** and **NON SUPERVISOR FIU**: see only applications routed to *your* local office
- **IT** roles: see all applications (read-only view)
- **OHSU** non-supervisor: see Injury Benefit claims

If you expect to see an application but don't, check the filters first. If filters are clear and you still don't see it, your role may not include that office's scope — ask your supervisor.

---

## 4. Reviewing an Application

Click any row in the queue to open the application detail page.

### 4.1 Claim application detail

![Claim application detail](images/admin/06-claims-application-detail.png)

The detail page is organized into sections:

1. **Header** — claim type and claim number (e.g., "Unemployment Claim #1") with a status badge (e.g., "Pending")
2. **Routed To** — which officer currently owns this application (or empty if not yet routed)
3. **Claimant Details** — the citizen's name, NI number, email
4. **Payment** — how the benefit is to be paid, shown read-only: the **Payment Method** (Bank Account, Funeral Home, or Local Office) and its supporting details. When the method is a local office, the field is labelled **Payment Collection Office** — the office where the citizen collects payment. This is *not* the same as the processing office shown in the address section; don't confuse the two.
5. **Claim-specific Details** — fields specific to this benefit type (for Unemployment: last working date, employer info, pension status, severance days, vacation days, etc.)
6. **Application Documents** — uploaded files (passport, B80, etc.) with **Download**, **Upload History**, and additional document-action links (see §4.5)
7. **Contact Information** — phone numbers and primary contact flag
8. **Application address Information** — the citizen's mailing/physical address
9. **Activity Log** — audit trail (scroll to the bottom)

### 4.2 Card application detail

![Card application detail](images/admin/07-cards-application-detail.png)

A card detail page has a similar structure with cards-specific sections:

- **Person Information** — full name, NI Number, **Registrant Type** (Bahamian / Non-Bahamian), gender, DOB, country of nationality, marital status
- **Application Information** — application type (Renewal / Replacement), reason for name change (if applicable), Ready for Pickup flag, Local Office
- **Non-Bahamian Details** — *(only for non-Bahamian registrants)* permanent-resident flag, resident card number + expiry, work permit number + expiry
- **Application Documents** — R4, Passport, Work Permit, etc.
- **Contact Information** and **Address Information**

### 4.3 Routing — claiming an application to work on

Most actions in the portal require an officer to be the **Routed To** owner of the application. When you find a new application in the unrouted pool, claim it by clicking **Route To Me**.

After you click Route To Me:

- The Routed To field now shows your name
- You're notified by the system if other officers try to act on the application
- You can take any further actions allowed by your role

If an application is already routed to someone else, you can still:

- Review its documents and details
- Read the activity log

But to take action, you need to either:

- Ask the current routed-to officer to hand it off (they can re-assign if their role allows — see Supervisor Manual)
- Or escalate to a supervisor who can re-assign on your behalf

### 4.4 Downloading documents

Each uploaded document in the **Application Documents** section has a **Download** link. Click it to retrieve the file (PDF, JPG, PNG) to your computer.

The download is served directly from the file storage shared between the citizen portal and the admin portal — the file you download is the same file the citizen uploaded. There's no copy / transfer delay.

> If a document fails to download with the error "**400: File does not exist**", do NOT ask the citizen to re-upload. Take a screenshot of the error and notify NIB IT — there may be a database / file-path issue that needs engineering attention. Asking the citizen to re-upload often masks the underlying problem.

### 4.5 Requesting a document re-upload

If a document is unreadable, blurry, incomplete, expired, or the wrong document type, you can ask the citizen to upload a replacement.

Click **Request Reuploads** in the Application Documents header. You'll be prompted to:

1. **Select which document(s)** need a new upload
2. **Choose a reason** from the fixed list (one reason per request):
    - Image quality is poor
    - Bank Client Card / Bank Letter Needed (Paper Card with Bank Account Info and Transient Number)
    - Claim is not signed
    - Claim is not stamped by Doctor
    - Revised dates needed
3. **Confirm** the request

> A reason is **required** and must be chosen from the list above — there is no free-text "Other" option.

After you confirm:

- The document is marked as **awaiting re-upload**
- The citizen receives an automatic email letting them know
- The citizen sees a banner / prompt on their portal home and "My Claims" / "Card Applications" list the next time they sign in
- The application's overall status reflects that it's waiting on the citizen

When the citizen uploads a replacement, the document returns to its normal submitted state, and you'll see the new file when you next open the application. You can then continue your review.

---

## 5. The Activity Log

Every significant action taken on an application is logged with a timestamp and the officer's identity. Scroll to the bottom of the application detail page to find the **Activity Log**.

The log records:

- Routing changes (who routed it, when, who claimed it)
- Re-upload requests (which document, the reason, who requested)
- Document downloads
- Status changes (Submitted → In Review → etc.)
- Approval / denial (when applicable)
- Local-office changes

You can filter the log by date range or activity type if it's long.

> The activity log is a **regulatory audit trail** — it's not just a UI feature. It's stored permanently in Oracle and used for NIB compliance reporting. Do not attempt to bypass it; every action you take should be visible in the log so others can follow what happened.

---

## 6. Common Tasks

### Find a specific citizen's application

Use **NI Number** in the queue filter. This is faster than scrolling. If you don't know the NI number, search by **Last Name + First Name**.

### Find work you're currently handling

Click the **Routed To** filter field to open the officer picker, then select your name. This shows your active workload.

### Check what's been recently submitted

Set **From Inserted Date** = today (or yesterday). Leave the **To** date blank. Sort by Inserted Date if needed.

### Read the audit history before acting

Always check the **Activity Log** at the bottom of the detail page before requesting a re-upload or asking for guidance. The log may show that another officer already requested a re-upload, or that the citizen has already responded to a prior request.

---

## 7. Common Issues

| Issue | What to do |
|---|---|
| **I can't sign in** — LDAP rejected my password | Contact NIB IT to reset your LDAP password. The admin portal has no self-service reset. |
| **I signed in but see a "no permission" toast** | Your LDAP account doesn't have an admin role. Ask your supervisor to request the role from NIB IT. |
| **I can see the application but can't approve / deny** | Approve / deny is reserved for supervisor-tier roles. Either escalate to your supervisor, or check the Supervisor Manual to confirm whether your role should have access. |
| **An expected application isn't showing in the queue** | Clear all filters and re-search. If still missing, the application may be assigned to a different local office (you only see your office by default). Ask your supervisor to widen the search or check Routed-To. |
| **A document download returns "400: File does not exist"** | Don't ask the citizen to re-upload. Screenshot and report to NIB IT. |
| **I can't find an officer in the Routed-To filter** | The Routed-To filter opens an officer-picker modal — click the field to open it and choose from the list. If you still can't narrow it down, use **NI Number** or claimant-name search instead. |
| **Filter shortcuts on the queue aren't applying** | Known issue at time of writing. Use the dropdown filters manually. |

---

## 8. Need Help?

- **LDAP / sign-in issues:** Contact NIB IT helpdesk.
- **Role assignment requests** (e.g., "I should be able to approve but the button isn't showing"): submit through your department head, who can have NIB IT update your admin role assignment.
- **A bug in the admin portal:** Report to the engineering team. Include the application ID, your username, and a screenshot if possible.
- **A specific application's data looks wrong** (e.g., "Why isn't the banking doc showing?"): the engineering team can run database queries to investigate.

---

## Document Information

**Title:** NIB Online Portal — Admin Manual
**Audience:** Customer Service Officers and Non-Supervisor Admin Staff
**Version:** 1.0
**Issued:** 2026-05-20
**Published by:** National Insurance Board of The Bahamas

This manual covers the workflows available to non-supervisor admin staff. For approve / deny / reassignment / form generation / statistics, please refer to the **Supervisor Manual**.

Screenshots reflect the portal as of the issue date. If you notice a significant difference between this manual and what you see on screen, please notify NIB IT.
