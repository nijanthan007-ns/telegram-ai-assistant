import logging
from telegram import Update, Document
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import openai
from io import BytesIO
import fitz  # PyMuPDF

# Replace these with your actual keys
TELEGRAM_BOT_TOKEN = "7411466363:AAFZzn3lKepc6n65RtRlpk8ogw9PdDM2nQM"
OPENAI_API_KEY = "sk-proj-xxx"  # Insert your OpenAI key here

openai.api_key = OPENAI_API_KEY
logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Send me a PDF and ask any question based on it!")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc: Document = update.message.document

    if doc.mime_type != "application/pdf":
        await update.message.reply_text("❌ Please send a PDF file.")
        return

    file = await context.bot.get_file(doc.file_id)
    file_bytes = BytesIO()
    await file.download(out=file_bytes)

    text = extract_text_from_pdf(file_bytes)
    context.user_data["pdf_text"] = text

    await update.message.reply_text("✅ PDF received! Now send your question.")

def extract_text_from_pdf(file_bytes: BytesIO) -> str:
    file_bytes.seek(0)
    text = ""
    with fitz.open(stream=file_bytes.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text
    pdf_text = context.user_data.get("pdf_text")

    if not pdf_text:
        await update.message.reply_text("❗ Please upload a PDF first.")
        return

    prompt = f"You are an assistant. Use the text below to answer the question.\n\nPDF Text:\n{pdf_text}\n\nQuestion: {user_question}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or gpt-4 if available
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
    )

    answer = response.choices[0].message.content
    await update.message.reply_text(answer)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()
