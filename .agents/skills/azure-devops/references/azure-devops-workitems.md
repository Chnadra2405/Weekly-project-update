# Azure Devops Workitems

## Fetch work item details

```powershell
.\<skill-folder>\scripts\Get-WorkItem.ps1 `
    -Org https://dev.azure.com/<ORG> `
    -Project <PROJECT> `
    -WorkItemId <WORK_ITEM_ID>
```

> Returns a unified JSON object with fields: `id`, `title`, `workItemType`, `state`, `aiStatus` (value of `Custom.AIStatus`), `assignedTo`, `priority`, `tags`, `areaPath`, `iterationPath`, `createdDate`, `changedDate`, `url`, `description`, `acceptanceCriteria`, `comments`, `branches`, `pullRequests`, `commits`.
> - `comments` is populated automatically when `CommentCount > 0`.
> - `branches`, `pullRequests`, `commits` are extracted from Git `Artifact Link` relations on the work item. Each entry includes `projectId` and `repoId` (GUIDs). `branches` entries also include `branchName` and `refName`; `pullRequests` entries include `pullRequestId`; `commits` entries include `commitSha`.
> - Use `branches[0].branchName` to resolve the working branch for a work item; if empty, no branch has been linked yet.

## Create a new work item

> Standard work item types: `Epic`, `Feature`, `User Story`, `Task`, `Bug`.
> Description and AcceptanceCriteria must use HTML elements and not carriage returns like '`n' because the lines will not be taken into account.

```powershell
.\<skill-folder>\scripts\New-WorkItem.ps1 `
    -Org https://dev.azure.com/<ORG> `
    -Project <PROJECT> `
    -Title "<WORK_ITEM_TITLE>" `
    -Type "User Story" `
    [-Description "<HTML_DESCRIPTION>"] `
    [-AcceptanceCriteria "<HTML_CRITERIA>"] `
    [-AreaPath "<AREA_PATH>"] `
    [-IterationPath "<ITERATION_PATH>"] `
    [-Priority <1-4>] `
    [-Tags "<tag1; tag2>"] `
    [-AssignedTo "<email_or_name>"] `
    [-ParentId <PARENT_WORK_ITEM_ID>]
```

> `-ParentId` links the item to a parent (relation type `System.LinkTypes.Hierarchy-Reverse`).

## Update workitem state

> Standard state types: `New`, `Active`, `Resolved`, `Closed`.

```powershell
.\<skill-folder>\scripts\Edit-WorkItemState.ps1 `
    -Org https://dev.azure.com/<ORG> `
    -Project <PROJECT> `
    -WorkItemId <WORK_ITEM_ID> `
    -NewState Closed `
    [-Comment "Optional comment to post after the state change"]
```

## Update workitem fields

Accepts short names (`Title`, `State`, `Priority`, `Tags`, `AssignedTo`, `Description`, `AcceptanceCriteria`, `AreaPath`, `IterationPath`) or full `System.*` / `Microsoft.VSTS.*` / `Custom.*` field paths.

```powershell
.\<skill-folder>\scripts\Edit-WorkItem.ps1 `
    -Org https://dev.azure.com/<ORG> `
    -Project <PROJECT> `
    -WorkItemId <WORK_ITEM_ID> `
    -Fields "Title=New title", "Priority=2"
```

### Update `Custom.AIStatus` (Zephyr pipeline)

The Zephyr orchestrator drives the autonomous workflow via the `Custom.AIStatus` picklist field. Each Zephyr agent must update this field at the end of its run to advance the pipeline. Use the full field path (`Custom.AIStatus=...`) because the short-name map does not include it.

```powershell
.\<skill-folder>\scripts\Edit-WorkItem.ps1 `
    -Org https://dev.azure.com/<ORG> `
    -Project <PROJECT> `
    -WorkItemId <WORK_ITEM_ID> `
    -Fields "Custom.AIStatus=02.01 - Ready to Implement"
```

> Values are case- and whitespace-sensitive; use them verbatim from the orchestrator `appsettings.json` (`ReadyValue` / `InProgressValue`).

## Query work items by assignee

Use the assignee's display name or email. To find items assigned to the current user, use their display name (e.g. `"John Doe"`).

```powershell
.\<skill-folder>\scripts\Search-WorkItems.ps1 `
    -Org https://dev.azure.com/<ORG> `
    -Project <PROJECT> `
    -AssignedTo "<DISPLAY_NAME_OR_EMAIL>" `
    [-State "Active"] `
    [-Top 50]
```

## Add a comment to a work item

Inline (short text):
```powershell
.\<skill-folder>\scripts\Add-WorkItemComment.ps1 `
    -Org https://dev.azure.com/<ORG> `
    -Project <PROJECT> `
    -WorkItemId <WORK_ITEM_ID> `
    -Comment "<COMMENT_TEXT>"
```

From a file (preferred for HTML / multi-line content, especially from bash):
```bash
pwsh ./<skill-folder>/scripts/Add-WorkItemComment.ps1 \
    -Org https://dev.azure.com/<ORG> \
    -Project <PROJECT> \
    -WorkItemId <WORK_ITEM_ID> \
    -File /tmp/comment.html
```

> Use `-File` instead of `-Comment (Get-Content ... -Raw)` &mdash; the latter is PowerShell-only syntax and will be passed as a literal string from bash.

## Link a Git branch to a work item

Creates an `Artifact Link` relation of type `Branch`. Idempotent: skips the PATCH if a branch link with the same artifact URL already exists.

```powershell
.\<skill-folder>\scripts\Add-WorkItemBranchLink.ps1 `
    -Org https://dev.azure.com/<ORG> `
    -Project <PROJECT> `
    -Repository <REPOSITORY_NAME> `
    -WorkItemId <WORK_ITEM_ID> `
    -BranchName "feature/<id>-<short-desc>"
```

> Returns `{ workItemId, branchName, artifactUrl, status }` where `status` is `linked` or `already-linked`. Use this right after creating a branch so downstream agents can recover the working branch via `Get-WorkItem.ps1` (`branches` field).