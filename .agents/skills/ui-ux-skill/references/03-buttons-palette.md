# 3. Buttons Palette

**Description**: A strict hierarchy of buttons using the full brand palette.

**Usage**:
- **Primary** (Dark Purple): Main action.
- **Secondary** (Light Purple): Accent/Focus action.
- **Tertiary** (White/Border): Cancel or neutral action.
- **Danger** (Red): Destructive action.
- **Warning** (Orange): Alert/Status action.
- **System** (Very Dark Purple): High contrast/System action.

---

## HTML Example

```html
<button class="ssg-btn ssg-btn-primary">Save Changes</button>
<button class="ssg-btn ssg-btn-secondary">Learn More</button>
<button class="ssg-btn ssg-btn-tertiary">Cancel</button>
<button class="ssg-btn ssg-btn-danger">Delete</button>
<button class="ssg-btn ssg-btn-warning">Review</button>
<button class="ssg-btn ssg-btn-system">System Action</button>

<!-- Icon-only button (must have aria-label) -->
<button class="ssg-btn ssg-btn-primary" aria-label="Close dialog"><i class="icon-close"></i></button>
```

---

## CSS Example

```css
.ssg-btn { 
  padding: 0.5rem 1rem; border: none; border-radius: 0.375rem; font-weight: 500; 
  cursor: pointer; transition: all 0.2s; font-size: 0.875rem; outline: none;
}
.ssg-btn:focus-visible { outline: 2px solid var(--color-dark-purple); outline-offset: 2px; }
.ssg-btn-primary { background: var(--color-dark-purple); color: white; }
.ssg-btn-primary:hover { background: #3d1566; }
.ssg-btn-secondary { background: var(--color-light-purple); color: white; }
.ssg-btn-tertiary { background: white; color: var(--color-dark-purple); border: 2px solid #d4d4d4; }
.ssg-btn-tertiary:hover { border-color: var(--color-dark-purple); background: #f5f5f5; }
.ssg-btn-danger { background: var(--color-red); color: white; }
.ssg-btn-warning { background: var(--color-orange); color: white; }
.ssg-btn-system { background: var(--color-very-dark-purple); color: white; }
.ssg-btn:disabled { opacity: 0.6; cursor: not-allowed; }
```

**Note**: Tertiary button uses 2px border for better contrast against light backgrounds (≥ 3:1).

---

## Optional: Blazor example

Optional Blazor-specific snippet — the HTML/CSS example above is the canonical reference. Keep this only if your project uses Blazor; otherwise skip.

```razor
@page "/button-demo"

<div class="button-container">
    <button class="ssg-btn ssg-btn-primary" @onclick="HandleSave">Save Changes</button>
    <button class="ssg-btn ssg-btn-secondary" @onclick="HandleLearnMore">Learn More</button>
    <button class="ssg-btn ssg-btn-tertiary" @onclick="HandleCancel">Cancel</button>
    <button class="ssg-btn ssg-btn-danger" @onclick="HandleDelete" disabled="@isDeleting">
        @if (isDeleting)
        {
            <span>Deleting...</span>
        }
        else
        {
            <span>Delete</span>
        }
    </button>
</div>

@code {
    private bool isDeleting = false;

    private async Task HandleSave()
    {
        // Save logic
        await Task.CompletedTask;
    }

    private void HandleLearnMore()
    {
        // Navigation logic
    }

    private void HandleCancel()
    {
        // Cancel logic
    }

    private async Task HandleDelete()
    {
        isDeleting = true;
        StateHasChanged();
        
        // Simulate async delete operation
        await Task.Delay(1000);
        
        isDeleting = false;
        StateHasChanged();
    }
}
```

---

## CSS Example
```css
.ssg-btn { 
    border-radius: 0.375rem; 
    padding: 0.5rem 1rem; 
    font-weight: 500; 
    color: white; 
    border: none; 
    cursor: pointer; 
    transition: all 0.2s; 
}
.ssg-btn-primary { background-color: var(--color-dark-purple); }
.ssg-btn-secondary { background-color: var(--color-light-purple); }
.ssg-btn-tertiary { 
    background-color: white; 
    color: var(--color-black); 
    border: 1px solid var(--color-grey); 
}
.ssg-btn-danger { background-color: var(--color-red); }
.ssg-btn-warning { background-color: var(--color-orange); }
.ssg-btn-system { background-color: var(--color-very-dark-purple); }
.ssg-btn:hover { 
    opacity: 0.9; 
    transform: translateY(-1px); 
    box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
}
```
