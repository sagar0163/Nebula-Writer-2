
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.
## 2024-10-24 - Empty State Micro-UX
**Learning:** Reusable UX pattern for empty states in complex data views like the Story Codex. Adding informative text and a clear primary Call-to-Action inside a visually distinct glass panel significantly improves user onboarding and guides interaction when there is no data to show.
**Action:** Consistently apply `.glass.rounded-2xl` with a centered muted icon (`aria-hidden="true"`) and `.btn-primary` CTAs for all complex empty states across the application.
