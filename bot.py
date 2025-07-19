from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import openai
import os

TELEGRAM_TOKEN = "7411466363:AAFZzn3lKepc6n65RtRlpk8ogw9PdDM2nQM"
openai.api_key = "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"

pdf_knowledge = ""

def load_pdfs(folder_path="pdfs"):
    global pdf_knowledge
    from PyPDF2 import PdfReader
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            reader = PdfReader(os.path.join(folder_path, filename))
            for page in reader.pages:
                pdf_knowledge += page.extract_text() + "\n"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I’m your AI assistant. Ask me anything.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    full_context = f"Context:\n{pdf_knowledge}\n\nUser Query: {query}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": full_context}]
    )
    await update.message.reply_text(response.choices[0].message.content.strip())

if __name__ == "__main__":
    load_pdfs("pdfs")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
