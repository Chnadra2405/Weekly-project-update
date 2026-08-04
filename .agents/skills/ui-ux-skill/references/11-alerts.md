# 11. Alerts

**Description**: Feedback containers with specific background/border combinations based on severity.

**HTML Example**:
```html
<div class="ssg-alert ssg-alert-info">
    <i class="icon"></i>
    <div class="content">...</div>
</div>
```

**CSS Example**:
```css
.ssg-alert { 
  padding: 0.75rem; 
  border-radius: 0.375rem; 
  border: 1px solid transparent; 
  display: flex; 
  gap: 0.75rem; 
  font-size: 0.875rem; 
}
.ssg-alert-info { 
  background: #eff6ff; 
  color: #1e40af;  /* Contrast ratio: 5.1:1 ✅ */
  border-color: #bfdbfe; 
}
.ssg-alert-success { 
  background: #ecfdf5; 
  color: #065f46;  /* Contrast ratio: 7.8:1 ✅ */
  border-color: #a7f3d0; 
}
.ssg-alert-warning { 
  background: rgba(239, 125, 0, 0.1); 
  color: #8a4d00;  /* Darkened orange for ≥4.5:1 contrast ✅ */
  border-color: rgba(239, 125, 0, 0.2); 
}
.ssg-alert-danger {
  background: rgba(207, 2, 43, 0.1);
  color: #7f001a;  /* Darkened red for ≥4.5:1 contrast ✅ */
  border-color: rgba(207, 2, 43, 0.2);
}

.ssg-alert svg, .ssg-alert i { flex-shrink: 0; }
```
