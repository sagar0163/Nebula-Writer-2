## 2024-06-03 - Vue Event Modifier Keyboard Interception
**Learning:** In Vue templates, `@keydown.enter.prevent` intercepts all enter keypresses, including those with modifiers like Shift+Enter, preventing their default behavior (like inserting a newline in a textarea).
**Action:** Always use the `.exact` modifier (`@keydown.enter.exact.prevent`) when listening for standard Enter in textareas if you want to preserve native modifier behaviors (like Shift+Enter for newlines).
