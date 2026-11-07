# Memória do projeto

Última revisão: **7 de novembro de 2026**. Este arquivo guarda conhecimento durável do repositório, não segredos nem histórico integral de sessões. Confira código, diff e estado do Git ao retomar o trabalho.

## Produto e comportamento atual

O Transcribe This converte áudios anexados a mensagens Discord em texto revisado. O pipeline é `anexo.read()` → transcrição OpenAI → refinamento OpenAI → cabeçalho → divisão → resposta Discord.

- Menu **Apps → Transcrever áudio**: atua na mensagem selecionada; adia e entrega respostas efêmeras.
- Resposta com menção: ignora bots, exige menção e referência; busca a referência se necessário e publica como resposta à mensagem do solicitante.
- Apenas o primeiro anexo com `content_type` iniciado por `audio/` é aceito. Anexos sem MIME são ignorados pelos caminhos públicos.
- Sem áudio, o menu informa o problema e o listener encerra silenciosamente.
- O arquivo é lido integralmente na memória, sem persistência própria. A mesma solicitação repetida repete o processamento.
- Resultados incluem o autor do áudio e são divididos em partes de até 2.000 caracteres Python, preferindo quebras de linha e espaços. O envio desabilita menções.
- Não há captura de chamadas, transcrição contínua, resumo, tradução, banco de dados ou cache de resultados.

## Mapa técnico

| Arquivo | Conhecimento relevante |
| --- | --- |
| `main.py` | Carrega `cogs/*.py` a partir do diretório atual, habilita Message Content Intent, sincroniza a árvore global em `setup_hook` e inicia com `DISCORD_TOKEN`. |
| `config/vars.py` | Carrega `.env`, credenciais e prompts. `OPENROUTER_KEY` é legado. |
| `cogs/messages.py` | `MessagesCog` registra/remove o menu, filtra mensagens, coordena os serviços e envia os trechos. |
| `services/transcribe.py` | `AsyncOpenAI` no escopo do módulo; `audio.transcriptions.create` com `gpt-transcribe`, tupla de arquivo e prompt; retorna `.text`. |
| `services/refine.py` | Outro cliente no escopo do módulo; `chat.completions.create` com `gpt-6-luna`; retorna o conteúdo ou uma frase de erro se vazio. |
| `tests/test_fluxo.py` | Seis testes assíncronos com mocks; configura uma chave fictícia se não houver uma no ambiente. |

O prefixo `"when_mentioned"` de `commands.Bot` é uma string literal. A menção funciona pelo listener próprio, não pelo mecanismo de prefixo. Não há comando de barra implementado.

Os prompts pedem conversa informal em português brasileiro ou inglês e revisão fiel ao sentido, idioma, gírias e palavrões. Não há parâmetro explícito de idioma na transcrição.

O refinamento envia `prompt_cache_key="refinamento-transcricao-v1"`, modo explícito e breakpoint no bloco de sistema. Não foram medidos acertos de cache, economia, duração ou custo médio. Os modelos e parâmetros são fatos do código, não prova de disponibilidade na conta de destino.

## Ambiente e dependências

- Referência local: Windows PowerShell, Python **3.13.3**, ambiente `.venv`; o README recomenda Python 3.13+.
- Instalação padrão: `python -m pip install -r requirements.txt`.
- Versões declaradas: `discord.py==2.7.1`, `openai==2.46.0`, `python-dotenv==1.2.2`, `dotenv==0.9.9`, `openrouter==1.1.35`, `jsonpath-python==1.1.6`.
- OpenRouter e jsonpath não têm uso direto nos módulos atuais. `package.json` está vazio; não há etapa npm.
- `poetry.lock` é versionado, mas `pyproject.toml` está ignorado. O manifesto local declara Python `>=3.13`; um clone não o recebe. Alinhar esse empacotamento é uma pendência, não uma mudança concluída.
- PyYAML **6.0.3** estava instalado no ambiente virtual ao criar as skills. É ferramenta de validação das skills, não dependência de execução do bot em `requirements.txt`.
- `.env` deve fornecer `DISCORD_TOKEN` e `OPENAI_API_KEY` para execução real. Nenhum valor de credencial pertence a este arquivo.
- Discloud: entrada `main.py`, `RAM=100`, `version=latest`. Não houve ensaio de capacidade ou validação de deploy nesta revisão.

