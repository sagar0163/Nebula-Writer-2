
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.

## 2024-05-18 - Empty States in Complex Views
**Learning:** For complex views like the Story Codex, empty states benefit from specific styling (glass panels: `.glass.rounded-2xl`, `.border-space-600`) to match the deep-space/cyberpunk aesthetic. Using a muted, centered SVG icon with `aria-hidden="true"`, helper text, and a prominent call-to-action (`.btn-primary`) improves usability and keeps users oriented.
**Action:** When adding empty states to grid/list views, use the glass panel pattern to maintain visual harmony and reduce visual noise for screen readers by marking decorative icons as hidden.
