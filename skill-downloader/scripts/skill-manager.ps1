param(
  [ValidateSet("list", "list-repos", "install", "info", "search", "categories")]
  [string]$Command = "list-repos",
  [string]$Repo = "",
  [string]$Skill = "",
  [string]$Dest = "",
  [string]$Subdir = "",
  [string]$Keyword = ""
)

$Proxy = "https://ghproxy.net"
$ApiBase = "$Proxy/https://api.github.com"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$IndexFile = Join-Path (Split-Path -Parent $ScriptDir) "SKILL-INDEX.md"

# -- Repo Registry --
# SingleSkill = "" means entire repo is one skill, auto-fills SkillName
$Repos = [ordered]@{
  # === 原 4 个仓库 ===
  "anthropics/skills" = @{
    DisplayName = "Anthropic Official"
    Prefix      = "skills/"
    Branch      = "main"
    Desc        = "Official skills: docx, pdf, pptx, xlsx, frontend-design, claude-api (17 total)"
  }
  "ComposioHQ/awesome-claude-skills" = @{
    DisplayName = "Composio Community"
    Prefix      = ""
    Branch      = "master"
    Desc        = "Community collection: root(31) + composio-skills/(100+) + document-skills/(4)"
  }
  "JimLiu/baoyu-skills" = @{
    DisplayName = "Baoyu Skills"
    Prefix      = "skills/"
    Branch      = "main"
    Desc        = "Chinese: translation, illustration, WeChat, Xiaohongshu, video (22 total)"
  }
  "stellarlinkco/myclaude" = @{
    DisplayName = "StellarLink Framework"
    Prefix      = "skills/"
    Branch      = "main"
    Desc        = "Full-stack dev workflow: do, omo, sparv"
  }
  # === 教育 ===
  "GarethManning/education-agent-skills" = @{
    DisplayName = "Education Agent Skills"
    Prefix      = "skills/"
    Branch      = "main"
    Desc        = "131 evidence-based education skills in 19 categories: memory science, assessment, SRL..."
  }
  "Orange0618/teach-me-skill" = @{
    DisplayName    = "Teach Me Skill"
    Prefix         = ""
    Branch         = "main"
    Desc           = "AI as tutor: explain-before-code, line-by-line annotation, wait-for-confirm"
    SingleSkill    = "teach-me-skill"
  }
  "SamuelSchlesinger/ai-tutor" = @{
    DisplayName = "AI Tutor"
    Prefix      = ""
    Branch      = "main"
    Desc        = "Personalized tutor: assess, curriculum, interactive lessons, track progress"
  }
  # === 演示 / Presentation ===
  "shawnzam/keynot" = @{
    DisplayName    = "Keynot"
    Prefix         = "skills/keynot/"
    Branch         = "main"
    Desc           = "Prompt-to-polished HTML slide deck, no Keynote/PPT needed"
    SingleSkill    = "keynot"
  }
  "op7418/guizang-ppt-skill" = @{
    DisplayName    = "Guizang PPT"
    Prefix         = ""
    Branch         = "main"
    Desc           = "Magazine-style HTML slides, horizontal swipe, 10 layouts, 5 themes"
    SingleSkill    = "guizang-ppt-skill"
  }
  "zarazhangrui/frontend-slides" = @{
    DisplayName    = "Frontend Slides"
    Prefix         = ""
    Branch         = "main"
    Desc           = "Animation-rich HTML presentations, 12 styles, PDF export"
  }
  "Noi1r/beamer-skill" = @{
    DisplayName    = "Beamer Skill"
    Prefix         = ""
    Branch         = "main"
    Desc           = "LaTeX Beamer academic presentations: create, compile, review, polish"
    SingleSkill    = "beamer-skill"
  }
  # === 开发 ===
  "obra/superpowers" = @{
    DisplayName = "Obra Superpowers"
    Prefix      = "skills/"
    Branch      = "main"
    Desc        = "14 battle-tested dev skills: brainstorming, TDD, debugging, code-review..."
  }
  "Jeffallan/claude-skills" = @{
    DisplayName = "Claude Skills (Jeffallan)"
    Prefix      = "skills/"
    Branch      = "main"
    Desc        = "66 full-stack dev skills across 12 categories"
  }
}

