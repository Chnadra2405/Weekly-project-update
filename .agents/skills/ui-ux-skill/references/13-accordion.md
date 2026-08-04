# 13. Accordion

**Description**: Details/Summary implementation with chevron rotation.

## HTML Example

```html
<div class="accordion-group">
    <details class="accordion" open>
        <summary class="accordion-header" role="button" aria-expanded="true" aria-controls="panel-1">Accordion Title</summary>
        <div id="panel-1" role="region" aria-labelledby="accordion-1" class="accordion-body">Content...</div>
    </details>
    <details class="accordion">
        <summary class="accordion-header" role="button" aria-expanded="false" aria-controls="panel-2">Another Title</summary>
        <div id="panel-2" role="region" aria-labelledby="accordion-2" class="accordion-body">More content...</div>
    </details>
</div>
```

**CSS Example**:
```css
details.accordion { border: 1px solid #e5e5e5; border-radius: 0.5rem; margin-bottom: 0.5rem; overflow: hidden; }
details.accordion[open] { border: 1px solid #d4d4d4; }
summary.accordion-header {
    background: #fafafa; padding: 1rem; cursor: pointer; font-weight: 500; outline: none; transition: all 0.2s;
    display: flex; justify-content: space-between; align-items: center;
}
summary.accordion-header:focus-visible { outline: 2px solid var(--color-dark-purple); outline-offset: -2px; }
details[open] summary.accordion-header { border-bottom: 1px solid #e5e5e5; }
summary::marker { display: none; }
.accordion-body { padding: 1rem; background: white; }
```
