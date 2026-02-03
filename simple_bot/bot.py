import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv('BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responds to the /start command."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responds to the /help command."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Available commands:\n/start - Start the bot\n/help - Show this help message\n/about - About this bot")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responds to the /about command."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I am a simple Telegram bot built with Python!")

async def python_regex_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responds to messages containing 'python'."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I love Python too! 🐍")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echoes the user message."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

if __name__ == '__main__':
    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(TOKEN).build()

    # Add a handler for the /start command
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    # Add other command handlers
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('about', about_command))

    # Add regex handler (higher priority than echo)
    # This matches any message containing "python" (case-insensitive by default with search, but we use Regex filter)
    # Note: filters.Regex expects a pattern string.
    application.add_handler(MessageHandler(filters.Regex(r"(?i)python"), python_regex_handler))

    # Add a handler for text messages
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(echo_handler)

    # Run the bot until the user presses Ctrl-C
    print("Bot is polling... Press Ctrl+C to stop.")
    application.run_polling()
