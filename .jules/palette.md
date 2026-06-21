
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.

## 2024-05-24 - Empty States for Complex Data Views
**Learning:** Complex internal application views like the Story Codex lack initial guidance when no data is present, which may confuse users trying to populate the database.
**Action:** When creating list-based views or data panels that may be empty, always implement a dedicated empty state containing an informative graphic/icon with `aria-hidden="true"`, descriptive text explaining what the view does, and a clear call-to-action button to initiate the primary data entry workflow.
