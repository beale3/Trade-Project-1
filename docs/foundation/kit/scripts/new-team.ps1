# new-team.ps1 — Governed Agent-Team Foundation Kit v2: executable scaffolder
# Creates the new team's local clone dir + docs skeleton, seeds the kit copy, git-inits,
# creates the private remote under the org via gh, and pushes the first commit.
# The paste-scripts (SCRIPT-1/SCRIPT-2) then author the real foundation on top of this scaffold.
#
# Usage (PowerShell 5.1+, from anywhere):
#   .\new-team.ps1 -Slug myproj [-ProjectName "My Project"] [-Org ShupeCapital]
#                  [-ParentDir "C:\Users\Shupe\Software Dev"] [-Branch main]
#                  [-Trailer "Authored by: Mähnbach <noreply@mahnbach.com>"] [-SkipRemote]
# Requires: git; gh (authenticated: `gh auth status`) unless -SkipRemote.

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [ValidatePattern('^[a-z0-9][a-z0-9-]*$')] [string]$Slug,
    [string]$ProjectName = $null,
    [string]$Org = 'ShupeCapital',
    [string]$ParentDir = 'C:\Users\Shupe\Software Dev',
    [string]$Branch = 'main',
    [string]$Trailer = 'Authored by: Mähnbach <noreply@mahnbach.com>',
    [switch]$SkipRemote
)

$ErrorActionPreference = 'Stop'
if (-not $ProjectName) { $ProjectName = $Slug }
$KitDir   = Split-Path -Parent $PSScriptRoot   # the kit root (this script lives in <kit>/scripts)
$LeadDir  = Join-Path $ParentDir "$Slug-lead"
$RepoName = "$Org/$Slug"

Write-Host "== Foundation Kit scaffolder =="
Write-Host "   project : $ProjectName ($Slug)"
Write-Host "   lead dir: $LeadDir"
Write-Host "   remote  : $(if ($SkipRemote) { '(skipped)' } else { "https://github.com/$RepoName (private)" })"

# -- Preflight ---------------------------------------------------------------
git --version | Out-Null
if (-not $SkipRemote) {
    gh auth status 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "gh is not authenticated. Run 'gh auth login' (or pass -SkipRemote) and retry." }
}
if (Test-Path $LeadDir) {
    if (@(Get-ChildItem $LeadDir -Force | Where-Object Name -ne '.git').Count -gt 0) {
        throw "Target '$LeadDir' exists and is not empty. Refusing to scaffold over existing content."
    }
} else {
    New-Item -ItemType Directory -Force $LeadDir | Out-Null
}

# -- Skeleton ----------------------------------------------------------------
$dirs = @(
    'docs', 'docs\foundation', 'docs\foundation\kit', 'docs\foundation\kit\roles',
    'docs\foundation\kit\scripts', 'docs\gate', 'docs\app-design', 'docs\roles\lead'
)
foreach ($d in $dirs) { New-Item -ItemType Directory -Force (Join-Path $LeadDir $d) | Out-Null }

# Seed the kit copy (linear-inheritance channel: docs/foundation/kit/)
$kitDest = Join-Path $LeadDir 'docs\foundation\kit'
Copy-Item (Join-Path $KitDir '*.md')          $kitDest                          -Force
Copy-Item (Join-Path $KitDir 'roles\*.md')    (Join-Path $kitDest 'roles')      -Force
Copy-Item (Join-Path $KitDir 'scripts\*.ps1') (Join-Path $kitDest 'scripts')    -Force
# The predecessor kit's WIP marker never travels
Remove-Item (Join-Path $kitDest '_WIP-STATUS.md') -Force -ErrorAction SilentlyContinue

# Starter docs (the real foundation is authored by SCRIPT-1/SCRIPT-2 on top of these)
$readme = @"
# $ProjectName

Founded with the Governed Agent-Team Foundation Kit (see ``docs/foundation/kit/``).

**Next steps (the Director):**
1. Open a fresh session in this repo as the team's Lead.
2. Paste ``docs/foundation/kit/SCRIPT-1-found.md`` (captures + validates config).
3. When the Lead confirms, paste ``docs/foundation/kit/SCRIPT-2-generate.md`` (generates the full foundation).
"@
Set-Content -Path (Join-Path $LeadDir 'README.md') -Value $readme -Encoding utf8

$gitignore = @"
.env
.env.*
*.local
node_modules/
dist/
build/
*.log
*api-key*
*.pem
.claude/settings.local.json
"@
Set-Content -Path (Join-Path $LeadDir '.gitignore') -Value $gitignore -Encoding utf8

