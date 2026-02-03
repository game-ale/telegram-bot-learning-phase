import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from db import init_db, save_user

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv('BOT_TOKEN')

# Define states for the ConversationHandler
NAME, AGE, BIO = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responds to the /start command with a Reply Keyboard."""
    keyboard = [
        ['/register', '/help'],
        ['/about', '/links']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!", reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responds to the /help command."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Available commands:\n/start - Start the bot\n/help - Show this help message\n/about - About this bot")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responds to the /about command."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I am a simple Telegram bot built with Python!")

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

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    logging.info(f"User {update.effective_user.first_name} clicked button: {query.data}")

    if query.data == 'more_info':
        await query.edit_message_text(text="Selected Option: More Info\n\nThis bot demonstrates various Telegram features like FSM, Databases, and Keyboards!")

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
    
    # Retrieve all data
    data = context.user_data
    summary = f"Registration Complete!\n\nName: {data['name']}\nAge: {data['age']}\nBio: {data['bio']}"
    
    # Save to database
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
    # Initialize the database
    # Note: init_db is async, so we can't call it directly in __main__ easily without an event loop.
    # However, since application.run_polling() handles the loop, we can use the 'post_init' hook of ApplicationBuilder.
    pass 

    async def post_init(application: ApplicationBuilder):
        await init_db()

    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    # Add a handler for the /start command
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    # Add other command handlers
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('about', about_command))
    application.add_handler(CommandHandler('links', links_command))

    # Add CallbackQueryHandler
    application.add_handler(CallbackQueryHandler(button_handler))

    # Add regex handler (higher priority than echo)
    # This matches any message containing "python" (case-insensitive by default with search, but we use Regex filter)
    # Note: filters.Regex expects a pattern string.
    application.add_handler(MessageHandler(filters.Regex(r"(?i)python"), python_regex_handler))

    # Add ConversationHandler
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

    # Add a handler for text messages
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(echo_handler)

    # Run the bot until the user presses Ctrl-C
    print("Bot is polling... Press Ctrl+C to stop.")
    application.run_polling()
