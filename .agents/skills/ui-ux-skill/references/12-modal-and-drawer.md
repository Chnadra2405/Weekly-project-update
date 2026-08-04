# 12. Modal & Drawer

**Description**: Overlays for dialogs and sidebars with backdrop blur.

**Accessibility**: Modals must trap focus and be dismissible by Esc key. On close, focus returns to trigger element.

**HTML Example**:
```html
<div class="ssg-overlay-backdrop" role="presentation">
    <div class="ssg-modal-content" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <header>
            <h2 id="modal-title">Dialog Title</h2>
            <button class="ssg-btn-close" aria-label="Close dialog">×</button>
        </header>
        <div class="ssg-modal-body">Content...</div>
    </div>
</div>
```

**CSS Example**:
```css
.ssg-overlay-backdrop {
    position: fixed; inset: 0; background: rgba(0,0,0,0.5); backdrop-filter: blur(4px);
    z-index: 50; display: flex; align-items: center; justify-content: center;
}
.ssg-modal-content {
    background: white; border-radius: 0.75rem; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
    max-width: 28rem; width: 100%; overflow: hidden; animation: zoomIn 0.2s ease-out; outline: none;
}
.ssg-modal-content:focus-visible { outline: 2px solid var(--color-dark-purple); }
.ssg-drawer {
    position: fixed; top: 0; right: 0; height: 100%; width: 20rem; background: white;
    z-index: 50; box-shadow: -10px 0 15px -3px rgba(0,0,0,0.1); transform: translateX(100%); 
    transition: transform 0.3s; outline: none;
}
.ssg-drawer.open { transform: translateX(0); }
.ssg-drawer:focus-visible { outline: none; }
```

**JS Note**: On modal open, focus first focusable element; on Esc key, close modal & return focus to trigger.
