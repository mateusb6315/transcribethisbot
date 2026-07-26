<div align="center">

# 🎙️ Transcribe This

### Transcrição inteligente de áudios do Discord com IA

*Converte mensagens de voz em texto claro, corrigido e bem formatado — direto no servidor.*

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![discord.py](https://img.shields.io/badge/discord.py-2.7.1-5865F2?style=for-the-badge&logo=discord&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?style=for-the-badge&logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

---

## 1. 📌 Sobre o Projeto

O **Transcribe This** é um bot para **Discord** que converte mensagens de voz e arquivos de áudio em **texto legível e bem estruturado**, utilizando os modelos de Inteligência Artificial da OpenAI.

O bot foi criado para as situações em que ouvir um áudio não é viável — em reuniões, ambientes silenciosos ou sem fones à mão. Ele não apenas transcreve o conteúdo, como também **refina o resultado**, entregando um texto com pontuação correta, boa fluidez e leitura agradável, sem descaracterizar o tom original de quem falou.

O processamento ocorre em **duas etapas de IA**:

1. **Transcrição** — o áudio é convertido em texto bruto.
2. **Refinamento** — o texto bruto é revisado e formatado (pontuação, concordância e ortografia), preservando gírias e o estilo do autor.

O acionamento pode ser feito de **duas formas** dentro do Discord, descritas na seção de funcionamento.

---

## 2. ⚙️ Pré-requisitos

### 🔧 Ambiente
- **Python 3.10 ou superior**.
- **pip** para instalar as dependências.

### 🤖 Aplicação no Discord
1. Crie uma aplicação no [Discord Developer Portal](https://discord.com/developers/applications).
2. Na aba **Bot**, gere o bot e copie o **token** (`DISCORD_TOKEN`).
3. Ative a intent **MESSAGE CONTENT INTENT** — obrigatória para que o bot leia as mensagens e localize os áudios.
4. Em **OAuth2 → URL Generator**, selecione os escopos `bot` e `applications.commands`, gere o link de convite e adicione o bot ao servidor.

### 🔑 Chave da OpenAI
- Uma conta na [OpenAI](https://platform.openai.com/) com acesso à API.
- Uma **API Key** (`OPENAI_API_KEY`). O uso da API é cobrado conforme o consumo.

### 📦 Instalação

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd "transcribe this bot"

# 2. (Recomendado) Crie e ative um ambiente virtual
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt
```

### 🗝️ Variáveis de ambiente

Crie um arquivo **`.env`** na raiz do projeto:

```env
DISCORD_TOKEN=seu_token_do_discord_aqui
OPENAI_API_KEY=sua_chave_da_openai_aqui
```

> ⚠️ O `.env` já está no `.gitignore` e não é versionado. Mantenha as credenciais em sigilo.

### ▶️ Execução

```bash
python main.py
```

Com a configuração correta, o terminal exibe: `Bot online como <nome-do-bot>`.

---

## 3. 🧠 Fluxo do processo de transcrição

Abaixo está a estrutura do projeto e o caminho percorrido por uma mensagem de voz até virar texto refinado.

### 🗂️ Estrutura de pastas

```
transcribe this bot/
├── main.py                 # Ponto de entrada: inicializa o bot e carrega os cogs
├── config/
│   └── vars.py             # Variáveis de ambiente e prompt do sistema
├── cogs/
│   └── messages.py         # Interação com o Discord (comandos e eventos)
├── services/
│   ├── transcribe.py       # Transcrição (áudio → texto bruto)
│   └── refine.py           # Refinamento (texto bruto → texto final)
├── requirements.txt        # Dependências
└── discloud.config         # Configuração de deploy na Discloud
```

O projeto separa responsabilidades com clareza: o `main.py` sobe o bot, os **cogs** cuidam da interação com o Discord e os **services** encapsulam a comunicação com a IA.

---

### 🚀 3.1. Inicialização — `main.py`

Ao executar `python main.py`:

1. As **intents** são configuradas com `message_content = True`, necessário para ler o conteúdo das mensagens.
2. O bot é criado com `commands.Bot`.
3. O código valida o `DISCORD_TOKEN`; se ausente, lança um erro explícito.
4. O `setup_hook()` executa automaticamente:
   - **`carregar_cogs()`** — carrega dinamicamente todo arquivo `.py` da pasta `./cogs` como extensão.
   - **`bot.tree.sync()`** — sincroniza os comandos de aplicação com o Discord.
5. O evento **`on_ready()`** confirma no console que o bot está online.

---

### ⚙️ 3.2. Configuração — `config/vars.py`

Centraliza os itens configuráveis:

- Carrega o `.env` via **`python-dotenv`**.
- Expõe `TOKEN` (`DISCORD_TOKEN`) e `OPENAI_API_KEY`.
- Define o **`PROMPT_SISTEMA`**, que orienta o refinador segundo quatro princípios:
  1. Corrigir pontuação, concordância e erros ortográficos da transcrição.
  2. Dividir textos longos em parágrafos legíveis.
  3. Preservar gírias e o tom original do autor.
  4. Responder apenas com o texto final, sem saudações ou comentários.

---

### 💬 3.3. Interação com o Discord — `cogs/messages.py`

O cog instancia os dois serviços (`TranscribeService` e `RefineService`) e oferece **duas formas de acionamento**:

#### ➤ Forma 1: Menu de Contexto ("Transcrever áudio")
Ao selecionar uma mensagem em **Apps → Transcrever áudio**:

1. O bot busca o primeiro anexo de áudio (`content_type` iniciando com `audio/`).
2. Sem áudio, responde de forma **efêmera**: `❌ Nenhuma mensagem de voz encontrada.`
3. Com áudio, faz um **`defer`** e executa transcrição + refinamento.
4. Envia o resultado de forma **efêmera**, identificando o autor do áudio.

#### ➤ Forma 2: Responder mencionando o bot
Pelo evento **`on_message`**, o bot reage quando **todas** as condições são atendidas:

1. A mensagem não foi enviada por um bot.
2. O bot foi **mencionado**.
3. A mensagem é uma **resposta (reply)** a outra mensagem.

Em seguida, ele localiza a mensagem respondida (via cache ou `fetch_message`), extrai o anexo de áudio e, exibindo o indicador de **"digitando…"**, executa a transcrição. O resultado é publicado como **resposta pública** no canal, em itálico e creditando o autor.

---

### 🔊 3.4. Núcleo da IA — `services/`

O método interno **`_transcrever_refinar()`** encadeia as duas etapas:

```
Áudio (bytes)  →  TranscribeService  →  texto bruto  →  RefineService  →  texto final
```

**`services/transcribe.py` — Transcrição**
- Recebe os bytes do áudio, o nome do arquivo e o `content_type`.
- Chama `audio.transcriptions.create` com o modelo **`gpt-4o-mini-transcribe`** via cliente **`AsyncOpenAI`**.
- Retorna o texto bruto.

**`services/refine.py` — Refinamento**
- Envia o texto bruto ao modelo de chat **`gpt-5.4-mini`**.
- Usa o **`PROMPT_SISTEMA`** como mensagem de sistema e a transcrição como mensagem do usuário.
- Aplica `temperature=0.2` para maior consistência e um limite de tokens de saída.
- Retorna o texto final formatado.

---

### 🔄 3.5. Fluxo completo

```
┌──────────────────────────────────────────────────────────────────────┐
│  1. Usuário aciona o bot (menu de contexto OU reply + menção)          │
│                              ↓                                         │
│  2. cogs/messages.py localiza o anexo de áudio na mensagem             │
│                              ↓                                         │
│  3. Áudio lido em bytes  →  TranscribeService                          │
│         (gpt-4o-mini-transcribe)  →  TEXTO BRUTO                       │
│                              ↓                                         │
│  4. RefineService (gpt-5.4-mini + PROMPT_SISTEMA)  →  TEXTO FINAL       │
│                              ↓                                         │
│  5. O bot responde no Discord com o texto refinado                     │
│         (efêmero no menu de contexto / público no reply)               │
└──────────────────────────────────────────────────────────────────────┘
```

Se alguma etapa falhar, a exceção é capturada e o bot responde com `❌ Ocorreu um erro ao transcrever o áudio.`, evitando travamentos.

---

## 4. 📎 Informações Importantes

- **Intent obrigatória:** o **MESSAGE CONTENT INTENT** precisa estar ativo no Developer Portal, ou o bot não localiza os áudios.
- **Formatos de áudio:** qualquer anexo com `content_type` iniciando em `audio/` é aceito (as mensagens de voz nativas do Discord costumam ser `.ogg`).
- **Custos da API:** transcrição e refinamento consomem créditos da OpenAI; acompanhe o uso na conta.
- **Privacidade:** respostas do menu de contexto são **efêmeras** (visíveis só para quem acionou); respostas via reply + menção são **públicas** no canal.
- **Credenciais:** nunca versione o `.env`. Em caso de vazamento de token, revogue-o e gere um novo.
- **Deploy na Discloud:** o arquivo **`discloud.config`** já define nome, tipo, arquivo principal e RAM para hospedagem na [Discloud](https://discloud.com/). Basta enviar o projeto com o `.env` configurado.
- **Extensibilidade:** novas funcionalidades podem ser adicionadas criando novos arquivos `.py` na pasta `cogs/`, graças ao carregamento dinâmico.
- **Modelos de IA:** `gpt-4o-mini-transcribe` (transcrição) e `gpt-5.4-mini` (refinamento), ajustáveis nos arquivos em `services/`.

---

## 5. 📄 Licença

Distribuído sob a **Licença MIT**, de código aberto e permissiva: é possível **usar, copiar, modificar, distribuir e comercializar** o software, desde que o aviso de copyright e a licença sejam mantidos. O software é fornecido "como está", sem garantias.

Contribuições e adaptações são bem-vindas.

<div align="center">

---

Feito com 🎙️ e ☕ • *Transcribe This*

</div>
