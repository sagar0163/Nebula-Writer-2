## 2024-05-14 - Aria Labels for Vue Icons
**Learning:** Icon-only buttons in the Vue application required manual ARIA labels and tooltips, as the existing Tailwind classes did not provide screen reader text automatically.
**Action:** Always verify icon-only interactive elements contain `aria-label` and `title` attributes.

## 2024-05-31 - Accessibility Screen Reader Noise from Decorative SVGs
**Learning:** Found instances where `<svg>` tags used purely for decorative purposes inside interactive `<button>` tags with `aria-label`s lacked the `aria-hidden="true"` attribute, leading to redundant noise for screen readers. In addition, some interactive buttons relied on external FontAwesome dependencies that were not optimal for a dependency-free frontend approach like the one used here.
**Action:** When adding inline SVGs (like Heroicons) inside interactive elements (such as buttons or links) that already have text content or `aria-label` attributes, always include `aria-hidden="true"` on the `<svg>` element to reduce noise for screen readers. Replace external icon font dependencies with standard inline SVGs whenever encountered.
