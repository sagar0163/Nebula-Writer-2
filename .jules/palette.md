
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.

## 2024-06-14 - Empty States as Onboarding Opportunities
**Learning:** Complex views like the Story Codex can feel daunting or broken when empty. Providing a structured empty state with a muted icon, explanation, and a clear primary CTA reduces cognitive load and naturally guides users to their next action.
**Action:** Implement structured empty states (using `.glass.rounded-2xl` and `.btn-primary`) for all list-based or complex data views when they are empty, rather than just showing nothing or a raw "0 items" message.
