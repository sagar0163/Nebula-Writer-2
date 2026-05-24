## 2024-05-14 - Aria Labels for Vue Icons
**Learning:** Icon-only buttons in the Vue application required manual ARIA labels and tooltips, as the existing Tailwind classes did not provide screen reader text automatically.
**Action:** Always verify icon-only interactive elements contain `aria-label` and `title` attributes.

## 2024-05-24 - Accessibility for Decorative SVGs
**Learning:** Decorative inline SVGs (like Heroicons) used inside interactive elements (buttons) that already contain a descriptive `aria-label` or text content can cause repetitive or confusing noise for screen readers if not properly hidden.
**Action:** When replacing or adding icon-only buttons, always apply `aria-hidden="true"` to the `<svg>` tag to improve the screen reader experience.
