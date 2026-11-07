import os
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

os.environ.setdefault("OPENAI_API_KEY", "chave-de-teste")

from config.vars import PROMPT_REFINAMENTO, PROMPT_TRANSCRIBE
from cogs.messages import MessagesCog
from services.refine import RefineService
from services.transcribe import TranscribeService


class ServicosTests(unittest.IsolatedAsyncioTestCase):
    async def test_transcricao_envia_audio_e_contexto(self):
        resposta = SimpleNamespace(text="texto bruto")
        with patch("services.transcribe.client.audio.transcriptions.create", new_callable=AsyncMock, return_value=resposta) as criar:
            resultado = await TranscribeService().transcribe_audio(b"audio", "voz.ogg", "audio/ogg")

        self.assertEqual(resultado, "texto bruto")
        criar.assert_awaited_once_with(
            model="gpt-transcribe", file=("voz.ogg", b"audio", "audio/ogg"), prompt=PROMPT_TRANSCRIBE
        )

    async def test_refinamento_mantem_prefixo_e_chave_estaveis(self):
        resposta = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="Texto revisado."))])
        with patch("services.refine.client.chat.completions.create", new_callable=AsyncMock, return_value=resposta) as criar:
            resultado = await RefineService().refine("texto bruto")

        self.assertEqual(resultado, "Texto revisado.")
        criar.assert_awaited_once_with(
            model="gpt-6-luna", prompt_cache_key="refinamento-transcricao-v1",
            prompt_cache_options={"mode": "explicit"},
            messages=[
                {"role": "system", "content": [{
                    "type": "text", "text": PROMPT_REFINAMENTO,
                    "prompt_cache_breakpoint": {"mode": "explicit"},
                }]},
                {"role": "user", "content": "texto bruto"},
            ],
        )

    async def test_refinamento_vazio_retorna_erro(self):
        resposta = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="  "))])
        with patch("services.refine.client.chat.completions.create", new_callable=AsyncMock, return_value=resposta):
            self.assertEqual(await RefineService().refine("texto"), "Ocorreu um erro na transcrição do áudio.")


class MensagensTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.bot = MagicMock()
        self.cog = MessagesCog(self.bot)

    def test_divisao_preserva_texto_e_limite(self):
        for texto in ("abc " * 1500, "x" * 4500, "a\n" * 1500):
            partes = self.cog._dividir_texto(texto)
            self.assertEqual("".join(partes), texto)
            self.assertTrue(all(0 < len(parte) <= 2000 for parte in partes))

    async def test_fluxo_transcreve_e_refina(self):
        anexo = SimpleNamespace(read=AsyncMock(return_value=b"audio"), filename="a.ogg", content_type=None)
        self.cog.transcribe_service.transcribe_audio = AsyncMock(return_value="bruto")
        self.cog.refine_service.refine = AsyncMock(return_value="refinado")
        self.assertEqual(await self.cog._transcrever_refinar(anexo), "refinado")
        self.cog.transcribe_service.transcribe_audio.assert_awaited_once_with(b"audio", "a.ogg", "audio/ogg")
        self.cog.refine_service.refine.assert_awaited_once_with("bruto")

    async def test_falha_ao_buscar_referencia_recebe_resposta(self):
        self.bot.user = object()
        message = SimpleNamespace(
            author=SimpleNamespace(bot=False), mentions=[self.bot.user],
            reference=SimpleNamespace(resolved=None, message_id=123),
            channel=SimpleNamespace(fetch_message=AsyncMock(side_effect=RuntimeError("falha"))),
            reply=AsyncMock(),
        )
        await self.cog.on_message(message)
        message.reply.assert_awaited_once_with("❌ Ocorreu um erro ao transcrever o áudio.")


if __name__ == "__main__":
    unittest.main()
