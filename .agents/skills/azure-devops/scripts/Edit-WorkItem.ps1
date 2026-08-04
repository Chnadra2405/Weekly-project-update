<#
.SYNOPSIS
    Updates one or more fields on an Azure DevOps work item.

.PARAMETER Org
    Full organization URL (e.g. https://dev.azure.com/myorg).

.PARAMETER Project
    Project name.

.PARAMETER WorkItemId
    Numeric work item ID.

.PARAMETER Fields
    One or more field assignments in "FieldName=Value" format.
    Accepts short names (Title, State, Priority, Tags, AssignedTo, Description,
    AcceptanceCriteria, AreaPath, IterationPath) or full System.* / Microsoft.VSTS.* paths.

.EXAMPLE
    .\Edit-WorkItem.ps1 -Org https://dev.azure.com/SISopra -Project ISSSG_Training -WorkItemId 123 -Fields "Title=New title", "Priority=2"

.EXAMPLE
    .\Edit-WorkItem.ps1 -Org https://dev.azure.com/SISopra -Project ISSSG_Training -WorkItemId 123 -Fields "IterationPath=ISSSG_Training\Sprint 3"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]   $Org,
    [Parameter(Mandatory)] [string]   $Project,
    [Parameter(Mandatory)] [int]      $WorkItemId,
    [Parameter(Mandatory)] [string[]] $Fields
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

# Map short names to full ADO field paths
$fieldMap = @{
    'Title'              = 'System.Title'
    'State'              = 'System.State'
    'AssignedTo'         = 'System.AssignedTo'
    'Tags'               = 'System.Tags'
    'AreaPath'           = 'System.AreaPath'
    'IterationPath'      = 'System.IterationPath'
    'Priority'           = 'Microsoft.VSTS.Common.Priority'
    'Description'        = 'System.Description'
    'AcceptanceCriteria' = 'Microsoft.VSTS.Common.AcceptanceCriteria'
}

$resolved = $Fields | ForEach-Object {
    $idx   = $_.IndexOf('=')
    $key   = $_.Substring(0, $idx).Trim()
    $value = $_.Substring($idx + 1).Trim()
    $path  = if ($fieldMap.ContainsKey($key)) { $fieldMap[$key] } else { $key }

    if ($path -eq 'System.Description') {
        $value = Convert-ToAzDoHtmlField -Value $value
    }
    elseif ($path -eq 'Microsoft.VSTS.Common.AcceptanceCriteria') {
        $value = Convert-ToAzDoHtmlField -Value $value -PreferList
    }

    "$path=$value"
}

$wi = az boards work-item update `
    --id $WorkItemId `
    --org $Org `
    --fields $resolved `
    --output json | ConvertFrom-Json

if ($null -eq $wi) { Write-Error "Failed to update work item $WorkItemId."; exit 1 }

[PSCustomObject]@{
    id           = $wi.id
    title        = $wi.fields.'System.Title'
    state        = $wi.fields.'System.State'
    assignedTo   = if ($wi.fields.'System.AssignedTo') { $wi.fields.'System.AssignedTo'.displayName } else { $null }
    priority     = $wi.fields.'Microsoft.VSTS.Common.Priority'
    areaPath     = $wi.fields.'System.AreaPath'
    iterationPath= $wi.fields.'System.IterationPath'
    url          = "$Org/$Project/_workitems/edit/$($wi.id)"
} | ConvertTo-Json
