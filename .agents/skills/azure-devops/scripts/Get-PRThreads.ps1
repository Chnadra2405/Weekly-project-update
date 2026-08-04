<#
.SYNOPSIS
    Lists comment threads on a pull request.

.PARAMETER Org
    Full organization URL (e.g. https://dev.azure.com/myorg).

.PARAMETER Project
    Project name.

.PARAMETER Repository
    Repository name.

.PARAMETER PullRequestId
    Pull request ID.

.EXAMPLE
    .\Get-PRThreads.ps1 -Org https://dev.azure.com/SISopra -Project ISSSG_Training -Repository POC_OpenShift_App -PullRequestId 465
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $Org,
    [Parameter(Mandatory)] [string] $Project,
    [Parameter(Mandatory)] [string] $Repository,
    [Parameter(Mandatory)] [int]    $PullRequestId
)

. "$PSScriptRoot/_AzdoCommon.ps1"
$headers = @{ Authorization = (Get-AzdoAuthHeader); "Content-Type" = "application/json" }

$orgName = $Org.TrimEnd('/').Split('/')[-1]
$url = "https://dev.azure.com/$orgName/$Project/_apis/git/repositories/$Repository/pullRequests/$PullRequestId/threads?api-version=7.1"

$response = Invoke-AzdoRest -Uri $url -Headers $headers -Method Get

$response.value |
    Where-Object { -not $_.isDeleted -and $_.comments[0].commentType -eq 'text' } |
    ForEach-Object {
        $activeComments = @($_.comments | Where-Object { -not $_.isDeleted })
        $root   = $activeComments[0]
        $replies = $activeComments | Select-Object -Skip 1

        [PSCustomObject]@{
            id       = $_.id
            status   = $_.status
            filePath = $_.threadContext.filePath
            line     = $_.threadContext.rightFileStart.line
            comment  = [PSCustomObject]@{
                id            = $root.id
                author        = $root.author.displayName
                content       = $root.content
                publishedDate = $root.publishedDate
            }
            replies  = @($replies | ForEach-Object {
                [PSCustomObject]@{
                    id            = $_.id
                    author        = $_.author.displayName
                    content       = $_.content
                    publishedDate = $_.publishedDate
                }
            })
        }
    } |
    ConvertTo-Json -Depth 5
