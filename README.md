# Command

Command - Assistente de comandos inteligente para Windows

## Descrição

Command é um assistente de comandos avançado para o Windows, projetado para ajudar desenvolvedores a executar comandos no sistema operacional usando linguagem natural. Basta descrever a ação desejada, e o Command interpretará e executará o comando apropriado.

Desenvolvido inicialmente com base na API da OpenAI (GPT-3.5-turbo e GPT-4), o Command agora suporta múltiplos modelos de IA, incluindo modelos locais via Ollama.

## Características

- Suporte a múltiplos modelos de IA (OpenAI GPT e modelos locais via Ollama)
- Execução de comandos do sistema através de descrições em linguagem natural
- Geração de imagens (apenas com modelos OpenAI)
- Histórico de conversas para contexto contínuo
- Mudança dinâmica entre modelos de IA

## Instalação

1. Certifique-se de ter o Python 3.7+ instalado em sua máquina.
2. Clone este repositório ou baixe os arquivos do projeto.
3. Instale as dependências do projeto: `pip install -r requirements.txt`
1. Configure o arquivo _command.py_:
- Adicione sua chave de API da OpenAI
- (Opcional) Defina um nome de usuário personalizado

## Configuração

- Para usar modelos da OpenAI, você precisa de uma chave de API válida.
- Para usar modelos locais, instale e configure o Ollama.

## Comandos especiais:
- `criar imagem`: Inicia o processo de geração de imagem (apenas com OpenAI)
- `mudar modelo`: Permite alternar entre diferentes modelos de IA

## Notas Importantes

- O modelo Llama, quando usado via Ollama, pode ter dificuldades em interpretar corretamente os prompts para execução de comandos. Recomenda-se usar modelos OpenAI para melhor precisão na execução de comandos do sistema.
- Tenha cuidado ao executar comandos sugeridos pela IA, especialmente se afetarem o sistema ou arquivos importantes.
