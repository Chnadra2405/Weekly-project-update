# 8. Search Input

**Description**: Rounded full input with icon inside.

**CSS Example**:
```css
.search-input-wrapper { position: relative; color: #737373; }
.search-input-wrapper svg { position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%); width: 1rem; height: 1rem; pointer-events: none; }
.search-input { padding-left: 2.5rem; padding-right: 0.75rem; border-radius: 9999px; background-color: #fafafa; border: 1px solid #e5e5e5; outline: none; transition: all 0.2s; }
.search-input:focus-visible { border-color: var(--color-dark-purple); box-shadow: 0 0 0 3px rgba(77,29,130,0.1); }
```
