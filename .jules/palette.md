
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.

## 2024-06-25 - Glass Panel Empty States
**Learning:** Complex views (like the Story Codex) feel empty or confusing when they have no content. A consistent empty state pattern drastically improves the experience.
**Action:** Empty states in complex views should use a glass panel (`.glass.rounded-2xl`, `.border-space-600`), a centered muted icon with `aria-hidden="true"`, an informative text element, and a prominent call-to-action button (`.btn-primary`).
