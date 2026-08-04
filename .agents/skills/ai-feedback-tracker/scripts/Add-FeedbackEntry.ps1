#Requires -Version 7.0
<#
.SYNOPSIS
  Append or create feedback entry in .ai-feedbacks.yml at repo root.
.PARAMETER Type
  "failure" or "improvement"
.PARAMETER Asset
  Skill/agent name
.PARAMETER Description
  What happened / what to improve
.PARAMETER RootCause
  Why it failed (optional, for failures)
.PARAMETER StackTrace
  Full error stacktrace for debugging (optional)
.PARAMETER Severity
  "low", "medium", or "high"
.PARAMETER RepoRoot
  Path to repo root (default: repo root from git)
#>
param(
    [ValidateSet("failure", "improvement")]
    [string]$Type = $(throw "Type required: 'failure' or 'improvement'"),
    
    [string]$Asset = $(throw "Asset name required"),
    
    [string]$Description = $(throw "Description required"),
    
    [string]$RootCause = "",
    
    [string]$StackTrace = "",
    
    [ValidateSet("low", "medium", "high")]
    [string]$Severity = "medium",
    
    [string]$RepoRoot = $null
)

# Determine repo root if not provided
if (-not $RepoRoot) {
    $repoRoot = git rev-parse --show-toplevel 2>$null
    if (-not $repoRoot) {
        $repoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
    }
}

$feedbackFile = Join-Path $repoRoot ".ai-feedbacks.yml"

# Generate ID: YYYYMMDD-### format
$dateStr = Get-Date -Format "yyyyMMdd"

if (Test-Path $feedbackFile) {
    # Parse existing file to find next ID
    $content = Get-Content $feedbackFile -Raw
    $matches = [regex]::Matches($content, '"(\d{8})-(\d{3})"')
    if ($matches.Count -gt 0) {
        $existingNums = @($matches | ForEach-Object { [int]$_.Groups[2].Value })
        $maxNum = ($existingNums | Measure-Object -Maximum).Maximum
        $nextNum = $maxNum + 1
    } else {
        $nextNum = 1
    }
} else {
    $nextNum = 1
}

$id = "{0}-{1:D3}" -f $dateStr, ([int]$nextNum)

# Create YAML entry
$stackTraceYaml = if ($StackTrace) { "
    stackTrace: |`n      $(($StackTrace -split '\`n' | ForEach-Object { '      ' + $_ }) -join "`n")" } else { "" }

$entry = @"
  - id: "$id"
    date: $(Get-Date -Format "yyyy-MM-dd")
    type: $Type
    asset: $Asset
    description: "$($Description -replace '"', '\"')"
    rootCause: "$($RootCause -replace '"', '\"')"$stackTraceYaml
    severity: $Severity
    resolutionStatus: "open"
"@

# Append or create file
if (-not (Test-Path $feedbackFile)) {
    $header = "# AI Feedback Log`nfeedbacks:`n"
    Set-Content -Path $feedbackFile -Value $header -NoNewline
    Add-Content -Path $feedbackFile -Value $entry
} else {
    Add-Content -Path $feedbackFile -Value $entry
}

Write-Host "✓ Feedback entry $id added to .ai-feedbacks.yml" -ForegroundColor Green