# ===========================
#  Helpers
# ===========================
function Invoke-GhApi($Url) {
  try {
    if ($env:GITHUB_TOKEN) {
      $result = curl.exe -skL -H "Authorization: Bearer $env:GITHUB_TOKEN" $Url 2>$null
    } else {
      $result = curl.exe -skL $Url 2>$null
    }
    if (-not $result) { return $null }
    return $result | ConvertFrom-Json
  } catch { return $null }
}

function Get-GhRawUrl($RepoKey, $Branch, $Prefix, $FilePath) {
  $owner, $repo = $RepoKey -split '/'
  return "$Proxy/https://raw.githubusercontent.com/$owner/$repo/$Branch/$Prefix$FilePath"
}

# ===========================
#  Commands
# ===========================
function List-Repos {
  Write-Host ""
  Write-Host "Available skill repositories:" -ForegroundColor Cyan
  Write-Host ""
  $i = 1
  foreach ($key in $Repos.Keys) {
    $r = $Repos[$key]
    $typeInfo = if ($r.SingleSkill) { " [single skill]" } else { "" }
    Write-Host "$i. $($r.DisplayName)$typeInfo" -ForegroundColor Yellow
    Write-Host "   $key" -ForegroundColor DarkGray
    Write-Host "   $($r.Desc)" -ForegroundColor Gray
    $i++
  }
  Write-Host ""
}

function List-Skills {
  param([string]$RepoKey, [string]$SubDir)
  $r = $Repos[$RepoKey]
  if (-not $r) { Write-Error "Unknown repo: $RepoKey"; exit 1 }

  # Single-skill repos just list themselves
  if ($r.SingleSkill) {
    Write-Host ""
    Write-Host "$($r.DisplayName) ($RepoKey)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  1. $($r.SingleSkill)" -ForegroundColor White
    Write-Host "     $($r.Desc)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Total: 1 skill" -ForegroundColor Green
    return @($r.SingleSkill)
  }

  $apiPath = if ($SubDir) { "$($r.Prefix)$SubDir/" } else { $r.Prefix }
  $displayName = if ($SubDir) { "$($r.DisplayName) /$SubDir" } else { $r.DisplayName }

  Write-Host "Fetching $displayName..." -ForegroundColor Cyan
  $url = "$ApiBase/repos/$RepoKey/contents/$apiPath"
  $items = Invoke-GhApi $url

  if (-not $items) {
    Write-Error "Failed to fetch. Check network or set GITHUB_TOKEN."
    exit 1
  }

  Write-Host ""
  Write-Host "$displayName" -ForegroundColor Cyan
  Write-Host ""
  $i = 1; $skills = @()
  foreach ($item in $items) {
    if ($item.type -eq "dir") {
      $skills += $item.name
      Write-Host "  $i. $($item.name)" -ForegroundColor White
      $i++
    }
  }
  Write-Host ""
  Write-Host "Total: $($skills.Count) skills" -ForegroundColor Green
  return $skills
}

function List-Categories {
  param([string]$RepoKey)
  $r = $Repos[$RepoKey]
  if (-not $r) { Write-Error "Unknown repo: $RepoKey"; exit 1 }
  if ($r.SingleSkill) {
    Write-Host "This is a single-skill repo, no subcategories." -ForegroundColor Yellow
    return
  }

  Write-Host ""
  Write-Host "Subcategories for ${RepoKey}:" -ForegroundColor Cyan
  Write-Host ""

  $url = "$ApiBase/repos/$RepoKey/contents/$($r.Prefix)"
  $items = Invoke-GhApi $url
  if (-not $items) {
    Write-Error "Failed to fetch."
    exit 1
  }

  $i = 1
  foreach ($item in $items) {
    if ($item.type -eq "dir") {
      Write-Host "  $i. $($item.name)/" -ForegroundColor White
      $i++
    }
  }
  Write-Host ""
}

