from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

ADMIN_ID = 553903664
waiting_for_admin = set()
user_map = {}

banned_users = set()


import os
TOKEN = os.getenv("TOKEN")

BOT_USERNAME = '@crashwrldbot'

def main_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["🏠 شروع"],
            ["❓ راهنما", "⚙️ دستور سفارشی"],
            ["📩 ارتباط با من"]
        ],
        resize_keyboard=True
    )





def cancel_keyboard():
    return ReplyKeyboardMarkup(
        [["لغو"]],
        resize_keyboard=True
    )



async def contact_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    waiting_for_admin.add(update.effective_user.id)
    await update.message.reply_text(
        "پیام خودتون را بنویسید تا برای من ارسال شود:",
        reply_markup=cancel_keyboard()
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"سلام {user.first_name or ''} به کرش ورلد خوش آمدید",
        reply_markup=main_keyboard()
    )



async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'من یک ربات برای کانال کرش ورلد هستم و دستورات من /start /help /custom هست همینطور به بعضی از نوشته های شما پاسخ میدهم'
    )


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("این یک دستور سفارشی هست")


def handle_response(text: str):
    if not text:
        return "چیزی دریافت نکردم!"
    user_text = text.lower()
    if "hello" in user_text or "سلام" in user_text or "درود" in user_text or "salam" in user_text:
        return "درود بر شما"
    if "how are you" in user_text or "چطوری" in user_text or "حالت چطوره" in user_text or "خوبی" in user_text:
        return "مرسی خوبم شما چطورید"
    if "i love you" in user_text or "دوست دارم" in user_text or "عاشقتم" in user_text:
        return "مرسی از محبت شما"
    return "شرمنده متوجه نشدم"


async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if update.message.reply_to_message:
        msg_id = update.message.reply_to_message.message_id

        if msg_id in user_map:
            user_id = user_map[msg_id]
            await context.bot.send_message(user_id, update.message.text)

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if update.message.reply_to_message:
        msg_id = update.message.reply_to_message.message_id

        if msg_id in user_map:
            user_id = user_map[msg_id]
            banned_users.add(user_id)
            await update.message.reply_text("کاربر بن شد و دیگر نمی‌تواند به شما پیام بدهد.")



async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):


    message = update.message
    user_id = update.effective_user.id
    chat_type = message.chat.type
    text = message.text if message.text else ""

    if user_id in banned_users:
        return
    
    # حالت ارتباط با مدیریت
    if user_id in waiting_for_admin:
        if text == "لغو":
            waiting_for_admin.remove(user_id)
            await message.reply_text("لغو شد.", reply_markup=main_keyboard())

            return

        header = f"پیام جدید از کاربر:\n\nID: {user_id}"
        await context.bot.send_message(ADMIN_ID, header)


        sent = await message.copy(chat_id=ADMIN_ID)


        user_map[sent.message_id] = user_id
        waiting_for_admin.remove(user_id)

        await message.reply_text(
            "پیام شما برای من ارسال شد.",
            reply_markup=main_keyboard()
        )

        return


    # دکمه ها
    if text == "🏠 شروع":
      await start_command(update, context)
      return

    if text == "❓ راهنما":
     await help_command(update, context)
     return

    if text == "⚙️ دستور سفارشی":
     await custom_command(update, context)
     return


    # اگر کاربر دکمه ارتباط با مدیریت را زد
    if text == "📩 ارتباط با من":
     waiting_for_admin.add(user_id)
     await message.reply_text(
          "پیام خودتون را بنویسید تا برای من ارسال شود:",
           reply_markup=cancel_keyboard()
     )
     return


    

    print(f"user : {message.chat.id} , chat type : {chat_type} , text : {text}")

    if chat_type in ("group", "supergroup"):
        if BOT_USERNAME.lower() in text.lower():
            t = text.replace(BOT_USERNAME, '').strip()
            respose = handle_response(t)
        else:
            return
    else:
        respose = handle_response(text)

    await message.reply_text(respose)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'update : {update} cause error : {context.error}')


if __name__ == "__main__":
    print("bot is starting...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("custom", custom_command))
    app.add_handler(CommandHandler("ban", ban_user))

    app.add_handler(CommandHandler("contact", contact_admin_command))

    app.add_handler(MessageHandler(filters.REPLY, admin_reply))
    app.add_handler(MessageHandler(~filters.COMMAND, handle_message))


    app.add_error_handler(error)

    print("polling")
    app.run_polling(poll_interval=3)
