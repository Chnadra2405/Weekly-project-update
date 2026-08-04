<#
.SYNOPSIS
    Creates a Pull Request on an Azure DevOps Git repository and links it to one
    or more work items.

.PARAMETER Org
    Full organization URL (e.g. https://dev.azure.com/myorg).

.PARAMETER Project
    Project name.

.PARAMETER Repository
    Git repository name.

.PARAMETER SourceBranch
    Source branch name without "refs/heads/" prefix (e.g. "feature/49163-html-page").

.PARAMETER TargetBranch
    Target branch name without "refs/heads/" prefix (e.g. "master").

.PARAMETER Title
    Pull request title.

.PARAMETER Description
    Pull request description (markdown or plain text).

.PARAMETER WorkItemIds
    One or more work item IDs to link to the PR.

.EXAMPLE
    .\New-PullRequest.ps1 `
        -Org https://dev.azure.com/SISopra `
        -Project ISSSG_Training `
        -Repository POC_TestAiSoftFactory `
        -SourceBranch "feature/49163-html-page" `
        -TargetBranch "master" `
        -Title "49163 - Create a html basic page" `
        -Description "Implements WI #49163." `
        -WorkItemIds 49163
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]   $Org,
    [Parameter(Mandatory)] [string]   $Project,
    [Parameter(Mandatory)] [string]   $Repository,
    [Parameter(Mandatory)] [string]   $SourceBranch,
    [Parameter(Mandatory)] [string]   $TargetBranch,
    [Parameter(Mandatory)] [string]   $Title,
    [string]                          $Description,
    [int[]]                           $WorkItemIds
)

$azArgs = @(
    'repos', 'pr', 'create',
    '--org', $Org,
    '--project', $Project,
    '--repository', $Repository,
    '--source-branch', $SourceBranch,
    '--target-branch', $TargetBranch,
    '--title', $Title,
    '--output', 'json'
)

if ($Description)              { $azArgs += @('--description', $Description) }
if ($WorkItemIds -and $WorkItemIds.Count -gt 0) {
    $azArgs += @('--work-items') + ($WorkItemIds | ForEach-Object { [string]$_ })
}

$pr = & az @azArgs | ConvertFrom-Json
if ($null -eq $pr) { Write-Error 'Failed to create pull request.'; exit 1 }

$orgName = $Org.TrimEnd('/') -replace '^.*/dev\.azure\.com/', ''
$prUrl   = "https://dev.azure.com/$orgName/$Project/_git/$Repository/pullrequest/$($pr.pullRequestId)"

[PSCustomObject]@{
    pullRequestId = $pr.pullRequestId
    title         = $pr.title
    status        = $pr.status
    sourceRefName = $pr.sourceRefName
    targetRefName = $pr.targetRefName
    createdBy     = if ($pr.createdBy) { $pr.createdBy.displayName } else { $null }
    url           = $prUrl
} | ConvertTo-Json
