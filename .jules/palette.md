
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.

## 2024-07-08 - Added Empty State to Story Codex
**Learning:** Empty states in complex views like the Story Codex must explicitly guide the user on what action to take next. A simple empty grid provides no affordance.
**Action:** Always include a visual empty state block (e.g., `.glass.rounded-2xl` panel) with an informative text, a centered decorative icon (with `aria-hidden="true"`), and a primary call-to-action button when a core data collection is empty.