function Get-SkillInfo {
  param([string]$RepoKey, [string]$SkillName, [string]$SubDir)
  $r = $Repos[$RepoKey]
  if (-not $r) { Write-Error "Unknown repo: $RepoKey"; exit 1 }
  if (-not $SkillName -and -not $r.SingleSkill) { Write-Error "Specify skill name"; exit 1 }
  if (-not $SkillName) { $SkillName = $r.SingleSkill }

  # Determine path to SKILL.md
  if ($r.SingleSkill) {
    $fileUrl = Get-GhRawUrl $RepoKey $r.Branch "" "$($r.Prefix)SKILL.md"
  } elseif ($SubDir) {
    $fileUrl = Get-GhRawUrl $RepoKey $r.Branch "" "$($r.Prefix)$SubDir/$SkillName/SKILL.md"
  } else {
    $fileUrl = Get-GhRawUrl $RepoKey $r.Branch "" "$($r.Prefix)$SkillName/SKILL.md"
  }

  Write-Host "Fetching info for $SkillName..." -ForegroundColor Cyan
  $content = curl.exe -skL $fileUrl 2>$null
  if (-not $content) {
    Write-Error "Skill '$SkillName' not found in $RepoKey"
    exit 1
  }
  # PowerShell captures native exe output as array; convert to single string
  if ($content -is [array]) { $content = $content -join "`n" }

  # Parse frontmatter for description
  if ($content -match '(?s)^---\s*\n(.*?)\n---') {
    $fm = $Matches[1]
    Write-Host ""; Write-Host "$SkillName" -ForegroundColor Yellow
    Write-Host "  Repo: $RepoKey" -ForegroundColor DarkGray
    if ($SubDir) { Write-Host "  Category: $SubDir" -ForegroundColor DarkGray }

    # Extract description (handles quoted, unquoted, and multi-line)
    if ($fm -match '(?s)description:\s*["''](.*?)["''](\n\S|\z)') {
      $desc = $Matches[1].Trim()
      Write-Host "  $desc" -ForegroundColor Gray
    } elseif ($fm -match '(?s)description:\s*\|(.*?)(\n\S|\z)') {
      $desc = $Matches[1].Trim()
      Write-Host "  $desc" -ForegroundColor Gray
    } elseif ($fm -match '(?s)description:\s*>\s*(.*?)(\n\S|\z)') {
      $desc = $Matches[1].Trim()
      Write-Host "  $desc" -ForegroundColor Gray
    } elseif ($fm -match '(?s)description:\s*(.*?)(\n\w+:\s*|\z)') {
      $desc = $Matches[1].Trim()
      Write-Host "  $desc" -ForegroundColor Gray
    } else {
      Write-Host "  (see SKILL.md for details)" -ForegroundColor Gray
    }
    Write-Host ""
  } else {
    Write-Host ""; Write-Host "$SkillName" -ForegroundColor Yellow
    Write-Host "  Repo: $RepoKey" -ForegroundColor DarkGray
    Write-Host "  (no YAML frontmatter)" -ForegroundColor Gray
    Write-Host ""
  }
}

