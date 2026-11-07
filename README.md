# Transcribe This

Bot para transformar mensagens de voz e anexos de áudio do Discord em texto revisado, com processamento assíncrono pela API da OpenAI.

## 1. O que é o Transcribe This e qual é seu objetivo

O **Transcribe This** facilita o acesso ao conteúdo de áudios em conversas do Discord: quem prefere ler, precisa consultar uma informação ou não pode ouvir uma mensagem pode solicitar uma transcrição sem sair do canal.

O processamento tem duas etapas: um modelo transcreve o arquivo de áudio e outro revisa o texto, corrigindo pontuação e erros ortográficos evidentes e organizando parágrafos. As instruções pedem a preservação do sentido, dos detalhes, do idioma, das gírias e dos palavrões, sem formalizar ou censurar a fala. Essa preservação é um objetivo dos prompts; o resultado ainda precisa de revisão humana quando a precisão for importante.

O bot oferece duas formas de uso:

| Acionamento | Como usar | Onde aparece o resultado |
| --- | --- | --- |
| Menu de contexto da mensagem | Na mensagem com áudio, abrir **Apps → Transcrever áudio**. | Resposta efêmera, visível para quem acionou o comando. |
| Resposta com menção | Responder à mensagem com áudio e mencionar o bot. | Resposta pública à mensagem de quem fez o pedido, no mesmo canal. |

Cada solicitação processa **somente o primeiro anexo cujo `content_type` começa com `audio/`**. O projeto não implementa gravação de chamadas, captura de canais de voz, transcrição contínua, processamento de links externos, diarização de falantes, timestamps, tradução ou resumo.

## 2. Requisitos e ferramentas necessárias

### Ambiente de execução

