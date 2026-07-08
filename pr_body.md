💡 **What:** Added a visual empty state for the Story Codex view when there are no entities.
🎯 **Why:** Previously, if a user navigated to the Codex with no items, they just saw a blank area (an empty CSS grid). This enhancement provides a clear explanation of what the Codex is and a prominent call-to-action button to start building their world.
📸 **Before/After:** (See attached PR screenshots showing the blank grid vs. the new glass panel empty state)
♿ **Accessibility:** Added `aria-hidden="true"` to the decorative book icon within the empty state so screen readers don't read out irrelevant graphics, focusing only on the text and actionable button.
