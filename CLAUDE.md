# Transcribe This — continuidade no Claude Code

As instruções comuns de desenvolvimento são importadas do arquivo compartilhado:

@AGENTS.md

Leia também [MEMORY.md](MEMORY.md) ao retomar uma tarefa. Ele registra o estado observado, as reproduções conhecidas e as lacunas de validação. Consulte o [README.md](README.md) para instalação, arquitetura e operação; confirme no código os fatos relevantes à mudança.

## Skills disponíveis

As entradas locais do Claude Code ficam em `.claude/skills/` e carregam os procedimentos canônicos de `.agents/skills/`:

| Skill | Uso |
| --- | --- |
| `/transcribe-discord-flow` | Acionamentos, anexos, referências e respostas Discord. |
| `/transcribe-ai-services` | Transcrição, refinamento, prompts e contratos OpenAI. |
| `/transcribe-validation` | Reprodução de falhas e validação com mocks. |

Leia o arquivo compartilhado indicado pela entrada da skill antes de aplicar seu procedimento. Os caminhos de código nesses procedimentos são relativos à raiz do repositório. Edite a fonte compartilhada quando o procedimento mudar, evitando manter versões diferentes para Claude e Codex.

## Memória e execução

O `MEMORY.md` da raiz é uma memória de projeto versionada e compartilhada pela equipe; ele não depende da memória automática particular do Claude Code. Atualize-o quando houver uma decisão durável, uma mudança no funcionamento ou nova evidência de investigação.

Execute testes a partir da raiz com `python -X utf8 -m unittest discover -s tests -v`. A suíte usa mocks; iniciar `main.py` tem efeitos reais no Discord. Mantenha a distinção entre teste local e integração real ao relatar resultados.
