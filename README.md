# Command

Super terminal com IA para Windows — powered by **Ollama** (local) ou **OpenAI** (online).

## Instalação rápida

```powershell
powershell -ExecutionPolicy Bypass -c "irm https://aiu4.com/install.ps1 | iex"
```

ou

```powershell
powershell -ExecutionPolicy Bypass -c "irm https://raw.githubusercontent.com/arismarioneves/Command/main/install.ps1 | iex"
```

## Instalação manual

```powershell
# 1. Instale o Ollama: https://ollama.com/download
ollama pull qwen2.5:3b

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute
python command.py
```

---

## Uso

O prompt mostra o diretório atual como um terminal real:

```
Command v6.0  [qwen2.5:3b]

root@C:\DEV\Command> abra o vscode aqui
  $ code .

root@C:\DEV\Command> crie uma pasta dog com um arquivo boing.txt dentro
  $ mkdir dog
  $ copy nul dog\boing.txt

root@C:\DEV\Command> !git status
On branch main
nothing to commit, working tree clean

root@C:\DEV\Command> :qwen2.5:3b
  modelo → qwen2.5:3b (ollama)
```

## Comandos especiais

| Entrada | Ação |
|---|---|
| `!<cmd>` | Executa diretamente sem passar pela IA |
| `:<modelo>` | Troca o modelo de IA |
| `:modelos` | Lista os modelos disponíveis |
| `sair` / `exit` | Encerra o terminal |

## Modo direto (`!`)

Use `!` para rodar qualquer comando sem IA:

```
!dir
!git log --oneline -5
!python app.py
!npm install
```

## Modelos suportados

**Ollama (local, gratuito)** — detectado automaticamente:

| Modelo | Tamanho | Indicado para |
|---|---|---|
| `qwen2.5:3b` | 2 GB | código e comandos (padrão) |
| `gemma3:1b` | 800 MB | máquinas com pouca RAM |
| `gemma3:4b` | 3 GB | raciocínio |
| `llama3.2` | 2 GB | uso geral |
| `mistral` | 4 GB | uso geral avançado |

**OpenAI (online)** — requer `OPENAI_API_KEY`:
- `gpt-4o-mini`, `gpt-4.1-mini`, `gpt-5-nano`

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `OPENAI_API_KEY` | — | Chave OpenAI (opcional) |
| `USUARIO` | `root` | Nome no prompt |
| `OLLAMA_URL` | `http://localhost:11434` | Endereço do Ollama |

## Segurança

Comandos destrutivos (`format c:`, `del /f /s /q c:\`, etc.) são bloqueados automaticamente.
