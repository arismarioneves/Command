# Command - Super Terminal com IA
# Autor: Mari05liM
# Versão: 6.0
#
# Instalacao:
#   1. Ollama: https://ollama.com/download  →  ollama pull llama3.2
#   2. pip install -r requirements.txt
#   3. python command.py

import os
import re
import subprocess
import requests
from typing import List, Dict

# Configuracoes
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
USUARIO = os.getenv("USUARIO", "root")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODELOS_OPENAI = ["gpt-4o-mini", "gpt-4.1-mini", "gpt-5-nano"]
MODELOS_PREFERIDOS = [
    "llama3.2", "llama3.2:3b",
    "qwen2.5:3b", "qwen2.5",
    "gemma3:4b", "gemma3:1b",
    "mistral", "llama3.1",
]

# Comandos que destroem dados sem volta
BLOQUEADOS = [
    "format c:", "format d:", "format e:",
    "del /f /s /q c:\\", "rd /s /q c:\\",
    "rmdir /s /q c:\\",
]

SYSTEM_PROMPT = """You are Command, an AI-powered terminal for Windows CMD.
Execute actions by wrapping commands in curly braces: {command}
Use multiple {command} blocks for multi-step tasks. Keep responses short.

Windows CMD syntax reference (always use these — never use Linux/bash syntax):
  List files          → {dir}
  Change directory    → {cd foldername}
  Create folder       → {mkdir foldername}
  Delete folder       → {rmdir /s /q foldername}
  Create empty file   → {copy nul filename.txt}
  Write to file       → {echo content > filename.txt}
  Read file           → {type filename.txt}
  Delete file         → {del filename.txt}
  Copy file           → {copy source.txt dest.txt}
  Move file           → {move source.txt dest\}
  Rename              → {ren oldname.txt newname.txt}
  Open app            → {start appname}  or  {appname}
  Open Notepad        → {notepad}
  Open Paint          → {start mspaint}
  Open VS Code        → {code .}
  Run Python          → {python script.py}
  Install package     → {pip install package}
  Git status          → {git status}
  For paths with spaces use quotes: {cd "C:\\My Folder"}

Multi-step example — "create folder dog with empty file boing.txt inside":
  {mkdir dog}
  {copy nul dog\\boing.txt}
"""


def limpar_tela():
    os.system("cls")


def prompt_dir(cwd: str) -> str:
    """Exibe o diretorio atual de forma curta no prompt."""
    try:
        home = os.path.expanduser("~")
        if cwd.startswith(home):
            cwd = "~" + cwd[len(home):]
    except Exception:
        pass
    return f"{USUARIO}@{cwd}> "


def executar(cmd: str, cwd: str) -> tuple[str, int, str]:
    """Executa um comando e retorna (output, returncode, novo_cwd)."""
    cmd = cmd.strip()

    # cd precisa alterar o cwd do processo pai
    if re.match(r"^cd\b", cmd, re.IGNORECASE):
        path = cmd[2:].strip().strip('"').strip("'")
        if not path or path == ".":
            return "", 0, cwd
        novo = path if os.path.isabs(path) else os.path.normpath(os.path.join(cwd, path))
        if os.path.isdir(novo):
            return "", 0, novo
        return f"Diretorio nao encontrado: {path}", 1, cwd

    # Bloqueia comandos destrutivos
    if any(b in cmd.lower() for b in BLOQUEADOS):
        return "Comando bloqueado por seguranca.", 1, cwd

    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            timeout=30, encoding="utf-8", errors="replace",
        )
        return result.stdout.strip(), result.returncode, cwd
    except subprocess.TimeoutExpired:
        return "Timeout (30s)", 1, cwd
    except Exception as e:
        return str(e), 1, cwd


def extrair_comandos(texto: str) -> tuple[str, List[str]]:
    """Separa o texto limpo dos {comandos} contidos na resposta."""
    cmds = re.findall(r"\{([^}]+)\}", texto)
    limpo = re.sub(r"\{[^}]+\}", "", texto).strip()
    return limpo, cmds


