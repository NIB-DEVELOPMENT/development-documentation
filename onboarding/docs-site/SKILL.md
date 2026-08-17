---
name: nib-design
description: Use this skill to generate well-branded interfaces and assets for the NIB Online Portal (The National Insurance Board of The Commonwealth of The Bahamas), either for production or throwaway prototypes / mocks / decks. Contains essential design guidelines, color tokens, typography, fonts, logo assets, benefit illustrations, and a UI kit of React components for prototyping.
user-invocable: true
---

Read the `README.md` file within this skill, and explore the other available files.

If creating visual artifacts (slides, mocks, throwaway prototypes, etc.), copy assets out and create static HTML files for the user to view, link `colors_and_type.css` and reference `assets/` directly. If working on production code, you can copy assets and read the rules here to become an expert in designing with this brand.

If the user invokes this skill without any other guidance, ask them what they want to build or design, ask some questions, and act as an expert designer who outputs HTML artifacts _or_ production code, depending on the need.

## Quick orientation

- **Brand**: The National Insurance Board (NIB), government social-security authority of The Bahamas. Voice is **formal, official, reassuring**. No emoji, no exclamation marks except in the institutional tagline.
- **Primary color**: `#1e40af` (Tailwind blue-800). Hover `#1d4ed8`. Deep `#1e3a8a`.
- **Accent**: cadmium-orange `#e27e2c`, used *only* in the "Ez" of the **EzCLAIMS** wordmark (`--ez-orange`). Replaced the former italic "Claims Portal" half on 2026-07-29; the new mark is upright.
- **Typeface**: **Sora** (Google Fonts, weights 300–800). Loaded via `colors_and_type.css`.
- **Shape language**: white surfaces, `shadow-sm`, `rounded-md` (6px) cards. No gradients in UI chrome (only login splash and the alternating home-page bands).
- **Icons**: Heroicons outline 24×24, 1.5 stroke. Never emoji.
- **Status chips**: `Approved` (green-600), `Denied` (red-600), `Pending` (blueGray-600).

## Key files

| Path | What's in it |
|---|---|
| `README.md` | Full company context, content rules, visual foundations, iconography rules |
| `colors_and_type.css` | All design tokens as CSS custom properties + semantic classes (`h1.page-title`, `.brand-top`, `.chip`, etc.) |
| `assets/` | Logos (incl. the updated 2025 mark), benefit illustrations, NIB-card mockup, EzRenew sub-brand, browsers strip |
| `ui_kits/nib-online-portal/` | Click-through React prototype + reusable component JSX |
| `preview/*.html` | Per-token / per-component preview cards (also surfaced in the Design System tab) |

## Patterns to follow

- Page titles: `<h1 class="page-title">`, Sora bold 24, color = primary, capitalized.
- Forms use 3-col grid `form-content`: section title on left, inputs span the right 2 columns.
- Tables: `blueGray-100` header, `blueGray-50` zebra rows, `text-xs uppercase tracking-wider` headers.
- Buttons: `rounded` 4px default; `rounded-xl` 12px on the login CTA only.
- Inputs: `rounded-md` 6px default; login inputs use `bg-platinum-gray rounded-xl`.
- Hover: darken background (primary → primaryLighten). No scale/transform effects.
- Animations: only Headless-UI dropdown transitions (`ease-out duration-100` enter, `ease-in duration-75` leave).

## Forbidden

- ❌ Emoji
- ❌ Bluish-purple gradients (the only purple in the system is `maj-blue` for the light portal band)
- ❌ Hand-drawn SVG icons, use Heroicons outline or the existing benefit SVGs in `assets/benefits/`
- ❌ Marketing exclamations or chatty copy
- ❌ Left-border accent stripes on cards (one exception: mobile nav active state)

## Further reading

- Original repo: https://github.com/NIB-DEVELOPMENT/online-claims-submissions-frontend
- Live wordmark recipe: `src/components/branding/EzClaimsBrand.vue` (metrics in `ezClaimsBrand.ts`). The retired `ClaimsPortalBrand.vue` is kept alongside it on purpose for rollback, do not prune it.
- Custom Tailwind palette: `tailwind.config.js`
