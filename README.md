# Translator GUI

Локальный GUI-инструмент для перевода текста между языками с поддержкой кавычек, логированием, лимитами и темами.

## 🚀 Возможности
- Поддержка движков: Google, DeepL, Microsoft, Lingvanex, Local
- Работает с API ключами и токенами
- Перевод текста или только фраз в кавычках
- Подсветка переведённых кавычек
- Лимит символов с отключением и прогресс-баром(количество сиволов, в основном для Bing)
- Сохранение и загрузка `.txt` и `.rpy` файлов
- Тёмная и светлая тема
- Контекстное меню и горячие клавиши
- Логирование переводов в `logs/`
- Настройки сохраняются в `settings.json` и `config.json`

## 🛠️ Установка
git clone https://github.com/slden26/translator-gui.git
cd translator-gui
pip install -r requirements.txt

## requirements.txt
requests
tk
googletrans==4.0.0rc1
deepl==1.12.0
pyinstaller

## 🧱 Сборка .exe через PyInstalle
pyinstaller main.py --onefile --noconsole --icon=icon.ico

## 📂 Структура проекта
translator-gui/
├── main.py
├── translator.py
├── usage.py
├── settings.json
├── config.json
├── logs/
└── README.md

## 📜 Лицензия
MIT — свободно используйте и модифицируйте.

