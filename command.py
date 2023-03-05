# Command - Assistente de comandos para o Windows
# Autor: Mari05liM
# Versão: 1.1

import os
import openai
import webbrowser
import config

openapiley = config.OPENAPIKEY
usuario = config.USUARIO

if usuario == "":
    usuario = "root"

os.system("cls" if os.name == "nt" else "clear")  # Limpa a tela
os.environ["PYTHONIOENCODING"] = "utf-8"  # Define a codificação do terminal
openai.api_key = openapiley
model = "text-davinci-003"
temperature = 0
max_tokens = 300
treinamento = (
    """
Seu nome é Command e a sua função é ajudar usuários a executar comandos no sistema operacional.
Em propts com a palavra "execute", motre comandos do CMD do Windows, caso contrário responda normalmente. Para lista comandos use chaves, exemplo {comando}, o diretório deve estar entre aspas.
Exemplos:
"""
    + usuario
    + """: Olá Command.
Command: {comando} Olá """
    + usuario
    + """. Como posso te ajudar?
"""
    + usuario
    + """: Execute listar arquivos do desktop.
Command: {dir "%USERPROFILE%\desktop"} Aqui está a saída do comando.
"""
    + usuario
    + """: Execute clima.
Command: {curl wttr.in?lang=pt} Aqui está o clima.
"""
)
historico = ""

print(
    "Command\n[criar imagem]: Abre a opção de criar uma imagem | [execute] + sugestão: Executa um comando\n"
)


# CRIAR IMAGEM
def createImage(prompt):
    resposta = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
    resposta = resposta["data"][0]["url"]
    # Abre a imagem criada no navegador
    webbrowser.open(resposta)


while True:
    # Prompt
    prompt = input(usuario + ": ")
    # Verifica se o comando é para criar uma imagem
    if prompt == "criar imagem":
        promptImage = input("Imagem: ")
        createImage(promptImage)
        print("Command: Imagem criada")
        continue
    resposta = openai.Completion.create(
        model=model,
        prompt=treinamento + historico + usuario + ": " + prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    resposta = resposta["choices"][0]["text"]
    # Verifica se no texto contem chaves
    if "{" in resposta:
        comand = resposta.split("{")[1].split("}")[0]

        # Verifica se o comando pode ser executado
        if comand.split(" ")[0] in [
            "format",
            "del",
            "erase",
            "rd",
            "rmdir",
            "attrib",
            "reg",
        ]:
            # print(resposta)
            print("Ação não permitida")
            continue

        # Executa o comando
        os.system(comand)
    historico += resposta
    print(resposta)
