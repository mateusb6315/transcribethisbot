from openai import AsyncOpenAI
from config.vars import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


class TranscribeService:
    async def transcribe_audio(
        self, audio_bytes: bytes, filename: str, content_type: str
    ) -> str:
        transcricao = await client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=(filename, audio_bytes, content_type),
        )
        return transcricao.text
