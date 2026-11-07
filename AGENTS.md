# Instruções de desenvolvimento

Estas instruções se aplicam ao repositório inteiro. Instruções específicas em subdiretórios devem ser consideradas ao trabalhar neles. As solicitações do usuário definem o escopo da tarefa.

## Retomar o contexto

Leia [MEMORY.md](MEMORY.md) para o estado verificado e as pendências, e as seções pertinentes do [README.md](README.md) para requisitos e funcionamento. Confirme os fatos nos módulos e no diff atual antes de alterar código: a memória é um registro datado, não substitui a implementação.

O projeto é um bot Discord assíncrono em Python. A instalação padrão usa `requirements.txt`; Python 3.13 é a referência atual. Não há etapa Node/npm. `poetry.lock` existe, mas `pyproject.toml` está ignorado e não acompanha o clone.

## Onde trabalhar

| Área | Arquivo |
| --- | --- |
| Inicialização, intents, extensões e sincronização | `main.py` |
| Ambiente e prompts | `config/vars.py` |
| Acionamentos, anexos, orquestração e respostas Discord | `cogs/messages.py` |
| Áudio para texto bruto | `services/transcribe.py` |
| Texto bruto para revisão | `services/refine.py` |
| Testes locais com mocks | `tests/test_fluxo.py` |

Mantenha as chamadas OpenAI nos serviços e a comunicação Discord no Cog. Preserve os métodos assíncronos nas operações de I/O. Use a linguagem e as convenções do módulo existente; mensagens ao usuário e documentação são predominantemente em português.

## Contratos que exigem atenção

- O menu de contexto responde de forma efêmera; a resposta com menção publica no canal e exige referência a outra mensagem.
- O áudio vem da mensagem selecionada/referenciada, não necessariamente da mensagem do solicitante.
- Apenas o primeiro anexo com MIME `audio/` é selecionado. O fallback interno de MIME não aceita anexos sem MIME na interface pública.
- Ambos os acionamentos compartilham `_transcrever_refinar`. Não duplique o pipeline para corrigir apenas uma entrada.
- Preserve a desativação de menções nos resultados e a divisão incluindo o cabeçalho no limite de 2.000 caracteres, sem perda de texto.
- Os clientes OpenAI são criados na importação dos serviços. Os testes precisam configurar uma chave fictícia antes dessas importações e simular as chamadas.
- O cache de prompt configurado não é cache local de transcrições. Não afirme economia ou disponibilidade remota apenas porque os mocks passaram.

Esses pontos descrevem o comportamento atual; mudanças solicitadas podem redefini-los, com testes e documentação correspondentes. Problemas registrados em MEMORY.md não autorizam correções fora do escopo da tarefa.

## Skills do projeto

Use a skill pertinente quando a tarefa se enquadrar na descrição; não é necessário carregar todas:

- [transcribe-discord-flow](.agents/skills/transcribe-discord-flow/SKILL.md): acionamentos, anexos, referências e entrega no Discord.
- [transcribe-ai-services](.agents/skills/transcribe-ai-services/SKILL.md): contratos de transcrição/refinamento, prompts e parâmetros OpenAI.
- [transcribe-validation](.agents/skills/transcribe-validation/SKILL.md): reprodução de bugs, testes assíncronos e diagnóstico do ambiente.

Os procedimentos canônicos ficam em `.agents/skills/`. As entradas em `.claude/skills/` apontam para os mesmos arquivos; evite copiar o corpo das instruções. Ao renomear uma skill, atualize os links e as duas entradas de descoberta.

## Verificação

Execute a partir da raiz com o ambiente virtual ativado:

```bash
python -X utf8 -m unittest discover -s tests -v
git diff --check
```

No Windows sem ativação, use `.\.venv\Scripts\python.exe`; no Linux/macOS, `.venv/bin/python`. UTF-8 contorna um bug conhecido dos logs com emojis em terminais `cp1252`. Não descreva esse contorno como uma correção no código.

Para mudanças funcionais, acrescente testes dos resultados observáveis afetados. Não há formatter, linter ou CI configurados no repositório. Mocks não comprovam integração remota. Para documentação, confira exemplos, links e consistência com o código; não é necessário criar testes que repliquem o texto.

`python -X utf8 main.py` inicia uma sessão real, autentica no Discord e sincroniza comandos; não o use como simples teste de importação. Testes reais devem estar dentro da autorização da tarefa e utilizar conteúdo não sensível.

## Credenciais, Git e continuidade

Não leia nem exponha valores de `.env` sem necessidade da tarefa; nunca inclua credenciais, áudios privados ou logs sensíveis em commits. Não versione `.venv`, caches ou arquivos locais ignorados como efeito colateral.

Antes de editar ou fazer staging, confira `git status` e preserve mudanças preexistentes. Use caminhos explícitos no `git add`. Faça commit e push quando solicitados, respeitando a autorização existente; não use force push para contornar divergência do remoto.

Quando mudar comportamento, requisitos ou decisões duráveis, atualize README.md e MEMORY.md no mesmo trabalho. Na memória, registre data, evidência, resultado dos testes e pendências reais. Remova fatos superados; não mantenha transcrições de conversa nem invente testes ou deploys concluídos.