def detectar_melhor_modelo_ollama() -> str | None:
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        if resp.status_code != 200:
            return None
        modelos = [m["name"] for m in resp.json().get("models", [])]
        for preferido in MODELOS_PREFERIDOS:
            for m in modelos:
                if preferido in m:
                    return m
        return modelos[0] if modelos else None
    except requests.RequestException:
        return None


def listar_modelos_ollama() -> List[str]:
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        return [m["name"] for m in resp.json().get("models", [])]
    except Exception:
        return []


def gerar_resposta_ollama(historico: List[Dict], modelo: str, cwd: str) -> str:
    mensagens = [
        {"role": "system", "content": SYSTEM_PROMPT + f"\n\nCurrent directory: {cwd}"}
    ] + historico
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={"model": modelo, "messages": mensagens, "stream": False},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"].strip()
    except Exception as e:
        return f"Erro Ollama: {e}"


def gerar_resposta_openai(historico: List[Dict], modelo: str, cwd: str) -> str:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        mensagens = [
            {"role": "system", "content": SYSTEM_PROMPT + f"\n\nCurrent directory: {cwd}"}
        ] + historico
        resp = client.chat.completions.create(
            model=modelo, messages=mensagens, temperature=0, max_tokens=500,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Erro OpenAI: {e}"


def main():
    limpar_tela()
    os.environ["PYTHONIOENCODING"] = "utf-8"
    cwd = os.getcwd()

    # Detecta provider
    modelo_ollama = detectar_melhor_modelo_ollama()
    if modelo_ollama:
        modelo_atual, provider = modelo_ollama, "ollama"
        print(f"Command v6.0  [{modelo_atual}]")
    elif OPENAI_API_KEY:
        modelo_atual, provider = "gpt-4o-mini", "openai"
        print(f"Command v6.0  [{modelo_atual}]")
    else:
        print("Command v6.0  — nenhum provider encontrado.")
        print("Instale o Ollama: https://ollama.com/download")
        print("Depois: ollama pull llama3.2")
        return

    print("Dica: use ! para rodar comandos diretos  ex: !dir  |  :modelo para trocar\n")

    historico: List[Dict] = []

    while True:
        try:
            entrada = input(prompt_dir(cwd)).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAte logo!")
            break

        if not entrada:
            continue

        # Sair
        if entrada.lower() in ("sair", "exit", "quit"):
            print("Ate logo!")
            break

        # Trocar modelo  →  :llama3.2  ou  :gpt-4o-mini
        if entrada.startswith(":"):
            novo = entrada[1:].strip()
            if not novo:
                continue
            provider = "openai" if novo in MODELOS_OPENAI else "ollama"
            modelo_atual = novo
            print(f"  modelo → {modelo_atual} ({provider})")
            continue

        # Listar modelos
        if entrada.lower() in (":modelos", ":models"):
            disp = listar_modelos_ollama()
            if disp:
                print(f"  Ollama: {', '.join(disp)}")
            if OPENAI_API_KEY:
                print(f"  OpenAI: {', '.join(MODELOS_OPENAI)}")
            continue

        # Modo direto  →  !dir  !git status  !python script.py
        if entrada.startswith("!"):
            cmd = entrada[1:].strip()
            output, code, cwd = executar(cmd, cwd)
            if output:
                print(output)
            continue

        # IA processa a entrada
        historico.append({"role": "user", "content": entrada})

        resposta = (
            gerar_resposta_ollama(historico, modelo_atual, cwd)
            if provider == "ollama"
            else gerar_resposta_openai(historico, modelo_atual, cwd)
        )

        historico.append({"role": "assistant", "content": resposta})
        if len(historico) > 30:
            historico = historico[-30:]

        texto, cmds = extrair_comandos(resposta)

        if texto:
            print(f"\n  {texto}\n")

        for cmd in cmds:
            print(f"  $ {cmd}")
            output, code, cwd = executar(cmd, cwd)
            if output:
                print(output)


if __name__ == "__main__":
    main()
