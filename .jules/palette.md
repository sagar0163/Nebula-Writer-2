
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.

## 2024-05-25 - Informative Empty States in Complex Views
**Learning:** Complex data views (like the Story Codex) appear broken or confusing when empty. Simply showing an empty grid provides zero guidance to the user on what the feature is for or what action to take next.
**Action:** Always implement a dedicated empty state for complex data views. Use a prominent, centered visual treatment (like a glass panel), an `aria-hidden="true"` muted icon, explanatory text, and a clear, primary call-to-action button to guide the user's next step.
