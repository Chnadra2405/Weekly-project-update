<#
.SYNOPSIS
    Updates the status of a pull request comment thread.

.PARAMETER Org
    Full organization URL (e.g. https://dev.azure.com/myorg).

.PARAMETER Project
    Project name.

.PARAMETER Repository
    Repository name.

.PARAMETER PullRequestId
    Pull request ID.

.PARAMETER ThreadId
    ID of the thread to update.

.PARAMETER Status
    New status: active, fixed, wontFix, closed, byDesign, pending.

.EXAMPLE
    .\Set-PRThreadStatus.ps1 -Org https://dev.azure.com/SISopra -Project ISSSG_Training -Repository POC_OpenShift_App -PullRequestId 465 -ThreadId 1280 -Status fixed
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $Org,
    [Parameter(Mandatory)] [string] $Project,
    [Parameter(Mandatory)] [string] $Repository,
    [Parameter(Mandatory)] [int]    $PullRequestId,
    [Parameter(Mandatory)] [int]    $ThreadId,
    [Parameter(Mandatory)]
    [ValidateSet('active', 'fixed', 'wontFix', 'closed', 'byDesign', 'pending')]
    [string] $Status
)

. "$PSScriptRoot/_AzdoCommon.ps1"
$headers = @{
    Authorization  = (Get-AzdoAuthHeader)
    Accept         = 'application/json; api-version=7.1'
    'Content-Type' = 'application/json'
}
$orgName = $Org.TrimEnd('/').Split('/')[-1]
$url = "https://dev.azure.com/$orgName/$Project/_apis/git/repositories/$Repository/pullRequests/$PullRequestId/threads/$($ThreadId)?api-version=7.1"

$statusMap = @{ active = 1; fixed = 2; wontFix = 3; closed = 4; byDesign = 5; pending = 6 }

$body = @{ status = $statusMap[$Status] } | ConvertTo-Json -Compress
$bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($body)
$result = Invoke-AzdoRest -Uri $url -Method PATCH -Headers $headers -Body $bodyBytes

[PSCustomObject]@{
    threadId = $ThreadId
    status   = $Status
} | ConvertTo-Json
