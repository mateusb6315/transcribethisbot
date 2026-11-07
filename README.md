<div align="center">

# Transcribe This

Bot para transcrever e refinar áudios no Discord.<br>
A Discord bot for transcribing and refining audio.

[Português](#português) · [English](#english)

</div>

---

# Português

O **Transcribe This** transforma mensagens de voz e anexos de áudio do Discord em texto. A transcrição é revisada para melhorar pontuação, ortografia e organização, procurando preservar o conteúdo, o idioma, as gírias e as expressões do locutor.

## Ferramentas usadas

| Ferramenta | Função |
| --- | --- |
| Python 3.13+ | Linguagem e execução do bot. |
| [discord.py](https://discordpy.readthedocs.io/) | Eventos, menu de contexto e comunicação com o Discord. |
| [OpenAI Python SDK](https://github.com/openai/openai-python) | Chamadas assíncronas à API da OpenAI. |
| [gpt-transcribe](https://developers.openai.com/api/docs/models/gpt-transcribe) | Transcrição dos arquivos de áudio. |
| [gpt-6-luna](https://developers.openai.com/api/docs/models/gpt-6-luna) | Refinamento do texto transcrito. |
| python-dotenv | Carregamento das variáveis do arquivo `.env`. |

As versões instaladas via pip estão em `requirements.txt`. O arquivo também inclui dependências legadas, como OpenRouter, que não é usado pelo fluxo atual.

## Instalação

### Pré-requisitos

- Python 3.13 ou superior e pip.
- Uma aplicação e um bot criados no [Discord Developer Portal](https://discord.com/developers/applications).
- Uma chave da [OpenAI Platform](https://platform.openai.com/) com acesso aos modelos e faturamento configurado.

No Discord Developer Portal, ative **Message Content Intent** na página do bot. Na instalação da aplicação, inclua os escopos `bot` e `applications.commands` e conceda permissões para visualizar canais, ler o histórico e enviar mensagens.

### Configuração

Clone o repositório e entre na pasta do projeto:

```bash
git clone <url-do-repositorio>
cd "transcribe this bot"
python -m venv .venv
```

Ative o ambiente virtual:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
source .venv/bin/activate
```

Instale as dependências e crie um arquivo `.env` na raiz:

```bash
pip install -r requirements.txt
```

```env
DISCORD_TOKEN=seu_token_do_discord
OPENAI_API_KEY=sua_chave_da_openai
```

Inicie o bot a partir da raiz do projeto:

```bash
python main.py
```

Quando conectado, o terminal exibirá `Bot online como <nome-do-bot>`. Os testes locais podem ser executados com `python -m unittest discover -s tests -v`.

## Fluxo de operação

Há duas formas de solicitar uma transcrição:

1. Na mensagem com áudio, selecione **Apps → Transcrever áudio**. O resultado é efêmero, visível apenas para quem acionou o comando.
2. Responda à mensagem com áudio mencionando o bot. O resultado é publicado como resposta no canal.

Em ambos os casos, o bot seleciona o primeiro anexo com `content_type` iniciado por `audio/`, baixa o arquivo e executa as duas etapas:

```text
Mensagem com áudio
    ↓
cogs/messages.py — identifica e baixa o anexo
    ↓
services/transcribe.py — gpt-transcribe gera o texto bruto
    ↓
services/refine.py — gpt-6-luna revisa o texto
    ↓
Discord — envia o resultado, dividido quando necessário
```

Os prompts ficam em `config/vars.py`. O prompt de transcrição fornece contexto de conversa informal; o de refinamento solicita correções e preservação do conteúdo e do estilo. O processamento é repetido em cada acionamento, inclusive para um mesmo anexo.

## Prompt caching e custo médio

### Como o cache está configurado

O refinamento usa uma chave estável e um ponto de cache explícito ao final do prompt de sistema. O modo explícito evita criar um ponto de cache automático após a transcrição variável. O cache é gerenciado pela OpenAI e não elimina o envio do prompt nas requisições.

A OpenAI exige um prefixo de pelo menos **1.024 tokens visíveis** para o cache dos modelos GPT-5.6 e posteriores. O prompt fixo atual é menor que esse limite; portanto, **não se espera economia de cache com ele**. A chamada de transcrição não configura um cache equivalente para seu prompt. Não existe cache de resultados de áudio no projeto. Consulte o [guia de prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) para regras, retenção e cobrança atualizadas.

### Estimativa ilustrativa

Valores em dólares americanos, consultados em **7 de novembro de 2026**, para processamento padrão. A OpenAI apresenta `gpt-transcribe` com custo estimado de **US$ 0,0045 por minuto**; para `gpt-6-luna`, informa **US$ 0,10 por milhão de tokens de entrada** e **US$ 0,50 por milhão de tokens de saída**. Consulte os [preços oficiais](https://developers.openai.com/api/docs/pricing), pois podem mudar.

| Hipótese por solicitação | Cálculo | Custo estimado |
| --- | --- | ---: |
| Áudio de 1 minuto | 1 × US$ 0,0045 | US$ 0,0045 |
| Refinamento: 500 tokens de entrada e 500 de saída | (500 × 0,10 + 500 × 0,50) / 1.000.000 | US$ 0,0003 |
| **Total por solicitação** | US$ 0,0045 + US$ 0,0003 | **US$ 0,0048** |
| **1.000 solicitações iguais** | 1.000 × US$ 0,0048 | **US$ 4,80** |

Os 500 tokens de entrada são uma hipótese para o prompt, a transcrição e demais tokens de entrada; os 500 de saída incluem possíveis tokens de raciocínio cobrados. A tabela assume ausência de leituras e gravações de cache cobradas. O valor por minuto de transcrição é uma estimativa, não uma garantia de cobrança fixa. Duração, idioma, conteúdo, tokens efetivos, processamento, taxas e impostos podem alterar o custo. O bot ainda não registra métricas de tokens ou duração, portanto esses números **não são uma média medida do projeto**. Para obter uma média real, divida o gasto observado na OpenAI pelo número de solicitações concluídas no mesmo período.

## Informações importantes

- O áudio é enviado à OpenAI para processamento. Avalie a privacidade e o consentimento antes de usar conteúdo sensível.
- O bot precisa estar online e ter acesso ao canal e à mensagem original. A intent de conteúdo deve estar ativa no portal e no código.
- Uma resposta com menção é pública no canal; a opção do menu de contexto é efêmera.
- Apenas o primeiro anexo identificado como áudio é processado. Formato, tamanho, disponibilidade dos modelos e limites da API podem impedir o processamento; consulte o [guia de transcrição](https://developers.openai.com/api/docs/guides/speech-to-text).
- Resultados podem conter erros ou alterações de sentido; revise transcrições importantes.
- Não versione o `.env` nem compartilhe suas chaves. Revogue credenciais expostas. `OPENROUTER_KEY` permanece como variável legada e não é necessária para o fluxo atual.
- O projeto é distribuído sob a [licença MIT](LICENSE). `discloud.config` contém configuração de hospedagem para a Discloud.

---

# English

**Transcribe This** converts Discord voice messages and audio attachments into text. The transcript is reviewed for punctuation, spelling, and organization while aiming to preserve the speaker's content, language, slang, and expressions.

## Tools used

| Tool | Purpose |
| --- | --- |
| Python 3.13+ | Bot language and runtime. |
| [discord.py](https://discordpy.readthedocs.io/) | Discord events, context menu, and communication. |
| [OpenAI Python SDK](https://github.com/openai/openai-python) | Asynchronous calls to the OpenAI API. |
| [gpt-transcribe](https://developers.openai.com/api/docs/models/gpt-transcribe) | Audio file transcription. |
| [gpt-6-luna](https://developers.openai.com/api/docs/models/gpt-6-luna) | Transcript refinement. |
| python-dotenv | Loads environment variables from `.env`. |

Versions installed with pip are listed in `requirements.txt`. The file also includes legacy dependencies, such as OpenRouter, which is not used by the current workflow.

## Installation

### Requirements

- Python 3.13 or later and pip.
- An application and bot created in the [Discord Developer Portal](https://discord.com/developers/applications).
- An [OpenAI Platform](https://platform.openai.com/) API key with access to the models and billing configured.

In the Discord Developer Portal, enable **Message Content Intent** on the bot page. When installing the application, include the `bot` and `applications.commands` scopes and grant permission to view channels, read message history, and send messages.

### Setup

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd "transcribe this bot"
python -m venv .venv
```

Activate the virtual environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
source .venv/bin/activate
```

Install dependencies and create a `.env` file in the project root:

```bash
pip install -r requirements.txt
```

```env
DISCORD_TOKEN=your_discord_token
OPENAI_API_KEY=your_openai_api_key
```

Start the bot from the project root:

```bash
python main.py
```

Once connected, the terminal displays `Bot online como <bot-name>`. Run local tests with `python -m unittest discover -s tests -v`.

## How it works

There are two ways to request a transcript:

1. On a message containing audio, select **Apps → Transcrever áudio**. The result is ephemeral and visible only to the person who invoked the command.
2. Reply to a message containing audio and mention the bot. The result is posted as a reply in the channel.

In both cases, the bot selects the first attachment whose `content_type` starts with `audio/`, downloads it, and performs two steps:

```text
Message containing audio
    ↓
cogs/messages.py — finds and downloads the attachment
    ↓
services/transcribe.py — gpt-transcribe produces a raw transcript
    ↓
services/refine.py — gpt-6-luna reviews the text
    ↓
Discord — sends the result, split into parts when necessary
```

The prompts are in `config/vars.py`. The transcription prompt provides informal conversation context; the refinement prompt requests corrections while preserving content and style. Each invocation repeats processing, including requests for the same attachment.

## Prompt caching and average cost

### Cache configuration

Refinement uses a stable key and an explicit cache breakpoint at the end of the system prompt. Explicit mode avoids automatically creating a cache breakpoint after the variable transcript. OpenAI manages the cache, and requests still send the prompt.

OpenAI requires a prefix of at least **1,024 visible tokens** to cache GPT-5.6 and later models. The current fixed prompt is shorter than this threshold, so **no cache savings are expected for it**. The transcription call does not configure an equivalent prompt cache. The project does not cache audio results. See the [prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching) for current rules, retention, and pricing.

### Illustrative estimate

Prices are in US dollars, checked on **November 7, 2026**, for standard processing. OpenAI lists `gpt-transcribe` at an estimated **$0.0045 per minute**; for `gpt-6-luna`, it lists **$0.10 per million input tokens** and **$0.50 per million output tokens**. Check [official pricing](https://developers.openai.com/api/docs/pricing), as rates can change.

| Assumption per request | Calculation | Estimated cost |
| --- | --- | ---: |
| 1 minute of audio | 1 × $0.0045 | $0.0045 |
| Refinement: 500 input and 500 output tokens | (500 × 0.10 + 500 × 0.50) / 1,000,000 | $0.0003 |
| **Total per request** | $0.0045 + $0.0003 | **$0.0048** |
| **1,000 identical requests** | 1,000 × $0.0048 | **$4.80** |

The 500 input tokens are an assumption covering the prompt, transcript, and other input tokens; the 500 output tokens include any billable reasoning tokens. The table assumes no billable cache reads or writes. The transcription price per minute is an estimate, not a guaranteed fixed charge. Duration, language, content, actual token counts, processing, fees, and taxes can change the cost. The bot does not currently record token or duration metrics, so these figures **are not a measured project average**. For a real average, divide observed OpenAI spending by the number of completed requests in the same period.

## Important information

- Audio is sent to OpenAI for processing. Consider privacy and consent before using sensitive content.
- The bot must be online and able to access the channel and original message. The message content intent must be enabled in the portal and in the code.
- A reply mentioning the bot is public in the channel; the context-menu response is ephemeral.
- Only the first attachment identified as audio is processed. Format, size, model availability, and API limits can prevent processing; see the [transcription guide](https://developers.openai.com/api/docs/guides/speech-to-text).
- Results may contain errors or changes in meaning; review important transcripts.
- Do not commit `.env` or share your keys. Revoke exposed credentials. `OPENROUTER_KEY` remains a legacy variable and is not required by the current workflow.
- The project is distributed under the [MIT license](LICENSE). `discloud.config` contains Discloud hosting configuration.
