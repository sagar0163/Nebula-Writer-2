## 2024-05-14 - Aria Labels for Vue Icons
**Learning:** Icon-only buttons in the Vue application required manual ARIA labels and tooltips, as the existing Tailwind classes did not provide screen reader text automatically.
**Action:** Always verify icon-only interactive elements contain `aria-label` and `title` attributes.

## 2026-05-21 - Component-less App Form A11y Pitfalls
**Learning:** In single-file component-less Vue applications like this one, it is easy to rely solely on visual placeholders for form inputs in modals rather than semantic labels. Without formal components enforcing accessibility props, developers often overlook programmatic labels entirely.
**Action:** Always check modal forms and raw input/textarea tags for missing `aria-label` or `<label>` associations when reviewing raw HTML templates.
