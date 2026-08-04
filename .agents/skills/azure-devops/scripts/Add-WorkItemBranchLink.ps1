<#
.SYNOPSIS
    Links a Git branch to an Azure DevOps work item by creating an "Artifact Link"
    relation of type "Branch".

.DESCRIPTION
    Creates the same kind of link Azure DevOps creates automatically when a branch
    name contains the work item ID prefix, but explicit so the agent does not have
    to rely on that side-effect. Idempotent: skips the PATCH if a Branch link with
    the same URL already exists on the work item.

.PARAMETER Org
    Full organization URL (e.g. https://dev.azure.com/myorg).

.PARAMETER Project
    Project name.

.PARAMETER Repository
    Git repository name (the human-readable one, e.g. "MyApp").

.PARAMETER WorkItemId
    Numeric work item ID.

.PARAMETER BranchName
    Branch name without the "refs/heads/" prefix (e.g. "feature/49163-html-page").

.EXAMPLE
    .\Add-WorkItemBranchLink.ps1 `
        -Org https://dev.azure.com/SISopra `
        -Project ISSSG_Training `
        -Repository POC_TestAiSoftFactory `
        -WorkItemId 49163 `
        -BranchName "feature/49163-html-page"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $Org,
    [Parameter(Mandatory)] [string] $Project,
    [Parameter(Mandatory)] [string] $Repository,
    [Parameter(Mandatory)] [int]    $WorkItemId,
    [Parameter(Mandatory)] [string] $BranchName
)

# Resolve repository to get projectId and repoId.
$repo = az repos show --repository $Repository --project $Project --org $Org --output json | ConvertFrom-Json
if ($null -eq $repo) { Write-Error "Repository '$Repository' not found in project '$Project'."; exit 1 }

$projectId = $repo.project.id
$repoId    = $repo.id

# Build the vstfs:// artifact URL. The resource segment is URL-encoded once, including the "GB" branch prefix.
$resource    = "$projectId/$repoId/GB$BranchName"
$encoded     = [System.Net.WebUtility]::UrlEncode($resource)
$artifactUrl = "vstfs:///Git/Ref/$encoded"

# Check existing relations to avoid duplicates.
$wiFull = az boards work-item relation show --id $WorkItemId --org $Org --output json | ConvertFrom-Json
if ($wiFull -and $wiFull.relations) {
    $alreadyLinked = $wiFull.relations | Where-Object {
        $_.rel -eq 'Artifact Link' -and $_.attributes.name -eq 'Branch' -and $_.url -eq $artifactUrl
    }
    if ($alreadyLinked) {
        Write-Verbose "Branch link already exists on work item $WorkItemId; skipping."
        [PSCustomObject]@{
            workItemId  = $WorkItemId
            branchName  = $BranchName
            artifactUrl = $artifactUrl
            status      = 'already-linked'
        } | ConvertTo-Json
        return
    }
}

# Auth + fail-loud REST helper.
. "$PSScriptRoot/_AzdoCommon.ps1"
$authValue = Get-AzdoAuthHeader
$patch = @(
    @{
        op    = 'add'
        path  = '/relations/-'
        value = @{
            rel        = 'ArtifactLink'
            url        = $artifactUrl
            attributes = @{ name = 'Branch' }
        }
    }
) | ConvertTo-Json -Depth 5 -Compress -AsArray

Invoke-AzdoRest `
    -Uri "$Org/_apis/wit/workitems/$WorkItemId`?api-version=7.1" `
    -Method PATCH `
    -Headers @{ Authorization = $authValue; 'Content-Type' = 'application/json-patch+json' } `
    -Body $patch | Out-Null

[PSCustomObject]@{
    workItemId  = $WorkItemId
    branchName  = $BranchName
    artifactUrl = $artifactUrl
    status      = 'linked'
} | ConvertTo-Json
