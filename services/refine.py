from openai import AsyncOpenAI
from config.vars import OPENAI_API_KEY, PROMPT_SISTEMA

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


class RefineService:
    async def refine(self, transcricao: str) -> str:
        refinamento = await client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA},
                {"role": "user", "content": f"Transcrição bruta: {transcricao}"},
            ],
            temperature=0.2,
            max_completion_tokens=1000,
        )
        return refinamento.choices[0].message.content or ""
