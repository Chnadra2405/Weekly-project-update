# 10. File Dropzone

**Description**: Dashed border area for drag & drop interactions. Support keyboard file input as alternative.

**HTML Example**:
```html
<label for="file-input" class="dropzone" role="button" tabindex="0" aria-label="Drag and drop files or click to select">
    <i class="dropzone-icon" aria-hidden="true"></i>
    <span>Drag files here or <strong>click</strong> to select</span>
    <input id="file-input" type="file" class="dropzone-input" hidden multiple>
</label>
```

**CSS Example**:
```css
.dropzone {
    display: flex; flex-direction: column; align-items: center; justify-content: center; outline: none;
    width: 100%; height: 8rem; border: 2px dashed #d4d4d4; border-radius: 0.5rem;
    background-color: #fafafa; cursor: pointer; transition: all 0.2s; padding: 1rem;
}
.dropzone:hover { background-color: #f5f5f5; border-color: var(--color-dark-purple); }
.dropzone:focus-visible { outline: 2px solid var(--color-dark-purple); outline-offset: 2px; }
.dropzone-icon { color: #a3a3a3; width: 2rem; height: 2rem; margin-bottom: 0.5rem; }
.dropzone-input { display: none; }
```
