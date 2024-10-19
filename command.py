# Command - Assistente de comandos para o Windows
# Autor: Mari05liM
# Versão: 2.0

import os
import openai
import webbrowser
from typing import List, Dict

# Configurações
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "chave_api")
USUARIO = os.getenv("USUARIO", "root")
MODELO = "gpt-4"
TEMPERATURA = 0
MAX_TOKENS = 300

# Configuração do OpenAI
openai.api_key = OPENAI_API_KEY

# Comandos perigosos que não devem ser executados
COMANDOS_PERIGOSOS = ["format", "del", "erase", "rd", "rmdir", "attrib", "reg"]

# Função para limpar a tela
def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")

# Função para criar imagem
def criar_imagem(prompt: str) -> None:
    try:
        resposta = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
        url_imagem = resposta["data"][0]["url"]
        webbrowser.open(url_imagem)
        print("Command: Imagem criada e aberta no navegador.")
    except Exception as e:
        print(f"Erro ao criar imagem: {e}")

# Função para gerar resposta do GPT-4
def gerar_resposta_gpt(prompt: str, historico: List[Dict[str, str]]) -> str:
    try:
        mensagens = [
            {"role": "system", "content": """
Seu nome é Command e a sua função é ajudar usuários a executar comandos no sistema operacional Windows.
Em prompts com a palavra "execute", mostre comandos do CMD do Windows, caso contrário responda normalmente.
Para listar comandos use chaves, exemplo {comando}, o diretório deve estar entre aspas.
"""}
        ] + historico + [{"role": "user", "content": prompt}]

        resposta = openai.ChatCompletion.create(
            model=MODELO,
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

    print("Command\n[criar imagem]: Abre a opção de criar uma imagem | [execute] + sugestão: Executa um comando\n")

    while True:
        prompt = input(f"{USUARIO}: ")

        if prompt.lower() == "criar imagem":
            prompt_imagem = input("Imagem: ")
            criar_imagem(prompt_imagem)
            continue

        resposta = gerar_resposta_gpt(prompt, historico)

        if "{" in resposta:
            comando = resposta.split("{")[1].split("}")[0]
            if any(cmd in comando.lower() for cmd in COMANDOS_PERIGOSOS):
                print("Ação não permitida")
                continue
            try:
                os.system(comando)
            except Exception as e:
                print(f"Erro ao executar o comando: {e}")

        print(f"Command: {resposta}")
        historico.append({"role": "assistant", "content": resposta})
        historico.append({"role": "user", "content": prompt})

        # Limitar o tamanho do histórico para evitar exceder o limite de tokens
        if len(historico) > 10:
            historico = historico[-10:]

if __name__ == "__main__":
    main()
