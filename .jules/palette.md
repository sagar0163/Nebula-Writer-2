
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.

## 2024-06-09 - Empty State UX Pattern for Complex Views
**Learning:** Complex views like the Story Codex require informative empty states to guide the user. Using a glass panel, a muted icon with aria-hidden="true", and a prominent call-to-action button improves discoverability and reduces confusion when no data is present.
**Action:** Apply this empty state pattern (glass panel + muted icon + description + CTA) consistently across all list/grid views in the application when there are no items to display.
