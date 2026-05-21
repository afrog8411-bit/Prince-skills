# AutoHotkey v2 安装检测脚本
# 用法: 右键 → 使用 PowerShell 运行
# 检测 AHK v2 是否已安装，未安装时自动下载安装

$ahkPaths = @(
    "$env:ProgramFiles\AutoHotkey\v2\AutoHotkey64.exe",
    "$env:ProgramFiles\AutoHotkey\v2\AutoHotkey32.exe",
    "$env:LOCALAPPDATA\Programs\AutoHotkey\v2\AutoHotkey64.exe",
    "$env:LOCALAPPDATA\Programs\AutoHotkey\v2\AutoHotkey32.exe"
)

foreach ($path in $ahkPaths) {
    if (Test-Path $path) {
        Write-Host "[OK] AutoHotkey v2 already installed ($path)" -ForegroundColor Green
        exit 0
    }
}

Write-Host "[WARN] AutoHotkey v2 not found, preparing download..." -ForegroundColor Yellow
Write-Host "Continue with installation? (Y/n) " -ForegroundColor Cyan -NoNewline
$confirm = Read-Host
if ($confirm -eq "n" -or $confirm -eq "N") {
    Write-Host "Installation cancelled." -ForegroundColor Gray
    exit 0
}

$url = "https://www.autohotkey.com/download/ahk-v2.exe"
$installer = "$env:TEMP\ahk-v2-install.exe"

try {
    # Try multiple download methods
    try {
        Write-Host "Downloading..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $url -OutFile $installer -UseBasicParsing -ErrorAction Stop
    } catch {
        Write-Host "Invoke-WebRequest failed, trying BITS transfer..." -ForegroundColor Yellow
        Start-BitsTransfer -Source $url -Destination $installer -ErrorAction Stop
    }

    if (-not (Test-Path $installer)) {
        throw "File not found after download"
    }

    $fileSizeBytes = (Get-Item $installer).Length
    $sizeMB = [math]::Round($fileSizeBytes / (1024 * 1024), 1)
    Write-Host "Downloaded ($sizeMB MB)" -ForegroundColor Green
    Write-Host "Installing (silent mode)..." -ForegroundColor Yellow
    Write-Host "If UAC prompts, click Yes" -ForegroundColor Cyan

    Start-Process -Wait -FilePath $installer -ArgumentList "/S"
    Remove-Item $installer -Force -ErrorAction SilentlyContinue

    # Verify installation
    $installed = $false
    foreach ($path in $ahkPaths) {
        if (Test-Path $path) { $installed = $true; break }
    }

    if ($installed) {
        Write-Host "[OK] AutoHotkey v2 installed!" -ForegroundColor Green
        Write-Host "Double-click .ahk files to run shortcuts." -ForegroundColor Cyan
    } else {
        Write-Host "[WARN] Installation may not have succeeded." -ForegroundColor Yellow
        Write-Host "Manual download: https://www.autohotkey.com/download/" -ForegroundColor Cyan
    }
} catch {
    Write-Host "[ERROR] Installation failed: $_" -ForegroundColor Red
    Write-Host "Manual download: https://www.autohotkey.com/download/" -ForegroundColor Cyan
    exit 1
}
