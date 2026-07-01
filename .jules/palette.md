
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.

## 2024-05-20 - [Add Empty State to Story Codex]
**Learning:** [Complex views like Story Codex need robust empty states to guide users. The established pattern uses a glass panel with a muted ARIA-hidden icon and a prominent call-to-action button, ensuring both visual consistency and accessibility.]
**Action:** [Always check for and implement empty states when dealing with dynamic list or grid views, using the existing `.glass.rounded-2xl` and `.btn-primary` classes.]
