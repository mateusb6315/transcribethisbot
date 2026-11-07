---
name: transcribe-discord-flow
description: "Implementar ou corrigir acionamentos, seleção de anexos e entrega de transcrições no Discord deste projeto. Use para mudanças em MessagesCog, menus de contexto, referências, divisão de mensagens e permissões; para payloads dos modelos, use transcribe-ai-services."
---

# Fluxo Discord do Transcribe This

Leia `AGENTS.md` na raiz, `cogs/messages.py` e os testes relacionados antes de alterar o comportamento. Os caminhos de código abaixo são relativos à raiz do repositório.

## Contratos da interface

- O menu **Transcrever áudio** atua na mensagem selecionada e responde de forma efêmera. Reconheça a interação antes de operações demoradas; após `defer`, use follow-ups, sem tentar responder novamente pela resposta inicial.
- O listener exige uma mensagem de usuário, uma menção ao bot e uma referência com ID. O áudio pertence à mensagem referenciada; o resultado público responde à mensagem do solicitante. Mantenha essa distinção nos cabeçalhos e testes.
- Referências podem vir resolvidas ou exigir `fetch_message`. O código aceita como referência resolvida somente um `discord.Message`, não qualquer objeto com atributos semelhantes.
- A seleção atual usa o primeiro anexo com MIME `audio/`. Sem áudio, o menu informa o problema e o listener encerra silenciosamente. Não transforme o fallback interno `audio/ogg` em suporte implícito a anexos sem MIME.
- Preserve `AllowedMentions.none()` em todos os trechos de resultado. Se ampliar o envio para erros ou outros caminhos, teste também a ausência de notificações involuntárias.
- A divisão atual inclui o cabeçalho no limite de 2.000 caracteres e preserva o texto por concatenação. Não introduza `strip()` por trecho, perda de separadores ou partes vazias sem uma decisão explícita sobre a saída.

Esses contratos descrevem o comportamento de referência; podem mudar quando a tarefa pedir, com documentação e testes correspondentes.

## Escolher o ponto da mudança

Mantenha a comunicação Discord no Cog e as chamadas OpenAI nos serviços. Os dois acionamentos compartilham `_transcrever_refinar`; evite duplicar download, transcrição ou refinamento ao adicionar um acionamento.

Ao corrigir robustez, cubra tanto o processamento quanto a entrega: hoje os loops de envio ficam fora do `try`, e o envio da mensagem de erro também pode falhar. Defina como informar entrega parcial sem retranscrever o áudio automaticamente, pois isso pode repetir custos.

Se alterar a seleção de anexos, decida explicitamente a política de MIME, múltiplos arquivos e tamanho antes do download. Se alterar limites de texto, avalie Unicode e entrega real separadamente dos testes de `len()`.

## Validação focada

Use `AsyncMock` para operações aguardadas e mocks compatíveis para gerenciadores de contexto assíncronos, como `channel.typing()`. Para o caminho de referência já resolvida, use um mock com `spec=discord.Message` ou outra construção que satisfaça o `isinstance` real; um `SimpleNamespace` cai no caminho de busca.

Selecione casos conforme a mudança: filtros sem processamento, ausência de áudio, defer efêmero, sucesso em várias partes, referência buscada/resolvida, falha de download e falha na segunda parte do envio. Verifique destinatário, visibilidade e chamadas, não apenas o texto de uma mensagem genérica.

Execute `python -X utf8 -m unittest discover -s tests -v` na raiz. A integração real não é comprovada pelos mocks; registre separadamente qualquer teste manual autorizado. Atualize o fluxo no README e os fatos afetados em MEMORY.md.