# Low-friction session defaults, committed so every seat/clone inherits them:
# - permissions.defaultMode "acceptEdits": file edits + allowlisted commands auto-approve;
#   only unusual actions prompt. Full-auto (bypassPermissions) is a per-seat opt-in via the
#   session mode toggle or .claude/settings.local.json — not the committed default.
# - deny keeps the brakes on the destructive class even in permissive modes.
# NOTE (LL-70): a governed agent driving this by hand may be REFUSED write to an active
#   .claude/settings.json by the harness permission classifier. If Set-Content below is blocked,
#   write it as docs/foundation/settings.json.template instead and hand the Director a copy-into-
#   place step — the Director placing it is consistent with full-auto being a per-seat Director act.
New-Item -ItemType Directory -Force (Join-Path $LeadDir '.claude') | Out-Null
$claudeSettings = @"
{
  "permissions": {
    "defaultMode": "acceptEdits",
    "allow": [
      "Bash(git status*)", "Bash(git log*)", "Bash(git diff*)", "Bash(git show*)",
      "Bash(git add *)", "Bash(git commit*)", "Bash(git pull*)", "Bash(git push origin*)",
      "Bash(git fetch*)", "Bash(git rebase*)", "Bash(git stash*)", "Bash(git branch*)",
      "Bash(git checkout -b *)", "Bash(git remote*)", "Bash(git tag*)",
      "Bash(gh repo view*)", "Bash(gh pr *)", "Bash(gh issue *)", "Bash(gh auth status*)",
      "Bash(npm run *)", "Bash(npm test*)", "Bash(npm ci*)", "Bash(npm install*)",
      "Bash(npx tsc*)", "Bash(node *)", "Bash(pnpm *)",
      "PowerShell(git *)", "PowerShell(gh *)", "PowerShell(npm *)", "PowerShell(npx *)", "PowerShell(node *)"
    ],
    "deny": [
      "Bash(git push --force*)", "Bash(git push -f*)", "Bash(git reset --hard*)",
      "Bash(git clean*)", "Bash(rm -rf*)",
      "PowerShell(git push --force*)", "PowerShell(git reset --hard*)",
      "PowerShell(Remove-Item * -Recurse*)"
    ]
  }
}
"@
Set-Content -Path (Join-Path $LeadDir '.claude\settings.json') -Value $claudeSettings -Encoding utf8

# Repo-level CLAUDE.md: auto-loaded by EVERY session in every clone of this repo —
# carries the universal spine so a fresh seat knows the rules before its first action.
$claudeMd = @"
# $ProjectName — team operating spine (auto-loaded; binding on every session)

You are ONE named role/seat on a governed multi-agent team (one session per clone).

FIRST, in order: ``git pull --rebase`` → read ``docs/AGENT-COORDINATION.md`` (charter: protocols 1–15,
symbol legend, live board) → ``docs/decisions-log.md`` → the canonical design doc (it WINS on any
conflict) → YOUR row in ``docs/gate/oracle-boundary.md`` → your profile in ``docs/roles/<role>/``
(mandate + lessons block).

Standing rules (full text in the charter):
- **No background/async subagents, ever.** You perform every assigned task yourself, in this visible
  session. A stall must be visible to the Director.
- **[Via messenger]:** the Lead assigns every task to a named seat by message; you report back to the Lead
  directly on completion (cross-session message + the repo artifact) — AND message the Lead the moment you hit
  a blocking question, ambiguity or issue mid-task (never sit on a blocker or guess past it); message other
  named seats DIRECTLY as the assignment requires. No silent finishes.
- **The decision-maker decides, never debugs (protocol 15).** Anything reaching the Director is COMPLETE,
  GROUNDED, RECONCILED, VERIFIED — five gates (scope → ground → reconcile → verify-at-source → decide). Show the
  COMPLETE picture — nothing under the rug; deferred ≠ excluded; flag every number measured/estimated/unmeasured.
- **Builder ≠ judge.** No seat certifies its own work.
- **Git:** rebase-first · targeted ``git add <paths>`` (never -A) · commit trailer exactly
  ``$Trailer`` · never commit secrets · no literal model IDs in the repo.
- **Two-document rule:** only the Lead edits the canonical design doc; every other seat appends to the
  working log. Hot-file rebase conflict = append collision → keep BOTH entries, yours last.
- **"Cost" means money** — price options in dollars + correctness-risk, never hours/effort.
"@
Set-Content -Path (Join-Path $LeadDir 'CLAUDE.md') -Value $claudeMd -Encoding utf8

# -- Git ---------------------------------------------------------------------
Push-Location $LeadDir
try {
    git init -b $Branch | Out-Null
    git add README.md .gitignore docs | Out-Null
    # Commit via -F from a UTF-8 (no BOM) temp file so the trailer's non-ASCII survives
    $msg = "chore: found $ProjectName - kit scaffold (docs skeleton + foundation kit copy)`n`n$Trailer"
    $msgFile = Join-Path $env:TEMP "newteam-commit-$Slug.txt"
    [System.IO.File]::WriteAllText($msgFile, $msg, (New-Object System.Text.UTF8Encoding($false)))
    git commit -F $msgFile | Out-Null
    Remove-Item $msgFile -Force

    if (-not $SkipRemote) {
        gh repo create $RepoName --private --source=. --remote=origin --push
        if ($LASTEXITCODE -ne 0) { throw "gh repo create failed for $RepoName (does it already exist?)." }
        Write-Host "Pushed to https://github.com/$RepoName"
    } else {
        Write-Host "Remote skipped. Later: gh repo create $RepoName --private --source=. --remote=origin --push"
    }
}
finally { Pop-Location }

Write-Host ""
Write-Host "== Scaffold complete =="
Write-Host "Lead clone: $LeadDir"
Write-Host "Now open a fresh Lead session there and paste docs/foundation/kit/SCRIPT-1-found.md"
