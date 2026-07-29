# NIB Online Portal — Design System

A design system that captures the visual language, content patterns, and component vocabulary of the **NIB Online Portal** — the public-facing claims-and-cards web application of **The National Insurance Board of The Commonwealth of The Bahamas**.

> "Reflecting on the past, building the present, securing the future!" — NIB tagline

---

## 1. What is NIB?

The National Insurance Board (NIB) is the social-security authority of The Bahamas. It administers contributory benefits and cash assistance for Bahamian residents. The Online Portal is the digital front door for two consumer-facing products:

| Product | Sub-brand | Purpose |
|---|---|---|
| **EzCLAIMS (Online Claims)** | "NIB Online" above **EzCLAIMS** — navy word, cadmium-orange "Ez" | Apply online for one of 10 cash benefits + 4 cash-assistance benefits (Sickness, Maternity, Funeral, Industrial Injury, Retirement, Unemployment, etc.). View past benefits and saved drafts. |
| **EzRENEW (Card Renewal)** | "EzRENEW" — sibling sub-brand, gold "Ez" | Apply online to renew an expired NIB photo-ID card. |

Both sub-brands follow the board's **EZ naming convention** (adopted 2026-07-29): a lowercase-`z` `Ez` prefix in the accent colour, joined to the product word in navy caps. `EzCLAIMS` replaced the former italic *"Claims Portal"* wordmark. "NIB Online" remains the umbrella brand above the product mark — the EZ names are product brands, not a portal rename, so the browser tab title, login headings, and email subject prefixes still read "NIB Online".

The two marks differ in accent: EzCLAIMS uses the claims cadmium-orange `#e27e2c`; EzRENEW uses a gold `#f5b400`.

Both products share the same shell (top nav, footer, login flow, account settings) — the design system treats the shell as primary and the two product sections as themed surfaces.

### Audience
- Bahamian residents 16+ who hold an NIB number ("NI number" — an 8-digit identifier referred to as the **EENI**).
- A wide age range, including older claimants for retirement/funeral benefits. The interface must be plain, large-text-friendly, and forgiving.

---

## 2. Sources of truth

This design system was built from the following source materials. The reader may not have access to all of them; they are listed so you can re-verify or extend.

| Type | Location | Notes |
|---|---|---|
| **Codebase** | `online-claims-submissions-frontend/` (mounted folder) | Vue 3 + Vite + TypeScript + Tailwind 2.x. Custom Tailwind palette in `tailwind.config.js`. Component library under `src/components/`. |
| **GitHub repo** | `NIB-DEVELOPMENT/online-claims-submissions-frontend` | Same code, online. Explore for further extraction. |
| **Logos** | `uploads/NIB-11-06-2025-new_Logo.png`, `uploads/nib-logo-updated.png` | Updated official mark (Nov 2025) — flamingo / sun / water / reeds roundel + full wordmark. |
| **In-app imagery** | `online-claims-submissions-frontend/public/img/` | Card mock-ups, illustration SVGs (one per benefit type), EzRenew sub-brand assets, supported-browsers strip. All copied into `assets/`. |

If you are continuing this work, **start in the GitHub repo above** — it's the canonical source.

---

## 3. Content fundamentals

The portal's copy is **formal, official, and reassuring** — appropriate for a government social-security service. It is not chatty, never playful, and avoids slang. The tone matches a teller speaking across a counter: polite, direct, with explicit instructions.

### Voice
- **Second person ("you" / "your")** for instructions and actions: *"To renew your card online, applicants must have an expired NIB card..."*
- **Third person + passive** for institutional statements: *"Benefits are awarded to persons who meet prescribed contribution conditions."*
- **No first person ("we")** — the institution is referenced by its full name or "The National Insurance Board".
- **No contractions** in body copy (*"cannot"*, not *"can't"*) — except inside small UI prompts like *"Don't have an account?"*.

