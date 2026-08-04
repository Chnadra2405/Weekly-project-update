<#
.SYNOPSIS
    Updates the state of an Azure DevOps work item and optionally posts a comment.

.PARAMETER Org
    Full organization URL (e.g. https://dev.azure.com/myorg).

.PARAMETER Project
    Project name.

.PARAMETER WorkItemId
    Numeric work item ID.

.PARAMETER NewState
    Target state (e.g. New, Active, Resolved, Closed).

.PARAMETER Comment
    Optional comment text to post on the work item after the state change.
    Uses az rest with the Work Item Comments API (resource 499b84ac-1321-427f-aa17-267ca6975798).

.EXAMPLE
    .\Edit-WorkItemState.ps1 -Org https://dev.azure.com/soprasteria-is -Project ISSSG -WorkItemId 123 -NewState Closed

.EXAMPLE
    .\Edit-WorkItemState.ps1 -Org https://dev.azure.com/soprasteria-is -Project ISSSG -WorkItemId 123 -NewState Closed -Comment "Closed after verification"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $Org,
    [Parameter(Mandatory)] [string] $Project,
    [Parameter(Mandatory)] [int]    $WorkItemId,
    [Parameter(Mandatory)] [string] $NewState,
    [string] $Comment
)

$wi = az boards work-item update `
    --id $WorkItemId `
    --org $Org `
    --fields "System.State=$NewState" `
    --output json | ConvertFrom-Json

if ($null -eq $wi) { Write-Error "Failed to update work item $WorkItemId."; exit 1 }

if ($Comment) {
    . "$PSScriptRoot/_AzdoCommon.ps1"
    $body  = @{ text = $Comment } | ConvertTo-Json -Compress
    Invoke-AzdoRest `
        -Uri "$Org/$Project/_apis/wit/workItems/$WorkItemId/comments?api-version=7.1-preview.3" `
        -Method POST `
        -Headers @{ Authorization = (Get-AzdoAuthHeader); 'Content-Type' = 'application/json' } `
        -Body $body | Out-Null
}

[PSCustomObject]@{
    id    = $wi.id
    title = $wi.fields.'System.Title'
    state = $wi.fields.'System.State'
    url   = "$Org/$Project/_workitems/edit/$($wi.id)"
} | ConvertTo-Json
