## 2024-05-15 - [Add ARIA Labels to Icon-Only Buttons]
**Learning:** Icon-only buttons (like chat send, modal close, and list action buttons) without `aria-label` attributes create a significant accessibility barrier for screen reader users in this application. Screen readers cannot deduce the purpose of these buttons from SVGs or font-icons alone.
**Action:** Always ensure any button relying solely on visual iconography includes a descriptive `aria-label` attribute to convey its exact function.
