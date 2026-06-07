## 2024-05-14 - Aria Labels for Vue Icons
**Learning:** Icon-only buttons in the Vue application required manual ARIA labels and tooltips, as the existing Tailwind classes did not provide screen reader text automatically.
**Action:** Always verify icon-only interactive elements contain `aria-label` and `title` attributes.

## 2024-05-15 - Missing Icon Fonts
**Learning:** Found `<i class="fas fa-..."></i>` tags used for icons, but FontAwesome is not included as a dependency in this project.
**Action:** Always verify icon dependencies and replace external font-based icons with inline SVG Heroicons. Ensure that the SVG elements have `aria-hidden="true"` so they don't cause screen reader noise for buttons that already have `aria-label` or visible text.

## 2026-06-07 - Empty States for Complex Views
**Learning:** Found that complex studio views (like the Story Codex) lack visual guidance when first opened without data, leaving users confused. Implementing an empty state with an icon and clear call-to-action improves usability.
**Action:** Always check complex views and lists for empty states, implementing a consistent glass panel pattern with a placeholder icon and a primary action button when data is missing.
