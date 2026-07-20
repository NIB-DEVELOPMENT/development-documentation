# NIB Online Portal — Citizen User Guide

**Audience:** Bahamian citizens using the NIB Online Portal to apply for benefits and NIB cards.
**Purpose:** Walks you through every screen and action in the customer portal.
**URL:** [https://nibonline.nib-bahamas.com](https://nibonline.nib-bahamas.com)
**Screenshots captured:** From the staging environment (`staging-nibonline.nib-bahamas.com`) 2026-05-19. Production screens are visually identical.

---

## Quick Map — What You Can Do Here

| Goal | Where to go |
|---|---|
| **Sign in** | [Login page](#1-signing-in) |
| **Create a new NIB Online account** | [Register page](#11-creating-a-new-account) |
| **Forgot your password?** | [Reset password](#12-forgot-password) |
| **Activate your account from an email link** | [Account activation](#13-account-activation) |
| **Apply for a benefit (claims)** | [Submit a claim](#3-applying-for-a-benefit-claims) |
| **Apply for / renew a NIB card** | [Card application](#4-applying-for-a-nib-card) |
| **Update your personal information** | [Account Information](#52-account-information) |
| **Add or update banking details** | [Banking Details](#53-banking-details) |
| **Check the status of your applications** | [My Claims / Card Applications](#6-checking-application-status) |
| **Respond to a request to re-upload a document** | [Document reupload](#7-responding-to-a-reupload-request) |
| **Change your password or notification preferences** | [General Settings](#51-general-settings) |

---

## 1. Signing In

When you visit [nibonline.nib-bahamas.com](https://nibonline.nib-bahamas.com), you land on the sign-in page if you're not already logged in.

![Login page](images/citizen/02-login-page.png)

**What you need:**

- Your **NIB Number** (this is your unique citizen identifier)
- Your **password**

If you don't yet have an online account, click **Register here** at the bottom of the sign-in card. If you've forgotten your password, click **Forgot your password?** above the sign-in button. If you registered but never received an activation email (or the link expired), click **Resend activation email** beside the forgot-password link.

After signing in successfully, you land on your **portal home**.

### 1.1 Creating a New Account

![Register page](images/citizen/03-register-page.png)

Registration captures just your identity and credentials:

- **First Name** and **Last Name**
- **Email Address** (with confirmation)
- **Password** (with confirmation)
- **NIB Number**

That's it for registration — you'll add contact info, addresses, and banking details later from your account section. After submitting, NIB sends you an activation email. Click the link to confirm your account before you can sign in.

### 1.2 Forgot Password

![Reset password page](images/citizen/04-reset-password-page.png)

Enter your NIB number and the email associated with your account. You'll receive a password-reset email with a one-time link.

### 1.3 Account Activation

![Account activation page](images/citizen/04b-account-activation-page.png)

The account activation page is what you reach after clicking the link in the activation email NIB sent you when you registered. Without a valid activation token in the URL, this page will show an error — it's not meant to be visited directly.

---

## 2. Your Portal Home

After signing in, you land here. This is the **center of everything** — two large cards represent the two services you can use.

![Portal home](images/citizen/05-portal-home.png)

- **Apply Online to Renew your Card** — takes you to the NIB Card renewal flow
- **Apply Online for Your Benefits** — takes you to the Claims portal

In the top-right, your name is displayed (here: "John Doe"). Clicking it opens a menu with your account options and a sign-out link. The top nav has a **Cards** tab and a **Claims** tab — these jump directly to those sections.

---

## 3. Applying for a Benefit (Claims)

Click **Go To Claims** from the portal home (or **Claims** in the top nav) to reach the benefits picker.

![Claims home — benefit picker](images/citizen/08-claims-home.png)

You'll see six benefit cards. Click **Apply** on the one you need:

| Benefit | When to apply |
|---|---|
| **Retirement** | You've reached retirement age and need to claim your pension |
| **Maternity** | You're a working mother and entitled to paid maternity leave |
| **Sickness** | You're temporarily unable to work due to illness |
| **Industrial** *(Injury Benefit)* | You suffered a workplace injury and need OHSU-related benefits |
| **Unemployment** | You lost your job and need temporary income support |
| **Funeral** | A family member has passed and you're claiming the funeral benefit |

Each claim flow walks you through several steps:

1. **Your information** — confirms your demographics on file (name, dob, address). Update if anything is out of date.
2. **Banking details** — choose the bank account you want the benefit paid into. If you haven't added one yet, you'll be prompted to add one here.
3. **Claim-specific questions** — details about the claim (last day of work, employer NIB number, dates of incapacity, etc. — varies by benefit type).
4. **Document upload** — upload supporting documents (medical certificate B81, employer's certificate B80, passport, etc. — varies by benefit type).
5. **Review and submit** — final summary; click Submit to send your claim to NIB.

After submission, you'll receive a confirmation email. Your claim moves into the **Submitted** state, where an NIB Claims Officer can review it.

### View Your Submitted Claims

![My Claims](images/citizen/09-my-claims.png)

Click **View Benefit History** or **View Applications** from the Claims home to see every claim you've submitted, its current status, and any actions required.

---

## 4. Applying for a NIB Card

Click **Apply Now** under **NIB Card EzRENEW** from the portal home, or click **Cards** in the top nav.

![Card renewal home — EzRENEW](images/citizen/14-card-renewal-home.png)

Card applications come in three flavors:

- **New Card** — you've never held a NIB card and need your first one
- **Renewal** — your existing card is at or near expiration
- **Replacement** — your card was lost, damaged, or stolen

Each flow follows a similar pattern:

1. **Your information** — same demographics confirmation as the claims flow
2. **Personal ID document** — a scan of your identity document (e.g. passport bio page), shown when you're updating your details. *(A passport-style photo upload field exists in the code but is disabled — `Create.vue` hides it with `v-if="false"`, "temporarily hidden". The application does NOT ask for a photo of yourself.)*
3. **Supporting documents** — varies by application type (marriage certificate for name changes, police report for lost cards, immigration documents, etc.)
4. **Review and submit**

![Card application — create form](images/citizen/16-card-renewal-create.png)

> You can **save for later** at any point. The portal keeps your in-progress application for **3 months from the submission date** before it's automatically removed. To resume, return to the Cards (or Claims) section and click the **Resume** button next to your saved application.

### View Your Submitted Card Applications

![Card applications list](images/citizen/15-card-applications-list.png)

Same idea as the claims list — every card application you've submitted, with status.

---

## 5. Managing Your Account

Click your name in the top-right and choose **My Account**, or visit `/my-account` directly. The My Account section has three sub-pages, shown as a sidebar on the left:

- **General Settings** — password and email
- **Account Information** — your personal details (addresses, contacts)
- **Banking Details** — bank accounts for receiving benefit payments

![My Account — General Settings landing](images/citizen/10-my-account.png)

When you first click My Account, you land on **General Settings**.

### 5.1 General Settings

The default page. From here you can:

- **Update Password** — click the **Update** link beside Password. You'll be prompted for your current password and a new one.
- **Update Email** — click **Update** beside Email. The page also shows which email address is currently being used for account notifications and password resets.

### 5.2 Account Information

![Account Information (claimant)](images/citizen/11-claimant-information.png)

Your **personal information**: addresses, phone numbers, contact details. Update this section if you move, change phone numbers, or update contact information. Changes are saved immediately and you'll receive an email confirmation.

*(Internally this section is also referred to as "Claimant Information" — same page.)*

### 5.3 Banking Details

![Banking details](images/citizen/12-banking-details.png)

Your bank accounts on file for receiving benefit payments. The page shows a table with **Account No.**, **Branch**, and **Primary** columns plus a **delete (×)** action per row, and an **Add Bank Account** button below.

- **Add Bank Account** — opens a form for name of bank, branch, account type, account number. You'll be asked to upload a **supporting document** (void cheque, bank statement, or bank confirmation letter).
- **Delete (×)** — removes a bank account you no longer want on file.
- **Primary** column shows which account receives benefit payments by default; the primary flag is set during the add flow or by editing a specific row.

The supporting document is verified by NIB during application review. You may be asked to re-upload if the document is unreadable or doesn't match the account details.

---

## 6. Checking Application Status

You have two places to check application status:

- **For benefit claims:** Click **Claims** in the top nav → **View Benefit History** ([screenshot above](#view-your-submitted-claims))
- **For card applications:** Click **Cards** in the top nav → **View Applications** ([screenshot above](#view-your-submitted-card-applications))

Status values you may see (status names can vary slightly depending on application type):

| Status | What it means |
|---|---|
| **Pending** | Application has been submitted and is awaiting NIB review (or — for saved applications shown in the **Saved Applications** section — still a draft you haven't submitted yet). |
| **Submitted** | NIB has received your application. An officer will review it. |
| **In Review** | An NIB officer is currently working on your application. |
| **Reupload Requested** | NIB needs you to upload a clearer or different version of one of your documents. **Action required from you.** See section 7. |
| **Approved** | Your application has been approved. For benefits, payment will follow per the benefit's pay schedule. |
| **Denied** | Your application has been denied. The denial reason will be shown; you can contact NIB if you have questions. |
| **Ready for Pickup** *(cards only)* | Your new/renewed NIB card has been printed and is ready for collection at your local office. |

The **My Claims** screen above also has a separate **Saved Applications** section at the bottom listing any in-progress drafts. Each saved application has **Resume** and **Delete** buttons.

---

## 7. Responding to a Reupload Request

If an NIB officer reviews your application and finds a document that's unreadable, incomplete, or missing, they'll request a **reupload**. You'll receive an email letting you know.

**How to respond:**

1. Sign in to the portal.
2. Go to **My Claims** (for benefits) or **Card Applications** (for cards).
3. Find the application marked **Reupload Requested**.
4. Click into it. You'll see which specific document(s) need a new upload, and the reason the officer gave.
5. Click the **Upload** or **Replace** action next to that document.
6. Choose a new file from your device.
7. Confirm.

The officer is notified automatically. Your application returns to **In Review**. No further action is needed unless they request another reupload.

> Tip: The customer SPA shows a banner / prompt on your applications list page so you don't miss the request. If you don't see it, check your email for the notification.

---

## 8. Common Questions

**Q: My NIB number isn't being accepted at sign-in.**
A: NIB numbers are typically 7–8 characters. Try entering yours in lowercase if upper case isn't working — the system normalizes case. If you still can't sign in, use **Forgot your password?** to verify the number-to-account mapping or call NIB customer service.

**Q: I registered but never got an activation email.**
A: Check spam/junk first. Then go to the sign-in page and click **Resend activation email**. The portal will look up your NIB number and email you a fresh activation link.

**Q: I uploaded a document but it shows the wrong filename / not visible.**
A: First refresh the page. If it's still missing, contact NIB customer service — there may be a banking-doc routing issue (a known historical bug; see workspace incident notes if you're internal staff).

**Q: How do I know which documents are required for my claim?**
A: Each claim type has a documents step that lists required documents before you can submit. If you're missing any, you can't proceed to submit. Save for later, gather your docs, then come back.

**Q: Can I edit a claim after submitting?**
A: Once submitted, you can't edit. You can only respond to reupload requests from an officer. If you submitted incorrect information, contact NIB customer service.

**Q: My card application is taking a long time to approve. What's normal?**
A: Card applications typically process within several business days. Status changes will trigger email notifications. If you've waited longer than two weeks without status change, contact your local NIB office.

---

## 9. Need Help?

Visit your nearest **NIB Local Office** for in-person help. Use the locations page on the public NIB website ([nib-bahamas.com](https://www.nib-bahamas.com)) for hours and addresses.

For password / sign-in issues that the self-service flows can't fix, NIB Customer Service can verify your identity and help recover access.

---

## How These Screenshots Were Captured

These screenshots were captured automatically with **Playwright** running against staging. The capture spec lives at `e2e/specs/customer/screenshots/citizen-walkthrough.spec.ts` in the workspace and can be re-run any time to refresh the visuals (handy when the SPA gets a redesign):

```bash
cd e2e
npx playwright test specs/customer/screenshots/citizen-walkthrough.spec.ts --project=customer-portal
```

Credentials for the test citizen come from `e2e/.env` (`TEST_CUSTOMER_EENI` / `TEST_CUSTOMER_PASSWORD`). Captures land in `development-documentation/onboarding/images/citizen/`.

---

**Next:** see [`06-ADMIN-GUIDE.md`](./06-ADMIN-GUIDE.md) for the NIB staff perspective (reviewing and processing the applications citizens submit here).
