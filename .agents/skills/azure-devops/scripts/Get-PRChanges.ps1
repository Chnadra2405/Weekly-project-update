<#
.SYNOPSIS
    Lists changed files in a pull request, or produces a unified diff (git diff style) for a specific file.

.DESCRIPTION
    Step 1: az repos pr show -> extract lastMergeSourceCommit / lastMergeTargetCommit
    Step 2: az repos pr changes -> parse changeEntries (blob files only)
    Step 3 (if -FilePath): fetch base and source versions of the file and run
             'git diff --no-index' to produce unified diff output

.PARAMETER Org
    Full organization URL (e.g. https://dev.azure.com/myorg).

.PARAMETER Project
    Project name.

.PARAMETER Repository
    Repository name.

.PARAMETER PullRequestId
    Pull request ID.

.PARAMETER FilePath
    (Optional) Path to a changed file to diff (e.g. 'src/MyClass.cs'). Produces unified diff output.

.EXAMPLE
    .\Get-PRChanges.ps1 -Org https://dev.azure.com/soprasteria-is -Project ISSSG -Repository <REPO_NAME> -PullRequestId <PR_ID>

.EXAMPLE
    .\Get-PRChanges.ps1 -Org https://dev.azure.com/soprasteria-is -Project ISSSG -Repository <REPO_NAME> -PullRequestId <PR_ID> -FilePath src/MyClass.cs
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $Org,
    [Parameter(Mandatory)] [string] $Project,
    [Parameter(Mandatory)] [string] $Repository,
    [Parameter(Mandatory)] [int]    $PullRequestId,
    [string] $FilePath
)

$pr = az repos pr show `
    --id $PullRequestId `
    --org $Org `
    --output json | ConvertFrom-Json

if ($null -eq $pr) { Write-Error "PR $PullRequestId not found."; exit 1 }

$sourceCommit = $pr.lastMergeSourceCommit.commitId
$repoId       = $pr.repository.id

# az rest has Windows encoding bugs with dev.azure.com URLs — use Invoke-RestMethod throughout.
. "$PSScriptRoot/_AzdoCommon.ps1"
$authValue = Get-AzdoAuthHeader
$headers   = @{ Authorization = $authValue }

# Get latest iteration ID
$iterations      = Invoke-AzdoRest -Uri "$Org/$Project/_apis/git/repositories/$repoId/pullRequests/$PullRequestId/iterations?api-version=7.1" -Headers $headers
$latestIteration = ($iterations.value | Sort-Object id | Select-Object -Last 1).id

# Get changed files for the latest iteration
$changesRaw = Invoke-AzdoRest -Uri "$Org/$Project/_apis/git/repositories/$repoId/pullRequests/$PullRequestId/iterations/$latestIteration/changes?api-version=7.1" -Headers $headers

$entries = if ($changesRaw.changeEntries) { $changesRaw.changeEntries } else { @() }

$changedFiles = @($entries | Where-Object { $_.item.path -and -not $_.item.path.EndsWith('/') } | ForEach-Object {
    [PSCustomObject]@{
        changeType   = $_.changeType
        path         = $_.item.path
        originalPath = $_.item.originalPath
    }
})

if ($FilePath) {
    $encodedPath = [Uri]::EscapeDataString($FilePath)
    $normalizedPath = $FilePath.TrimStart('/')
    $fileChange  = $changedFiles | Where-Object { $_.path.TrimStart('/') -eq $normalizedPath } | Select-Object -First 1
    $changeType  = if ($fileChange) { $fileChange.changeType } else { 'edit' }
    $baseCommit  = $pr.lastMergeTargetCommit.commitId

    $baseContent   = $null
    $sourceContent = $null

    if ($changeType -notmatch 'delete') {
        $sourceContent = Invoke-AzdoRest `
            -Uri "$Org/$Project/_apis/git/repositories/$repoId/items?path=$encodedPath&versionDescriptor.versionType=commit&versionDescriptor.version=$sourceCommit&api-version=7.1" `
            -Headers @{ Authorization = $authValue; Accept = 'text/plain' }
    }

    if ($changeType -notmatch 'add') {
        try {
            $baseContent = Invoke-RestMethod `
                -Uri "$Org/$Project/_apis/git/repositories/$repoId/items?path=$encodedPath&versionDescriptor.versionType=commit&versionDescriptor.version=$baseCommit&api-version=7.1" `
                -Headers @{ Authorization = $authValue; Accept = 'text/plain' } -ErrorAction Stop
        } catch { $baseContent = $null }
    }

    $tmpBase   = [System.IO.Path]::GetTempFileName()
    $tmpSource = [System.IO.Path]::GetTempFileName()
    try {
        $baseText   = if ($baseContent)   { [string]$baseContent }   else { '' }
        $sourceText = if ($sourceContent) { [string]$sourceContent } else { '' }
        [System.IO.File]::WriteAllText($tmpBase,   $baseText,   [System.Text.Encoding]::UTF8)
        [System.IO.File]::WriteAllText($tmpSource, $sourceText, [System.Text.Encoding]::UTF8)

        # -c core.autocrlf=false suppresses LF/CRLF warnings; stderr discarded
        $rawDiff = & git -c core.autocrlf=false diff --no-index --unified=3 -- $tmpBase $tmpSource 2>$null

        # Replace temp-file paths in the specific header lines git emits
        $diffLines = $rawDiff | Where-Object { $_ -isnot [System.Management.Automation.ErrorRecord] } | ForEach-Object {
            if     ($_ -match '^diff --git') { "diff --git a/$normalizedPath b/$normalizedPath" }
            elseif ($_ -match '^--- ')       { "--- a/$normalizedPath" }
            elseif ($_ -match '^\+\+\+ ')    { "+++ b/$normalizedPath" }
            else                             { $_ }
        }

        [PSCustomObject]@{
            filePath = $FilePath
            diff     = ($diffLines -join "`n")
        } | ConvertTo-Json
    } finally {
        Remove-Item $tmpBase, $tmpSource -ErrorAction SilentlyContinue
    }
} else {
    [PSCustomObject]@{
        pullRequestId = $PullRequestId
        sourceCommit  = $sourceCommit
        changedFiles  = $changedFiles
    } | ConvertTo-Json -Depth 5
}
