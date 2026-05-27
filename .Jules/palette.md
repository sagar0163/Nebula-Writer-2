## 2024-05-14 - Aria Labels for Vue Icons
**Learning:** Icon-only buttons in the Vue application required manual ARIA labels and tooltips, as the existing Tailwind classes did not provide screen reader text automatically.
**Action:** Always verify icon-only interactive elements contain `aria-label` and `title` attributes.
## 2026-05-27 - [Reduce Screen Reader Noise]
**Learning:** When using decorative inline SVGs inside interactive elements (like buttons) that already have text content or `aria-label` attributes, the screen reader may announce the SVG unnecessarily, causing confusion.
**Action:** Always include `aria-hidden="true"` on the `<svg>` element inside such buttons to ensure a cleaner and less noisy experience for screen reader users.
