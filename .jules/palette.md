
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.

## 2024-05-24 - Empty States in Complex Views
**Learning:** Empty states in complex views (like the Story Codex) can feel sparse and unintuitive without visual guidance, leaving users unsure of what to do next.
**Action:** When implementing empty states for list/grid views, use a centered glass panel (`.glass.rounded-2xl`, `.border-space-600`), a muted and decorative inline SVG icon (with `aria-hidden="true"`), informative text, and a prominent call-to-action button to guide the user's next steps.
