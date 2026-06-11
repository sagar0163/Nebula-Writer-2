
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.

## 2026-06-11 - Add Empty State for Story Codex
**Learning:** Users need guidance when lists like Story Codex entities are empty. Complex empty states should use a glass panel (`.glass.rounded-2xl`, `.border-space-600`), a centered muted icon with `aria-hidden="true"`, informative text, and a prominent call-to-action button (`.btn-primary`).
**Action:** Always include empty states for lists that can be empty, following the standard codebase UI pattern for empty states.