## Evidências de validação

Em 07/11/2026, `python -X utf8 -m unittest discover -s tests -v` passou nos **seis testes**, com serviços externos simulados. Os cenários cobrem payloads dos dois serviços, refinamento vazio, divisão sem perda, encadeamento do pipeline e falha de busca da referência. Não houve autenticação real nem chamada de áudio à OpenAI nessa análise.

Uma execução sem UTF-8, com stdout `cp1252`, passou em cinco testes e falhou no teste de referência: `print` tentou emitir `❌` e lançou `UnicodeEncodeError` antes da resposta de erro. Usar `-X utf8` fez os seis passarem. O contorno foi documentado; o logging permanece sem correção no código.

No sandbox Windows desta sessão, a criação do loop assíncrono também bloqueou antes do corpo do primeiro teste. Uma captura com `faulthandler` apontou `socket._fallback_socketpair`/`accept`, e a execução fora dessa restrição passou. Essa observação é do ambiente de execução, sem comprovação de bug do projeto ou exigência de privilégios para usuários comuns.

## Pendências confirmadas e investigações

| Estado | Tema | Próxima evidência útil |
| --- | --- | --- |
| Bug reproduzido | Log com emoji quebra em `cp1252`. | Testar logging com saída restrita e resposta de erro preservada. |
| Limitação do código | Loops de envio fora do `try`; a própria resposta de erro pode falhar. | Simular falha de entrega, inclusive após uma primeira parte enviada. |
| Limitação do código | Sem validação prévia de tamanho/duração, fila, semáforo, cota ou deduplicação. | Definir política solicitada e medir recursos em carga controlada. |
| Limitação do código | Refinamento vazio vira frase de erro com cabeçalho de resultado; exceção de refinamento perde a transcrição bruta. | Definir contrato de erro e testar consumidores antes de alterá-lo. |
| Limitação do código | Execução depende da raiz por causa de `./cogs`. | Reproduzir lançamento por outro diretório se essa correção for solicitada. |
| Investigação pendente | Entrega com muitos emojis, permissões em threads e interação expirada. | Testes focados e eventual integração manual autorizada. |
| Validação remota pendente | Modelos, formatos reais, cache e custos. | Verificar conta/documentação atual e uso real autorizado; mocks não bastam. |

Não há configuração versionada de CI, formatter ou linter. A cobertura do Cog ainda é parcial. A presença de uma pendência aqui não é autorização para ampliar o escopo de uma tarefa.

## Organização da continuidade

- `README.md`: documentação de produto e operação, organizada nas nove seções solicitadas, terminando com a licença MIT padrão já existente em `LICENSE`.
- `AGENTS.md`: instruções comuns de desenvolvimento e entrada para Codex.
- `CLAUDE.md`: importa as instruções comuns e orienta o uso no Claude Code.
- `.agents/skills/`: fontes canônicas de `transcribe-discord-flow`, `transcribe-ai-services` e `transcribe-validation`.
- `.claude/skills/`: entradas de descoberta que apontam às mesmas fontes, sem duplicar os procedimentos.

Ao continuar, leia o estado do Git para identificar mudanças locais de outras tarefas. O remoto observado era `origin` em `https://github.com/mateusb6315/transcribethisbot.git`; branch e sincronização devem ser consultadas novamente, não presumidas a partir desta memória.

Atualize este arquivo quando novos fatos substituírem os atuais. Registre data e evidência de testes ou reproduções; mantenha tarefas propostas separadas das concluídas. Use `git log` para histórico de commits, sem perpetuar hashes ou status transitórios aqui.
