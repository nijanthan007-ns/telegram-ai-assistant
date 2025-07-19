import openai
import telegram
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# === Replace these with your own credentials ===
TELEGRAM_BOT_TOKEN = "6175633479:AAHrauvrxDspT5MVa3JL7-wZNuUoRz_LKqA"
OPENAI_API_KEY = "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"

openai.api_key = OPENAI_API_KEY

# === Handle incoming messages ===
async def handle_message(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or gpt-4 if available
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response['choices'][0]['message']['content']
    except Exception as e:
        reply = "Sorry, something went wrong. 😔"

    await update.message.reply_text(reply)

# === Start the bot ===
if __name__ == "__main__":
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running...")
    app.run_polling()
