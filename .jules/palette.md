
## 2024-05-24 - Avoiding External Icon Font Dependencies
**Learning:** Found instances of invisible buttons because the UI relied on external icon font classes (FontAwesome `fas fa-*`) that were never imported.
**Action:** Always prefer using inline SVGs (like Heroicons, matching the rest of the application's design system) over assuming global icon font availability to ensure critical UX actions remain visible and accessible.
