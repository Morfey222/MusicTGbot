
# 🎧 Music Genre Telegram Bot

Этот Telegram-бот позволяет находить случайные музыкальные треки с YouTube по выбранному жанру. Бот использует кнопочное меню, поддерживает избранное, выводит обложки и названия треков, а также предоставляет статистику активности.

## 🔧 Возможности

* Выбор жанра: рок, поп, фонк, метал
* Получение случайного трека с YouTube
* Инлайн-кнопки:

  * 🎲 Ещё — получить другой трек того же жанра
  * 🔗 Открыть на YouTube
  * ❤️ В избранное
  * 📋 Меню (возврат к жанрам)
* Команда `/fav` — просмотр избранных треков
* Возможность удалить избранные треки по кнопке
* Команда `/stats` — статистика
* Команда `/clearfav` — очистить избранное
* Команда `/help` — инструкция

## 📦 Установка

1. **Клонируй репозиторий или скачай скрипт**

```bash
git clone https://github.com/your_username/music-genre-bot.git
cd music-genre-bot
```

2. **Установи зависимости**

Рекомендуется использовать виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # Для Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Создай Telegram-бота**

* Перейди в Telegram → @BotFather
* Создай нового бота: `/newbot`
* Получи `TELEGRAM_TOKEN`

4. **Получи YouTube API Key**

* Перейди в [Google Cloud Console](https://console.cloud.google.com/)
* Создай проект → Включи API "YouTube Data API v3"
* Получи ключ → вставь в код в переменную `YOUTUBE_API_KEY`

5. **Запусти бота**

```bash
python "MusicBot version 1.2.py"
```

## 📌 Структура кода

* `start()` — приветствие и запуск
* `handle_genre()` — обработка выбора жанра
* `get_random_video_link()` — запрос к YouTube API
* `send_track()` — отправка трека пользователю
* `button_handler()` — инлайн-кнопки: ещё, избранное, меню
* `show_favorites()` — просмотр и удаление избранного
* `stats_command()` — статистика
* `clearfav_command()` — очистка избранного
* `help_command()` — справка

## 📎 Примечание по безопасности

**Никогда не публикуй `TELEGRAM_TOKEN` и `YOUTUBE_API_KEY` в открытом доступе (GitHub, форумы и т.д.)**
Храни ключи в `.env` файле и используй `python-dotenv`:

```txt
# .env
TELEGRAM_TOKEN=your_token_here
YOUTUBE_API_KEY=your_api_key_here
```

И в коде:

```python
from dotenv import load_dotenv
import os
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
```

## 🧑‍💻 Автор

\[Morfey22]
TG: [Morfey22](@Morfey22)


