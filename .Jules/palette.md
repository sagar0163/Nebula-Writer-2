## 2024-05-14 - Aria Labels for Vue Icons
**Learning:** Icon-only buttons in the Vue application required manual ARIA labels and tooltips, as the existing Tailwind classes did not provide screen reader text automatically.
**Action:** Always verify icon-only interactive elements contain `aria-label` and `title` attributes.
## 2024-05-29 - Aria-Hidden for SVG Icons
**Learning:** Inline SVG icons inside interactive elements like buttons and links can create noise for screen readers, even if the element already has text or an `aria-label`.
**Action:** Always verify that `<svg>` tags within interactive elements use `aria-hidden="true"` to ensure a cleaner and less confusing experience for screen reader users.
