<#
.SYNOPSIS
    Lists open pull requests for a repository.

.PARAMETER Org
    Full organization URL (e.g. https://dev.azure.com/myorg).

.PARAMETER Project
    Project name.

.PARAMETER Repository
    Repository name.

.PARAMETER Status
    PR status filter: open, completed, abandoned, all. Default: open.

.EXAMPLE
    .\Get-PRList.ps1 -Org https://dev.azure.com/SISopra -Project ISSSG_Training -Repository POC_OpenShift_App
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $Org,
    [Parameter(Mandatory)] [string] $Project,
    [Parameter(Mandatory)] [string] $Repository,
    [ValidateSet('active', 'completed', 'abandoned', 'all')]
    [string] $Status = 'active'
)

$prs = az repos pr list `
    --org $Org `
    --project $Project `
    --repository $Repository `
    --status $Status `
    --output json | ConvertFrom-Json

if ($null -eq $prs) { Write-Error 'Failed to list pull requests.'; exit 1 }

@($prs | ForEach-Object { $_ } | ForEach-Object {
    $orgSegment = $_.repository.url.Split('/')[3]
    [PSCustomObject]@{
        pullRequestId = $_.pullRequestId
        title         = $_.title
        status        = $_.status
        createdBy     = $_.createdBy.displayName
        sourceRefName = $_.sourceRefName
        targetRefName = $_.targetRefName
        mergeStatus   = $_.mergeStatus
        url           = "https://dev.azure.com/$orgSegment/$($_.repository.project.name)/_git/$($_.repository.name)/pullrequest/$($_.pullRequestId)"
    }
}) | ConvertTo-Json -Depth 3
