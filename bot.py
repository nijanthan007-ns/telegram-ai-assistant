import os
import logging
import openai
import fitz  # PyMuPDF
from telegram import Update, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# === YOUR CREDENTIALS ===
TELEGRAM_BOT_TOKEN = "7411466363:AAFZzn3lKepc6n65RtRlpk8ogw9PdDM2nQM"
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

# === LOGGING ===
logging.basicConfig(level=logging.INFO)

# === PDF STORAGE ===
PDF_FOLDER = "pdfs"
if not os.path.exists(PDF_FOLDER):
    os.makedirs(PDF_FOLDER)

# === UTIL: Extract all text from all PDFs ===
def load_all_pdf_text():
    text = ""
    for file in os.listdir(PDF_FOLDER):
        if file.endswith(".pdf"):
            with fitz.open(os.path.join(PDF_FOLDER, file)) as doc:
                for page in doc:
                    text += page.get_text()
    return text

# === AI REPLY ===
async def ai_reply(user_message):
    pdf_data = load_all_pdf_text()
    prompt = f"You are a helpful assistant. Answer simply and clearly.\n\nPDF Info:\n{pdf_data[:3000]}\n\nUser Question:\n{user_message}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# === START ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Hello! I’m your AI Assistant.\n\nSend me a PDF *once* to load your manuals. Then ask any questions!")

# === HANDLE PDF ===
async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    if file.mime_type == "application/pdf":
        file_path = os.path.join(PDF_FOLDER, file.file_name)
        await file.get_file().download_to_drive(file_path)
        await update.message.reply_text(f"✅ PDF '{file.file_name}' saved!")
    else:
        await update.message.reply_text("❌ Please upload only PDF files.")

# === HANDLE TEXT ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    response = await ai_reply(user_text)
    await update.message.reply_text(response)

# === MAIN ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running...")
    app.run_polling()
