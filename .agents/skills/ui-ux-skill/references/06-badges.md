# 6. Badges

**Description**: Semantic badges using brand colors with low opacity backgrounds (10%) and borders (20%).

**CSS Example**:
```css
.ssg-badge { 
  display: inline-flex; 
  align-items: center; 
  padding: 0.125rem 0.625rem; 
  border-radius: 99px; 
  font-size: 0.75rem; 
  font-weight: 500; 
  border: 1px solid transparent; 
}
.ssg-badge-primary { 
  background: rgba(77, 29, 130, 0.1); 
  color: var(--color-dark-purple); 
  border-color: rgba(77, 29, 130, 0.2); 
}
.ssg-badge-danger { 
  background: rgba(207, 2, 43, 0.1); 
  color: var(--color-red); 
  border-color: rgba(207, 2, 43, 0.2); 
}
.ssg-badge-success { 
  background: #d1fae5; 
  color: #065f46; 
  border-color: #a7f3d0; 
}

**HTML**: Use semantic markup with aria-label for icon-only badges:
```html
<span class="ssg-badge ssg-badge-primary" aria-label="Critical priority"><i class="icon-alert"></i></span>
```
```
