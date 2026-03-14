# Command - Script de instalacao para Windows
# Uso: powershell -ExecutionPolicy Bypass -c "irm https://raw.githubusercontent.com/arismarioneves/Command/main/install.ps1 | iex"

$ErrorActionPreference = "Stop"

# Força UTF-8 para renderizar corretamente os caracteres do banner
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

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

# ── Utilitario: recarrega PATH da sessao atual a partir do registro ────────────
function Refresh-EnvPath {
    $machine = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $user    = [Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = ($machine, $user | Where-Object { $_ }) -join ";"
}

# ── Escolha do modo ───────────────────────────────────────────────────────────
Write-Host "  Escolha o modo de funcionamento:" -ForegroundColor White
Write-Host ""
Write-Host "    [1] Local   — Ollama + qwen2.5:3b  (gratuito, roda na sua maquina)" -ForegroundColor Cyan
Write-Host "    [2] Online  — OpenAI API            (requer chave, sem download de LLM)" -ForegroundColor Cyan
Write-Host ""

do {
    $modo = (Read-Host "  Opcao [1/2]").Trim()
} while ($modo -notin @("1", "2"))

$modoOnline = ($modo -eq "2")

if ($modoOnline) {
    Write-Host ""
    $apiKey = (Read-Host "  Cole sua OpenAI API key (sk-...)").Trim()
    if (-not $apiKey.StartsWith("sk-")) {
        Write-Host "  Chave invalida. Deve comecar com 'sk-'." -ForegroundColor Red
        exit 1
    }
    Write-Host ""
}

Write-Host ("  " + ("─" * 62)) -ForegroundColor DarkGray
Write-Host ""

# ── [1/4 ou 1/5] Python ───────────────────────────────────────────────────────
$totalSteps = if ($modoOnline) { 4 } else { 5 }

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "  [1/$totalSteps] Instalando Python..." -ForegroundColor Yellow
    winget install --id Python.Python.3.12 -e --silent
    Refresh-EnvPath
} else {
    Write-Host "  [1/$totalSteps] Python OK  $(python --version)" -ForegroundColor Green
}

# ── [2/N] Ollama (somente modo local) ────────────────────────────────────────
if (-not $modoOnline) {
    if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
        Write-Host "  [2/$totalSteps] Instalando Ollama..." -ForegroundColor Yellow
        winget install --id Ollama.Ollama -e --silent
        Start-Sleep -Seconds 3
        Refresh-EnvPath
    } else {
        Write-Host "  [2/$totalSteps] Ollama OK  $(ollama --version)" -ForegroundColor Green
    }

    Write-Host "        Baixando qwen2.5:3b..." -ForegroundColor DarkGray
    ollama pull qwen2.5:3b
}

# ── [2 ou 3] Dependencias Python ──────────────────────────────────────────────
$step = if ($modoOnline) { 2 } else { 3 }
Write-Host "  [$step/$totalSteps] Instalando dependencias Python..." -ForegroundColor Yellow
python -m pip install -q requests openai "rich>=13.0.0"
Write-Host "  [$step/$totalSteps] Dependencias OK" -ForegroundColor Green

# ── [3 ou 4] Download command.py ──────────────────────────────────────────────
$step = if ($modoOnline) { 3 } else { 4 }
Write-Host "  [$step/$totalSteps] Baixando Command..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri "$REPO/command.py"      -OutFile "$INSTALL_DIR\command.py"      -UseBasicParsing
    Invoke-WebRequest -Uri "$REPO/requirements.txt" -OutFile "$INSTALL_DIR\requirements.txt" -UseBasicParsing
    Write-Host "  [$step/$totalSteps] command.py salvo em $INSTALL_DIR" -ForegroundColor Green
} catch {
    Write-Host "  [$step/$totalSteps] Erro ao baixar: $_" -ForegroundColor Red
    exit 1
}

# ── [4 ou 5] Launcher + .env + PATH ───────────────────────────────────────────
$step = if ($modoOnline) { 4 } else { 5 }
Write-Host "  [$step/$totalSteps] Criando launcher..." -ForegroundColor Yellow

# Launcher simples — as configuracoes ficam no .env
$launcher = "$INSTALL_DIR\command.bat"
"@python `"$INSTALL_DIR\command.py`" %*" | Out-File -FilePath $launcher -Encoding ascii

# Salva configuracoes no .env
if ($modoOnline) {
    @"
PROVIDER=openai
MODELO_ATUAL=gpt-5-nano
OPENAI_API_KEY=$apiKey
"@ | Out-File -FilePath "$INSTALL_DIR\.env" -Encoding utf8
    Write-Host "        Configuracoes salvas em $INSTALL_DIR\.env" -ForegroundColor DarkGray
} else {
    @"
PROVIDER=ollama
MODELO_ATUAL=qwen2.5:3b
"@ | Out-File -FilePath "$INSTALL_DIR\.env" -Encoding utf8
    Write-Host "        Configuracoes salvas em $INSTALL_DIR\.env" -ForegroundColor DarkGray
}

# Adiciona ao PATH do usuario (sem sobrescrever)
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*\.command*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$INSTALL_DIR", "User")
    Write-Host "        Adicionado ao PATH do usuario" -ForegroundColor DarkGray
}

# Recarrega PATH na sessao atual para que 'command' funcione imediatamente
Refresh-EnvPath

Write-Host "  [$step/$totalSteps] Launcher criado" -ForegroundColor Green

# ── Conclusao ─────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host ("  " + ("─" * 62)) -ForegroundColor DarkGray
Write-Host "  ✓ Instalacao concluida!" -ForegroundColor Green
Write-Host ""
if ($modoOnline) {
    Write-Host "  Modo: Online (OpenAI)  —  modelo: gpt-5-nano" -ForegroundColor DarkGray
} else {
    Write-Host "  Modo: Local (Ollama)   —  modelo: qwen2.5:3b" -ForegroundColor DarkGray
}
Write-Host "  Para trocar de modelo:  :" -ForegroundColor DarkGray
Write-Host "  Para trocar de provider: reinstale com a outra opcao" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Para iniciar:" -ForegroundColor White
Write-Host "    command" -ForegroundColor Cyan
Write-Host ""
