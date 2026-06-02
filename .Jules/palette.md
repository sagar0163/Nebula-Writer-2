## 2024-05-14 - Aria Labels for Vue Icons
**Learning:** Icon-only buttons in the Vue application required manual ARIA labels and tooltips, as the existing Tailwind classes did not provide screen reader text automatically.
**Action:** Always verify icon-only interactive elements contain `aria-label` and `title` attributes.

## 2024-06-02 - [Accessibility: aria-hidden on decorative icons]
**Learning:** Many interactive elements (like buttons) containing both an `aria-label` and an inline SVG/FontAwesome icon lacked `aria-hidden="true"` on the icon itself. This causes screen readers to redundantly announce the icon element alongside the button's explicit label, creating noise for visually impaired users.
**Action:** When adding inline SVG icons (like Heroicons) or FontAwesome icons inside interactive elements that already have text content or `aria-label` attributes, always include `aria-hidden="true"` on the icon element.
