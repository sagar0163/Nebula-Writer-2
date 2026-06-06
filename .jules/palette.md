
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.
## 2026-06-06 - AI Chat Input Accessibility and Feedback
**Learning:** Textareas intended as primary chat inputs in generative AI UIs often lack programmatic labels because they visually rely on placeholder text ("Talk to the AI..."), failing screen readers. Additionally, replacing the send icon with a loading spinner inline within the button provides crucial, frictionless state feedback during long inference delays without shifting layout.
**Action:** Always ensure chat `<textarea>` elements have an explicit `aria-label` (e.g., "Message input") regardless of placeholder content. When adding loading states to submit buttons, replace the existing icon inline with a spinner to maintain button dimensions and prevent layout shift.
