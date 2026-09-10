param([ValidateSet('en','de')][string]$Language = 'en')
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
py -3 -m venv .venv
if ($LASTEXITCODE -ne 0) {
    if ($Language -eq 'de') { throw 'Das Erstellen der Python-Umgebung ist fehlgeschlagen' }
    throw 'Python environment creation failed'
}
& .\.venv\Scripts\python.exe -m pip install .
if ($LASTEXITCODE -ne 0) {
    if ($Language -eq 'de') { throw 'Die Installation von PersonaLife ist fehlgeschlagen' }
    throw 'PersonaLife installation failed'
}
& .\.venv\Scripts\python.exe -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) {
    if ($Language -eq 'de') { throw 'Die PersonaLife-Tests sind fehlgeschlagen' }
    throw 'PersonaLife tests failed'
}
if ($Language -eq 'de') {
    Write-Host 'PersonaLife ist bereit. Starte .\.venv\Scripts\personalife.exe --language de persona create'
} else {
    Write-Host 'PersonaLife ready. Run .\.venv\Scripts\personalife.exe --language en persona create'
}
