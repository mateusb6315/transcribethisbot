from openrouter import OpenRouter
from config.vars import OPENROUTER_KEY, PROMPT_SISTEMA


class RefineService:
    async def refine(self, transcricao: str) -> str:
        async with OpenRouter(api_key=OPENROUTER_KEY) as op:
            refinamento = await op.chat.send_async(
                model="google/gemma-4-26b-a4b-it:free",
                messages=[
                    {"role": "system", "content": PROMPT_SISTEMA},
                    {"role": "user", "content": transcricao},
                ],
            )

        mensagem_refinada = refinamento.choices[0].message.content
        erro_transcricao = "Ocorreu um erro na transcrição do áudio."

        if mensagem_refinada is not None and mensagem_refinada.strip() != "":
            return mensagem_refinada
        else:
            return erro_transcricao
