## 2024-05-14 - Aria Labels for Vue Icons
**Learning:** Icon-only buttons in the Vue application required manual ARIA labels and tooltips, as the existing Tailwind classes did not provide screen reader text automatically.
**Action:** Always verify icon-only interactive elements contain `aria-label` and `title` attributes.

## 2024-05-18 - Missing Loading States
**Learning:** Found that async form submissions in modals (like saving a new entity) lacked loading states, leaving users without immediate feedback during API calls.
**Action:** Always add an `isSaving` state, disable the submit button, and show a loading spinner during async form saves to improve interaction feedback.
