
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.

## 2024-05-24 - Consistent Empty States for Complex Views
**Learning:** Complex studio views (like the Story Codex) previously rendered as empty grids without any guidance, leading to confusing empty states.
**Action:** When implementing empty states for list/grid views, use the established pattern: a glass panel (`.glass.rounded-2xl`, `.border-space-600`), a centered muted icon with `aria-hidden="true"`, informative guidance text, and a prominent call-to-action button (`.btn-primary`) to initiate the creation flow.
