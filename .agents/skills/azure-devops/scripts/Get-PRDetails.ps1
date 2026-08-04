<#
.SYNOPSIS
    Shows details of a pull request including reviewers and their votes.

.PARAMETER Org
    Full organization URL (e.g. https://dev.azure.com/myorg).

.PARAMETER PullRequestId
    Pull request ID.

.EXAMPLE
    .\Get-PRDetails.ps1 -Org https://dev.azure.com/SISopra -PullRequestId 465

.NOTES
    Reviewer vote values: 10=Approved, 5=Approved with suggestions, 0=No vote,
    -5=Waiting for author, -10=Rejected.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $Org,
    [Parameter(Mandatory)] [int]    $PullRequestId
)

$pr = az repos pr show `
    --id $PullRequestId `
    --org $Org `
    --output json | ConvertFrom-Json

if ($null -eq $pr) { Write-Error "PR $PullRequestId not found."; exit 1 }

$orgSegment = $pr.url.Split('/')[3]

[PSCustomObject]@{
    pullRequestId = $pr.pullRequestId
    title         = $pr.title
    description   = $pr.description
    author        = $pr.createdBy.displayName
    creationDate  = $pr.creationDate
    status        = $pr.status
    mergeStatus   = $pr.mergeStatus
    sourceRefName = $pr.sourceRefName
    targetRefName = $pr.targetRefName
    sourceCommit  = $pr.lastMergeSourceCommit.commitId
    reviewers     = @($pr.reviewers | ForEach-Object {
        [PSCustomObject]@{
            displayName  = $_.displayName
            vote         = $_.vote
            hasDeclined  = $_.hasDeclined
        }
    })
    url           = "https://dev.azure.com/$orgSegment/$($pr.repository.project.name)/_git/$($pr.repository.name)/pullrequest/$($pr.pullRequestId)"
} | ConvertTo-Json -Depth 5
