const DATE_PATTERN = /^\d{4}-\d{2}-\d{2}$/;
const RICH_TEXT_FIELDS = new Set(["achievements", "initiatives", "next_weeks_plan"]);

function stripHtml(html) {
  return (html || "").replace(/<[^>]*>/g, "");
}

export function endOfWeek(startOfWeek) {
  if (!DATE_PATTERN.test(startOfWeek)) return "";
  const value = new Date(`${startOfWeek}T00:00:00Z`);
  if (Number.isNaN(value.getTime())) return "";
  value.setUTCDate(value.getUTCDate() + 6);
  return value.toISOString().slice(0, 10);
}

export function validateForm(values) {
  const errors = {};
  for (const field of ["start_of_week", "end_of_week", "team_project", "achievements", "initiatives", "next_weeks_plan"]) {
    const raw = values[field] || "";
    const check = RICH_TEXT_FIELDS.has(field) ? stripHtml(raw) : raw;
    if (!check.trim()) errors[field] = "This field is required.";
  }
  if (values.start_of_week && !DATE_PATTERN.test(values.start_of_week)) {
    errors.start_of_week = "Choose a valid start date.";
  }
  if (values.end_of_week && !DATE_PATTERN.test(values.end_of_week)) {
    errors.end_of_week = "Choose a valid end date.";
  }
  if (values.start_of_week && values.end_of_week && values.end_of_week !== endOfWeek(values.start_of_week)) {
    errors.end_of_week = "End of week must be six days after start of week.";
  }
  return errors;
}