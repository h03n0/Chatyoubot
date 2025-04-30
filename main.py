import os
os.system("pip install python-telegram-bot")

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# لیست انتظار و جفت‌های چت
waiting_users = []
chat_pairs = {}

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    if user_id in chat_pairs:
        await update.message.reply_text("شما در حال حاضر در حال گفتگو هستید.")
        return

    if waiting_users and waiting_users[0] != user_id:
        partner_id = waiting_users.pop(0)
        chat_pairs[user_id] = partner_id
        chat_pairs[partner_id] = user_id

        await context.bot.send_message(chat_id=user_id, text="شما به یک فرد ناشناس متصل شدید. پیام بفرست!")
        await context.bot.send_message(chat_id=partner_id, text="شما به یک فرد ناشناس متصل شدید. پیام بفرست!")
    else:
        waiting_users.append(user_id)
        await update.message.reply_text("در صف انتظار هستید تا فرد دیگری متصل شود...")

# دستور /stop
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    partner_id = chat_pairs.pop(user_id, None)

    if partner_id:
        chat_pairs.pop(partner_id, None)
        await context.bot.send_message(chat_id=partner_id, text="طرف مقابل گفتگو را ترک کرد.")
        await update.message.reply_text("گفتگو پایان یافت.")
    else:
        if user_id in waiting_users:
            waiting_users.remove(user_id)
        await update.message.reply_text("شما در گفتگویی نبودید.")

# ارسال پیام بین دو فرد
async def relay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    partner_id = chat_pairs.get(user_id)

    if partner_id:
        await context.bot.send_message(chat_id=partner_id, text=update.message.text)
    else:
        await update.message.reply_text("شما هنوز به کسی وصل نشدید. دستور /start رو بزن.")

# راه‌اندازی بات
app = Application.builder().token("7917802610:AAEhxG4w7xAiuCA9PULQIoWY6vucMQHKKy8").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, relay))

app.run_polling()
