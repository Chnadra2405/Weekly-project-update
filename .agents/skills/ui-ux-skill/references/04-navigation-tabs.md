# 4. Navigation Tabs

**Description**: Tabs use a bottom gradient border to indicate the active state, maintaining a clean look.

**HTML Example**:
```html
<nav role="tablist" aria-label="User settings" class="tabs">
    <button role="tab" aria-selected="true" aria-controls="profile-panel" id="tab-profile" class="tab active">Profile</button>
    <button role="tab" aria-selected="false" aria-controls="settings-panel" id="tab-settings" class="tab">Settings</button>
</nav>
<div id="profile-panel" role="tabpanel" aria-labelledby="tab-profile">
    Profile content...
</div>
<div id="settings-panel" role="tabpanel" aria-labelledby="tab-settings" hidden>
    Settings content...
</div>
```

**Keyboard**: Arrow Left/Right to switch tabs; Tab to enter tab panel.

**CSS Example**:
```css
.tab {
    padding: 0.5rem 0.75rem;
    background: transparent;
    color: var(--color-grey);
    border: none; font-weight: 500; cursor: pointer; outline: none; transition: all 0.2s;
}
.tab:focus-visible {
    outline: 2px solid var(--color-dark-purple); outline-offset: -2px; border-radius: 2px;
}
.tab[aria-selected="true"] {
    color: var(--color-dark-purple);
    background-color: rgba(77, 29, 130, 0.05);
    position: relative;
}
.tab[aria-selected="true"]::after {
    content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 2px;
    background: var(--brand-gradient);
}
```
