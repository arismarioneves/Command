#!/usr/bin/env bash
# Command - Instalador para macOS e Linux
# Uso: curl -fsSL https://aiu4.com/command/install.sh | bash

set -euo pipefail

# Locale — ignora erro em ambientes sem en_US.UTF-8 (ex: WSL básico)
export LANG=en_US.UTF-8 2>/dev/null || true
export LC_ALL=en_US.UTF-8 2>/dev/null || true

REPO="https://raw.githubusercontent.com/arismarioneves/Command/main"
INSTALL_DIR="$HOME/.command"
OS="$(uname -s)"

# ── Cores ──────────────────────────────────────────────────────────────────────
CYAN='\033[0;36m'
DCYAN='\033[1;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;90m'
WHITE='\033[1;37m'
NC='\033[0m'

# ── Banner ─────────────────────────────────────────────────────────────────────
echo ""
printf "${DCYAN} ██████╗ ██████╗ ███╗   ███╗███╗   ███╗ █████╗ ███╗   ██╗██████╗ ${NC}\n"
printf "${DCYAN}██╔════╝██╔═══██╗████╗ ████║████╗ ████║██╔══██╗████╗  ██║██╔══██╗${NC}\n"
printf "${DCYAN}██║     ██║   ██║██╔████╔██║██╔████╔██║███████║██╔██╗ ██║██║  ██║${NC}\n"
printf "${CYAN}╚██████╗╚██████╔╝██║ ╚═╝ ██║██║ ╚═╝ ██║██║  ██║██║ ╚████║██████╔╝${NC}\n"
printf "${CYAN} ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ ${NC}\n"
echo ""
printf "${GRAY}  Super Terminal com IA  —  Instalador v6.0${NC}\n"
printf "${GRAY}  ──────────────────────────────────────────────────────────────${NC}\n"
echo ""

# ── Escolha do modo ────────────────────────────────────────────────────────────
printf "${WHITE}  Escolha o modo de funcionamento:${NC}\n"
echo ""
printf "${CYAN}    [1] Local   — Ollama + qwen2.5:3b  (gratuito, roda na sua maquina)${NC}\n"
printf "${CYAN}    [2] Online  — OpenAI API            (requer chave, sem download de LLM)${NC}\n"
echo ""

while true; do
    printf "  Opcao [1/2]: "
    read -r modo </dev/tty
    [[ "$modo" == "1" || "$modo" == "2" ]] && break
    printf "${RED}  Opcao invalida.${NC}\n"
done

MODO_ONLINE=false
API_KEY=""
if [[ "$modo" == "2" ]]; then
    MODO_ONLINE=true
    echo ""
    while true; do
        printf "  Cole sua OpenAI API key (sk-...): "
        read -r API_KEY </dev/tty
        [[ "$API_KEY" == sk-* ]] && break
        printf "${RED}  Chave invalida. Deve comecar com 'sk-'.${NC}\n"
    done
fi

echo ""
printf "${GRAY}  ──────────────────────────────────────────────────────────────${NC}\n"
echo ""

TOTAL_STEPS=4
$MODO_ONLINE || TOTAL_STEPS=5

# ── [1/N] Python ───────────────────────────────────────────────────────────────
if command -v python3 &>/dev/null; then
    printf "${GREEN}  [1/$TOTAL_STEPS] Python OK  $(python3 --version)${NC}\n"
else
    printf "${YELLOW}  [1/$TOTAL_STEPS] Instalando Python...${NC}\n"
    if [[ "$OS" == "Darwin" ]]; then
        if command -v brew &>/dev/null; then
            brew install python3
        else
            printf "${RED}  Python nao encontrado. Instale via: https://python.org${NC}\n"
            exit 1
        fi
    elif command -v apt-get &>/dev/null; then
        sudo apt-get install -y python3 python3-pip
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y python3 python3-pip
    elif command -v pacman &>/dev/null; then
        sudo pacman -S --noconfirm python python-pip
    else
        printf "${RED}  Python nao encontrado. Instale via: https://python.org${NC}\n"
        exit 1
    fi
    printf "${GREEN}  [1/$TOTAL_STEPS] Python OK  $(python3 --version)${NC}\n"
fi

# ── [2/N] Ollama (somente modo local) ─────────────────────────────────────────
if ! $MODO_ONLINE; then
    if command -v ollama &>/dev/null; then
        printf "${GREEN}  [2/$TOTAL_STEPS] Ollama OK  $(ollama --version)${NC}\n"
    else
        printf "${YELLOW}  [2/$TOTAL_STEPS] Instalando Ollama...${NC}\n"
        curl -fsSL https://ollama.com/install.sh | sh
        printf "${GREEN}  [2/$TOTAL_STEPS] Ollama instalado${NC}\n"
    fi
    printf "${GRAY}        Baixando qwen2.5:3b...${NC}\n"
    ollama pull qwen2.5:3b
