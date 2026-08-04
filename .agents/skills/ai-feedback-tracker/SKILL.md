---
name: ai-feedback-tracker
description: "Track AI failures, AI unexpected behavior & AI improvement suggestions. ALWAYS LOAD if an AI had an error while doing something specified in an Agent/Skill/... ALWAYS LOAD if an Agent/Skill/.. behaves outside of its specification. ALWAYS LOAD if you are doing something that could benefit to be add in Agent/Skill/... ALWAYS LOAD when user make you iterate on a problem.Use for troubleshooting patterns, failure root-causes, and improvement ideas."
---

# AI Feedback Tracker

Centralized troubleshooting log for:
- **Agent/Skill failures**: When skill/agent specification are wrong and cause a failure (step missing, script failing, ..) or when agent/skill behave outside of its specs.
- **Improvements**: When something could benefit to be add in skill/agent/..

## Quick Add Entry

Use the PowerShell script at `./scripts/Add-FeedbackEntry.ps1`:

```powershell
# Example behave outside of specs
& ".\scripts\Add-FeedbackEntry.ps1" `
  -Type failure `
  -Asset "dotnet-error-management-service" `
  -Description "Executed delete operation on database" `
  -RootCause "Validation was not specified in specifications" `
  -Severity high

# Example skill script failure
& ".\scripts\Add-FeedbackEntry.ps1" `
  -Type failure `
  -Asset "axway-api-management" `
  -Description "Get-AxwayApiList.ps1 exits with 403 Forbidden" `
  -RootCause "Script doesn't handle auth token refresh on expiry" `
  -StackTrace "at Invoke-Validation, C:\scripts\Get-AxwayApiList.ps1: line 42`nat Process-Request, C:\scripts\ProcessController.ps1: line 18" `
  -Severity high

# Example improvement suggestion
& ".\scripts\Add-FeedbackEntry.ps1" `
  -Type improvement `
  -Asset "ui-ux-skill" `
  -Description "Accessibility aria-labels are missing on buttons" `
  -Severity medium
```

**Parameters:**
- `-Type` (required): "failure" or "improvement"
- `-Asset` (required): Skill/agent name
- `-Description` (required): What happened / improvement needed
- `-RootCause` (optional): Why it failed (for failures)
- `-StackTrace` (optional): Full error stacktrace for debugging
- `-Severity` (default: medium): "low", "medium", or "high"
```