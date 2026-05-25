## 2024-05-14 - Aria Labels for Vue Icons
**Learning:** Icon-only buttons in the Vue application required manual ARIA labels and tooltips, as the existing Tailwind classes did not provide screen reader text automatically.
**Action:** Always verify icon-only interactive elements contain `aria-label` and `title` attributes.
## 2026-05-25 - Add aria-hidden to decorative icons
**Learning:** Found multiple instances of decorative `<svg>` and `<i>` icons inside `<button>` tags that already possessed an `aria-label`. These inner icons were missing `aria-hidden="true"`, which can cause screen readers to announce redundant or confusing fallback information. This is a common pattern in this app's UI components.
**Action:** When adding or reviewing buttons with both an icon and an `aria-label` (or descriptive text content), ensure that the inner `<svg>` or font icon elements explicitly include `aria-hidden="true"` to hide them from the accessibility tree.
