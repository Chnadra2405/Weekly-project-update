<#
.SYNOPSIS
    Adds a reply to an existing pull request comment thread.

.PARAMETER Org
    Full organization URL (e.g. https://dev.azure.com/myorg).

.PARAMETER Project
    Project name.

.PARAMETER Repository
    Repository name.

.PARAMETER PullRequestId
    Pull request ID.

.PARAMETER ThreadId
    ID of the thread to reply to.

.PARAMETER Content
    Reply text.

.EXAMPLE
    .\Add-PRReply.ps1 -Org https://dev.azure.com/SISopra -Project ISSSG_Training -Repository POC_OpenShift_App -PullRequestId 465 -ThreadId 1280 -Content "Acknowledged."
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $Org,
    [Parameter(Mandatory)] [string] $Project,
    [Parameter(Mandatory)] [string] $Repository,
    [Parameter(Mandatory)] [int]    $PullRequestId,
    [Parameter(Mandatory)] [int]    $ThreadId,
    [Parameter(Mandatory)] [string] $Content
)

# Auth + fail-loud REST helper.
. "$PSScriptRoot/_AzdoCommon.ps1"
$headers = @{ Authorization = (Get-AzdoAuthHeader); 'Content-Type' = 'application/json' }
$orgName = $Org.TrimEnd('/').Split('/')[-1]
$url = "https://dev.azure.com/$orgName/$Project/_apis/git/repositories/$Repository/pullRequests/$PullRequestId/threads/$ThreadId/comments?api-version=7.1"

$body = @{
    parentCommentId = 1
    content         = $Content
    commentType     = 1
} | ConvertTo-Json -Compress

$bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($body)
$result = Invoke-AzdoRest -Uri $url -Method POST -Headers $headers -Body $bodyBytes

[PSCustomObject]@{
    threadId      = $ThreadId
    commentId     = $result.id
    author        = $result.author.displayName
    content       = $result.content
    publishedDate = $result.publishedDate
} | ConvertTo-Json
