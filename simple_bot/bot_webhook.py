import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from db import init_db, save_user

# Load environment variables
load_dotenv()

# Configure logging to both file and console
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# File Handler
file_handler = logging.FileHandler('bot.log')
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

# Get root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

logger = logging.getLogger(__name__)

TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL') # e.g. https://xxxx.ngrok-free.app
PORT = int(os.getenv('PORT', '8443'))

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    # Notify the user
    if isinstance(update, Update) and update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ An internal error occurred. Our developers have been notified."
        )

# Define states for the ConversationHandler
NAME, AGE, BIO = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responds to the /start command with a Reply Keyboard."""
    logger.info(f"User {update.effective_user.first_name} started the bot.")
    keyboard = [
        ['/register', '/help'],
        ['/about', '/links']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot (Webhook mode), please talk to me!", reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responds to the /help command."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Available commands:\n/start - Start the bot\n/help - Show this help message\n/about - About this bot\n/links - Show links")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responds to the /about command."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I am a simple Telegram bot built with Python and running on Webhooks!")

async def links_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a message with an Inline Keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("GitHub", url='https://github.com/python-telegram-bot/python-telegram-bot'),
            InlineKeyboardButton("Python Docs", url='https://docs.python.org/3/'),
        ],
        [InlineKeyboardButton("More Info", callback_data='more_info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Check out these resources:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()

    logging.info(f"User {update.effective_user.first_name} clicked button: {query.data}")

    if query.data == 'more_info':
        await query.edit_message_text(text="Selected Option: More Info\n\nThis bot demonstrates various Telegram features like FSM, Databases, Keyboards and Webhooks!")

async def error_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """A command that deliberately raises an error to test the error handler."""
    logger.info("Simulating an error via /error command.")
    # This will raise a ZeroDivisionError
    result = 1 / 0

async def python_regex_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responds to messages containing 'python'."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I love Python too! 🐍")

# --- FSM Handlers ---

async def start_register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the registration process."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! Let's get you registered.\n\nWhat is your full name? (/cancel to stop)")
    return NAME

async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stores the name and asks for age."""
    user_name = update.message.text
    context.user_data['name'] = user_name
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Nice to meet you, {user_name}! \n\nNow, how old are you?")
    return AGE

async def receive_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stores the age and asks for bio."""
    user_age = update.message.text
    if not user_age.isdigit():
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter a valid number for your age.")
        return AGE
    
    context.user_data['age'] = user_age
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Got it! Last question:\n\nTell me a little bit about yourself (Bio).")
    return BIO

async def receive_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stores the bio and ends conversation."""
    user_bio = update.message.text
    context.user_data['bio'] = user_bio
    
    data = context.user_data
    summary = f"Registration Complete!\n\nName: {data['name']}\nAge: {data['age']}\nBio: {data['bio']}"
    
    try:
        await save_user(data['name'], data['age'], data['bio'])
        summary += "\n\n(Saved to Database ✅)"
    except Exception as e:
        logging.error(f"Failed to save user: {e}")
        summary += "\n\n(Failed to save to Database ❌)"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=summary)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels and ends the conversation."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Registration canceled. See you later!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echoes the user message."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

if __name__ == '__main__':
    async def post_init(application):
        await init_db()

    application = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('about', about_command))
    application.add_handler(CommandHandler('links', links_command))
    application.add_handler(CommandHandler('error', error_command))
    
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_error_handler(error_handler)
    
    application.add_handler(MessageHandler(filters.Regex(r"(?i)python"), python_regex_handler))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('register', start_register)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_age)],
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_bio)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))

    if not WEBHOOK_URL:
        print("WEBHOOK_URL not set in .env. Please set it to your public URL (e.g. from ngrok).")
    else:
        print(f"Starting webhook on port {PORT} with URL {WEBHOOK_URL}")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
        )
