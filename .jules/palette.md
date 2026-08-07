
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.

## 2024-05-19 - Added Empty State for Story Codex
**Learning:** Complex views like the Story Codex can appear broken or confusing when empty. Providing a clear empty state with an informative message and a prominent call-to-action reduces friction for new users.
**Action:** When creating new list or grid views, always implement a specific empty state following the standard glass panel pattern (`.glass.rounded-2xl`, `.border-space-600`) with a muted icon, description, and primary CTA.
