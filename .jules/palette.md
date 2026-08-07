
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.
## 2024-07-06 - Empty States for Complex Views
**Learning:** Complex views like the Codex feel broken or unresponsive when empty.
**Action:** Use a standardized empty state pattern (glass panel `.glass.rounded-2xl`, `.border-space-600`, muted aria-hidden icon, descriptive text, primary CTA) to guide the user.
