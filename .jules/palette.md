
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.

## 2024-05-25 - Guided Empty States in Complex Views
**Learning:** Complex views like the Story Codex can feel like a dead-end when empty, leaving users unsure of how to begin.
**Action:** Always provide guided empty states for complex lists/grids using the established design pattern (glass panel, muted icon with `aria-hidden="true"`, informative helper text, and a prominent primary CTA button) to encourage user action and onboarding.
