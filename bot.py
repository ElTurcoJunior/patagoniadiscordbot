import discord
from discord.ext import tasks
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuración
DISCORD_TOKEN = 'TU_TOKEN_DE_DISCORD'
DISCORD_CHANNEL_ID = TU_ID_DE_CANAL  # Ejemplo: 123456789
# Ruta típica del log en Linux
PZ_CHAT_LOG = '/home/pzserver/Zomboid/Logs/chat.txt'

class ChatBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.last_position = 0

    async def setup_hook(self):
        # Iniciar el loop de verificación del chat
        self.check_chat.start()

    async def on_ready(self):
        print(f'Bot conectado como {self.user}')
        # Establecer la posición inicial del archivo
        if os.path.exists(PZ_CHAT_LOG):
            self.last_position = os.path.getsize(PZ_CHAT_LOG)

    @tasks.loop(seconds=5)  # Verificar cada 5 segundos
    async def check_chat(self):
        if not os.path.exists(PZ_CHAT_LOG):
            return

        try:
            with open(PZ_CHAT_LOG, 'r', encoding='utf-8') as file:
                # Ir a la última posición leída
                file.seek(self.last_position)

                # Leer las nuevas líneas
                new_lines = file.readlines()

                if new_lines:
                    channel = self.get_channel(DISCORD_CHANNEL_ID)

                    for line in new_lines:
                        # Filtrar solo mensajes del chat
                        if "Chat (" in line and "]:" in line:
                            # Formatear el mensaje
                            try:
                                # Ejemplo de línea: "12-31-2023 15:30:55.200 - Chat (General) [Player]: Mensaje"
                                message_parts = line.split("]:", 1)
                                if len(message_parts) == 2:
                                    player_info = message_parts[0].split("(General) [", 1)[1]
                                    message_content = message_parts[1].strip()

                                    formatted_message = f"**{player_info}**: {message_content}"
                                    await channel.send(formatted_message)
                            except Exception as e:
                                print(f"Error al procesar línea: {e}")

                # Actualizar la última posición leída
                self.last_position = file.tell()

        except Exception as e:
            print(f"Error al leer el archivo: {e}")

# Crear instancia del bot y ejecutarlo
bot = ChatBot()
bot.run(DISCORD_TOKEN)