### Casing
- **Title Case** for page titles and CTAs: *"Apply for a Benefit"*, *"Resend Activation Email"*, *"My Account"*.
- **Sentence case** for help text and meta lines.
- **`text-transform: capitalize`** is applied via CSS to `h1.page-title` and to user-typed names in claim summaries — visually capitalises whatever was typed in.
- **UPPERCASE** is used only for table headers (`uppercase tracking-wider` on `<th>`).
- Initialisms are written out the first time: *"NIB Number"*, *"N.I Number"* (with the period — that's how the live forms label it).

### Terminology
- The user's social-security ID is **"NIB Number"** in marketing copy, **"N.I Number"** (with period) in form labels, and **"EENI"** in code. Use "NIB Number" or "N.I Number" externally.
- Cards: **"NIB card"** — physical photo ID.
- Benefits are always *applied for*; never *requested* or *claimed*.
- Saved drafts are **"Saved Applications"**. They expire automatically: *"Saved applications are removed after 3 months from its submitted date."*
- Status values are exactly: `Approved`, `Denied`, `Pending`.

### Punctuation, copy quirks
- Exclamation marks appear in **one** place: the institutional tagline (*"...securing the future!"*). Avoid elsewhere.
- Italics are reserved for meta/helper notes (e.g. *"\*Note: Saved applications are removed..."*). They were previously also used for the *"Claims Portal"* wordmark; the EzCLAIMS mark that replaced it is upright, so italics no longer carry any brand meaning.
- Asterisk-prefixed notes (`*Note:`) are the convention for inline disclaimers.
- "Cards cannot be renewed before it's expiration date" — the live copy contains this typo (*it's* → *its*). Do not propagate it.

### Forbidden patterns
- ❌ **No emoji** anywhere in the product or in this design system. The brand is governmental — emoji read as unserious.
- ❌ No marketing exclamations ("Great!", "Easy!").
- ❌ No imperative-shouty CTAs ("Get started now").
- ❌ No persona ("Hi, I'm NIB!"). The institution speaks in a neutral register.

### Examples lifted from the live app

> *"All employed persons are required to register with the National Insurance Board and to receive an NIB card upon registration. To renew your card online, applicants must have an expired NIB card with a photograph and a signature affixed."*

> *"The National Insurance Board provides ten (10) cash benefits and four (4) cash assistance benefits. Benefits are awarded to persons who meet prescribed contribution conditions."*

> Inline warning banner: *"Before using this portal, your local office, contact and address information must be up to date."*

> Footer hours: *"Monday - Friday: 9:00AM - 5:00PM" / "Saturday & Sunday: Closed"*

---

## 4. Visual foundations

### Color
The palette is **navy-blue-led with a single warm accent**. The official mark contains five hues (navy, flamingo pink, sun yellow, water blue, reed green) but only navy + a complementary cadmium-orange make it into the product UI. Pinks, yellows, greens stay inside the logo.

- **Primary surfaces**: white (`#ffffff`) with subtle `shadow-sm`. Pages, cards, modals.
- **Brand primary**: Tailwind **blue-800** `#1e40af` — used for buttons, links, page-title text. Lighten = `blue-700` (hover), Darken = `blue-900` (deep gradients).
- **Brand accent**: **cadmium-orange** `#e27e2c` — appears *only* in the "Ez" of the EzCLAIMS wordmark. Exposed as the CSS custom property `--ez-orange` and the Tailwind alias `ez-orange`.
- **Brand secondary wordmark**: **navy** `#1a237e` — the "NIB Online" qualifier and the "CLAIMS" half of the mark. Exposed as `--ez-navy` / `ez-navy`.
- Both mark colours are declared in `src/assets/styles/index.css`, deliberately behind their own names so the wordmark can be re-tinted without touching the component or the page palette.
- **Login / portal-dark gradient**: `linear-gradient(180deg, #fff 0%, #7b8ecd 60%, #1e40af 100%)` (login splash, top→bottom) and `linear-gradient(340deg, #1e3a8a 0%, #3b82f6 100%)` (alternating portal sections).
- **Neutrals**: Tailwind `gray` + `blueGray` scales. The footer uses `gray-200`; table headers use `blueGray-100`; striped table rows use `blueGray-50`; inputs on the login screen use a custom `platinum-gray` `#e8e8e8`.
- **Status**: `green-600` (approved), `red-600` (denied), `blueGray-600` (pending), `amber-50/300/500/800` (callout warning box).

### Type
- **Single typeface — Sora** (Google Fonts, weights 300–800). Loaded via `<link>` in `index.html` and applied at `html, body`. Montserrat is the declared fallback in the Tailwind config but Sora is what users see.
- **Scale (in use)**: `text-xs` 12, `text-sm` 14, `text-base` 16, `text-lg` 18, `text-xl` 20, `text-2xl` 24, `text-3xl` 30, `text-4xl` 36, `text-5xl` 48, `text-6xl` 60.
- **Roles**:
  - `h1` (page title) — Sora **bold 24**, color = primary, capitalised.
  - `h2` (section) — Sora **semibold 20**, default fg.
  - `h3` (subsection) — Sora **light 18**.
  - Body — Sora regular 14–16, gray-700.
  - Meta / italic notes — Sora regular 12–14, gray-500, optionally italic.
  - Brand wordmark — Sora **extrabold** (top) + **black italic** (bottom).
  - Table headers — Sora **medium 12 uppercase**, `tracking-wider`, gray-500.
- **Tracking**: default; `tracking-wider` only on table headers; `tracking-widest` on portal sub-headlines; `tracking-tight` on the wordmark.

### Spacing & layout
- Tailwind default 4-unit scale. Common rhythms: 4, 8, 16, 24, 32, 64, 96 px.
- Content max-widths: `max-w-7xl` (1280px — top nav, main content), `max-w-5xl` (footer), `max-w-2xl` (portal copy column on tablet).
- `.page-section` = `px-4 py-8 shadow-sm rounded-md` — the canonical card.
- Forms use a 1-col → 3-col grid (`form-content`) where the right 2 columns hold inputs and the left holds the section title (classic government-form layout).

### Backgrounds & imagery
- **Predominantly flat white**. No textures, no patterns, no full-bleed photography.
- **Imagery is illustrative SVG**, not photographic — one illustration per benefit (`/img/benefits/*.svg`), plus two "portal" illustrations on the home page (`claims.svg`, the NIB card mock-up PNG).
- The home page uses **alternating dark-blue and white portal bands** (`linear-gradient(340deg, …)`) — the only place the design uses a non-white background at scale.
- The login splash uses a **vertical 3-stop gradient** white → pastel blue → primary blue, with the round logo centred.

### Corners & cards
- Buttons → `rounded` (4px) by default; `rounded-xl` (12px) for the login form's primary CTA.
- Inputs → `rounded-md` (6px); login inputs upgrade to `rounded-xl`.
- Cards / `.page-section` / modals → `rounded-md` (6px); top-level claims wrappers occasionally `rounded-lg` (8px).
- Status chips → `rounded-md` (not pill).
- Avatars → `rounded-full`.
- **Cards = white surface + `shadow-sm` + `rounded-md` + no border** (or `border-blueGray-100` on tables). No left-border accent stripes. No gradient borders.

### Shadows / elevation
- `shadow-sm` — every input, button, page-section, table wrapper.
- `shadow` — default cards (rare).
- `shadow-lg` — dropdown menus, modal panels.
- No inner shadows. No coloured shadows.

### Borders
- Inputs: `border-gray-300`, focus `ring-gray-400 + border-gray-400` (calm grey ring, not coloured).
- Mobile nav (active state): `border-l-4` indigo accent — the **only** left-accent-stripe in the system.
- Footer: thin `border-t border-gray-300` divider.

### Hover & press
- Buttons darken from `primary` → `primaryLighten` (blue-800 → blue-700). Note: the names are counter-intuitive — "lighten" is actually slightly *darker* in the Tailwind scale because blue-700 is darker than blue-800 in some Tailwind v2 builds; the developer just chose this naming. Treat *Lighten* as the hover token.
- Tertiary links: `text-indigo-600` → `text-indigo-500` (lighter on hover).
- Social icons / soft links: opacity → 80%.
- Table rows: full row turns `primaryLighten` background + white text (`group-hover` pattern).
- **No transform-based press states** (no `scale(0.97)` etc.). Buttons get `cursor-not-allowed` + `bg-gray-300` when disabled.

### Motion
- The only animations are **Headless UI menu transitions**: `ease-out duration-100/200` enter, `ease-in duration-75` leave, `opacity-0 scale-95` → `opacity-100 scale-100`. Used for the profile dropdown, the "Apply for a Benefit" menu, and modals.
- No page transitions. No scroll animations. No bounces.
- `@vueuse/motion` is installed but used sparingly.

### Transparency & blur
- No backdrop blur. No glassmorphism.
- Modals use a flat semi-transparent overlay (vue-final-modal default).
- Focus rings use `ring-opacity-5` on dropdowns (`ring-1 ring-black ring-opacity-5`) — a hairline edge, not a glow.

### Fixed elements
- Top navigation: not sticky in code, sits at the top of the page (`bg-white shadow-sm`).
- Footer: standard flow, gray-200 background, includes social icons + hours + supported-browsers strip + copyright.
- Loading spinner: appears at `fixed bottom-10 right-10` during login.

### Iconography
See **§ 5. Iconography** below.

---

## 5. Iconography

The NIB portal uses **two icon libraries plus a small set of one-off SVG illustrations**:

| Source | Where it's used | Style |
|---|---|---|
| **Heroicons (Vue v1 — "outline" variant)** | All navigational / UI icons: `MenuIcon`, `XIcon`, `UserCircleIcon`, `ChevronDownIcon`, `ExclamationIcon`. 24×24, **1.5px stroke**, no fill. | Outline / stroke |
| **Font Awesome 6 (free-solid-svg-icons)** | Imported in `package.json` but used only incidentally — a few inline solid glyphs. | Solid fill |
| **Custom illustration SVGs** | One per benefit type, plus two portal illustrations. Multi-colour, mid-detail. Located in `assets/benefits/` and `assets/`. | Spot illustration |
| **Inline SVG paths** | Social icons (Facebook → brand blue `#3b5998`, Instagram → brand pink `#d62976`) drawn in `DefaultLayout.vue`. | Brand glyphs, filled |

### Rules
- **Default icon style = Heroicons outline 24×24 with 1.5 stroke.** When picking a new icon, match this look. From CDN: `https://cdn.jsdelivr.net/npm/heroicons@1.0.6/outline/<name>.svg`. We use Heroicons **v1** to match the live app (`@heroicons/vue@1.0.5`) — v2 is similar but slightly redrawn.
- **Sized in increments of 4**: `h-4 w-4`, `h-5 w-5` (inline-with-text), `h-6 w-6` (nav), `h-8 w-8` (user-circle avatar).
- **Colour follows text**: icons inherit `currentColor`. Coloured icons only inside the brand mark and social icons.
- **No emoji.** No unicode glyphs as icons. No iconfonts beyond Font Awesome's incidental presence.
- For benefit illustrations, use the SVG in `assets/benefits/<benefit>.svg` directly. They are mid-saturation, slightly playful, but stay within the navy-blue palette.

### Font substitution
None. **Sora** is loaded directly from Google Fonts — no local TTF files in the source. This design system points at the same Google Fonts CDN URL, so no substitution is required.

---

## 6. Index — what's in this folder

```
.
├── README.md                       ← you are here
├── SKILL.md                        ← Agent SKills-compatible entrypoint
├── colors_and_type.css             ← CSS custom properties + semantic classes
├── assets/                         ← logos, illustrations, mocks (copied from source)
│   ├── nib-logo-no-text.png        ← roundel mark (used in app nav)
│   ├── nib-logo-full.png
│   ├── nib-logo-transparent.png
│   ├── nib-logo-new-2025.png       ← updated official mark (2025)
│   ├── nib-logo-updated.png
│   ├── nib-card-mockup.png         ← physical NIB card render
│   ├── ezrenew_logo.png            ← EzRenew sub-brand
│   ├── ezrenew1.png, ezrenew2.png
│   ├── claims.svg, online-claim-submission.svg
│   ├── browsers.png                ← footer "supported browsers" strip
│   ├── favicon-16x16.png, favicon-32x32.png
│   └── benefits/
│       ├── funeral.svg
│       ├── industrial.svg
│       ├── maternity.svg
│       ├── retirement.svg
│       ├── sickness.svg
│       └── unemployment.svg
├── preview/                        ← design-system cards (registered for the DS tab)
│   ├── logo.html
│   ├── colors-primary.html
│   ├── colors-brand.html
│   ├── colors-neutral.html
│   ├── colors-semantic.html
│   ├── type-display.html
│   ├── type-scale.html
│   ├── type-roles.html
│   ├── radii-shadows.html
│   ├── spacing.html
│   ├── buttons.html
│   ├── inputs.html
│   ├── chips.html
│   ├── callouts.html
│   ├── tables.html
│   └── benefits-illustrations.html
└── ui_kits/
    └── nib-online-portal/          ← The single product (see §2)
        ├── README.md
        ├── index.html              ← interactive click-through prototype
        └── *.jsx                   ← component recreations
```

---

## 7. Notes & caveats

- **One product, two sub-brands**: the only "product" surface is the Online Portal itself. Inside, the home page splits into two themed bands (EzCLAIMS + EzRENEW). The UI kit recreates the shared shell and the EzCLAIMS flow, since that's where 90% of the codebase lives.
- **No marketing site** was provided. If NIB has a separate public-facing nib-bahamas.com site, treat this system as **portal-only** and verify the marketing brand separately.
- **No mobile app** was provided; the portal is responsive web, mobile-first at the breakpoints `sm` 640, `md` 768, `lg` 1024.
- **Sora** is the only typeface. Montserrat is declared as a fallback in the Tailwind config but is never seen.
- The 2025 logo (`assets/nib-logo-new-2025.png`) is more recent than the in-app PNG; prefer it for new artefacts.

---

## 8. Further reading

To extend or rebuild this design system, browse the source repository:
**https://github.com/NIB-DEVELOPMENT/online-claims-submissions-frontend**

Useful entry points:
- `tailwind.config.js` — full custom palette
- `src/views/Login.vue`, `src/views/home/HomeIndex.vue` — splash + home
- `src/components/branding/EzClaimsBrand.vue` — wordmark recipe (four lockups × three sizes), with its metrics in the sibling `ezClaimsBrand.ts` so they can be unit tested without a DOM
- `src/components/branding/ClaimsPortalBrand.vue` — the retired *"Claims Portal"* wordmark, **retained on purpose** so the previous brand can be restored if the decision is reversed. Not dead code; do not prune.
- `src/components/layout/DefaultLayout.vue` — top nav + footer
- `src/components/auth/forms/LoginForm.vue` — form anatomy
- `src/views/claims/index.vue` — table + status-chip pattern
