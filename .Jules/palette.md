## 2024-05-14 - Aria Labels for Vue Icons
**Learning:** Icon-only buttons in the Vue application required manual ARIA labels and tooltips, as the existing Tailwind classes did not provide screen reader text automatically.
**Action:** Always verify icon-only interactive elements contain `aria-label` and `title` attributes.

## 2024-05-15 - Missing Icon Fonts
**Learning:** Found `<i class="fas fa-..."></i>` tags used for icons, but FontAwesome is not included as a dependency in this project.
**Action:** Always verify icon dependencies and replace external font-based icons with inline SVG Heroicons. Ensure that the SVG elements have `aria-hidden="true"` so they don't cause screen reader noise for buttons that already have `aria-label` or visible text.

## 2024-06-28 - Empty States for Complex Views
**Learning:** Found that the Story Codex view lacked an empty state when no entities were loaded, leaving a blank and unhelpful interface.
**Action:** Implemented a standardized empty state pattern using a glass panel, a muted icon with `aria-hidden="true"`, informative text, and a call-to-action button to guide users. Always verify that dynamic lists have a fallback empty state.
