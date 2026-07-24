export const MAX_FILE_BYTES = 10 * 1024 * 1024;

export function validateForm(values, files) {
  const errors = {};
  for (const field of ["employee_name", "employee_email", "reporting_month", "team_project", "achievements", "initiatives", "next_weeks_plan"]) {
    if (!values[field]?.trim()) errors[field] = "This field is required.";
  }
  if (values.employee_email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.employee_email)) {
    errors.employee_email = "Enter a valid email address.";
  }
  if (values.reporting_month && !/^\d{4}-\d{2}$/.test(values.reporting_month)) {
    errors.reporting_month = "Choose a reporting month.";
  }
  if (files.reference_email && !/\.(eml|msg)$/i.test(files.reference_email.name)) {
    errors.reference_email = "Choose an EML or MSG file.";
  }
  if (files.image && !/\.(png|jpe?g|webp)$/i.test(files.image.name)) {
    errors.image = "Choose a PNG, JPEG, or WebP image.";
  }
  for (const [name, file] of Object.entries(files)) {
    if (file && file.size > MAX_FILE_BYTES) errors[name] = "File must be 10 MiB or smaller.";
  }
  return errors;
}