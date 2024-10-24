# Command - Assistente de comandos para o Windows
# Autor: Mari05liM
# Versão: 3.0

import os
import openai
import webbrowser
import requests
import json
from typing import List, Dict

# Configurações
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "chave_api")
USUARIO = os.getenv("USUARIO", "root")
MODELO_PADRAO = "llama3.2"
TEMPERATURA = 0
MAX_TOKENS = 300

# Configuração do OpenAI
openai.api_key = OPENAI_API_KEY

# Comandos perigosos que não devem ser executados
COMANDOS_PERIGOSOS = ["format", "del", "erase", "rd", "rmdir", "attrib", "reg"]

# Função para limpar a tela
def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")

# Função para criar imagem (apenas para OpenAI)
def criar_imagem(prompt: str) -> None:
    if not OPENAI_API_KEY or OPENAI_API_KEY == "chave_api":
        print("Criação de imagem não disponível. Chave API do OpenAI não configurada.")
        return
    try:
        resposta = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
        url_imagem = resposta["data"][0]["url"]
        webbrowser.open(url_imagem)
        print("Command: Imagem criada e aberta no navegador.")
    except Exception as e:
        print(f"Erro ao criar imagem: {e}")

def verificar_ollama():
    try:
        response = requests.get('http://localhost:11434/api/tags')

        if response.status_code == 200:
            print("Ollama está rodando. - Modelo:", response.json()['models'][0]['model'])
            return True
        else:
            print("Ollama não está respondendo corretamente.")
            return False
    except requests.RequestException:
        print("Não foi possível conectar ao Ollama. Certifique-se de que ele está rodando.")
        return Falsen

def gerar_resposta_ollama(prompt: str, modelo: str) -> str:
    url = "http://localhost:11434/api/generate"
    data = {
        "model": modelo,
        "prompt": prompt
    }

    try:
        response = requests.post(url, json=data, stream=True)
        response.raise_for_status()

        resposta_completa = ""
        for line in response.iter_lines():
            if line:
                try:
                    json_response = json.loads(line)
                    if 'response' in json_response:
                        resposta_completa += json_response['response']
                except json.JSONDecodeError:
                    print(f"Erro ao decodificar linha JSON: {line}")

        return resposta_completa.strip()

    except requests.RequestException as e:
        print(f"Erro na requisição HTTP: {e}")
        return f"Erro ao conectar com o Ollama: {e}"
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return f"Erro inesperado ao gerar resposta com Ollama: {e}"

# Função para gerar resposta do GPT
def gerar_resposta_gpt(prompt: str, historico: List[Dict[str, str]], modelo: str) -> str:
    try:
        mensagens = [
            {"role": "system", "content": """
Seu nome é Command e a sua função é ajudar usuários a executar comandos no sistema operacional Windows.
Em prompts com a palavra "execute", mostre comandos do CMD do Windows, caso contrário responda normalmente.
Para listar comandos use chaves, exemplo {comando}, o diretório deve estar entre aspas.
"""}
        ] + historico + [{"role": "user", "content": prompt}]

        resposta = openai.ChatCompletion.create(
            model=modelo,
            messages=mensagens,
            temperature=TEMPERATURA,
            max_tokens=MAX_TOKENS
        )
        return resposta.choices[0].message['content']
    except Exception as e:
        return f"Erro ao gerar resposta: {e}"

# Função principal
def main():
    limpar_tela()
    os.environ["PYTHONIOENCODING"] = "utf-8"
    historico = []

    print("Command\n[criar imagem]: Abre a opção de criar uma imagem (apenas OpenAI) | [execute] + sugestão: Executa um comando")
    print("[mudar modelo]: Muda o modelo de IA em uso\n")

    modelo_atual = MODELO_PADRAO

    # Verifica se o Ollama está rodando
    ollama_disponivel = verificar_ollama()

    while True:
        prompt = input(f"{USUARIO}: ")

        if prompt.lower() == "criar imagem":
            if modelo_atual.startswith("gpt"):
                prompt_imagem = input("Imagem: ")
                criar_imagem(prompt_imagem)
            else:
                print("Criação de imagem disponível apenas com modelos OpenAI.")
            continue

        if prompt.lower() == "mudar modelo":
            novo_modelo = input("Digite o novo modelo (ex: gpt-4, llama2): ")
            if not novo_modelo.startswith("gpt") and not ollama_disponivel:
                print("Ollama não está disponível. Usando modelo OpenAI.")
                novo_modelo = "gpt-3.5-turbo"  # ou outro modelo OpenAI de sua escolha
            modelo_atual = novo_modelo
            print(f"Modelo alterado para: {modelo_atual}")
            continue

        if modelo_atual.startswith("gpt"):
            resposta = gerar_resposta_gpt(prompt, historico, modelo_atual)
        else:
            if ollama_disponivel:
                resposta = gerar_resposta_ollama(prompt, modelo_atual)
            else:
                print("Ollama não está disponível. Usando modelo OpenAI.")
                resposta = gerar_resposta_gpt(prompt, historico, "gpt-3.5-turbo")

        if prompt.lower().startswith("execute"):
            # Verifica se há um comando entre chaves na resposta
            if "{" in resposta and "}" in resposta:
                comando = resposta.split("{")[1].split("}")[0]
                if any(cmd in comando.lower() for cmd in COMANDOS_PERIGOSOS):
                    print("Ação não permitida")
                    continue
                try:
                    os.system(comando)
                    print(f"Command: Comando executado: {comando}")
                except Exception as e:
                    print(f"Erro ao executar o comando: {e}")
        else:
            print(f"Command: {resposta}")

        historico.append({"role": "assistant", "content": resposta})
        historico.append({"role": "user", "content": prompt})

        # Limitar o tamanho do histórico para evitar exceder o limite de tokens
        if len(historico) > 10:
            historico = historico[-10:]

if __name__ == "__main__":
    main()
