
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.

## 2026-07-02 - [Empty State Guidelines for Complex Data Views]
**Learning:** [Implementing a properly styled empty state for complex data views like the Story Codex (using a prominent glass panel, muted icon, clear description, and primary CTA button) drastically improves user discoverability and provides necessary guidance on system functionality that may otherwise be confusing when empty.]
**Action:** [Always include an empty state view consisting of a helpful message, muted icon with aria-hidden, and a prominent primary CTA pointing to the corresponding 'add' or 'create' flow for any complex data grids to enhance UX onboarding.]
