# 2. Cards

**Description**: Clean white containers with rounded corners (xl), subtle shadows, and a distinct header style.

**HTML Example**:
```html
<div class="ssg-card">
    <header class="ssg-card-header">
        <h3>Card Title</h3>
    </header>
    <div class="ssg-card-body">
        Content...
    </div>
</div>
```

**CSS Example**:
```css
.ssg-card {
    background: var(--color-white);
    border: 1px solid var(--color-light-grey);
    border-radius: 0.75rem;
    box-shadow: 0 1px 2px rgba(77, 29, 130, 0.1);
    overflow: hidden;
    display: flex;
    flex-direction: column;
}
.ssg-card-header {
    background: rgba(77, 29, 130, 0.1);
    padding: 0.75rem 1.25rem;
    border-bottom: 1px solid var(--color-light-grey);
    text-transform: uppercase;
    font-size: 0.875rem;
    font-weight: 600;
}
.ssg-card-body { 
  padding: 1.25rem; 
  flex: 1; 
}
```
