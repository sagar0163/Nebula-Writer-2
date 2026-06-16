
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.
## 2026-06-16 - Empty States for Complex Views
**Learning:** Users encountering complex, empty data views (like a Story Codex) without guidance can feel lost. A robust empty state provides immediate orientation and clear next steps.
**Action:** When creating or modifying complex list or grid views, always ensure an empty state exists that uses the glass panel pattern, features a muted icon, explains the view's purpose, and includes a primary CTA to create the first item.
