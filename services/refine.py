from openai import AsyncOpenAI
from config.vars import OPENAI_API_KEY, PROMPT_REFINAMENTO

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


class RefineService:
    async def refine(self, transcricao: str) -> str:
        refinamento = await client.chat.completions.create(
            model="gpt-6-luna",
            prompt_cache_key="refinamento-transcricao-v1",
            prompt_cache_options={"mode": "explicit"},
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": PROMPT_REFINAMENTO,
                            "prompt_cache_breakpoint": {"mode": "explicit"},
                        }
                    ],
                },
                {"role": "user", "content": transcricao},
            ],
        )

        mensagem_refinada = refinamento.choices[0].message.content
        erro_transcricao = "Ocorreu um erro na transcrição do áudio."

        if mensagem_refinada is not None and mensagem_refinada.strip() != "":
            return mensagem_refinada
        else:
            return erro_transcricao