fi

# ── [2 ou 3] Dependencias Python (virtualenv isolado) ─────────────────────────
STEP=2; $MODO_ONLINE || STEP=3
printf "${YELLOW}  [$STEP/$TOTAL_STEPS] Criando ambiente virtual...${NC}\n"
mkdir -p "$INSTALL_DIR"

# Garante que python3-venv está disponível (Debian/Ubuntu)
if ! python3 -m venv --help &>/dev/null; then
    if command -v apt-get &>/dev/null; then
        sudo apt-get install -y python3-venv python3-full
    fi
fi

python3 -m venv "$INSTALL_DIR/venv"
VENV_PIP="$INSTALL_DIR/venv/bin/pip"
VENV_PY="$INSTALL_DIR/venv/bin/python3"

"$VENV_PIP" install -q --upgrade pip
"$VENV_PIP" install -q requests openai "rich>=13.0.0"
printf "${GREEN}  [$STEP/$TOTAL_STEPS] Dependencias OK${NC}\n"

# ── [3 ou 4] Download command.py ──────────────────────────────────────────────
STEP=3; $MODO_ONLINE || STEP=4
printf "${YELLOW}  [$STEP/$TOTAL_STEPS] Baixando Command...${NC}\n"
curl -fsSL "$REPO/command.py"       -o "$INSTALL_DIR/command.py"
curl -fsSL "$REPO/requirements.txt" -o "$INSTALL_DIR/requirements.txt"
printf "${GREEN}  [$STEP/$TOTAL_STEPS] command.py salvo em $INSTALL_DIR${NC}\n"

# ── [4 ou 5] Launcher + .env + PATH ───────────────────────────────────────────
STEP=4; $MODO_ONLINE || STEP=5
printf "${YELLOW}  [$STEP/$TOTAL_STEPS] Criando launcher...${NC}\n"

# Launcher usa o Python do venv
cat > "$INSTALL_DIR/command" <<EOF
#!/usr/bin/env bash
exec "$INSTALL_DIR/venv/bin/python3" "$INSTALL_DIR/command.py" "\$@"
EOF
chmod +x "$INSTALL_DIR/command"

# .env
if $MODO_ONLINE; then
    cat > "$INSTALL_DIR/.env" <<EOF
PROVIDER=openai
MODELO_ATUAL=gpt-5-nano
OPENAI_API_KEY=$API_KEY
EOF
else
    cat > "$INSTALL_DIR/.env" <<EOF
PROVIDER=ollama
MODELO_ATUAL=qwen2.5:3b
EOF
fi
printf "${GRAY}        Configuracoes salvas em $INSTALL_DIR/.env${NC}\n"

# Adiciona ao PATH
SHELL_RC=""
if [[ -f "$HOME/.zshrc" ]]; then
    SHELL_RC="$HOME/.zshrc"
elif [[ -f "$HOME/.bashrc" ]]; then
    SHELL_RC="$HOME/.bashrc"
elif [[ -f "$HOME/.bash_profile" ]]; then
    SHELL_RC="$HOME/.bash_profile"
fi

if [[ -n "$SHELL_RC" ]]; then
    if ! grep -q '\.command' "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo "export PATH=\"\$HOME/.command:\$PATH\"" >> "$SHELL_RC"
        printf "${GRAY}        Adicionado ao PATH em $SHELL_RC${NC}\n"
    fi
fi

export PATH="$INSTALL_DIR:$PATH"
printf "${GREEN}  [$STEP/$TOTAL_STEPS] Launcher criado${NC}\n"

# ── Conclusao ──────────────────────────────────────────────────────────────────
echo ""
printf "${GRAY}  ──────────────────────────────────────────────────────────────${NC}\n"
printf "${GREEN}  ✓ Instalacao concluida!${NC}\n"
echo ""
if $MODO_ONLINE; then
    printf "${GRAY}  Modo: Online (OpenAI)  —  modelo: gpt-5-nano${NC}\n"
else
    printf "${GRAY}  Modo: Local (Ollama)   —  modelo: qwen2.5:3b${NC}\n"
fi
printf "${GRAY}  Para trocar de modelo:  :${NC}\n"
printf "${GRAY}  Para trocar de provider: reinstale com a outra opcao${NC}\n"
echo ""
printf "${WHITE}  Para iniciar (abra um novo terminal ou execute):${NC}\n"
printf "${CYAN}    source $SHELL_RC && command${NC}\n"
echo ""
