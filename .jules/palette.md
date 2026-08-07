
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.

## 2024-07-04 - Empty States for Complex Views
**Learning:** Users can get lost when opening complex grid views (like the Story Codex) for the first time if there's no data. A blank screen with just an "+ Add" button isn't inviting.
**Action:** Always provide a styled empty state in main content areas using a muted icon, descriptive text explaining the view's purpose, and a prominent call-to-action button to help users start.