function Install-Skill {
  param([string]$RepoKey, [string]$SkillName, [string]$DestDir, [string]$SubDir)
  $r = $Repos[$RepoKey]
  if (-not $r) { Write-Error "Unknown repo: $RepoKey"; exit 1 }

  # Auto-fill skill name for single-skill repos
  if (-not $SkillName -and $r.SingleSkill) {
    $SkillName = $r.SingleSkill
  }
  if (-not $SkillName) { Write-Error "Specify skill name"; exit 1 }

  if (-not $DestDir) {
    $DestDir = Join-Path $env:USERPROFILE ".claude\skills\$SkillName"
  }

  Write-Host "Installing $SkillName to $DestDir ..." -ForegroundColor Cyan

  $owner, $repo = $RepoKey -split '/'
  $treeUrl = "$ApiBase/repos/$owner/$repo/git/trees/$($r.Branch)?recursive=1"
  $tree = Invoke-GhApi $treeUrl

  if (-not $tree -or -not $tree.tree) {
    Write-Error "Failed to get file list."
    exit 1
  }

  # Determine path prefix for tree search
  if ($r.SingleSkill) {
    $searchPrefix = $r.Prefix
  } elseif ($SubDir) {
    $searchPrefix = "$($r.Prefix)$SubDir/$SkillName/"
  } else {
    $searchPrefix = "$($r.Prefix)$SkillName/"
  }

  $files = $tree.tree | Where-Object { $_.path -like "$searchPrefix*" -and $_.type -eq "blob" }

  if ($files.Count -eq 0) {
    Write-Error "No files found for $SkillName (path: $searchPrefix)"
    exit 1
  }

  $downloaded = 0
  foreach ($f in $files) {
    $relPath = $f.path.Substring($searchPrefix.Length)
    $targetPath = Join-Path $DestDir $relPath
    $parentDir = Split-Path $targetPath -Parent

    New-Item -ItemType Directory -Path $parentDir -Force | Out-Null

    $dlUrl = Get-GhRawUrl $RepoKey $r.Branch "" $f.path
    try {
      curl.exe -skL -o "$targetPath" $dlUrl 2>$null
      if ($?) { $downloaded++ }
    } catch {
      Write-Host "  Ignored: $relPath" -ForegroundColor DarkYellow
    }
  }

  $skillMd = Join-Path $DestDir "SKILL.md"
  if (Test-Path $skillMd) {
    Write-Host ""
    Write-Host "[OK] Installation successful!" -ForegroundColor Green
    Write-Host "    Path: $DestDir" -ForegroundColor Gray
    Write-Host "    Files: $downloaded" -ForegroundColor Gray
    Write-Host "    Usage: /$SkillName (restart Claude Code to activate)" -ForegroundColor Gray
  } else {
    Write-Host ""
    Write-Host "Installation may be incomplete - SKILL.md not found" -ForegroundColor DarkYellow
  }
}

