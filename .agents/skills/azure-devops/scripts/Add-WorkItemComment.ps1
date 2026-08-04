<#
.SYNOPSIS
    Adds a comment to an Azure DevOps work item.

.PARAMETER Org
    Full organization URL (e.g. https://dev.azure.com/myorg).

.PARAMETER Project
    Project name.

.PARAMETER WorkItemId
    Numeric work item ID.

.PARAMETER Comment
    Comment text (plain text or HTML). Mutually exclusive with -File.

.PARAMETER File
    Path to a file whose UTF-8 content is used as the comment body. Use this from bash
    instead of `-Comment (Get-Content ...)` which is PowerShell-only syntax. Mutually
    exclusive with -Comment.

.EXAMPLE
    .\Add-WorkItemComment.ps1 -Org https://dev.azure.com/SISopra -Project ISSSG_Training -WorkItemId 123 -Comment "Investigation complete."

.EXAMPLE
    pwsh ./Add-WorkItemComment.ps1 -Org https://dev.azure.com/SISopra -Project ISSSG_Training -WorkItemId 123 -File /tmp/plan.html
#>
[CmdletBinding(DefaultParameterSetName = 'Inline')]
param(
    [Parameter(Mandatory)] [string] $Org,
    [Parameter(Mandatory)] [string] $Project,
    [Parameter(Mandatory)] [int]    $WorkItemId,
    [Parameter(Mandatory, ParameterSetName = 'Inline')]   [string] $Comment,
    [Parameter(Mandatory, ParameterSetName = 'FromFile')] [string] $File
)

if ($PSCmdlet.ParameterSetName -eq 'FromFile') {
    if (-not (Test-Path -LiteralPath $File)) {
        [Console]::Error.WriteLine("ERROR: -File '$File' not found.")
        exit 1
    }
    $Comment = Get-Content -LiteralPath $File -Raw -Encoding UTF8
}

if ([string]::IsNullOrWhiteSpace($Comment)) {
    [Console]::Error.WriteLine("ERROR: comment body is empty.")
    exit 1
}

. "$PSScriptRoot/_AzdoCommon.ps1"
$headers = @{ Authorization = (Get-AzdoAuthHeader); 'Content-Type' = 'application/json' }
$orgName = $Org.TrimEnd('/').Split('/')[-1]
$url = "https://dev.azure.com/$orgName/$Project/_apis/wit/workItems/$($WorkItemId)/comments?api-version=7.1-preview.3"

$body = @{ text = $Comment } | ConvertTo-Json -Compress
$bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($body)

$result = Invoke-AzdoRest -Uri $url -Method POST -Headers $headers -Body $bodyBytes

[PSCustomObject]@{
    workItemId  = $WorkItemId
    commentId   = $result.id
    author      = $result.createdBy.displayName
    createdDate = $result.createdDate
    text        = $result.text
} | ConvertTo-Json
