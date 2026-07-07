
## 2024-05-24 - Screen Reader Noise from Inline SVGs
**Learning:** Legacy UI components (like buttons and links) with explicit text or `aria-label`s were exposing nested inline SVGs to assistive technologies, causing repetitive/confusing screen reader output.
**Action:** When adding inline SVGs (like Heroicons or FontAwesome) inside interactive elements with existing context, explicitly add `aria-hidden="true"` to the SVG node.

## 2026-07-07 - Add Empty State to Story Codex
**Learning:** Implementing empty states in data-heavy views prevents user confusion and serves as a critical onboarding touchpoint. Reusing standard glass/glass-panel UI patterns and call-to-action buttons here reinforces consistent app behavior.
**Action:** Always verify complex lists or grid views have a fallback `v-if="items.length === 0"` empty state with clear guidance and actionable 'create/add' buttons.
