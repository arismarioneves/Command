# Command

Command - Assistente de comandos inteligente para Windows

## Descrição

Command é um assistente de comandos avançado para o Windows, projetado para ajudar desenvolvedores a executar comandos no sistema operacional usando linguagem natural. Basta descrever a ação desejada, e o Command interpretará e executará o comando apropriado.

## Características

- **Modelos OpenAI suportados**: GPT-5-nano (padrão), GPT-4o-mini, GPT-4.1-mini
- **Modelos Ollama suportados**: Gemma3:1b (padrão), Gemma2:2b, Llama3.2
- Execução de comandos do sistema através de descrições em linguagem natural
- Geração de imagens com DALL-E 3 (apenas com modelos OpenAI)
- Histórico de conversas para contexto contínuo
- Mudança dinâmica entre modelos de IA
- Interface modernizada com melhor detecção de modelos disponíveis

## Instalação

1. Certifique-se de ter o Python 3.8+ instalado em sua máquina.
2. Clone este repositório ou baixe os arquivos do projeto.
3. Instale as dependências do projeto: `pip install -r requirements.txt`
4. Configure suas credenciais:
   - **OpenAI**: Defina a variável de ambiente `OPENAI_API_KEY` com sua chave de API
   - **Usuário**: (Opcional) Defina `USUARIO` para personalizar o prompt

### Para usar Ollama (modelos locais):
1. Instale o Ollama: https://ollama.ai
2. Baixe o modelo Gemma3:1b: `ollama pull gemma3:1b`
3. Inicie o Ollama: `ollama serve`

## Uso

### Comandos especiais:
- `criar imagem`: Gera imagens com DALL-E 3 (apenas modelos OpenAI)
- `mudar modelo`: Alterna entre modelos disponíveis
- `execute [descrição]`: Executa comandos do sistema baseados na descrição

### Exemplo de uso:
```
root: execute listar arquivos da pasta atual
Command: {dir}
Command: Comando executado: dir

root: criar imagem
Imagem: um gato astronauta no espaço
Command: Imagem criada e aberta no navegador.
```

## Modelos Recomendados

- **GPT-5-nano**: Mais eficiente para tarefas simples
- **GPT-4.1**: Melhor precisão para comandos complexos
- **Gemma3:1b**: Modelo local rápido e eficiente

## Segurança

O Command possui proteções contra comandos perigosos como `format`, `del`, `erase`, etc. Sempre revise os comandos antes da execução.
