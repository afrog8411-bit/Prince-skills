# save-clipimg.ps1
# Save clipboard image to file, output file path
# Usage: powershell -NoProfile -File save-clipimg.ps1 [output-dir]

param(
    [string]$OutputDir = "C:\free\screenshots"
)

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$ts = Get-Date -Format "yyyy-MM-dd_HHmmss"
$path = Join-Path $OutputDir "$ts.png"

Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
$img = [System.Windows.Forms.Clipboard]::GetImage()
if ($img) {
    $img.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $img.Dispose()
    Write-Host $path
}
