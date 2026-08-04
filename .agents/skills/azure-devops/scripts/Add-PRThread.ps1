<#
.SYNOPSIS
    Creates a new comment thread on a pull request, optionally scoped to a file and line.

.DESCRIPTION
    Without -FilePath: uses az account get-access-token + Invoke-RestMethod to POST a general thread.
    With -FilePath: uses az account get-access-token + Invoke-RestMethod to POST a thread with
    threadContext (file path + optional line), because az CLI does not support threadContext.

.PARAMETER Org
    Full organization URL (e.g. https://dev.azure.com/myorg).

.PARAMETER Project
    Project name.

.PARAMETER Repository
    Repository name.

.PARAMETER PullRequestId
    Pull request ID.

.PARAMETER Content
    Comment text.

.PARAMETER FilePath
    (Optional) File path to anchor the comment to (e.g. 'src/MyClass.cs').

.PARAMETER LineNumber
    (Optional) Line number within the file. Requires -FilePath.

.EXAMPLE
    .\Add-PRThread.ps1 -Org https://dev.azure.com/soprasteria-is -Project ISSSG -Repository <REPO_NAME> -PullRequestId <PR_ID> -Content "LGTM!"

.EXAMPLE
    .\Add-PRThread.ps1 -Org https://dev.azure.com/soprasteria-is -Project ISSSG -Repository <REPO_NAME> -PullRequestId <PR_ID> -Content "Null ref risk." -FilePath src/MyService.cs -LineNumber 87
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $Org,
    [Parameter(Mandatory)] [string] $Project,
    [Parameter(Mandatory)] [string] $Repository,
    [Parameter(Mandatory)] [int]    $PullRequestId,
    [Parameter(Mandatory)] [string] $Content,
    [string] $FilePath,
    [int]    $LineNumber
)

# Auth + fail-loud REST helper.
. "$PSScriptRoot/_AzdoCommon.ps1"
$headers = @{ Authorization = (Get-AzdoAuthHeader); 'Content-Type' = 'application/json' }
$orgName = $Org.TrimEnd('/').Split('/')[-1]
$url = "https://dev.azure.com/$orgName/$Project/_apis/git/repositories/$Repository/pullRequests/$PullRequestId/threads?api-version=7.1"

if (-not $FilePath) {
    # General (non-file-scoped) thread
    $body = @{
        status   = 'active'
        comments = @(
            @{
                parentCommentId = 0
                content         = $Content
                commentType     = 1
            }
        )
    } | ConvertTo-Json -Depth 5 -Compress

    $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($body)
    $result = Invoke-AzdoRest -Uri $url -Method POST -Headers $headers -Body $bodyBytes
    [PSCustomObject]@{
        threadId = $result.id
        status   = $result.status
        author   = $result.comments[0].author.displayName
        content  = $result.comments[0].content
    } | ConvertTo-Json
    return
}

$threadContext = @{ filePath = "/$($FilePath.TrimStart('/'))" }
if ($LineNumber -gt 0) {
    $threadContext.rightFileStart = @{ line = $LineNumber; offset = 1 }
    $threadContext.rightFileEnd   = @{ line = $LineNumber; offset = 1 }
}

$body = @{
    status        = 'active'
    threadContext = $threadContext
    comments      = @(
        @{
            parentCommentId = 0
            content         = $Content
            commentType     = 1
        }
    )
} | ConvertTo-Json -Depth 5 -Compress

$bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($body)
$result = Invoke-AzdoRest -Uri $url -Method POST -Headers $headers -Body $bodyBytes
[PSCustomObject]@{
    threadId = $result.id
    status   = $result.status
    author   = $result.comments[0].author.displayName
    content  = $result.comments[0].content
} | ConvertTo-Json