function Search-Skills {
  param([string]$Keyword)
  if (-not $Keyword) { Write-Error "Provide a keyword, e.g.: search translate"; exit 1 }

  Write-Host ""
  Write-Host "Searching for '$Keyword' across all repos..." -ForegroundColor Cyan
  Write-Host ""

  $found = @()
  $kw = $Keyword.ToLower()

  foreach ($key in $Repos.Keys) {
    $r = $Repos[$key]
    if ($r.SingleSkill) {
      if ($r.SingleSkill.ToLower() -match $kw -or $r.Desc.ToLower() -match $kw) {
        $found += [PSCustomObject]@{ Name = $r.SingleSkill; Repo = $key; Desc = $r.Desc; Category = "" }
      }
      continue
    }

    # Try API to get skill names
    $url = "$ApiBase/repos/$key/contents/$($r.Prefix)"
    $items = Invoke-GhApi $url
    if (-not $items) { continue }

    foreach ($item in $items) {
      if ($item.type -eq "dir" -and $item.name.ToLower() -match $kw) {
        $found += [PSCustomObject]@{ Name = $item.name; Repo = $key; Desc = ""; Category = "" }
      }
    }
  }

  # Also scan local SKILL-INDEX.md for keyword matches
  if (Test-Path $IndexFile) {
    $index = Get-Content $IndexFile -Raw
    # Extract all markdown table rows
    if ($index -match "(?s)\|.*\|") {
      # Simple approach: extract lines that contain the keyword
      $lines = $index -split "`n"
      $inSkillTable = $false
      $currentRepo = ""
      foreach ($line in $lines) {
        if ($line -match "^##\s+(.+)") {
          $currentRepo = $Matches[1].Trim()
          $inSkillTable = $false
        }
        if ($line -match "^\|.*\|.*\|.*\|") {
          # Check if it's a data row (not header/separator)
          if ($line -notmatch "^[\|\s:-]+$" -and $line -notmatch "^\|\\#") {
            $cells = $line -split "\|" | Where-Object { $_.Trim() -ne "" }
            if ($cells.Count -ge 2) {
              $nameCell = $cells[0].Trim()
              $descCell = if ($cells.Count -ge 2) { $cells[1].Trim() } else { "" }
              if ($nameCell.ToLower() -match $kw -or $descCell.ToLower() -match $kw) {
                # Skip if already found via API
                $alreadyFound = $found | Where-Object { $_.Name -eq $nameCell -and $_.Repo -eq $currentRepo }
                if (-not $alreadyFound) {
                  $found += [PSCustomObject]@{ Name = $nameCell; Repo = $currentRepo; Desc = $descCell; Category = "" }
                }
              }
            }
          }
        }
      }
    }
  }

  if ($found.Count -eq 0) {
    Write-Host "No skills matching '$Keyword' found." -ForegroundColor Yellow
    Write-Host "Try: search slide, search translate, search memory, search quiz" -ForegroundColor Gray
    return
  }

  Write-Host "Found $($found.Count) matching skills:" -ForegroundColor Green
  Write-Host ""

  # Group by repo
  $groups = $found | Group-Object Repo
  foreach ($g in $groups) {
    Write-Host "  $($g.Name):" -ForegroundColor Yellow
    foreach ($s in $g.Group) {
      $extra = if ($s.Desc) { " — $($s.Desc)" } else { "" }
      Write-Host "    $($s.Name)$extra" -ForegroundColor White
    }
    Write-Host ""
  }
}

# ===========================
#  Main
# ===========================
switch ($Command) {
  "list-repos" { List-Repos }

  "list" {
    if (-not $Repo) {
      Write-Host "Usage: list (repo) [-Subdir (category)]" -ForegroundColor Yellow
      Write-Host "  Example: list anthropics/skills" -ForegroundColor Gray
      Write-Host "  Example: list GarethManning/education-agent-skills -Subdir memory-learning-science" -ForegroundColor Gray
      Write-Host "  Example: list ComposioHQ/awesome-claude-skills -Subdir composio-skills" -ForegroundColor Gray
      exit
    }
    List-Skills $Repo $Subdir
  }

  "categories" {
    if (-not $Repo) {
      Write-Host "Usage: categories (repo)" -ForegroundColor Yellow
      Write-Host "  Example: categories GarethManning/education-agent-skills" -ForegroundColor Gray
      exit
    }
    List-Categories $Repo
  }

  "search" {
    Search-Skills $Keyword
  }

  "info" {
    if (-not $Repo -or -not $Skill) {
      Write-Host "Usage: info (repo) (skill) [-Subdir (category)]" -ForegroundColor Yellow
      Write-Host "  Example: info anthropics/skills docx" -ForegroundColor Gray
      Write-Host "  Example: info GarethManning/education-agent-skills retrieval-practice-generator -Subdir memory-learning-science" -ForegroundColor Gray
      exit
    }
    Get-SkillInfo $Repo $Skill $Subdir
  }

  "install" {
    if (-not $Repo) {
      Write-Host "Usage: install (repo) [skill] [-Subdir (category)] [-Dest (path)]" -ForegroundColor Yellow
      Write-Host "  Example: install JimLiu/baoyu-skills baoyu-translate" -ForegroundColor Gray
      Write-Host "  Example: install shawnzam/keynot" -ForegroundColor Gray
      Write-Host "  Example: install GarethManning/education-agent-skills retrieval-practice-generator -Subdir memory-learning-science" -ForegroundColor Gray
      exit
    }
    Install-Skill $Repo $Skill $Dest $Subdir
  }
}
