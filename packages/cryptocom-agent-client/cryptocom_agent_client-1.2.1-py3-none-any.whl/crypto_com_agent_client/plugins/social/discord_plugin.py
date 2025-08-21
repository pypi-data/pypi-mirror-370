# Third-party imports
import logging
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


class DiscordPlugin:
    """
    A Discord bot plugin that handles user interactions and forwards messages to an AI agent.

    Features:
        - Handles incoming text messages and forwards them to the AI agent.
        - Supports a command handler (`!start`) to initiate interaction.
        - Implements error handling to prevent bot crashes.
        - Splits long responses exceeding Discord's 2000-character limit.
    """

    def __init__(self, bot_token: str, agent):
        """
        Initializes the Discord bot plugin and sets up message handlers.

        Args:
            bot_token (str): The Discord bot token used for authentication.
            agent (Agent): The AI agent that processes user messages and generates responses.
        """
        self.agent = agent
        self.bot_token = bot_token

        intents = discord.Intents.default()
        intents.message_content = True

        self.bot = commands.Bot(command_prefix="!", intents=intents)

        # Register handlers
        @self.bot.event
        async def on_ready():
            logger.info(f"Discord bot is ready: {self.bot.user}")

        @self.bot.command(name="start")
        async def start(ctx):
            """
            Handles the !start command and sends a welcome message.
            """
            try:
                await ctx.send(
                    "Hello! I am your Crypto.com AI Agent. Send me a message to interact!"
                )
            except Exception as e:
                logger.error(f"[DiscordPlugin/start] - Error: {e}")
                await ctx.send("An error occurred. Please try again.")

        @self.bot.event
        async def on_message(message):
            """
            Handles incoming messages and routes them to the agent.
            """
            if message.author == self.bot.user:
                return

            try:
                user_message = message.content
                chat_id = message.channel.id
                response = self.agent.interact(user_message, thread_id=chat_id)

                # Discord limit is 2000 characters
                MAX_MESSAGE_LENGTH = 2000
                if len(response) > MAX_MESSAGE_LENGTH:
                    for i in range(0, len(response), MAX_MESSAGE_LENGTH):
                        await message.channel.send(response[i : i + MAX_MESSAGE_LENGTH])
                else:
                    await message.channel.send(response)

            except Exception as e:
                logger.error(f"[DiscordPlugin/on_message] - Error: {e}")
                await message.channel.send(
                    "An error occurred while processing your request."
                )

            await self.bot.process_commands(message)

    def run(self):
        """Starts the Discord bot."""
        logger.info("Starting Discord bot...")
        self.bot.run(self.bot_token)
