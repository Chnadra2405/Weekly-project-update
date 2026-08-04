<#
.SYNOPSIS
    Fetches an Azure DevOps work item with all key fields, its comments, and its
    linked Git artifacts (branches, pull requests, commits).

.PARAMETER Org
    Full organization URL (e.g. https://dev.azure.com/myorg).

.PARAMETER Project
    Project name.

.PARAMETER WorkItemId
    Numeric work item ID.

.EXAMPLE
    .\Get-WorkItem.ps1 -Org https://dev.azure.com/soprasteria-is -Project ISSSG -WorkItemId 12345
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $Org,
    [Parameter(Mandatory)] [string] $Project,
    [Parameter(Mandatory)] [int]    $WorkItemId
)

$fields = 'System.Id,System.Title,System.WorkItemType,System.State,System.AssignedTo,System.Tags,System.Description,Microsoft.VSTS.Common.AcceptanceCriteria,Microsoft.VSTS.Common.Priority,System.AreaPath,System.IterationPath,System.CreatedDate,System.ChangedDate,System.CommentCount,Custom.AIStatus'

$wi = az boards work-item show `
    --id $WorkItemId `
    --org $Org `
    --expand none `
    --fields $fields `
    --output json | ConvertFrom-Json

if ($null -eq $wi) { Write-Error "Work item $WorkItemId not found."; exit 1 }

$comments = @()
if ([int]$wi.fields.'System.CommentCount' -gt 0) {
    . "$PSScriptRoot/_AzdoCommon.ps1"
    $raw = Invoke-AzdoRest `
        -Uri "$Org/$Project/_apis/wit/workItems/$WorkItemId/comments?api-version=7.1-preview.3" `
        -Headers @{ Authorization = (Get-AzdoAuthHeader) }
    $comments = @($raw.comments | Select-Object id, @{n='author';e={$_.createdBy.displayName}}, createdDate, text)
}

# Fetch linked Git artifacts (branches, pull requests, commits) from work item relations.
# `az boards work-item relation show` returns the full work item including its `relations` array.
$wiFull = az boards work-item relation show `
    --id $WorkItemId `
    --org $Org `
    --output json | ConvertFrom-Json

$branches      = @()
$pullRequests  = @()
$commits       = @()

if ($wiFull -and $wiFull.relations) {
    foreach ($rel in $wiFull.relations) {
        if ($rel.rel -ne 'Artifact Link') { continue }

        $artifactName = $rel.attributes.name
        $url          = $rel.url

        # vstfs:///Git/<Type>/<projectId>%2f<repoId>%2f<resourceId>
        if ($url -notmatch '^vstfs:///Git/(?<type>[^/]+)/(?<rest>.+)$') { continue }
        $type       = $Matches['type']
        $decoded    = [System.Net.WebUtility]::UrlDecode($Matches['rest'])
        $parts      = $decoded -split '/'
        if ($parts.Count -lt 3) { continue }
        $projectId  = $parts[0]
        $repoId     = $parts[1]
        $resourceId = ($parts[2..($parts.Count - 1)]) -join '/'

        switch ($artifactName) {
            'Branch' {
                # resourceId is prefixed with "GB" (Git Branch).
                $branchName = if ($resourceId -like 'GB*') { $resourceId.Substring(2) } else { $resourceId }
                $branches += [PSCustomObject]@{
                    projectId  = $projectId
                    repoId     = $repoId
                    branchName = $branchName
                    refName    = "refs/heads/$branchName"
                }
            }
            'Pull Request' {
                $pullRequests += [PSCustomObject]@{
                    projectId     = $projectId
                    repoId        = $repoId
                    pullRequestId = [int]$resourceId
                }
            }
            'Fixed in Commit' {
                $commits += [PSCustomObject]@{
                    projectId = $projectId
                    repoId    = $repoId
                    commitSha = $resourceId
                }
            }
        }
    }
}

[PSCustomObject]@{
    id                 = $wi.id
    title              = $wi.fields.'System.Title'
    workItemType       = $wi.fields.'System.WorkItemType'
    state              = $wi.fields.'System.State'
    aiStatus           = $wi.fields.'Custom.AIStatus'
    assignedTo         = if ($wi.fields.'System.AssignedTo') { $wi.fields.'System.AssignedTo'.displayName } else { $null }
    priority           = $wi.fields.'Microsoft.VSTS.Common.Priority'
    tags               = $wi.fields.'System.Tags'
    areaPath           = $wi.fields.'System.AreaPath'
    iterationPath      = $wi.fields.'System.IterationPath'
    createdDate        = $wi.fields.'System.CreatedDate'
    changedDate        = $wi.fields.'System.ChangedDate'
    url                = "$Org/$Project/_workitems/edit/$($wi.id)"
    description        = $wi.fields.'System.Description'
    acceptanceCriteria = $wi.fields.'Microsoft.VSTS.Common.AcceptanceCriteria'
    comments           = $comments
    branches           = $branches
    pullRequests       = $pullRequests
    commits            = $commits
} | ConvertTo-Json -Depth 5
