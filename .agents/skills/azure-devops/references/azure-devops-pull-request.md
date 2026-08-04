# Azure DevOps Pull Request

## List open PRs for a repository

Default status is `active`. Other values: `completed`, `abandoned`, `all`.

```powershell
.\<skill-folder>\skills\azure-devops\scripts\Get-PRList.ps1 `
    -Org https://dev.azure.com/<ORGANIZATION_NAME> `
    -Project <PROJECT_NAME> `
    -Repository <REPOSITORY_NAME> `
    [-Status active]
```

## Show PR details

```powershell
.\<skill-folder>\skills\azure-devops\scripts\Get-PRDetails.ps1 `
    -Org https://dev.azure.com/<ORGANIZATION_NAME> `
    -PullRequestId <PR_ID>
```

> Reviewer `vote` values: `10` = Approved, `5` = Approved with suggestions, `0` = No vote, `-5` = Waiting for author, `-10` = Rejected.

## List changed files in a PR

```powershell
.\<skill-folder>\skills\azure-devops\scripts\Get-PRChanges.ps1 `
    -Org https://dev.azure.com/<ORGANIZATION_NAME> `
    -Project <PROJECT_NAME> `
    -Repository <REPOSITORY_NAME> `
    -PullRequestId <PR_ID>
```

## Get a unified diff for a specific file in a PR

Returns a JSON object with `filePath` and `diff` — the diff is formatted like `git diff` (unified, 3 lines of context).

```powershell
.\<skill-folder>\skills\azure-devops\scripts\Get-PRChanges.ps1 `
    -Org https://dev.azure.com/<ORGANIZATION_NAME> `
    -Project <PROJECT_NAME> `
    -Repository <REPOSITORY_NAME> `
    -PullRequestId <PR_ID> `
    -FilePath "src/MyClass.cs"
```

Example output:
```json
{
    "filePath": "src/MyClass.cs",
    "diff": "diff --git a/src/MyClass.cs b/src/MyClass.cs\nindex ...\n--- a/src/MyClass.cs\n+++ b/src/MyClass.cs\n@@ -10,3 +10,5 @@\n ..."
}
```

> The diff compares `lastMergeTargetCommit` (base branch) against `lastMergeSourceCommit` (PR branch).


## PR Threads 

### Get PR threads

```powershell
.\<skill-folder>\skills\azure-devops\scripts\Get-PRThreads.ps1 `
    -Org https://dev.azure.com/<ORGANIZATION_NAME> `
    -Project <PROJECT_NAME> `
    -Repository <REPOSITORY_NAME> `
    -PullRequestId <PR_ID>
```


### Add a PR comment (new thread)

General thread:
```powershell
.\<skill-folder>\skills\azure-devops\scripts\Add-PRThread.ps1 `
    -Org https://dev.azure.com/<ORGANIZATION_NAME> `
    -Project <PROJECT_NAME> `
    -Repository <REPOSITORY_NAME> `
    -PullRequestId <PR_ID> `
    -Content "<COMMENT_CONTENT>"
```

File-scoped thread (optional line number):
```powershell
.\<skill-folder>\skills\azure-devops\scripts\Add-PRThread.ps1 `
    -Org https://dev.azure.com/<ORGANIZATION_NAME> `
    -Project <PROJECT_NAME> `
    -Repository <REPOSITORY_NAME> `
    -PullRequestId <PR_ID> `
    -Content "<COMMENT_CONTENT>" `
    -FilePath "src/MyClass.cs" `
    [-LineNumber 42]
```

### Reply to a comment thread

```powershell
.\<skill-folder>\skills\azure-devops\scripts\Add-PRReply.ps1 `
    -Org https://dev.azure.com/<ORGANIZATION_NAME> `
    -Project <PROJECT_NAME> `
    -Repository <REPOSITORY_NAME> `
    -PullRequestId <PR_ID> `
    -ThreadId <THREAD_ID> `
    -Content "<REPLY_CONTENT>"
```

### Update thread status

Valid statuses: `active`, `fixed`, `wontFix`, `closed`, `byDesign`, `pending`.

```powershell
.\<skill-folder>\skills\azure-devops\scripts\Set-PRThreadStatus.ps1 `
    -Org https://dev.azure.com/<ORGANIZATION_NAME> `
    -Project <PROJECT_NAME> `
    -Repository <REPOSITORY_NAME> `
    -PullRequestId <PR_ID> `
    -ThreadId <THREAD_ID> `
    -Status fixed
```

## Create a pull request

Creates a PR via `az repos pr create` and optionally links it to one or more work items via `--work-items`. Returns `{ pullRequestId, title, status, sourceRefName, targetRefName, createdBy, url }` as JSON.

```powershell
.\<skill-folder>\skills\azure-devops\scripts\New-PullRequest.ps1 `
    -Org https://dev.azure.com/<ORGANIZATION_NAME> `
    -Project <PROJECT_NAME> `
    -Repository <REPOSITORY_NAME> `
    -SourceBranch "feature/<id>-<short-desc>" `
    -TargetBranch "master" `
    -Title "<PR_TITLE>" `
    [-Description "<PR_DESCRIPTION>"] `
    [-WorkItemIds <WORK_ITEM_ID>[,<WORK_ITEM_ID>...]]
```

> Branch names must omit the `refs/heads/` prefix. The script reconstructs the human-readable PR URL (`.../pullrequest/<id>`) for the response.