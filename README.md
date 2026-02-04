# Telegram Bot Learning Phase - Documentation

## 🚀 Overview
A sophisticated Telegram Bot built with Python, featuring a multi-step registration flow (FSM), PostgreSQL database integration, real-time Webhook communication, and automated cloud deployment.

## ✨ Key Features
- **Interactive Menu**: Uses `ReplyKeyboardMarkup` for persistent buttons and `InlineKeyboardMarkup` for dynamic message updates.
- **FSM Registration**: A guided multi-step user registration (`/register`) collecting Name, Age, and Bio.
- **Database Storage**: Asynchronous saving of user data to a PostgreSQL database using `asyncpg`.
- **Webhook Integration**: Real-time message delivery via HTTPS webhooks (switched from long polling).
- **Advanced Logging**: Persistent logging to `bot.log` with a global exception handler to prevent crashes.

## 🛠 Tech Stack
- **Language**: Python 3.12+
- **Library**: `python-telegram-bot`
- **Database**: PostgreSQL
- **Hosting**: Render.com
- **Tunneling**: ngrok (for local development)

## 📂 Project Structure
```text
telegram-bot-learning-phase/
├── render.yaml          # Cloud deployment blueprint
├── simple_bot/
│   ├── bot.py           # Legacy bot script (Long Polling)
│   ├── bot_webhook.py   # Final production bot (Webhooks)
│   ├── db.py            # Database connection & operations
│   ├── requirements.txt # Project dependencies
│   ├── .env             # Environment variables (excluded from git)
│   └── bot.log          # Application logs
└── .gitignore           # Git ignore rules
```

## ⚙️ Setup & Installation

### Local Development
1. **Clone the repo**:
   ```bash
   git clone https://github.com/game-ale/telegram-bot-learning-phase.git
   ```
2. **Install dependencies**:
   ```bash
   pip install -r simple_bot/requirements.txt
   ```
3. **Configure Environment**:
   Create a `.env` file in `simple_bot/`:
   ```text
   BOT_TOKEN=your_token
   DB_HOST=localhost
   DB_NAME=telegram_bot_db
   DB_USER=postgres
   DB_PASS=password
   DB_PORT=5432
   WEBHOOK_URL=https://your-ngrok-url.dev
   PORT=8443
   ```
4. **Run with Long Polling**:
   ```bash
   python simple_bot/bot.py
   ```
5. **Run with Webhooks**:
   ```bash
   ngrok http 8443
   python simple_bot/bot_webhook.py
   ```

## ☁️ Deployment (Render)
1. **Push code** to a GitHub repository.
2. **Connect to Render**: Use the "Blueprints" feature to connect your repo.
3. **Automatic Setup**: Render will use `render.yaml` to:
   - Provision a Free PostgreSQL database.
   - Start a Web Service for the bot.
4. **Set Secrets**: Fill in `BOT_TOKEN` and `WEBHOOK_URL` in the Render dashboard.

## 🔒 Security
- **No Hardcoded Secrets**: All tokens and passwords reside in environment variables.
- **Git Protection**: Sensitive files like `.env` and `bot.log` are never pushed to GitHub.
- **Encrypted Communication**: All webhook traffic is handled over HTTPS.

## 📝 Commands
- `/start` - Launch the main menu.
- `/register` - Start the registration FSM.
- `/links` - Show clickable resource links.
- `/help` - List available commands.
- `/error` - Simulate a crash to test logging.
