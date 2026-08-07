
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.

## 2024-10-27 - Complex View Empty States
**Learning:** Complex views that rely on collections (like the Story Codex grid) can appear broken or confusing to users when empty, with no intuitive way to understand their purpose or how to begin.
**Action:** Always implement a glass-panel empty state (`.glass.rounded-2xl`, `.border-space-600`) featuring a centered decorative icon (`aria-hidden="true"`), informative context text, and a prominent call-to-action button to guide the user's first interaction.
