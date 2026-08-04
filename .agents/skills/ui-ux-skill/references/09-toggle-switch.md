# 9. Toggle, Checkbox & Radios

**Description**: Boolean controls styled with Sopra Steria colors. Toggles provide a modern switch, while checkboxes and radio buttons keep the same white background and focus treatment as other inputs.

## Toggle switch

**HTML Example**:
```html
<label class="switch">
  <input type="checkbox">
  <span class="slider round"></span>
</label>
```

**CSS Example**:
```css
.switch { position: relative; display: inline-block; width: 2.75rem; height: 1.5rem; }
.switch input { opacity: 0; width: 0; height: 0; }
.switch input:focus-visible + .slider { box-shadow: 0 0 0 3px rgba(77,29,130,0.2); }
.slider {
  position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
  background-color: #e5e5e5; transition: .4s; border-radius: 34px;
}
.slider:before {
  position: absolute; content: ""; height: 1.25rem; width: 1.25rem;
  left: 2px; bottom: 2px; background-color: white; transition: .4s; border-radius: 50%;
}
input:checked + .slider { background-color: var(--color-dark-purple); }
input:checked + .slider:before { transform: translateX(1.25rem); }
```

## Checkboxes

**HTML Example**:
```html
<div class="form-check">
  <input class="form-check-input" type="checkbox" value="" id="notify-weekly" checked>
  <label class="form-check-label" for="notify-weekly">Email me weekly updates</label>
</div>
<div class="form-check">
  <input class="form-check-input" type="checkbox" value="" id="notify-monthly">
  <label class="form-check-label" for="notify-monthly">Monthly digest</label>
</div>
```

**CSS Example**:
```css
.form-check-input {
  width: 1.1rem; 
  height: 1.1rem; 
  margin-top: 0.15rem;
  border: 1.5px solid #d4d4d4; 
  border-radius: 0.3rem;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.form-check-input:focus {
  border-color: var(--color-dark-purple);
  box-shadow: 0 0 0 3px rgba(77,29,130,0.4);
}
.form-check-input:checked {
  background-color: var(--color-dark-purple);
  border-color: var(--color-dark-purple);
}
.form-check-label {
  margin-left: 0.4rem; 
  font-size: 0.875rem; 
  color: #404040;
}
```

## Radio buttons

**HTML Example**:
```html
<div class="form-check">
  <input class="form-check-input" type="radio" name="status" id="status-active" checked>
  <label class="form-check-label" for="status-active">Active</label>
</div>
<div class="form-check">
  <input class="form-check-input" type="radio" name="status" id="status-paused">
  <label class="form-check-label" for="status-paused">Paused</label>
</div>
```

**CSS Example**:
```css
.form-check-input[type="radio"] {
  border-radius: 50%;
}
.form-check-input[type="radio"]:checked {
  background-color: transparent;
  border-color: var(--color-dark-purple);
  background-image: radial-gradient(circle at center, var(--color-dark-purple) 45%, transparent 50%);
}
.form-check-input[type="radio"]:focus {
  border-color: var(--color-dark-purple);
  box-shadow: 0 0 0 3px rgba(77,29,130,0.4);
}
```
