---
name: transcribe-ai-services
description: "Alterar ou diagnosticar transcrição, refinamento, prompts, configuração OpenAI e parâmetros de cache do Transcribe This. Use para os serviços de IA e seus contratos com o Cog; não para mudanças apenas na apresentação de mensagens do Discord."
---

# Serviços de IA do Transcribe This

Leia `services/transcribe.py`, `services/refine.py`, `config/vars.py` e os testes relacionados. Os caminhos de código são relativos à raiz do repositório. Use README.md para a arquitetura e MEMORY.md para o estado verificado; confira os fatos no código antes de decidir.

## Contratos atuais

- `TranscribeService.transcribe_audio(bytes, filename, content_type)` usa `audio.transcriptions.create`, modelo `gpt-transcribe`, arquivo `(filename, bytes, content_type)` e `PROMPT_TRANSCRIBE`. Retorna `.text`.
- `RefineService.refine(str)` usa `chat.completions.create`, modelo `gpt-6-luna`, instrução de sistema e transcrição como conteúdo de usuário. Retorna `choices[0].message.content` quando há texto não vazio.
- O refinamento configura `prompt_cache_key="refinamento-transcricao-v1"`, modo explícito e breakpoint no bloco do prompt de sistema. Isso não é cache de resultados de áudio nem evidência de economia.
- Cada módulo cria seu próprio `AsyncOpenAI` na importação. Configure uma chave fictícia antes de importar em testes isolados e substitua chamadas no módulo consumidor.
- Refinamento vazio retorna uma frase de erro como string; exceções sobem ao Cog. Uma falha no refinamento não devolve a transcrição bruta atualmente.

Não migre endpoint, modelo, provedor ou estratégia de cache como efeito colateral de uma correção não relacionada. Se a tarefa pedir a mudança, atualize contratos, testes e documentação em conjunto.

## Implementação e investigação

Antes de mudar argumentos de API, inspecione a assinatura e os tipos do SDK instalado e as versões em `requirements.txt`. Consulte a documentação oficial atual quando a mudança depender de suporte remoto, limites ou disponibilidade do modelo. Os mocks confirmam o payload local; não validam aceitação pelo servidor. Não renomeie modelos apenas por uma suposição sobre disponibilidade.

Preserve nos prompts a revisão fiel ao idioma, sentido e estilo, sem resumo ou formalização, a menos que a tarefa redefina o produto. Use transcrições sintéticas como exemplos; não copie dados privados para testes ou memória versionada.

Para tratamento de erros, escolha explicitamente entre lançar exceção, retornar resultado estruturado ou oferecer texto bruto. Verifique todos os consumidores antes de alterar o retorno `str`. Não confunda ausência de conteúdo, `choices` vazio e falha de rede.

Se a tarefa envolver custo ou latência, diferencie repetições do SDK de novas tentativas do fluxo completo. A etapa de transcrição pode já ter gerado custo antes de o refinamento falhar. Não adicione retries ilimitados nem prolongue prompts apenas para tentar obter cache. Métricas devem evitar registrar conteúdo e credenciais.

`OPENROUTER_KEY` e a biblioteca OpenRouter são legados; o fluxo atual usa OpenAI diretamente. Alterações de dependências devem considerar `requirements.txt`, o lockfile e a ausência de `pyproject.toml` versionado, sem introduzir esse manifesto incidentalmente.

## Validação focada

Substitua as chamadas em `services.transcribe.client.audio.transcriptions.create` e `services.refine.client.chat.completions.create` com `AsyncMock`. Verifique os argumentos afetados e resultados observáveis: texto válido, conteúdo ausente/vazio, resposta inesperada e propagação de erro, conforme o escopo.

Execute `python -X utf8 -m unittest discover -s tests -v`. Não inicie `main.py` para testar payloads: ele autentica no Discord e sincroniza comandos. Uma chamada real deve ter autorização de uso do serviço; se já fornecida pela tarefa, prossiga dentro dela. Reporte validação com mocks e validação remota separadamente e atualize README.md e MEMORY.md quando os contratos mudarem.
