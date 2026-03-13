# Command - Script de instalacao para Windows
# Uso: powershell -ExecutionPolicy Bypass -c "irm https://aiu4.com/install.ps1 | iex"

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "  Command v6.0 - Instalador" -ForegroundColor Cyan
Write-Host "  Super Terminal com IA" -ForegroundColor Cyan
Write-Host ""

# ── Python ────────────────────────────────────────────────────────────────────
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[1/4] Instalando Python..." -ForegroundColor Yellow
    winget install --id Python.Python.3.12 -e --silent
} else {
    Write-Host "[1/4] Python OK  $(python --version)" -ForegroundColor Green
}

# ── Ollama ────────────────────────────────────────────────────────────────────
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "[2/4] Instalando Ollama..." -ForegroundColor Yellow
    winget install --id Ollama.Ollama -e --silent
    Start-Sleep -Seconds 3
} else {
    Write-Host "[2/4] Ollama OK  $(ollama --version)" -ForegroundColor Green
}

Write-Host "      Baixando llama3.2..." -ForegroundColor DarkGray
ollama pull llama3.2

# ── Dependencias Python ───────────────────────────────────────────────────────
Write-Host "[3/4] Instalando dependencias Python..." -ForegroundColor Yellow
python -m pip install -q requests openai
Write-Host "[3/4] Dependencias OK" -ForegroundColor Green

# ── Open WebUI (opcional) ─────────────────────────────────────────────────────
Write-Host "[4/4] Instalacao concluida" -ForegroundColor Green

Write-Host ""
Write-Host "  Instalacao concluida!" -ForegroundColor Green
Write-Host "  Para iniciar: python command.py" -ForegroundColor Cyan
Write-Host ""
