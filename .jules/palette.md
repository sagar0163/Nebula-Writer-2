
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.

## 2024-05-24 - Consistent Empty States for Complex Views
**Learning:** Complex internal views (like the Story Codex or manuscript management) lacked clear direction when empty, leading to a "dead end" user experience and confusing first impressions.
**Action:** Establish a standard empty state pattern using existing design tokens: a glass container (`.glass.rounded-2xl`, `.border-space-600`), a centered muted icon with `aria-hidden="true"`, informative text explaining the view's purpose, and a prominent primary CTA button (`.btn-primary`) to initiate content creation.
