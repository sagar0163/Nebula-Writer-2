## 2026-05-23 - Interactive Div Elements Lack Keyboard Support
**Learning:** Entity cards in this application were built using `<div>` elements with `@click` handlers, making them inaccessible to keyboard users and screen readers. This is a common pattern in Vue applications without strict accessibility linting.
**Action:** When building custom interactive elements, always include `tabindex="0"`, `@keydown.enter`, and `@keydown.space.prevent` handlers, along with visible focus states (e.g., `focus:outline-none focus:ring-2`) to ensure keyboard navigability.
