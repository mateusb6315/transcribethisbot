import os

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

PROMPT_REFINAMENTO = (
    "Corrija pontuação e erros ortográficos evidentes e organize em parágrafos "
    "quando necessário. Preserve o sentido, os detalhes, o idioma, as gírias e "
    "os palavrões, sem censura ou formalização. Retorne apenas o texto revisado."
)

PROMPT_TRANSCRIBE = (
    "Áudio de conversa informal, possivelmente com gírias e palavrões em "
    "português brasileiro ou inglês."
)
