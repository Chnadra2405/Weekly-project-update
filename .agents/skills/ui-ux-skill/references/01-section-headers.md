# 1. Section Headers

**Description**: Headers must include a subtle gradient underline to reinforce branding without overwhelming the content.

**HTML Example**:
```html
<section>
    <header class="ssg-section-header">
        <i class="icon" aria-hidden="true"></i>
        <h2>Section Title</h2>
        <div class="ssg-gradient-underline" aria-hidden="true"></div>
    </header>
    <!-- Content follows -->
</section>
```

**CSS Example**:
```css
.ssg-section-header { position: relative; display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem; }
.ssg-section-header h2 { font-weight: 700; color: var(--color-black); margin: 0; outline: none; }
.ssg-section-header h2:focus-visible { outline: 2px solid var(--color-dark-purple); outline-offset: 2px; border-radius: 2px; }
.ssg-gradient-underline {
    position: absolute; bottom: 0; left: 0; width: 100%; height: 2px;
    background: var(--brand-gradient); opacity: 0.6; border-radius: 99px;
}
```
