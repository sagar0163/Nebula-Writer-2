
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.

## 2024-06-17 - Complex View Empty States
**Learning:** The complex 'Story Codex' view lacked an empty state when no entities were present, making the screen look broken or confusing for new projects. Adding a clear empty state with a call-to-action button improves onboarding.
**Action:** When creating complex views that render lists/grids of data (like entities, chapters), always ensure a structured empty state (`.glass.rounded-2xl`, centered muted icon with `aria-hidden="true"`, informative text, and a `.btn-primary` CTA) is present when the collection length is 0.
