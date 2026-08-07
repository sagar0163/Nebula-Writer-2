
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.
## 2026-07-05 - Empty States in Story Codex
**Learning:** Empty states in complex views improve UX by providing clear guidance.
**Action:** Always include a glass panel, a muted icon, informative text, and a call-to-action button for empty states.
