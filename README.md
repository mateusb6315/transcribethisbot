<div align="center">

# Transcribe This

### Bot de transcrição e refinamento de áudios para Discord

O Transcribe This converte mensagens de voz e arquivos de áudio enviados no Discord em texto claro, revisado e bem estruturado.

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![discord.py](https://img.shields.io/badge/discord.py-2.7.1-5865F2?style=for-the-badge&logo=discord&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?style=for-the-badge&logo=openai&logoColor=white)
![OpenRouter](https://img.shields.io/badge/OpenRouter-API-111827?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

---

## 1. Sobre o projeto

O **Transcribe This** é um bot para **Discord** que utiliza serviços de Inteligência Artificial para transformar mensagens de voz e anexos de áudio em texto legível.

O projeto é útil quando ouvir um áudio não é conveniente ou possível, como em reuniões, ambientes silenciosos ou situações sem acesso a fones de ouvido. Além de transcrever o conteúdo, o bot refina o texto para melhorar pontuação, ortografia e organização, preservando o sentido, as gírias e o tom original da fala.

O processamento é dividido em duas etapas:

1. **Transcrição**: o áudio é convertido em texto bruto pela API da OpenAI.
2. **Refinamento**: a transcrição é revisada e formatada por um modelo disponibilizado através do OpenRouter.

O usuário pode iniciar esse processo pelo menu de contexto de uma mensagem ou respondendo a uma mensagem de áudio com uma menção ao bot.

## 2. Pré-requisitos

### Ambiente

- **Python 3.13 ou superior**, conforme definido no `pyproject.toml`.
- **pip** ou **Poetry** para instalação das dependências.

### Aplicação no Discord

1. Crie uma aplicação no [Discord Developer Portal](https://discord.com/developers/applications).
2. Na aba **Bot**, crie o bot e copie o token (`DISCORD_TOKEN`).
3. Ative a intent **MESSAGE CONTENT INTENT**, necessária para que o bot processe mensagens e menções.
4. Em **OAuth2 → URL Generator**, selecione os escopos `bot` e `applications.commands`.
5. Conceda ao bot permissões para visualizar mensagens, ler o histórico, enviar mensagens e responder a interações.

### Serviços de IA

O projeto depende de duas credenciais:

- Uma chave da [OpenAI Platform](https://platform.openai.com/) (`OPENAI_API_KEY`), usada para transcrição de áudio.
- Uma chave do [OpenRouter](https://openrouter.ai/) (`OPENROUTER_KEY`), usada para o refinamento do texto.

O uso desses serviços pode gerar custos ou estar sujeito a limites definidos pelos respectivos provedores.

### Instalação

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd "transcribe this bot"

# 2. Crie e ative um ambiente virtual (recomendado)
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt
```

Como alternativa, o projeto também possui configuração para Poetry:

```bash
poetry install
```

### Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
DISCORD_TOKEN=seu_token_do_discord_aqui
OPENAI_API_KEY=sua_chave_da_openai_aqui
OPENROUTER_KEY=sua_chave_do_openrouter_aqui
```

O arquivo `.env` não deve ser versionado. Mantenha todas as credenciais em sigilo e revogue imediatamente qualquer chave exposta.

### Execução

```bash
python main.py
```

Quando a configuração estiver correta, o terminal exibirá uma mensagem semelhante a:

```text
Bot online como <nome-do-bot>
```

## 3. Fluxo do processo de transcrição

A estrutura do projeto separa a inicialização do bot, a interação com o Discord e a comunicação com os serviços de IA.

### Estrutura de pastas

```text
transcribe this bot/
├── main.py                 # Ponto de entrada e inicialização do bot
├── config/
│   └── vars.py             # Variáveis de ambiente e prompt do sistema
├── cogs/
│   └── messages.py         # Comandos, eventos e respostas no Discord
├── services/
│   ├── transcribe.py       # Transcrição de áudio para texto bruto
│   └── refine.py           # Refinamento do texto transcrito
├── requirements.txt        # Dependências para instalação via pip
├── pyproject.toml          # Metadados e configuração do Poetry
└── discloud.config         # Configuração de deploy na Discloud
```

O carregamento dos cogs é dinâmico: arquivos Python adicionados à pasta `cogs/` podem ser carregados durante a inicialização, desde que implementem a estrutura esperada pelo `discord.py`.

### 3.1. Inicialização — `main.py`

Ao executar `python main.py`:

1. As intents padrão são configuradas e `message_content` é habilitada.
2. Uma instância de `commands.Bot` é criada.
3. O código verifica se `DISCORD_TOKEN` foi configurado.
4. O `setup_hook()` carrega os arquivos da pasta `cogs/` e sincroniza os comandos de aplicação com o Discord.
5. O evento `on_ready()` confirma no terminal que o bot está conectado.

### 3.2. Configuração — `config/vars.py`

Esse módulo carrega o arquivo `.env` e disponibiliza:

- `TOKEN`, obtido de `DISCORD_TOKEN`;
- `OPENAI_API_KEY`, usada pelo cliente assíncrono da OpenAI;
- `OPENROUTER_KEY`, usada pelo cliente do OpenRouter;
- `PROMPT_SISTEMA`, que define as regras de refinamento da transcrição.

O prompt orienta o modelo a corrigir pontuação, concordância e erros ortográficos, dividir textos longos em parágrafos e preservar gírias, expressões coloquiais, termos ofensivos e o estilo original. A resposta deve conter somente o texto refinado.

### 3.3. Interação com o Discord — `cogs/messages.py`

O cog `MessagesCog` instancia os serviços de transcrição e refinamento e disponibiliza duas formas de acionamento.

#### Menu de contexto — “Transcrever áudio”

Ao selecionar uma mensagem e acessar **Apps → Transcrever áudio**:

1. O bot procura o primeiro anexo cujo `content_type` começa com `audio/`.
2. Se nenhum áudio for encontrado, envia uma resposta efêmera informando o problema.
3. Se houver áudio, a interação é adiada enquanto o processamento é executado.
4. O bot baixa o anexo, realiza as duas etapas de IA e envia o resultado de forma efêmera, identificando o autor do áudio.

#### Resposta com menção ao bot

O bot também processa uma mensagem quando todas as condições abaixo são atendidas:

1. A mensagem não foi enviada por outro bot.
2. O bot foi mencionado.
3. A mensagem é uma resposta a outra mensagem.
4. A mensagem respondida contém um anexo de áudio.

Nesse fluxo, a mensagem referenciada é obtida do cache ou buscada no canal. Durante o processamento, o bot exibe o indicador de digitação e publica a transcrição refinada como resposta no canal.

### 3.4. Núcleo da IA — `services/`

O método `_transcrever_refinar()` coordena as duas etapas:

```text
Áudio (bytes)
    ↓
TranscribeService — OpenAI / whisper-1
    ↓
Texto bruto
    ↓
RefineService — OpenRouter / google/gemma-4-26b-a4b-it:free
    ↓
Texto refinado
```

#### `services/transcribe.py` — transcrição

O serviço recebe os bytes do áudio, o nome do arquivo e o tipo MIME. Em seguida, envia o arquivo ao endpoint de transcrição da OpenAI utilizando o modelo `whisper-1` e retorna o texto produzido.

#### `services/refine.py` — refinamento

O serviço envia a transcrição ao modelo `google/gemma-4-26b-a4b-it:free` por meio do OpenRouter. O prompt do sistema orienta a revisão do texto sem modificar seu conteúdo ou estilo. Caso o modelo não retorne um texto válido, o serviço informa que ocorreu um erro na transcrição.

### 3.5. Fluxo completo

```text
1. O usuário aciona o bot pelo menu de contexto ou por reply + menção
                              ↓
2. messages.py localiza o anexo de áudio
                              ↓
3. O anexo é baixado como bytes
                              ↓
4. A OpenAI gera o texto bruto com whisper-1
                              ↓
5. O OpenRouter refina o texto com o modelo Gemma
                              ↓
6. O bot envia o resultado no Discord
```

Exceções durante o processamento são capturadas pelo cog. Nesses casos, o erro é registrado no terminal e o usuário recebe uma mensagem informando que a transcrição não pôde ser concluída.

## 4. Informações importantes

- A intent **MESSAGE CONTENT INTENT** deve estar habilitada no Developer Portal e no código do bot.
- São aceitos anexos cujo `content_type` começa com `audio/`. Mensagens de voz nativas do Discord normalmente utilizam o formato OGG.
- O fluxo pelo menu de contexto gera uma resposta efêmera, visível apenas para quem o acionou.
- O fluxo por reply e menção publica a resposta no canal.
- A transcrição e o refinamento dependem de serviços externos e podem sofrer limitações de disponibilidade, cota ou custo.
- O conteúdo do áudio é enviado aos provedores configurados para processamento. Avalie requisitos de privacidade antes de utilizar o bot em canais com informações sensíveis.
- Nunca versione o arquivo `.env`. Em caso de vazamento de credenciais, revogue as chaves e gere novas imediatamente.
- O arquivo `discloud.config` contém parâmetros básicos para hospedagem na Discloud.
- Novas funcionalidades podem ser adicionadas como cogs na pasta `cogs/`.
- Os modelos podem ser alterados nos arquivos `services/transcribe.py` e `services/refine.py`, desde que as APIs e os formatos de requisição permaneçam compatíveis.

## 5. Licença

Este projeto é distribuído sob a **Licença MIT**. É permitido usar, copiar, modificar, distribuir e comercializar o software, desde que o aviso de copyright e o texto da licença sejam mantidos.

O software é fornecido “como está”, sem garantias expressas ou implícitas.

