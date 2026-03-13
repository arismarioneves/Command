# Command - Script de instalacao para Windows
# Uso: powershell -ExecutionPolicy Bypass -c "irm https://raw.githubusercontent.com/arismarioneves/Command/main/install.ps1 | iex"

$ErrorActionPreference = "Stop"

$REPO        = "https://raw.githubusercontent.com/arismarioneves/Command/main"
$INSTALL_DIR = "$env:USERPROFILE\.command"

# ── Banner ────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host " ██████╗ ██████╗ ███╗   ███╗███╗   ███╗ █████╗ ███╗   ██╗██████╗ " -ForegroundColor Cyan
Write-Host "██╔════╝██╔═══██╗████╗ ████║████╗ ████║██╔══██╗████╗  ██║██╔══██╗" -ForegroundColor Cyan
Write-Host "██║     ██║   ██║██╔████╔██║██╔████╔██║███████║██╔██╗ ██║██║  ██║" -ForegroundColor Cyan
Write-Host "╚██████╗╚██████╔╝██║ ╚═╝ ██║██║ ╚═╝ ██║██║  ██║██║ ╚████║██████╔╝" -ForegroundColor DarkCyan
Write-Host " ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ " -ForegroundColor DarkCyan
Write-Host ""
Write-Host "  Super Terminal com IA  —  Instalador v6.0" -ForegroundColor DarkGray
Write-Host ("  " + ("─" * 62)) -ForegroundColor DarkGray
Write-Host ""

# Cria diretorio de instalacao
New-Item -ItemType Directory -Force -Path $INSTALL_DIR | Out-Null

# ── [1/5] Python ──────────────────────────────────────────────────────────────
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "  [1/5] Instalando Python..." -ForegroundColor Yellow
    winget install --id Python.Python.3.12 -e --silent
} else {
    Write-Host "  [1/5] Python OK  $(python --version)" -ForegroundColor Green
}

# ── [2/5] Ollama ──────────────────────────────────────────────────────────────
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "  [2/5] Instalando Ollama..." -ForegroundColor Yellow
    winget install --id Ollama.Ollama -e --silent
    Start-Sleep -Seconds 3
} else {
    Write-Host "  [2/5] Ollama OK  $(ollama --version)" -ForegroundColor Green
}

Write-Host "        Baixando llama3.2..." -ForegroundColor DarkGray
ollama pull llama3.2

# ── [3/5] Dependencias Python ─────────────────────────────────────────────────
Write-Host "  [3/5] Instalando dependencias Python..." -ForegroundColor Yellow
python -m pip install -q requests openai "rich>=13.0.0"
Write-Host "  [3/5] Dependencias OK" -ForegroundColor Green

# ── [4/5] Download command.py ─────────────────────────────────────────────────
Write-Host "  [4/5] Baixando Command..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri "$REPO/command.py"      -OutFile "$INSTALL_DIR\command.py"      -UseBasicParsing
    Invoke-WebRequest -Uri "$REPO/requirements.txt" -OutFile "$INSTALL_DIR\requirements.txt" -UseBasicParsing
    Write-Host "  [4/5] command.py salvo em $INSTALL_DIR" -ForegroundColor Green
} catch {
    Write-Host "  [4/5] Erro ao baixar: $_" -ForegroundColor Red
    exit 1
}

# ── [5/5] Launcher + PATH ─────────────────────────────────────────────────────
Write-Host "  [5/5] Criando launcher..." -ForegroundColor Yellow

$launcher = "$INSTALL_DIR\command.bat"
"@python `"$INSTALL_DIR\command.py`" %*" | Out-File -FilePath $launcher -Encoding ascii

# Adiciona ao PATH do usuario (sem sobrescrever)
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*\.command*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$INSTALL_DIR", "User")
    Write-Host "        Adicionado ao PATH do usuario" -ForegroundColor DarkGray
}

Write-Host "  [5/5] Launcher criado" -ForegroundColor Green

# ── Conclusao ─────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host ("  " + ("─" * 62)) -ForegroundColor DarkGray
Write-Host "  ✓ Instalacao concluida!" -ForegroundColor Green
Write-Host ""
Write-Host "  Para iniciar agora:" -ForegroundColor White
Write-Host "    python $INSTALL_DIR\command.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Apos reiniciar o terminal, use apenas:" -ForegroundColor White
Write-Host "    command" -ForegroundColor Cyan
Write-Host ""
