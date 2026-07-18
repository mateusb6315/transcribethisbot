import discord
from discord import app_commands
from discord.ext import commands
from services.transcribe import TranscribeService
from services.refine import RefineService


class MessagesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.transcribe_service = TranscribeService()
        self.refine_service = RefineService()
        self.ctx_menu = app_commands.ContextMenu(
            name="Transcrever áudio",
            callback=self.transcrever,
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def cog_unload(self):
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

    def _extrair_audio(self, message: discord.Message):
        for anexo in message.attachments:
            if anexo.content_type and anexo.content_type.startswith("audio/"):
                return anexo
        return None

    async def _transcrever_refinar(self, anexo: discord.Attachment) -> str:
        arquivo_audio = await anexo.read()
        transcricao = await self.transcribe_service.transcribe_audio(
            arquivo_audio, anexo.filename, anexo.content_type or "audio/ogg"
        )
        return await self.refine_service.refine(transcricao)

    async def transcrever(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        anexo = self._extrair_audio(message)
        if not anexo:
            await interaction.response.send_message(
                "❌ Nenhuma mensagem de voz encontrada.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)
        try:
            texto = await self._transcrever_refinar(anexo)
        except Exception:
            await interaction.followup.send(
                "❌ Ocorreu um erro ao transcrever o áudio.", ephemeral=True
            )
            return

        await interaction.followup.send(
            content=f"📝 Áudio de {message.author.display_name}\n{texto}",
            ephemeral=True,
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if self.bot.user not in message.mentions:
            return
        if message.reference is None or message.reference.message_id is None:
            return

        referencia = message.reference.resolved
        if not isinstance(referencia, discord.Message):
            referencia = await message.channel.fetch_message(
                message.reference.message_id
            )

        anexo = self._extrair_audio(referencia)
        if not anexo:
            return

        try:
            async with message.channel.typing():
                texto = await self._transcrever_refinar(anexo)
        except Exception:
            await message.reply("❌ Ocorreu um erro ao transcrever o áudio.")
            return

        await message.reply(
            f"""🎙️ Áudio de **{referencia.author.display_name}**:\n\n*{texto}*"""
        )


async def setup(bot):
    await bot.add_cog(MessagesCog(bot))
