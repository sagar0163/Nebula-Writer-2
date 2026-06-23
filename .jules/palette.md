
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.

## 2026-06-23 - Consistent aria-hidden on SVGs
**Learning:** Found multiple instances where SVGs lacked `aria-hidden="true"`, which can lead to screen reader noise, especially in nested components or those with their own ARIA labels.
**Action:** Applied `aria-hidden="true"` to all decorative inline SVGs throughout the frontend to ensure a consistent and accessible experience for screen reader users.
