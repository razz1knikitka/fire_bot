import datetime
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Логирование для отладки
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Хранилище активных серий
active_series = {}

# Рекламный юзернейм
AD_USERNAME = "razz1kq"

# Реклама: автоматически при старте бота
async def start_private(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📣 Связаться по рекламе", url=f"https://t.me/{AD_USERNAME}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 *Добро пожаловать в бота!* 👋\n\n"
        "🔥 Здесь вы можете начать *серию общения* с друзьями, поддерживать её и проверять активность!\n\n"
        "📣 *Реклама и сотрудничество:*\n"
        "Нажмите кнопку ниже, чтобы связаться со мной по рекламе ⬇️",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


# Начать серию огоньков
async def start_series(update: Update, context: ContextTypes.DEFAULT_TYPE):
    words = update.message.text.split()
    if len(words) < 3 or words[0].lower() != "начать" or words[1].lower() != "серию":
        await update.message.reply_text("⚠️ Используйте: *начать серию @username*", parse_mode="Markdown")
        return

    user1 = update.effective_user.username
    user2 = words[2].lstrip("@")

    if user1 == user2 or not user2:
        await update.message.reply_text("❌ Укажите корректный тег другого пользователя!")
        return

    # Уникальный ключ для пары пользователей
    key = tuple(sorted([user1, user2]))
    if key in active_series:
        await update.message.reply_text(
            f"🔥 *Серия уже активна* между @{user1} и @{user2}! 🔥", parse_mode="Markdown"
        )
    else:
        active_series[key] = {
            "count": 1,
            "last_update": datetime.datetime.now(),
            "today_users": set(),
        }
        await update.message.reply_text(
            f"🎉 *Серия общения началась!* 🎉\n\n"
            f"👥 Участники: @{user1} и @{user2}\n"
            f"🔥 *Количество огоньков:* 1 🔥",
            parse_mode="Markdown",
        )


# Поддержка серии "Огонь"
async def fire_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.username
    text = update.message.text.strip().lower()

    if text == "огонь":
        now = datetime.datetime.now()
        updated_series = False

        for (user1, user2), series in active_series.items():
            if user in [user1, user2]:  # Если пользователь участвует в серии
                # Проверка: прошло ли 24 часа с последнего огонька
                time_difference = now - series["last_update"]
                if time_difference.total_seconds() < 86400:  # 86400 секунд = 24 часа
                    await update.message.reply_text(
                        f"⏰ *Огонь уже был записан сегодня!* ⏰\n\n"
                        f"🔥 *Следующий огонь можно отправить через {24 - time_difference.seconds // 3600} часов!*",
                        parse_mode="Markdown",
                    )
                    return

                # Добавляем пользователя, если он ещё не написал "огонь" сегодня
                if user not in series["today_users"]:
                    series["today_users"].add(user)

                # Проверка, что оба участника написали "огонь"
                if user1 in series["today_users"] and user2 in series["today_users"]:
                    # Продолжаем серию
                    series["count"] += 1
                    series["last_update"] = now
                    series["today_users"].clear()  # Сбрасываем сегодняшних участников
                    await update.message.reply_text(
                        f"🔥 *Серия продолжается!* 🔥\n\n"
                        f"👥 Участники: @{user1} и @{user2}\n"
                        f"🔥 *Количество огоньков:* {series['count']} 🔥",
                        parse_mode="Markdown",
                    )
                else:
                    # Ждем второго участника
                    await update.message.reply_text("🔥 Огонь записан! Ждём второго участника! 🔥")

                updated_series = True
                break

        if not updated_series:
            await update.message.reply_text("❌ У вас нет активной серии. Начните с команды `начать серию @username`.")

    elif text == "огонь инфо":
        await update.message.reply_text(
            "📋 *Команды:*\n\n"
            "🔹 `начать серию @username` — начать серию\n"
            "🔹 `огонь` — поддержать серию\n"
            "🔹 `огонь инфо` — показать команды\n\n"
            "🔥 *Поддерживайте общение и накапливайте огоньки!* 🔥",
            parse_mode="Markdown",
        )




# Главная функция запуска бота
def main():
    TOKEN = "7191585720:AAGXSdAY-pCdrUi2_K1AN6eabkdPdMY2_j4"  # Вставьте сюда токен вашего бота
    app = Application.builder().token(TOKEN).build()

    # Обработчики
    app.add_handler(CommandHandler("start", start_private))  # Автоматическая реклама
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^начать серию @"), start_series))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^огонь( инфо)?$"), fire_message))

    # Лог
    logger.info("🔥 Бот запущен и готов к работе!")
    app.run_polling()


if __name__ == "__main__":
    main()
