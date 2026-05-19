## 2024-05-14 - Aria Labels for Vue Icons
**Learning:** Icon-only buttons in the Vue application required manual ARIA labels and tooltips, as the existing Tailwind classes did not provide screen reader text automatically.
**Action:** Always verify icon-only interactive elements contain `aria-label` and `title` attributes.

## 2026-05-19 - Empty States and Discoverability in Manuscript Editor
**Learning:** The chapters view lacked both an empty state and a clear call-to-action to create a new chapter, relying solely on AI interaction or external state changes. Users expect discoverable manual actions even in AI-first tools.
**Action:** Always provide explicit action buttons (e.g., '+ Add Chapter') and descriptive empty states for core entities to ensure manual workflows are not hidden behind conversational interfaces.