- **Python 3.13 ou superior** como referência de ambiente do projeto. A análise local e os testes foram executados com Python 3.13.3. O `pyproject.toml` local declara `>=3.13`, mas esse arquivo está ignorado e não acompanha o clone; o repositório versionado não impõe a versão do interpretador.
- **pip** e um ambiente virtual para instalar as dependências de `requirements.txt`.
- **Git**, caso a instalação seja feita por clone.
- Conectividade com Discord e OpenAI durante a execução real.
- Uma aplicação com bot no [Discord Developer Portal](https://discord.com/developers/applications) e seu token.
- Uma chave da API da OpenAI, com acesso aos modelos configurados e capacidade de uso na conta.

### Bibliotecas e ferramentas

As versões abaixo são as declaradas no arquivo de instalação do repositório:

| Ferramenta | Versão/configuração | Responsabilidade |
| --- | --- | --- |
| `discord.py` | `2.7.1` | Conexão com Discord, eventos, Cog, menu de contexto e respostas. |
| `openai` | `2.46.0` | Clientes `AsyncOpenAI` para transcrição e refinamento. |
| `python-dotenv` | `1.2.2` | Carregamento das variáveis de `.env`. |
| `dotenv` | `0.9.9` | Dependência declarada; o carregamento de `.env` usa a implementação de `python-dotenv`. |
| `openrouter` | `1.1.35` | Dependência legada, sem uso nos módulos atuais. |
| `jsonpath-python` | `1.1.6` | Dependência declarada, sem importação direta no código do bot. |
| `unittest` e `unittest.mock` | Biblioteca padrão do Python | Testes assíncronos e simulação dos serviços externos. |
| Discloud | `discloud.config` | Configuração opcional de hospedagem. |

O caminho padrão de instalação é **pip + `requirements.txt`**. Há um `poetry.lock` versionado, mas o respectivo `pyproject.toml` está no `.gitignore`; por isso, o clone não contém uma configuração completa para instalação por Poetry. `package.json` está vazio e `package-lock.json` não define uma aplicação JavaScript: Node.js e npm não são necessários ao fluxo atual.

Não há conversão local de mídia nem dependência direta de FFmpeg no código. O bot envia os bytes originais do anexo ao serviço de transcrição.

### Configuração do Discord

Na configuração do bot no Developer Portal, habilite **Message Content Intent**. No código, `main.py` já ativa `intents.message_content = True`.

Para a instalação da aplicação no servidor, inclua os escopos `bot` e `applications.commands`. O bot deve conseguir visualizar o canal, ler o histórico e enviar mensagens no local de uso. Canais e threads podem ter restrições próprias de acesso e envio.

O menu de contexto é registrado pela aplicação e sincronizado globalmente no início da execução. Não há um comando de barra `/transcrever` implementado.

### Variáveis de ambiente

| Variável | Necessária? | Uso |
| --- | --- | --- |
| `DISCORD_TOKEN` | Sim | Autenticação do bot; `main.py` verifica sua presença antes de chamar `bot.run`. |
| `OPENAI_API_KEY` | Sim | Criação dos clientes OpenAI importados pelos serviços. |
| `OPENROUTER_KEY` | Não | Variável legada carregada em `config/vars.py`, sem consumo no fluxo atual. |

`load_dotenv()` carrega o arquivo `.env`. Variáveis já definidas no ambiente têm precedência no comportamento padrão dessa chamada. Não há uma camada central de validação de todas as configurações: a ausência da chave OpenAI pode impedir o carregamento da extensão, e credenciais inválidas podem falhar apenas na autenticação ou nas chamadas remotas.

## 3. Quick start padrão

### 1. Clonar e criar o ambiente virtual

```bash
git clone https://github.com/mateusb6315/transcribethisbot.git
cd transcribethisbot
python -m venv .venv
```

Ative o ambiente conforme seu sistema:

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

### 2. Instalar as dependências

```bash
python -m pip install -r requirements.txt
```

### 3. Configurar as credenciais

Crie manualmente um arquivo `.env` na raiz do projeto; não há `.env.example` versionado:

```dotenv
DISCORD_TOKEN=seu_token_do_bot_discord
OPENAI_API_KEY=sua_chave_da_api_openai
```

Não inclua aspas ou outros textos copiados do portal por engano. O `.env` está ignorado pelo Git e não deve ser incluído em commits.

### 4. Iniciar o bot

Execute a partir da raiz do repositório:

```bash
python -X utf8 main.py
```

A opção `-X utf8` evita o problema de codificação dos logs com emojis em terminais Windows que usam `cp1252`; também pode ser usada nos demais sistemas. O diretório de trabalho importa porque o carregamento das extensões usa o caminho relativo `./cogs`.

Ao conectar, o terminal exibe:

```text
Bot online como <nome-do-bot>
```

### 5. Solicitar uma transcrição

1. Envie um áudio em um canal acessível ao bot.
2. Abra o menu da mensagem e selecione **Apps → Transcrever áudio**, ou responda à mensagem mencionando o bot.
3. Aguarde a transcrição e o refinamento; o resultado pode ser dividido em várias mensagens.

Enviar um áudio sozinho, mencionar o bot sem responder a uma mensagem ou responder sem mencioná-lo não aciona o listener de transcrição.

### 6. Executar os testes locais

```bash
python -X utf8 -m unittest discover -s tests -v
```

A suíte atual tem **seis testes**. Ela simula as chamadas OpenAI e os objetos do Discord, sem fazer login no bot ou enviar áudios reais. O teste define uma chave fictícia quando `OPENAI_API_KEY` não existe. Não é necessário configurar credenciais reais para essa suíte.

## 4. Arquitetura dos módulos

### Estrutura do repositório

```text
transcribethisbot/
├── main.py                  # Inicialização e ciclo de vida do bot
├── config/
│   └── vars.py              # Variáveis de ambiente e prompts
├── cogs/
│   └── messages.py          # Entradas Discord e orquestração do processamento
├── services/
│   ├── transcribe.py        # Áudio → texto bruto
│   └── refine.py            # Texto bruto → texto revisado
├── tests/
│   └── test_fluxo.py        # Testes unitários assíncronos
├── .agents/skills/          # Skills compartilhadas e descoberta pelo Codex
├── .claude/skills/          # Entradas Claude Code para as skills compartilhadas
├── AGENTS.md               # Instruções de desenvolvimento para agentes
├── CLAUDE.md               # Entrada de contexto para Claude Code
├── MEMORY.md               # Estado verificado e conhecimento durável
├── requirements.txt         # Dependências para instalação padrão
├── poetry.lock              # Lockfile sem manifesto versionado correspondente
├── package.json             # Manifesto vazio, sem scripts de execução
├── package-lock.json        # Arquivo auxiliar de npm
├── discloud.config          # Configuração de hospedagem
├── .gitignore               # Exclusão de credenciais e arquivos locais
├── LICENSE                  # Licença MIT
└── README.md
```

### `main.py`: inicialização

- Cria as intents padrão do Discord e habilita o acesso ao conteúdo das mensagens.
- Instancia `commands.Bot` e registra os eventos de inicialização.
- Em `carregar_cogs()`, percorre os arquivos `.py` diretamente em `./cogs` e carrega cada um como extensão.
- Em `setup_hook()`, carrega as extensões e executa `bot.tree.sync()` para sincronizar os comandos de aplicação.
- Em `on_ready()`, imprime a identificação do bot conectado.
- Quando executado como programa principal, valida `DISCORD_TOKEN` e inicia `bot.run(TOKEN)`.

O valor de `command_prefix` é a string literal `"when_mentioned"`; ele não é a função `commands.when_mentioned`. O acionamento por menção funciona pela lógica própria de `MessagesCog.on_message`. Não há comandos tradicionais de prefixo definidos no projeto.

### `config/vars.py`: configurações e instruções dos modelos

Centraliza o carregamento de `.env`, as três variáveis de credenciais e os dois prompts:

- `PROMPT_TRANSCRIBE`: contextualiza o áudio como conversa informal, possivelmente com gírias e palavrões em português brasileiro ou inglês. Não fixa um parâmetro `language` na API.
- `PROMPT_REFINAMENTO`: solicita correções evidentes, organização em parágrafos e preservação de conteúdo e estilo; pede somente o texto revisado como saída.

Os nomes dos modelos ficam nos serviços, e não nesse módulo. Alterar os prompts exige mudar o código; não há painel administrativo, comandos de configuração ou configuração por servidor.

### `cogs/messages.py`: interface e orquestração

`MessagesCog` concentra a integração com Discord e compõe os dois serviços:

| Método | Responsabilidade |
| --- | --- |
| `__init__` | Instancia os serviços e registra o menu de contexto **Transcrever áudio** na árvore de comandos. |
| `cog_unload` | Remove o menu de contexto ao descarregar a extensão. |
| `_extrair_audio` | Percorre os anexos em ordem e retorna o primeiro com MIME `audio/`; retorna `None` se não encontrar. |
| `_transcrever_refinar` | Lê o anexo em memória, envia bytes, nome e MIME à transcrição e repassa o texto ao refinamento. |
| `_dividir_texto` | Divide a resposta em partes de até 2.000 caracteres, preferindo quebra de linha, depois espaço e, por último, corte direto. Preserva o texto ao concatenar as partes. |
| `transcrever` | Atende ao menu de contexto, adia a resposta como efêmera e envia os trechos com identificação do autor do áudio. |
| `on_message` | Filtra mensagens, resolve a mensagem respondida e publica os trechos no canal quando há menção e referência válidas. |
| `setup` | Ponto de entrada da extensão que adiciona o Cog ao bot. |

O MIME alternativo `audio/ogg` existe na chamada interna de `_transcrever_refinar`. Nos caminhos públicos atuais, anexos sem `content_type` são descartados antes por `_extrair_audio`; portanto, esse fallback não torna esses anexos automaticamente elegíveis.

Os resultados são enviados com `discord.AllowedMentions.none()`, evitando notificações por menções contidas na transcrição. A resposta de erro do listener não configura essa opção explicitamente. A saída é texto comum, sem escape de Markdown.

### `services/transcribe.py`: transcrição

Cria um cliente `AsyncOpenAI` no escopo do módulo. `TranscribeService.transcribe_audio(audio_bytes, filename, content_type)` chama `client.audio.transcriptions.create` com:

- Modelo configurado: `gpt-transcribe`.
- Arquivo: tupla `(filename, audio_bytes, content_type)`.
- Contexto: `PROMPT_TRANSCRIBE`.

Retorna `transcricao.text`. Não converte o arquivo, não valida sua extensão ou tamanho, não persiste o áudio e não trata exceções localmente. As falhas sobem para o Cog.

### `services/refine.py`: refinamento

Cria seu próprio cliente `AsyncOpenAI`, também no escopo do módulo. `RefineService.refine(transcricao)` chama `client.chat.completions.create` com:

- Modelo configurado: `gpt-6-luna`.
- Instrução de sistema: `PROMPT_REFINAMENTO` em um bloco de texto.
- Conteúdo de usuário: a transcrição bruta.
- `prompt_cache_key="refinamento-transcricao-v1"`.
- `prompt_cache_options={"mode": "explicit"}` e um `prompt_cache_breakpoint` explícito no bloco de sistema.

Lê `choices[0].message.content` e devolve o conteúdo quando ele não é nulo nem composto somente de espaços. Caso contrário, retorna a string `Ocorreu um erro na transcrição do áudio.`. Esse retorno é tratado pelo Cog como texto de resultado, sem uma sinalização estruturada de falha. Uma lista `choices` vazia geraria uma exceção, capturada pelo tratamento genérico do Cog durante o processamento.

### `tests/test_fluxo.py`: verificação automatizada

Usa `unittest.IsolatedAsyncioTestCase`, `AsyncMock`, `MagicMock` e `patch`. Os seis cenários cobrem:

1. Payload de transcrição com bytes, nome, MIME e prompt.
2. Payload de refinamento com prompt e configuração estável de cache.
3. Fallback quando o refinamento retorna somente espaços.
4. Divisão de textos longos, preservando conteúdo e limite de tamanho.
5. Encadeamento entre leitura do anexo, transcrição e refinamento, incluindo o MIME alternativo.
6. Resposta de erro quando a busca da mensagem referenciada falha.

Não há teste de integração com as APIs reais. A suíte também não cobre completamente o menu de contexto, filtros de anexos, envio de múltiplas partes, permissões, sincronização de comandos ou esgotamento de recursos.

### Padrões e decisões de implementação

- **Programação assíncrona:** operações de Discord e OpenAI usam `async`/`await`. Dentro de cada solicitação, transcrição e refinamento são sequenciais.
- **Extensões e Cog:** o ciclo de vida do Discord fica em `main.py`; a interface das mensagens fica em uma extensão.
- **Separação por responsabilidade:** serviços cuidam das chamadas aos modelos, enquanto o Cog coordena o fluxo e as respostas.
- **Composição direta:** o Cog instancia serviços concretos; não há contêiner de injeção de dependências. Os testes substituem serviços ou chamadas por mocks.
- **Configuração parcial centralizada:** credenciais e prompts estão em `config/vars.py`; modelos, limite das mensagens e parâmetros de cache permanecem no código consumidor.
- **Execução sem persistência própria:** não há banco de dados, cache de resultados ou arquivos de áudio gravados pelo fluxo. Os dados do anexo são lidos integralmente na memória.
- **Tratamento de erro na interface:** exceções do processamento viram mensagens genéricas no Discord e logs com `print`; não há categorias de erro, identificador de solicitação ou logging estruturado.

## 5. Fluxo operacional

### Inicialização

```text
python -X utf8 main.py
  → importa configurações e carrega .env
  → cria o bot com as intents
  → autentica com DISCORD_TOKEN
  → setup_hook carrega cogs/*.py e registra o menu
  → sincroniza a árvore de comandos
  → on_ready informa que o bot está online
```

Os clientes OpenAI são construídos na importação dos serviços durante o carregamento do Cog. Uma falha nessa etapa pode impedir a conclusão da inicialização.

### Menu de contexto

1. O usuário seleciona **Transcrever áudio** na mensagem original.
2. O Cog procura o primeiro anexo de áudio.
3. Sem áudio elegível, responde `❌ Nenhuma mensagem de voz encontrada.` de forma efêmera e encerra.
4. Com áudio, chama `defer(ephemeral=True)` antes do processamento remoto.
5. Baixa o arquivo, transcreve e refina.
6. Acrescenta o cabeçalho `📝 Áudio de <autor>`, divide a saída e envia cada trecho como follow-up efêmero, com menções desabilitadas.
7. Se o processamento falhar, registra o erro e tenta enviar um follow-up efêmero com a mensagem genérica de falha.

### Resposta com menção

1. O listener ignora mensagens de bots.
2. Exige que o bot esteja identificado, mencionado na mensagem e que exista uma referência com `message_id`.
3. Usa a mensagem referenciada já resolvida quando ela é um `discord.Message`; caso contrário, tenta buscá-la no canal com `fetch_message`.
4. Procura o primeiro áudio na mensagem referenciada. Sem áudio, encerra silenciosamente.
5. Mantém o indicador de digitação do canal durante o download e as duas etapas de processamento.
6. Acrescenta o cabeçalho `🎙️ Áudio de <autor>:`, divide a saída e envia respostas públicas à mensagem do solicitante, com menções desabilitadas.
7. Após o envio, imprime um log com os nomes de exibição do autor do áudio e do solicitante.
8. Falhas na busca da referência ou no processamento entram no tratamento genérico, que registra o erro e tenta responder no canal.

### Caminho compartilhado de processamento

```text
Anexo Discord elegível
  → anexo.read(): bytes em memória
  → TranscribeService: bytes + nome + MIME + prompt → texto bruto
  → RefineService: instrução de sistema + texto bruto → texto revisado
  → cabeçalho com autor + divisão em partes de até 2.000 caracteres
  → Discord: resposta efêmera ou pública
```

Uma nova solicitação para o mesmo áudio repete todo o caminho. Se o refinamento lançar uma exceção depois de a transcrição funcionar, o texto bruto não é oferecido como resultado alternativo.

## 6. Problemas conhecidos e bugs em investigação

Os itens abaixo separam comportamentos observados, limitações verificadas por leitura do código e cenários que ainda precisam de reprodução. Não representam um rastreador de issues já abertas.

### Bug reproduzido: codificação dos logs no Windows

**Sintoma:** com saída padrão em `cp1252`, a suíte pode falhar com `UnicodeEncodeError` ao imprimir `❌` no tratamento de erro de `on_message`. Na execução analisada com Python 3.13.3, cinco testes passaram e o teste de falha na busca da referência terminou com esse erro de codificação. A impressão interrompeu o caminho antes da resposta ao usuário.

**Contorno verificado:** executar com UTF-8:

```bash
python -X utf8 main.py
python -X utf8 -m unittest discover -s tests -v
```

Com essa opção, os seis testes passaram. O código de logging ainda precisa de uma solução que funcione independentemente da codificação do terminal.

### Limitações confirmadas no código

| Ponto | Comportamento e impacto |
| --- | --- |
| Envio de resultados fora do `try` | Os loops de `followup.send` e `message.reply` não estão no bloco que protege o processamento. Falhas de permissão, canal indisponível ou interação expirada podem deixar a entrega incompleta sem a resposta genérica prevista. |
| Resposta de erro também pode falhar | Não há proteção adicional se o envio da própria mensagem de erro lançar exceção. |
| Dependência de MIME | Áudios sem `content_type` ou identificados como outro tipo são ignorados, mesmo que tenham extensão de áudio. |
| Apenas um anexo | Anexos de áudio adicionais na mesma mensagem não são processados. |
| Sem validação prévia de tamanho ou duração | O arquivo inteiro é baixado antes da chamada OpenAI; o bot não antecipa rejeições do serviço nem controla o consumo de memória por solicitação. |
| Sem fila, semáforo ou cota por usuário | Várias solicitações podem executar simultaneamente, elevando uso de memória e chamadas às APIs. |
| Sem deduplicação ou cache de resultado | Repetir a solicitação pode repetir custos e trabalho. |
| Falha no refinamento descarta o resultado bruto | Não há modo degradado que devolva somente a transcrição quando a revisão falha. |
| Refinamento vazio retorna uma frase de erro como resultado | O usuário recebe essa frase com cabeçalho de transcrição; não há um estado de falha distinguível pelo chamador. |
| Configuração espalhada | Modelos são constantes nos serviços; mudanças exigem edição do código e alinhamento dos testes. |
| Logging limitado | Não há métricas de latência, duração, tokens, custo ou taxa de falha; exceções são impressas sem traceback explícito. |
| Empacotamento incompleto para Poetry | `poetry.lock` está versionado, mas `pyproject.toml` está ignorado; o caminho reproduzível documentado usa `requirements.txt`. |
| Dependência do diretório de execução | Iniciar fora da raiz pode impedir `os.listdir("./cogs")` de encontrar as extensões. |

### Pontos em investigação e validação pendente

- **Disponibilidade dos modelos e comportamento do cache na conta de destino:** os testes verificam os argumentos enviados com mocks, mas não comprovam acesso aos modelos, aceitação de arquivos reais ou ocorrência de cache na API. Não houve chamada real às APIs nesta revisão.
- **Áudios longos ou solicitações concorrentes:** medir memória, tempo total e sucesso da entrega, especialmente pelo menu de contexto. Não há configuração própria de timeout global ou retentativa do fluxo; aplicam-se os comportamentos das bibliotecas utilizadas.
- **Caracteres especiais na divisão de mensagens:** `_dividir_texto` usa `len(str)` e cortes de Python. A suíte cobre texto simples, espaços e quebras de linha, mas não valida a entrega de trechos com muitos emojis ou outros caracteres Unicode no Discord.
- **Formatação e conteúdo gerado:** Markdown, nomes de exibição incomuns e texto interpretado como instruções pelo modelo não têm tratamento específico. Avaliar exemplos e fidelidade antes de alterar os prompts ou a apresentação.
- **Ciclo completo do Discord:** validar registro e remoção do menu, permissões em canais e threads, mensagens removidas e erros no envio das partes. A cobertura atual não comprova esses cenários.

Ao investigar, registre o comportamento esperado, a reprodução mínima e a mensagem do erro, sem publicar credenciais ou áudio privado.

## 7. Como colaborar com o código

Contribuições para confiabilidade, testes, experiência no Discord e documentação são bem-vindas. Use as [issues](https://github.com/mateusb6315/transcribethisbot/issues) para relatar problemas ou propor melhorias e os [pull requests](https://github.com/mateusb6315/transcribethisbot/pulls) para enviar alterações.

### Abrir uma issue útil

Inclua:

- O resultado esperado e o comportamento observado.
- Passos mínimos para reproduzir e a forma de acionamento utilizada.
- Sistema operacional, versão do Python e versões das dependências envolvidas.
- Tipo, tamanho aproximado e MIME do anexo, quando forem relevantes.
- Logs ou traceback sem tokens, chaves, URLs privadas ou conteúdo sensível.
- Se o problema ocorre também em uma instalação com as versões de `requirements.txt`.

Para sugestões, explique o problema de uso e o efeito esperado. Para mudanças amplas, uma issue ajuda a discutir o escopo antes da implementação.

### Enviar um pull request

1. Faça um fork, clone-o e configure o ambiente pelo quick start.
2. Crie uma branch com nome descritivo, por exemplo `fix/logs-windows` ou `feat/limite-audio`.
3. Faça uma alteração focada e mantenha a separação entre configuração, interface Discord e serviços.
4. Adicione ou ajuste testes para mudanças de comportamento. Use mocks nas chamadas externas para manter os testes locais independentes das contas reais.
5. Execute `python -X utf8 -m unittest discover -s tests -v`.
6. Atualize o README quando mudar requisitos, configuração ou funcionamento.
7. Abra o PR com problema resolvido, comportamento final, validação realizada e referência à issue, se houver.

O código usa funções assíncronas nas integrações, classes de serviço, nomes predominantemente em português na interface e tipagem em parte dos métodos. Preserve as convenções do módulo alterado. Não há configuração versionada de formatter, linter ou pipeline de CI; descreva as verificações executadas no PR.

Boas frentes de colaboração incluem o bug de codificação, proteção dos envios, ampliação dos testes do Cog, validação dos anexos, controle de concorrência e alinhamento dos arquivos de dependências. Não inclua `.env`, chaves de API, tokens Discord ou arquivos de áudio privados nos commits.

### Continuidade com Codex e Claude Code

O [AGENTS.md](AGENTS.md) reúne as instruções comuns de desenvolvimento. O [CLAUDE.md](CLAUDE.md) importa essas instruções para Claude Code. Ao retomar uma tarefa, leia o [MEMORY.md](MEMORY.md), que registra fatos verificados, bugs reproduzidos, limites dos testes e pendências; confirme no código e no Git o que ainda se aplica.

Há três skills específicas do projeto:

| Skill compartilhada | Quando usar |
| --- | --- |
| [transcribe-discord-flow](.agents/skills/transcribe-discord-flow/SKILL.md) | Alterar acionamentos, seleção de anexos, referências e entrega no Discord. |
| [transcribe-ai-services](.agents/skills/transcribe-ai-services/SKILL.md) | Trabalhar nos serviços de transcrição e revisão, prompts e contratos OpenAI. |
| [transcribe-validation](.agents/skills/transcribe-validation/SKILL.md) | Reproduzir falhas, ampliar testes e diagnosticar o ambiente de execução. |

As fontes ficam em `.agents/skills/`, diretório de skills de repositório documentado para o [Codex](https://learn.chatgpt.com/docs/customization/overview). Para o [Claude Code](https://code.claude.com/docs/en/skills), as entradas em `.claude/skills/` apontam para essas fontes. No Codex, invoque, por exemplo, `$transcribe-validation`; no Claude Code, `/transcribe-validation`. A seleção automática também pode aplicar a skill pertinente conforme o cliente e sua configuração.

Ao evoluir um procedimento, edite o `SKILL.md` compartilhado e preserve o link da entrada Claude. Se mudar nome ou escopo, atualize os metadados de descoberta em ambos os diretórios. As skills são instruções de desenvolvimento e não dependências do bot.

As skills foram criadas com `skill-creator` e validadas com seu `scripts/quick_validate.py`. Para repetir essa validação, use o Python do ambiente virtual, com UTF-8, e forneça o diretório de cada skill ao validador da sua instalação de `skill-creator`. Ele requer PyYAML, disponível no ambiente local de criação; em outro ambiente de desenvolvimento, instale-o com `python -m pip install PyYAML` se necessário. Não é preciso adicionar PyYAML às dependências de execução do bot apenas para manter essas instruções.

Mantenha a memória compartilhada curta e factual ao longo do tempo: atualize evidências, substitua informações superadas e evite registrar credenciais, dados privados ou conclusões ainda não verificadas. O arquivo da raiz é versionado pelo projeto e não depende da memória automática particular de um cliente.

## 8. Informações relevantes e considerações adicionais

### Privacidade e visibilidade

O fluxo envia os bytes do áudio à OpenAI para transcrição e, depois, o texto bruto para refinamento. O código do bot não implementa armazenamento persistente desses dados; isso não define as políticas de retenção dos serviços externos.

A opção efêmera controla a visibilidade da resposta no Discord, mas o áudio e o texto ainda passam pelas chamadas de processamento. No caminho por menção, a transcrição fica no canal como mensagem comum. Os logs de sucesso desse caminho contêm nomes de exibição; erros podem incluir detalhes fornecidos pelas bibliotecas.

### Qualidade e idioma

Os prompts contextualizam português brasileiro e inglês, sem impor um idioma na chamada de transcrição. Não há avaliação automatizada de qualidade, identificação de falantes ou garantia de preservação exata da fala. Áudio com ruído, falas sobrepostas, nomes próprios e termos técnicos exige atenção na revisão.

### Cache e custos

O refinamento configura uma chave estável e um ponto explícito de cache ao final da instrução de sistema. Isso é uma configuração de requisição ao provedor, não um cache local de áudios ou transcrições. O código não inspeciona métricas de cache; portanto, não há comprovação de acertos nem de economia obtida.

Cada solicitação que chega à etapa de refinamento envolve uma chamada de transcrição e uma de revisão. Não há medição de custo médio no bot. Para estimá-lo, use o gasto observado na conta, o número de solicitações e os dados efetivos de uso, considerando chamadas malsucedidas ou repetidas. Os valores devem ser conferidos na [página oficial de preços](https://developers.openai.com/api/docs/pricing) antes de planejar a operação; este README não fixa uma tabela de preços externos.

### Hospedagem na Discloud

O `discloud.config` versionado declara:

| Campo | Valor |
| --- | --- |
| `NAME` | `Transcribe This` |
| `TYPE` | `bot` |
| `MAIN` | `main.py` |
| `RAM` | `100` |
| `version` | `latest` |

Também há uma URL de avatar no arquivo. Esses valores registram a configuração existente e não comprovam capacidade para determinada carga. Valide o consumo de memória com o tamanho e a concorrência dos áudios esperados, configure as variáveis de ambiente na hospedagem e confira o interpretador disponibilizado: `version=latest` não fixa Python 3.13.3.

### Manutenção e operação

- Para interromper a execução local em primeiro plano, use `Ctrl+C`. Não há gerenciador próprio de reinício ou serviço do sistema incluído.
- Mantenha um único caminho de instalação bem definido. Antes de atualizar dependências, confira os payloads dos serviços e os testes, principalmente os parâmetros de cache.
- A suíte com mocks valida a lógica local, mas um teste manual com áudio não sensível é necessário para comprovar a integração após mudanças em credenciais, modelos, permissões ou hospedagem.
- O repositório não inclui banco de dados, painel web, Dockerfile, pipeline de CI ou monitoramento de produção.

## 9. Licença MIT

O projeto é distribuído sob a [licença MIT](LICENSE), com copyright de **2026 Mateus Barbosa**. É permitido usar, copiar, modificar, distribuir e comercializar o software, mantendo o aviso de copyright e a licença nas cópias ou partes substanciais. O software é fornecido sem garantia, conforme o texto padrão abaixo e o arquivo `LICENSE`.

```text
MIT License

Copyright (c) 2026 Mateus Barbosa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
