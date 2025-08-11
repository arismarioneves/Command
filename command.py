# Command - Assistente de comandos para o Windows
# Autor: Mari05liM
# Versão: 4.0

import os
from openai import OpenAI
import webbrowser
import requests
import json
from typing import List, Dict

# Configurações
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "chave_api")
USUARIO = os.getenv("USUARIO", "root")
MODELO_PADRAO = "gemma3:1b"
TEMPERATURA = 0
MAX_TOKENS = 300

# Configuração do OpenAI
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY != "chave_api" else None

# Comandos perigosos que não devem ser executados
COMANDOS_PERIGOSOS = ["format", "del", "erase", "rd", "rmdir", "attrib", "reg"]

# Função para limpar a tela
def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")

# Função para criar imagem (apenas para OpenAI)
def criar_imagem(prompt: str) -> None:
    if not client:
        print("Criação de imagem não disponível. Chave API do OpenAI não configurada.")
        return
    try:
        resposta = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        url_imagem = resposta.data[0].url
        webbrowser.open(url_imagem)
        print("Command: Imagem criada e aberta no navegador.")
    except Exception as e:
        print(f"Erro ao criar imagem: {e}")

def verificar_ollama():
    try:
        response = requests.get('http://localhost:11434/api/tags')

        if response.status_code == 200:
            modelos = response.json().get('models', [])
            if modelos:
                print(f"Ollama está rodando. - Modelos disponíveis: {len(modelos)}")
                # Verifica se gemma3:1b está disponível
                gemma_disponivel = any('gemma3:1b' in modelo.get('name', '') for modelo in modelos)
                if gemma_disponivel:
                    print("✓ Gemma3:1b detectado")
            return True
        else:
            print("Ollama não está respondendo corretamente.")
            return False
    except requests.RequestException:
        print("Não foi possível conectar ao Ollama. Certifique-se de que ele está rodando.")
        return False

def gerar_resposta_ollama(prompt: str, modelo: str) -> str:
    url = "http://localhost:11434/api/generate"
    data = {
        "model": modelo,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()

        json_response = response.json()
        if 'response' in json_response:
            return json_response['response'].strip()
        else:
            return "Erro: Resposta inválida do Ollama"

    except requests.RequestException as e:
        print(f"Erro na requisição HTTP: {e}")
        return f"Erro ao conectar com o Ollama: {e}"
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return f"Erro inesperado ao gerar resposta com Ollama: {e}"

# Função para gerar resposta do GPT/OpenAI
def gerar_resposta_openai(prompt: str, historico: List[Dict[str, str]], modelo: str) -> str:
    if not client:
        return "Erro: Cliente OpenAI não configurado. Verifique sua chave API."

    try:
        mensagens = [
            {"role": "system", "content": """
Seu nome é Command e a sua função é ajudar usuários a executar comandos no sistema operacional Windows.
Em prompts com a palavra "execute", mostre comandos do CMD do Windows, caso contrário responda normalmente.
Para listar comandos use chaves, exemplo {comando}, o diretório deve estar entre aspas.
"""}
        ] + historico + [{"role": "user", "content": prompt}]

        resposta = client.chat.completions.create(
            model=modelo,
            messages=mensagens,
            temperature=TEMPERATURA,
            max_tokens=MAX_TOKENS
        )
        return resposta.choices[0].message.content
    except Exception as e:
        return f"Erro ao gerar resposta: {e}"

# Função principal
def main():
    limpar_tela()
    os.environ["PYTHONIOENCODING"] = "utf-8"
    historico = []

    print("Command\n[criar imagem]: Abre a opção de criar uma imagem | [execute] + sugestão: Executa um comando")
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
            print("\nModelos disponíveis:")
            print("OpenAI: gpt-4o-mini, gpt-4.1-mini, gpt-5-nano")
            print("Ollama: gemma2:2b, gemma3:1b, llama3.2")
            novo_modelo = input("\nDigite o novo modelo: ")

            # Verifica se é um modelo OpenAI válido
            modelos_openai = ["gpt-4o-mini", "gpt-4.1-mini", "gpt-5-nano"]

            if novo_modelo in modelos_openai:
                if not client:
                    print("Erro: Chave API do OpenAI não configurada.")
                    continue
            elif not ollama_disponivel:
                print("Ollama não está disponível. Usando modelo OpenAI padrão.")
                novo_modelo = "gpt-5-nano"

            modelo_atual = novo_modelo
            print(f"Modelo alterado para: {modelo_atual}")
            continue

        # Determina qual API usar baseado no modelo
        modelos_openai = ["gpt-4o-mini", "gpt-4.1-mini", "gpt-5-nano"]

        if modelo_atual in modelos_openai:
            resposta = gerar_resposta_openai(prompt, historico, modelo_atual)
        else:
            if ollama_disponivel:
                resposta = gerar_resposta_ollama(prompt, modelo_atual)
            else:
                print("Ollama não está disponível. Usando modelo OpenAI.")
                resposta = gerar_resposta_openai(prompt, historico, "gpt-5-nano")

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
