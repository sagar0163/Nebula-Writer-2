
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.

## 2024-06-08 - Complex View Empty States
**Learning:** Empty states in complex views like Story Codex need robust structural guidance for the user. A blank screen can lead to drop-off.
**Action:** Use a reusable glass panel pattern (`.glass.rounded-2xl`, `.border-space-600`) with a centered muted icon (using `aria-hidden="true"`), informative text, and a prominent primary call-to-action button (`.btn-primary`) to guide the user into creating their first entry.
