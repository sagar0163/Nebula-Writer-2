
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.
## 2026-07-03 - [Add Story Codex Empty State]
**Learning:** Complex views like the Story Codex need an empty state pattern using glass panels and clear CTAs when data is missing, to guide user actions.
**Action:** Applied a consistent empty state layout for the entities view.
