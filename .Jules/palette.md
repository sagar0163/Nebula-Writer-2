## 2024-05-14 - Aria Labels for Vue Icons
**Learning:** Icon-only buttons in the Vue application required manual ARIA labels and tooltips, as the existing Tailwind classes did not provide screen reader text automatically.
**Action:** Always verify icon-only interactive elements contain `aria-label` and `title` attributes.
## 2026-05-28 - SVG Screen Reader Accessibility
**Learning:** When using inline SVG icons (like Heroicons) inside interactive elements (such as buttons or links) that already have text content or `aria-label` attributes, the SVG creates redundant noise for screen readers.
**Action:** Always include `aria-hidden="true"` on the `<svg>` element inside such interactive components.
