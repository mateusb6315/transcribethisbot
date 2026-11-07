---
name: transcribe-validation
description: "Reproduzir bugs e validar mudanças do Transcribe This com unittest, mocks assíncronos e diagnóstico de ambiente Windows. Use ao investigar falhas, ampliar cobertura ou verificar uma alteração funcional; não exige chamadas reais ao Discord ou à OpenAI."
---

# Validação do Transcribe This

Leia o diff da tarefa e `tests/test_fluxo.py`; use `MEMORY.md` para comparar com a última evidência, não como garantia do estado atual. Execute comandos na raiz do repositório, usando o interpretador do ambiente virtual.

## Executar a suíte

Com o ambiente ativado:

```bash
python -X utf8 -m unittest discover -s tests -v
```

Sem ativação no Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -v
```

No Linux/macOS, use `.venv/bin/python` no lugar do executável Windows.

A referência inicial é de seis testes passando em Python 3.13.3 com UTF-8. `tests/test_fluxo.py` define uma chave fictícia quando necessário e simula chamadas OpenAI; não são necessários token Discord nem chave real para a suíte. Em novos testes, defina a chave fictícia antes da importação dos serviços, pois os clientes são criados nesse momento. Não sobrescreva uma credencial real para executar chamadas externas com ela por engano; mantenha as chamadas sob mocks.

## Distinguir bug, ambiente e limite de cobertura

- `UnicodeEncodeError` ao imprimir `❌` em `cp1252`: bug conhecido nos logs. `-X utf8` é um contorno de execução, não uma correção do código. Se corrigir o logging, reproduza com uma saída restrita, como `io.TextIOWrapper` sobre `io.BytesIO` com `encoding="cp1252"`, e verifique se a resposta de erro continua ocorrendo.
- Travamento antes do corpo do primeiro teste: nesta sessão, a criação do loop assíncrono no sandbox Windows bloqueou em `socket._fallback_socketpair`/`accept`. Uma execução fora daquela restrição passou. Em outro ambiente, obtenha a pilha com `faulthandler.dump_traceback_later` e prazo finito antes de atribuir a falha ao projeto. Use o mecanismo de permissões do ambiente somente se necessário; isso não é uma exigência de execução do bot.
- Falha de importação: confira o interpretador, dependências instaladas e momento da configuração da chave fictícia. Não inicie o bot para resolver testes unitários.
- Suíte verde: comprova apenas os cenários simulados; não prova permissões do Discord, acesso aos modelos, custo, cache remoto ou aceitação de um arquivo real.

## Ampliar testes com propósito

Escolha casos pelo comportamento alterado. Preserve o isolamento: `AsyncMock` para métodos aguardados, `MagicMock` para operações síncronas e objetos de resposta com os atributos realmente consumidos. Faça patch no namespace usado pelo código, não em um símbolo equivalente que o consumidor não usa.

Para falhas de interface, verifique se a resposta correta é tentada e se a API de IA não é chamada quando os filtros rejeitam a mensagem. Para divisão de texto, teste preservação, limites e ausência de partes vazias. Para serviços, verifique payload e retorno sem fazer requisições reais.

Não crie testes que apenas copiem headings da documentação ou detalhes privados de implementação. Mudanças só de documentação pedem revisão de links, exemplos e consistência; repetir a suíte é opcional se ela já foi executada sobre o mesmo código.

## Registrar o resultado

Informe comando, interpretador, resultado e limite da verificação. Atualize `MEMORY.md` quando surgir uma reprodução ou mudança durável; não grave logs integrais nem segredos. Se o comportamento público mudar, ajuste o README. Antes de um commit autorizado, execute `git diff --check` e confira os caminhos staged, preservando alterações anteriores que não pertençam à tarefa.
