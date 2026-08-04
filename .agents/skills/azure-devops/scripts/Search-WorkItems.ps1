<#
.SYNOPSIS
    Queries Azure DevOps work items assigned to a specific person, with optional state filter.

.PARAMETER Org
    Full organization URL (e.g. https://dev.azure.com/myorg).

.PARAMETER Project
    Project name.

.PARAMETER AssignedTo
    Display name or email of the assignee (e.g. 'John Doe' or 'john.doe@company.com').

.PARAMETER State
    Optional state filter (e.g. 'Active', 'New', 'Resolved'). Omit to return all states.

.PARAMETER Top
    Maximum number of results to return. Default: 50.

.EXAMPLE
    .\Search-WorkItems.ps1 -Org https://dev.azure.com/SISopra -Project ISSSG_Training -AssignedTo "John Doe"

.EXAMPLE
    .\Search-WorkItems.ps1 -Org https://dev.azure.com/SISopra -Project ISSSG_Training -AssignedTo "John Doe" -State Active
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $Org,
    [Parameter(Mandatory)] [string] $Project,
    [Parameter(Mandatory)] [string] $AssignedTo,
    [string] $State,
    [int]    $Top = 50
)

$stateClause = if ($State) { "AND [System.State] = '$State'" } else { '' }

$wiql = "SELECT [System.Id] FROM WorkItems WHERE [System.TeamProject] = '$Project' AND [System.AssignedTo] = '$AssignedTo' $stateClause ORDER BY [System.ChangedDate] DESC"

$result = az boards query `
    --org $Org `
    --project $Project `
    --wiql $wiql `
    --output json 2>$null | ConvertFrom-Json

$ids = @($result | Where-Object { $_ } | Select-Object -First $Top | ForEach-Object { [int]$_.fields.'System.Id' })

if ($ids.Count -eq 0) {
    Write-Output '[]'
    return
}

$fields = 'System.Id,System.Title,System.WorkItemType,System.State,System.AssignedTo,System.AreaPath,System.IterationPath,System.ChangedDate'

# Fetch details for each work item (batch in chunks of 200 to respect API limits)
$items = @()
for ($i = 0; $i -lt $ids.Count; $i += 200) {
    $chunk = $ids[$i..([Math]::Min($i + 199, $ids.Count - 1))]
    foreach ($id in $chunk) {
        $wi = az boards work-item show `
            --id $id `
            --org $Org `
            --expand none `
            --fields $fields `
            --output json | ConvertFrom-Json
        if ($wi) {
            $items += [PSCustomObject]@{
                id           = $wi.id
                title        = $wi.fields.'System.Title'
                type         = $wi.fields.'System.WorkItemType'
                state        = $wi.fields.'System.State'
                assignedTo   = if ($wi.fields.'System.AssignedTo') { $wi.fields.'System.AssignedTo'.displayName } else { $null }
                areaPath     = $wi.fields.'System.AreaPath'
                iterationPath= $wi.fields.'System.IterationPath'
                changedDate  = $wi.fields.'System.ChangedDate'
                url          = "$Org/$Project/_workitems/edit/$($wi.id)"
            }
        }
    }
}

$items | ConvertTo-Json -Depth 3
