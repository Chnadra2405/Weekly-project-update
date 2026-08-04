# 7. Form Inputs

**Description**: Standard rounded inputs with specific focus states using the primary color ring. Includes masked inputs and error states.

---

## HTML Example

```html
<!-- Email -->
<div class="form-group">
    <label for="email-input">Email <span class="required">*</span></label>
    <input id="email-input" type="email" class="form-control" placeholder="name@example.com" aria-required="true">
</div>

<!-- Email with Error -->
<div class="form-group">
    <label for="email-error">Email <span class="required">*</span></label>
    <input id="email-error" type="email" class="form-control invalid" placeholder="name@example.com" aria-invalid="true" aria-describedby="email-error-msg">
    <p id="email-error-msg" class="helper-text error">Email is required.</p>
</div>

<!-- Password -->
<div class="form-group">
    <label for="password-input">Password</label>
    <input id="password-input" type="password" class="form-control" placeholder="••••••••">
</div>

<!-- Time & Date -->
<div class="form-group">
    <label for="standup-time">Daily Stand-up Time</label>
    <input id="standup-time" type="time" class="form-control">
</div>
<div class="form-group">
    <label for="launch-date">Launch Date</label>
    <input id="launch-date" type="date" class="form-control">
</div>

<!-- Field Group (Fieldset) -->
<fieldset>
    <legend>Contact Preferences</legend>
    <div class="form-check">
        <input class="form-check-input" type="checkbox" id="contact-email">
        <label class="form-check-label" for="contact-email">Email</label>
    </div>
    <div class="form-check">
        <input class="form-check-input" type="checkbox" id="contact-phone">
        <label class="form-check-label" for="contact-phone">Phone</label>
    </div>
</fieldset>

<!-- Dropdown -->
<div class="form-group dropdown form-field">
    <label for="release-train-btn">Release Train</label>
    <button id="release-train-btn" class="dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false" aria-haspopup="listbox" aria-label="Release train options">
        Select release train
    </button>
    <ul class="dropdown-menu" role="listbox">
        <li><a class="dropdown-item" role="option" href="#">Q1 Momentum</a></li>
        <li><a class="dropdown-item" role="option" href="#">Q2 Elevate</a></li>
        <li><a class="dropdown-item" role="option" href="#">Q3 Horizon</a></li>
    </ul>
</div>
```

---

## Optional: Blazor example

Optional Blazor-specific snippet — the HTML examples above are canonical for cross-framework usage. Keep this only if your project is Blazor-based.

```razor
@page "/user-form"

<div class="form-container">
    <EditForm Model="@userModel" OnValidSubmit="HandleSubmit">
        <DataAnnotationsValidator />
        
        <!-- Email -->
        <div class="form-group">
            <label>Email <span class="required">*</span></label>
            <InputText @bind-Value="userModel.Email" 
                       class="form-control" 
                       placeholder="name@example.com" />
            <ValidationMessage For="@(() => userModel.Email)" class="helper-text error" />
        </div>

        <!-- Password -->
        <div class="form-group">
            <label>Password</label>
            <InputText type="password" 
                       @bind-Value="userModel.Password" 
                       class="form-control" 
                       placeholder="••••••••" />
        </div>

        <!-- Date -->
        <div class="form-group">
            <label>Launch Date</label>
            <InputDate @bind-Value="userModel.LaunchDate" class="form-control" />
        </div>

        <!-- Dropdown -->
        <div class="form-group">
            <label>Release Train</label>
            <InputSelect @bind-Value="userModel.ReleaseTrain" class="form-control">
                <option value="">Select release train</option>
                <option value="Q1">Q1 Momentum</option>
                <option value="Q2">Q2 Elevate</option>
                <option value="Q3">Q3 Horizon</option>
            </InputSelect>
        </div>

        <button type="submit" class="ssg-btn ssg-btn-primary">Submit</button>
    </EditForm>
</div>

@code {
    private UserModel userModel = new();

    private async Task HandleSubmit()
    {
        // Handle form submission
        await Task.CompletedTask;
    }

    public class UserModel
    {
        [Required(ErrorMessage = "Email is required.")]
        [EmailAddress(ErrorMessage = "Invalid email format.")]
        public string Email { get; set; } = string.Empty;

        public string Password { get; set; } = string.Empty;
        
        public DateTime LaunchDate { get; set; } = DateTime.Today;
        
        public string ReleaseTrain { get; set; } = string.Empty;
    }
}
```

---

## CSS Examples

_Base labels & inputs_
```css
.form-group label { 
  display: block; 
  font-size: 0.875rem; 
  font-weight: 500; 
  color: #404040; 
  margin-bottom: 0.25rem; 
}
.form-group .required { color: var(--color-red); }
.form-control {
  width: 100%; 
  border-radius: 0.375rem; 
  border: 1px solid #d4d4d4;
  padding: 0.5rem 0.75rem; 
  box-shadow: 0 1px 2px rgba(0,0,0,0.05); 
  transition: border-color 0.2s, box-shadow 0.2s;
}
.form-control:focus {
    border-color: var(--color-dark-purple); 
    outline: none;
    box-shadow: 0 0 0 3px rgba(77, 29, 130, 0.4);
}
.form-control.invalid { 
  border-color: var(--color-red); 
  color: var(--color-red); 
}
```

_Dropdown override_
```css
.dropdown.form-field .dropdown-toggle {
    width: 100%; text-align: left; background-color: #fff; border: 1px solid #d4d4d4;
    border-radius: 0.375rem; padding: 0.5rem 2rem 0.5rem 0.75rem; box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    color: #404040; display: flex; align-items: center; justify-content: space-between; gap: 0.5rem;
}
.dropdown.form-field .dropdown-toggle:focus,
.dropdown.form-field .dropdown-toggle:focus-visible {
    border-color: var(--color-dark-purple); box-shadow: 0 0 0 3px rgba(77, 29, 130, 0.4);
}
.dropdown.form-field .dropdown-toggle::after { margin-left: 0; border-top-color: var(--color-dark-purple); }
.dropdown.form-field .dropdown-menu {
    width: 100%; border-radius: 0.5rem; border: 1px solid #ededed; box-shadow: 0 10px 30px rgba(32, 8, 59, 0.08);
}
.dropdown-item { padding: 0.5rem 0.75rem; }
.dropdown-item:hover { background-color: rgba(77, 29, 130, 0.05); color: var(--color-dark-purple); }
.dropdown-item.active,
.dropdown-item:active {
    background-color: rgba(77, 29, 130, 0.08); 
    color: var(--color-dark-purple);
}
```

_Helper text_
```css
.helper-text { font-size: 0.75rem; margin-top: 0.25rem; color: #737373; }
.helper-text.error { color: var(--color-red); }
```
