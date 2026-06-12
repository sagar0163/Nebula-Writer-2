
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.

## 2024-06-12 - [Story Codex Empty State]
**Learning:** Empty states in complex data views like the Story Codex require visual anchors. A blank grid provides no affordance. Adding a glass-paneled empty state with a muted icon and a prominent call-to-action button significantly improves user onboarding and discoverability.
**Action:** Consistently apply this glass-paneled empty state pattern (`.glass.rounded-2xl`, muted `aria-hidden="true"` SVG icon, clear instruction, `.btn-primary` CTA) across all data-driven views when their collections are empty.
