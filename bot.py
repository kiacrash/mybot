#code bot telegram
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

ADMIN_ID = 553903664

user_map = {}

all_users = set()
broadcast_mode = False

banned_users = set()

active_admin_chats = {}
import json

import os
TOKEN = os.getenv("TOKEN")

BOT_USERNAME = '@crashwrldbot'

def main_keyboard(user_id=None):
    buttons = [
        ["🏠 شروع"],
        ["❓ راهنما", "⚙️ دستور سفارشی"],
        ["📩 ارتباط با من"]
    ]

    if user_id == ADMIN_ID:
        buttons.append(["🛠 پنل مدیریت"])

    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def admin_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["📢 پیام همگانی"],
            ["❌ خروج از چت"],
        ],
        resize_keyboard=True
    )





def cancel_keyboard():
    return ReplyKeyboardMarkup(
        [["لغو"]],
        resize_keyboard=True
    )





async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"سلام {user.first_name or ''} به کرش ورلد خوش آمدید",
        reply_markup=main_keyboard(update.effective_user.id)

    )
    




async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'من یک ربات برای کانال کرش ورلد هستم و دستورات من /start /help /custom هست همینطور به بعضی از نوشته های شما پاسخ میدهم'
    )


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("این یک دستور سفارشی هست")

def save_state():
    data = {
        "banned_users": list(banned_users),
        "active_admin_chats": active_admin_chats
    }
    with open("state.json", "w") as f:
        json.dump(data, f)

def load_state():
    global banned_users, active_admin_chats
    try:
        with open("state.json", "r") as f:
            data = json.load(f)
            banned_users = set(data.get("banned_users", []))
            active_admin_chats = data.get("active_admin_chats", {})
    except:
        pass



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
            active_admin_chats[ADMIN_ID] = user_id
            active_admin_chats[user_id] = True
            save_state()

    if ADMIN_ID in active_admin_chats:
        user_id = active_admin_chats[ADMIN_ID]
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


async def banlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not banned_users:
        await update.message.reply_text("لیست بن خالی است.")
        return
    text = "\n".join(str(u) for u in banned_users)
    await update.message.reply_text(f"کاربران بن شده:\n{text}")


async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if context.args:
        uid = int(context.args[0])
        banned_users.discard(uid)
        save_state()
        await update.message.reply_text("آن‌بن شد.")
    else:
        await update.message.reply_text("آیدی عددی بده: /unban 123456")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(
        f"""آمار ربات:

👥 کل کاربران: {len(all_users)}
🚫 بن شده‌ها: {len(banned_users)}
💬 چت فعال: {"دارد" if ADMIN_ID in active_admin_chats else "ندارد"}
"""
    )



async def end_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if ADMIN_ID in active_admin_chats:
        user_id = active_admin_chats[ADMIN_ID]
        active_admin_chats.pop(user_id, None)
        active_admin_chats.pop(ADMIN_ID, None)
        await context.bot.send_message(user_id, "ادمین از چت خارج شد.")
        await update.message.reply_text("از چت خارج شدی.")



async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global broadcast_mode
    if update.effective_user.id == ADMIN_ID:
        broadcast_mode = True
        await update.message.reply_text("پیام همگانی را بفرست:")



async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):


    message = update.message
    user_id = update.effective_user.id
    all_users.add(user_id)
    chat_type = message.chat.type
    text = message.text if message.text else ""

    if user_id in banned_users:
        return
    
    global broadcast_mode

    if broadcast_mode and user_id == ADMIN_ID:
        for u in all_users:
            try:
               await context.bot.send_message(u, text)
            except:
                pass
        broadcast_mode = False
        await message.reply_text("ارسال شد.")
        return


    

    if user_id == ADMIN_ID:
        if text == "📢 پیام همگانی":
            await broadcast_command(update, context)
            return

        if text == "❌ خروج از چت":
            await end_chat(update, context)
            return

    if text == "🛠 پنل مدیریت" and user_id == ADMIN_ID:
         await message.reply_text(
             "پنل مدیریت:",
             reply_markup=ReplyKeyboardMarkup(
                [
                      ["📢 پیام همگانی"],
                   ["📋 آمار ربات", "🚫 لیست بن"],
                   ["❌ خروج از چت"]
                ],
                resize_keyboard=True
            )
        )
         return


    if text == "📋 آمار ربات" and user_id == ADMIN_ID:
        await stats(update, context)
        return

    if text == "🚫 لیست بن" and user_id == ADMIN_ID:
        await banlist(update, context)
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


    if text == "📩 ارتباط با من":
        await message.reply_text(
          "پیام‌هات رو بفرست. هرچی بفرستی مستقیم برای من میاد.\nبرای خروج «لغو» بزن.",
         reply_markup=cancel_keyboard()
        )
        active_admin_chats[user_id] = True
        return

    
    # چت ادامه‌دار کاربر با ادمین
    if user_id in active_admin_chats and user_id != ADMIN_ID:
        if text == "لغو":
            active_admin_chats.pop(user_id, None)
            await message.reply_text("از چت خارج شدی.", reply_markup=main_keyboard(user_id))
            return

        header = f"پیام جدید از کاربر:\n\nID: {user_id}"
        await context.bot.send_message(ADMIN_ID, header)

        sent = await message.copy(chat_id=ADMIN_ID)
        user_map[sent.message_id] = user_id
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
    load_state()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("custom", custom_command))

    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("banlist", banlist))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("stats", stats))


    app.add_handler(CommandHandler("end", end_chat))

    app.add_handler(CommandHandler("broadcast", broadcast_command))


    app.add_handler(MessageHandler(filters.REPLY & filters.User(ADMIN_ID), admin_reply))

    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

    app.add_error_handler(error)

    print("polling")
    app.run_polling(poll_interval=3)
