# 15. Progress Bars

**Description**: Rounded bars showing completion percentage.

**CSS Example**:
```css
.ssg-progress-container { 
  width: 100%; 
  background-color: #e5e5e5; 
  border-radius: 9999px; 
  height: 0.625rem; 
  overflow: hidden; 
}
.ssg-progress-bar { 
  height: 100%; 
  border-radius: 9999px; 
  background-color: var(--color-dark-purple); 
  transition: width 0.3s ease; 
}
.ssg-progress-bar.warning { 
  background-color: var(--color-orange); 
}

**HTML**: Add `role="progressbar"` and `aria-valuenow` for screen readers:
```html
<div class="ssg-progress-container" role="progressbar" aria-valuenow="65" aria-valuemin="0" aria-valuemax="100" aria-label="Task progress">
    <div class="ssg-progress-bar" style="width: 65%;"></div>
</div>
```
```
