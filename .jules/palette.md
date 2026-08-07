
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.

## 2024-05-24 - Glass Panel Empty States
**Learning:** Complex views (like the Story Codex) can feel confusing when they are empty because the intended data structure isn't visible.
**Action:** When a main feature view has no data, use a standardized "empty state" glass panel (`.glass.rounded-2xl`, `.border-space-600`) with a centered, muted icon (`aria-hidden="true"`), informative text about the feature's purpose, and a prominent primary CTA button (`.btn-primary`) to initiate the first action.
