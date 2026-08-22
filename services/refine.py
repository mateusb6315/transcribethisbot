from openai import OpenAI
from config.vars import OPENAI_API_KEY, PROMPT_REFINAMENTO

client = OpenAI(api_key=OPENAI_API_KEY)


class RefineService:
    async def refine(self, transcricao: str) -> str:
        refinamento = client.chat.completions.create(
            model="gpt-5.6-luna",
            messages=[
                {"role": "system", "content": PROMPT_REFINAMENTO},
                {"role": "user", "content": transcricao},
            ],
        )

        mensagem_refinada = refinamento.choices[0].message.content
        erro_transcricao = "Ocorreu um erro na transcrição do áudio."

        if mensagem_refinada is not None and mensagem_refinada.strip() != "":
            return mensagem_refinada
        else:
            return erro_transcricao
