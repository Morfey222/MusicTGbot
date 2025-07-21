import logging
import random
import requests
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
)
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters,
    CallbackContext, CallbackQueryHandler
)

# ТВОИ КЛЮЧИ
TELEGRAM_TOKEN = 'your token'
YOUTUBE_API_KEY = 'your api'

GENRES = ['рок', 'поп', 'фонк', 'метал']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def get_random_video_link(genre, history=None):
    if history is None:
        history = []

    SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
    all_results = []
    params = {
        "part": "snippet",
        "q": genre + " music",
        "key": YOUTUBE_API_KEY,
        "type": "video",
        "videoEmbeddable": "true",
        "videoDuration": "medium",
        "maxResults": 50
    }

    try:
        next_page_token = None
        for _ in range(3):  # 3 страницы по 50 видео
            if next_page_token:
                params['pageToken'] = next_page_token
            else:
                params.pop('pageToken', None)

            response = requests.get(SEARCH_URL, params=params)
            response.raise_for_status()
            data = response.json()

            all_results.extend(data.get("items", []))
            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break

        valid_videos = []
        for item in all_results:
            video_id = item["id"]["videoId"]
            if video_id in history:
                continue

            title = item["snippet"]["title"]
            thumbnail = item["snippet"]["thumbnails"]["high"]["url"]
            url = f"https://www.youtube.com/watch?v={video_id}"

            if "shorts" not in url and "embed" not in url:
                valid_videos.append({
                    "video_id": video_id,
                    "title": title,
                    "url": url,
                    "thumbnail": thumbnail
                })

        if valid_videos:
            return random.choice(valid_videos)
        else:
            return None

    except Exception as e:
        print("❌ Ошибка при загрузке:", e)
        return None


def start(update: Update, context: CallbackContext):
    keyboard = [['▶️ Старт']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text("🎧 Добро пожаловать! Нажми Старт, чтобы выбрать жанр.", reply_markup=reply_markup)


def handle_genre(update: Update, context: CallbackContext):
    text = update.message.text.lower()

    if text == '▶️ старт':
        keyboard = [[g for g in GENRES]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text("Выбери жанр 🎶", reply_markup=reply_markup)
        return

    if text in GENRES:
        # Автоочистка истории — максимум 30 последних
        user_history = context.user_data.setdefault('history', [])
        if len(user_history) > 30:
            context.user_data['history'] = user_history[-30:]

        send_track(update, context, text)
    else:
        update.message.reply_text("Пожалуйста, выбери жанр из меню.")


def send_track(update_or_query, context: CallbackContext, genre):
    if hasattr(update_or_query, 'message'):
        chat = update_or_query.message
    else:
        chat = update_or_query.callback_query.message

    user_history = context.user_data.setdefault('history', [])
    result = get_random_video_link(genre, history=user_history)

    if not result:
        chat.reply_text("⚠️ Все треки уже были показаны.")
        return

    title = result["title"]
    url = result["url"]
    thumbnail = result["thumbnail"]
    video_id = result["video_id"]

    user_history.append(video_id)
    # Обрезаем историю сразу при добавлении (чтобы не разрасталась)
    if len(user_history) > 30:
        context.user_data['history'] = user_history[-30:]

    context.user_data['last_genre'] = genre
    context.user_data['last_track'] = f"{title}\n{url}"

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎲 Ещё", callback_data='more')],
        [InlineKeyboardButton("🔗 Открыть на YouTube", url=url)],
        [InlineKeyboardButton("❤️ В избранное", callback_data='fav')],
        [InlineKeyboardButton("📋 Меню", callback_data='menu')]
    ])

    chat.reply_photo(
        photo=thumbnail,
        caption=f"🎶 {title}\n{url}",
        reply_markup=buttons
    )


def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == 'more':
        genre = context.user_data.get('last_genre')
        if genre:
            send_track(query, context, genre)

    elif query.data == 'fav':
        last = context.user_data.get('last_track')
        if last:
            favorites = context.user_data.setdefault('favorites', [])
            if last not in favorites:
                favorites.append(last)
            query.message.reply_text("💾 Добавлено в избранное!")

    elif query.data == 'menu':
        help_command(update.callback_query, context)

    elif query.data.startswith('fav_del_'):
        # Удаляем избранный трек по индексу
        try:
            idx = int(query.data.split('_')[-1])
            favorites = context.user_data.setdefault('favorites', [])
            if 0 <= idx < len(favorites):
                removed = favorites.pop(idx)
                query.message.reply_text(f"🗑️ Удалено из избранного:\n{removed}")
            else:
                query.message.reply_text("❌ Не удалось удалить трек.")
        except Exception:
            query.message.reply_text("❌ Ошибка удаления трека.")
        # Обновляем меню избранного после удаления
        show_favorites(update, context)


def show_favorites(update: Update, context: CallbackContext):
    favorites = context.user_data.get('favorites', [])

    if not favorites:
        update.message.reply_text("⭐ У тебя нет избранных треков.")
        return

    buttons = []
    text_lines = []
    for i, track in enumerate(favorites):
        # Добавляем трек с кнопкой удалить
        text_lines.append(f"{i+1}. {track}")
        buttons.append([InlineKeyboardButton(f"❌ Удалить {i+1}", callback_data=f'fav_del_{i}')])

    reply_markup = InlineKeyboardMarkup(buttons)
    update.message.reply_text(
        "🎧 Избранное:\n\n" + "\n".join(text_lines),
        reply_markup=reply_markup
    )


def show_favorites_callback(update: Update, context: CallbackContext):
    # Для вызова меню избранного по кнопке (из CallbackQuery)
    query = update.callback_query
    query.answer()
    show_favorites(update, context)


def stats_command(update: Update, context: CallbackContext):
    user_data = context.user_data
    total_history = len(user_data.get('history', []))
    total_favorites = len(user_data.get('favorites', []))

    text = (
        f"📊 Статистика твоей активности:\n"
        f"• Просмотрено треков: {total_history}\n"
        f"• Добавлено в избранное: {total_favorites}\n"
        f"• Текущая история хранит не более 30 последних треков."
    )
    update.message.reply_text(text)


def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🎵 Я бот, который находит случайную музыку с YouTube по жанрам.\n\n"
        "Команды:\n"
        "/start — перезапуск\n"
        "/help — помощь\n"
        "/fav — избранные треки\n"
        "/stats — статистика\n"
        "/clearfav — очистить избранное\n\n"
        "Нажимай кнопки и слушай музыку! 🎶"
    )


def clearfav_command(update: Update, context: CallbackContext):
    context.user_data['favorites'] = []
    update.message.reply_text("🗑️ Избранное очищено.")


def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("fav", show_favorites))
    dp.add_handler(CommandHandler("stats", stats_command))
    dp.add_handler(CommandHandler("clearfav", clearfav_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_genre))
    dp.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Бот запущен!")
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
