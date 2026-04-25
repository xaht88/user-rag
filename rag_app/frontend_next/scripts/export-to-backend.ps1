$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path "$PSScriptRoot\..\.."
$frontendRoot = Resolve-Path "$PSScriptRoot\.."
$outDir = Join-Path $frontendRoot "out"
$backendStatic = Join-Path $projectRoot "backend\static\next"
$backendTemplate = Join-Path $projectRoot "backend\templates\next_index.html"

if (-not (Test-Path $outDir)) {
    throw "Каталог out не найден. Сначала выполните next export."
}

if (-not (Test-Path $backendStatic)) {
    New-Item -ItemType Directory -Path $backendStatic -Force | Out-Null
}

Copy-Item -Path (Join-Path $outDir "*") -Destination $backendStatic -Recurse -Force

$entryFile = Join-Path $outDir "index.html"
if (Test-Path $entryFile) {
    Copy-Item -Path $entryFile -Destination $backendTemplate -Force
}

Write-Output "Frontend экспортирован в backend static/template."
