# claude-ahk AHK v2 syntax validator
# Usage: .\scripts\validate-ahk.ps1 <target.ahk>
param(
    [Parameter(Mandatory, Position=0)]
    [string]$ScriptPath
)

if (-not (Test-Path $ScriptPath)) {
    Write-Host "[ERROR] File not found: $ScriptPath" -ForegroundColor Red
    exit 1
}

function Get-NormalizedContent {
    param([string]$Path)
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    # Try UTF-8 first, then default encoding
    try {
        return [System.Text.Encoding]::UTF8.GetString($bytes)
    } catch {
        return [System.Text.Encoding]::Default.GetString($bytes)
    }
}

$content = Get-NormalizedContent $ScriptPath
$lines = $content -split "`r?`n"
$errors = @()

# 1. Check #Requires directive
if ($content -notmatch '#Requires\s+AutoHotkey\s*>=\s*v?2') {
    $errors += "Missing '#Requires AutoHotkey >=2.0' header"
}

# 2. Check #SingleInstance
if ($content -notmatch '#SingleInstance') {
    $errors += "Consider adding '#SingleInstance Force'"
}

# 3. Check brace balance
$openBraces = 0
$closeBraces = 0
$depth = 0
for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    $stripped = $line -replace ';.*$', ''
    foreach ($ch in $stripped.ToCharArray()) {
        if ($ch -eq '{') { $openBraces++; $depth++ }
        if ($ch -eq '}') { $closeBraces++; $depth-- }
    }
    if ($depth -lt 0) {
        $errors += "Line $($i+1): Extra closing brace"
        $depth = 0
    }
}
if ($openBraces -ne $closeBraces) {
    $errors += "Brace mismatch: $openBraces opening, $closeBraces closing"
}

# 4. Check parenthesis balance
$openParen = 0
$closeParen = 0
for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    $stripped = $line -replace ';.*$', ''
    foreach ($ch in $stripped.ToCharArray()) {
        if ($ch -eq '(') { $openParen++ }
        if ($ch -eq ')') { $closeParen++ }
    }
}
if ($openParen -ne $closeParen) {
    $errors += "Parenthesis mismatch: $openParen opening, $closeParen closing"
}

# 5. Check common AHK v2 issues
$linenum = 0
foreach ($line in $lines) {
    $linenum++
    $trimmed = $line.Trim()
    if ($trimmed -eq '' -or $trimmed.StartsWith(';') -or $trimmed.StartsWith('#')) { continue }

    # Check for AHK v1 := vs = confusion
    # In v2, assignment is always :=, and = is only for legacy compatibility
    if ($trimmed -match '^[a-zA-Z_]+\s*=[^=]' -and $trimmed -notmatch '^(if|else if)\s') {
        $errors += "Line ${linenum}: Use := for assignment in AHK v2: '${trimmed}'"
    }
}

# 6. Validate hotkey definitions
$hasHotkey = $false
foreach ($line in $lines) {
    if ($line -match '^[!^+#<>\w]+\s*::') {
        $hasHotkey = $true
    }
    # Check hotkey definition with opening brace
    if ($line -match '::\s*\{' -or $line -match '::\{') {
        # Valid v2 hotkey syntax
    }
}

# 7. Check for MsgBox without comma (v2 style)
foreach ($line in $lines) {
    if ($line -match 'MsgBox\s*,' -and $line -notmatch 'MsgBox\s*\(.*\)') {
        $errors += "Line ${linenum}: MsgBox in AHK v2 uses function syntax MsgBox() not MsgBox,"
    }
}

# Results
if ($errors.Count -eq 0) {
    Write-Host "[PASS] Syntax check OK ($ScriptPath)" -ForegroundColor Green
    Write-Host "  $($lines.Count) lines, $openBraces code blocks" -ForegroundColor Gray
    exit 0
} else {
    Write-Host ("[WARN] Found " + $errors.Count + " issue(s):") -ForegroundColor Yellow
    foreach ($err in $errors) {
        Write-Host ("  * " + $err) -ForegroundColor Yellow
    }
    exit 1
}
