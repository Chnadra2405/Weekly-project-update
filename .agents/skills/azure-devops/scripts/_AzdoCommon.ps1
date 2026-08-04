<#
.SYNOPSIS
    Shared helpers for Azure DevOps REST scripts (auth + fail-loud Invoke-RestMethod).

.DESCRIPTION
    Dot-source from any script in this folder:
        . "$PSScriptRoot/_AzdoCommon.ps1"

    Then:
        $authValue = Get-AzdoAuthHeader
        $result    = Invoke-AzdoRest -Uri $url -Method POST -Headers @{ Authorization = $authValue; 'Content-Type' = 'application/json' } -Body $bodyBytes

    On HTTP failure, Invoke-AzdoRest writes a structured error to stderr (URL, method,
    HTTP status, response body) and calls `exit 1`. Callers must NOT wrap it in their
    own try/catch unless they have a specific recovery path.

    On missing credentials, Get-AzdoAuthHeader writes a structured error to stderr and
    calls `exit 1`.
#>

function Get-AzdoAuthHeader {
    [CmdletBinding()]
    param()

    if ($env:AZURE_DEVOPS_EXT_PAT) {
        return 'Basic ' + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$($env:AZURE_DEVOPS_EXT_PAT)"))
    }

    $token = (az account get-access-token --resource 499b84ac-1321-427f-aa17-267ca6975798 --query accessToken -o tsv 2>$null)
    if (-not $token) {
        [Console]::Error.WriteLine("ERROR: No Azure DevOps credentials available.")
        [Console]::Error.WriteLine("       Set AZURE_DEVOPS_EXT_PAT (PAT) or run 'az login' before invoking this script.")
        exit 1
    }
    return "Bearer $($token.Trim())"
}

function Invoke-AzdoRest {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string]    $Uri,
        [string]    $Method  = 'GET',
        [hashtable] $Headers = @{},
                    $Body
    )

    try {
        if ($PSBoundParameters.ContainsKey('Body') -and $null -ne $Body) {
            return Invoke-RestMethod -Uri $Uri -Method $Method -Headers $Headers -Body $Body -ErrorAction Stop
        }
        return Invoke-RestMethod -Uri $Uri -Method $Method -Headers $Headers -ErrorAction Stop
    } catch {
        $status = if ($_.Exception.Response) { [int]$_.Exception.Response.StatusCode } else { 'N/A' }
        $msg    = if ($_.ErrorDetails -and $_.ErrorDetails.Message) { $_.ErrorDetails.Message } else { $_.Exception.Message }
        [Console]::Error.WriteLine("ERROR: Azure DevOps REST call failed.")
        [Console]::Error.WriteLine("  URL    : $Uri")
        [Console]::Error.WriteLine("  Method : $Method")
        [Console]::Error.WriteLine("  Status : HTTP $status")
        [Console]::Error.WriteLine("  Body   : $msg")
        exit 1
    }
}
