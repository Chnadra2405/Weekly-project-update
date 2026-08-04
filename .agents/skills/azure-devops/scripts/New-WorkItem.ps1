<#
.SYNOPSIS
    Creates a new work item in Azure DevOps, optionally linking it to a parent.

.PARAMETER Org
    Full organization URL (e.g. https://dev.azure.com/myorg).

.PARAMETER Project
    Project name.

.PARAMETER Title
    Work item title.

.PARAMETER Type
    Work item type. Default: 'User Story'. Other values: 'Bug', 'Task', 'Feature', 'Epic'.

.PARAMETER Description
    HTML description (optional).

.PARAMETER AcceptanceCriteria
    HTML acceptance criteria (optional).

.PARAMETER AreaPath
    Area path (optional, e.g. 'ISSSG\MyTeam').

.PARAMETER IterationPath
    Iteration/sprint path (optional, e.g. 'ISSSG\Sprint 1').

.PARAMETER Priority
    Priority level 1-4 (optional).

.PARAMETER Tags
    Tags separated by semicolons (optional).

.PARAMETER AssignedTo
    Assignee display name or email (optional).

.PARAMETER ParentId
    ID of a parent work item to link to (optional).
    Uses az account get-access-token + Invoke-RestMethod to patch the parent relation.

.EXAMPLE
    .\New-WorkItem.ps1 -Org https://dev.azure.com/soprasteria-is -Project ISSSG -Title "My User Story" -Description "<p>As a user...</p>"

.EXAMPLE
    .\New-WorkItem.ps1 -Org https://dev.azure.com/soprasteria-is -Project ISSSG -Title "Sub-task" -ParentId 338962
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $Org,
    [Parameter(Mandatory)] [string] $Project,
    [Parameter(Mandatory)] [string] $Title,
    [string] $Type = 'User Story',
    [string] $Description,
    [string] $AcceptanceCriteria,
    [string] $AreaPath,
    [string] $IterationPath,
    [ValidateRange(1, 4)] [int] $Priority,
    [string] $Tags,
    [string] $AssignedTo,
    [int] $ParentId
)

function Convert-ToAzDoHtmlField {
    param(
        [string] $Value,
        [switch] $PreferList
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $null
    }

    # Keep user-provided HTML untouched.
    if ($Value -match '<\s*[a-zA-Z][^>]*>') {
        return $Value
    }

    $normalized = $Value -replace "`r`n|`r|`n", "`n"
    $lines = $normalized -split "`n"

    if ($PreferList) {
        $items = @()
        foreach ($line in $lines) {
            $trimmed = $line.Trim()
            if ([string]::IsNullOrWhiteSpace($trimmed)) {
                continue
            }

            if ($trimmed -match '^(?:[-*]|[0-9]+[.)])\s+(.*)$') {
                $items += $Matches[1]
            }
            else {
                $items += $trimmed
            }
        }

        if ($items.Count -gt 1) {
            $encodedItems = $items | ForEach-Object { [System.Net.WebUtility]::HtmlEncode($_) }
            return '<ul><li>' + ($encodedItems -join '</li><li>') + '</li></ul>'
        }
    }

    $encodedLines = $lines | ForEach-Object { [System.Net.WebUtility]::HtmlEncode($_) }
    return ($encodedLines -join '<br/>')
}

$azArgs = @('boards', 'work-item', 'create', '--org', $Org, '--project', $Project, '--title', $Title, '--type', $Type, '--output', 'json')

$descriptionValue = Convert-ToAzDoHtmlField -Value $Description
$acceptanceCriteriaValue = Convert-ToAzDoHtmlField -Value $AcceptanceCriteria -PreferList

$fields = @()
if ($descriptionValue)        { $fields += "System.Description=$descriptionValue" }
if ($acceptanceCriteriaValue) { $fields += "Microsoft.VSTS.Common.AcceptanceCriteria=$acceptanceCriteriaValue" }
if ($AreaPath)           { $fields += "System.AreaPath=$AreaPath" }
if ($IterationPath)      { $fields += "System.IterationPath=$IterationPath" }
if ($Priority)           { $fields += "Microsoft.VSTS.Common.Priority=$Priority" }
if ($Tags)               { $fields += "System.Tags=$Tags" }
if ($AssignedTo)         { $fields += "System.AssignedTo=$AssignedTo" }
if ($fields.Count -gt 0) { $azArgs += @('--fields') + $fields }

$wi = & az @azArgs | ConvertFrom-Json

if ($null -eq $wi) { Write-Error 'Failed to create work item.'; exit 1 }

if ($ParentId) {
    $orgName   = $Org.TrimEnd('/') -replace '^.*/dev\.azure\.com/', ''
    $parentUrl = "https://dev.azure.com/$orgName/_apis/wit/workitems/$ParentId"
    . "$PSScriptRoot/_AzdoCommon.ps1"
    $authValue = Get-AzdoAuthHeader
    $patch = @(
        @{
            op    = 'add'
            path  = '/relations/-'
            value = @{ rel = 'System.LinkTypes.Hierarchy-Reverse'; url = $parentUrl }
        }
    ) | ConvertTo-Json -Depth 5 -Compress -AsArray
    Invoke-AzdoRest `
        -Uri "$Org/_apis/wit/workitems/$($wi.id)?api-version=7.1" `
        -Method PATCH `
        -Headers @{ Authorization = $authValue; 'Content-Type' = 'application/json-patch+json' } `
        -Body $patch | Out-Null
}

[PSCustomObject]@{
    id           = $wi.id
    title        = $wi.fields.'System.Title'
    workItemType = $wi.fields.'System.WorkItemType'
    state        = $wi.fields.'System.State'
    assignedTo   = if ($wi.fields.'System.AssignedTo') { $wi.fields.'System.AssignedTo'.displayName } else { $null }
    priority     = $wi.fields.'Microsoft.VSTS.Common.Priority'
    areaPath     = $wi.fields.'System.AreaPath'
    iterationPath= $wi.fields.'System.IterationPath'
    url          = "$Org/$Project/_workitems/edit/$($wi.id)"
} | ConvertTo-Json
