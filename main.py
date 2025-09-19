# === Блок 1: Импорты и расширения ===
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json, os, re
from datetime import datetime
from translator import translate
from usage import save_usage

# === Блок 2: Константы и словари ===
SETTINGS_PATH = "settings.json"
USAGE_PATH = "usage.json"
FONT_SETTINGS = {"family": "Consolas", "size": 12}

LANGS = {
    "ru": "Русский",
    "uk": "Український",
    "en": "Английский",
    "it": "Итальянский",
    "de": "Немецкий"
}

ENGINES = {
    "google": "Google",
    "deepl": "DeepL",
    "lingvanex": "Lingvanex",
    "microsoft": "Microsoft",
    "local": "Локальный"
}

ENGINE_NAMES = {v: k for k, v in ENGINES.items()}

# === Блок 3: Инициализация GUI и переменные состояния ===
root = tk.Tk()
root.title("Translator GUI")
root.geometry("800x500")

theme = tk.StringVar()
mode = tk.StringVar()
engine_var = tk.StringVar()
limit_enabled_var = tk.BooleanVar()
settings = {}

# === Блок 4: Загрузка настроек ===
def load_settings():
    global settings
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            settings = json.load(f)
    theme.set(settings.get("theme", "dark"))
    mode.set(settings.get("mode", "quotes"))
    engine_var.set(ENGINES.get(settings.get("engine", "google"), "Google"))
    limit_enabled_var.set(settings.get("limit_enabled", True))

# === Блок 5: Сохранение настроек ===
def save_settings():
    settings["theme"] = theme.get()
    settings["mode"] = mode.get()
    settings["engine"] = ENGINE_NAMES.get(engine_var.get(), "google")
    settings["limit_enabled"] = limit_enabled_var.get()
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
    if os.path.exists("config.json"):
        with open("config.json", "r+", encoding="utf-8") as f:
            cfg = json.load(f)
            cfg["engine"] = settings["engine"]
            f.seek(0)
            json.dump(cfg, f, ensure_ascii=False, indent=2)
            f.truncate()

# === Блок 6: Загрузка статистики использования ===
def load_usage():
    if os.path.exists(USAGE_PATH):
        with open(USAGE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"month": datetime.now().strftime("%Y-%m"), "used": 0}

# === Блок 7: Сохранение статистики использования ===
def save_usage(char_count):
    usage = load_usage()
    current_month = datetime.now().strftime("%Y-%m")
    if usage["month"] != current_month:
        usage = {"month": current_month, "used": 0}
    usage["used"] += char_count
    with open(USAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(usage, f, ensure_ascii=False, indent=2)
    if usage["used"] >= 0.9 * 2_000_000:
        messagebox.showwarning("Лимит почти исчерпан", f"Вы использовали {usage['used']:,} символов из 2 000 000.")
    update_limit_bar()

# === Блок 8: Обновление прогресс-бара лимита ===
def update_limit_bar():
    usage = load_usage()
    used = usage["used"]
    percent = used / 2_000_000
    limit_bar["value"] = used
    limit_label.config(text=f"{used:,} / 2 000 000")
    if percent >= 0.9:
        limit_bar.configure(style="Red.Horizontal.TProgressbar")
    elif percent >= 0.75:
        limit_bar.configure(style="Yellow.Horizontal.TProgressbar")
    else:
        limit_bar.configure(style="Green.Horizontal.TProgressbar")

# === Блок 9: Обработка кавычек и логирование переводов ===
def extract_quotes(text):
    return re.findall(r'"(.*?)"', text)

def replace_quotes(text, translations):
    def repl(match): return f'"{translations.pop(0)}"'
    return re.sub(r'"(.*?)"', repl, text)

def log_translation(source, result, src_lang, tgt_lang):
    os.makedirs("logs", exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_path = os.path.join("logs", f"log_{date_str}.jsonl")
    entry = {
        "timestamp": datetime.now().isoformat(),
        "from": src_lang,
        "to": tgt_lang,
        "source": source,
        "result": result
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# === Блок 10: Основная функция перевода ===
def run_translation():
    raw_text = input_text.get("1.0", tk.END).strip()
    if not raw_text:
        messagebox.showinfo("Пустой ввод", "Введите текст для перевода.")
        return
    if '"' in raw_text and mode.get() != "quotes":
        mode.set("quotes")
        save_settings()
    src_lang = [code for code, name in LANGS.items() if name == combo_from.get()][0]
    tgt_lang = [code for code, name in LANGS.items() if name == combo_to.get()][0]
    if mode.get() == "quotes":
        quoted = extract_quotes(raw_text)
        translated = [translate(q, src_lang, tgt_lang) for q in quoted]
        result = replace_quotes(raw_text, translated)
    else:
        result = translate(raw_text, src_lang, tgt_lang)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, result)
    output_text.tag_config("highlight", background="#ffd966")
    for match in re.finditer(r'"(.*?)"', result):
        start = f"1.0+{match.start()}c"
        end = f"1.0+{match.end()}c"
        output_text.tag_add("highlight", start, end)
    log_translation(raw_text, result, src_lang, tgt_lang)
    engine_name = ENGINE_NAMES.get(combo_engine.get(), "").lower()
    if settings.get("limit_enabled") and engine_name == "microsoft":
        save_usage(len(raw_text))

# === Блок 11: Управление файлами, очисткой, темой оформления ===
def open_file():
    path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt *.rpy"), ("All files", "*.*")])
    if path:
        with open(path, "r", encoding="utf-8") as f:
            input_text.delete("1.0", tk.END)
            input_text.insert(tk.END, f.read())

def save_result():
    path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt *.rpy")])
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(output_text.get("1.0", tk.END).strip())

def clear_fields():
    input_text.delete("1.0", tk.END)
    output_text.delete("1.0", tk.END)

def translate_and_save():
    run_translation()
    save_result()

def toggle_theme():
    if theme.get() == "dark":
        root.configure(bg="#2e2e2e")
        input_text.configure(bg="#1e1e1e", fg="#ffffff", insertbackground="#ffffff")
        output_text.configure(bg="#1e1e1e", fg="#ffffff", insertbackground="#ffffff")
        style.theme_use("clam")
    else:
        root.configure(bg="#f0f0f0")
        input_text.configure(bg="#ffffff", fg="#000000", insertbackground="#000000")
        output_text.configure(bg="#ffffff", fg="#000000", insertbackground="#000000")
        style.theme_use("default")
    save_settings()

# === Блок 12: Информация о программе (Окно "О программе") ===

def show_about():
    usage = load_usage()
    info = (
        f"Translator GUI\n"
        f"Автор: Денис\n"
        f"Версия: 1.0\n\n"
        f"Движок: {combo_engine.get()}\n"
        f"Месяц: {usage['month']}\n"
        f"Использовано: {usage['used']:,} символов\n"
        f"Остаток: {max(0, 2_000_000 - usage['used']):,}"
    )
    messagebox.showinfo("О программе", info)
# === Блок 13: Контекстное меню, главное меню и запуск интерфейса ===

def copy_to_clipboard(event=None):
    try:
        selected = output_text.get(tk.SEL_FIRST, tk.SEL_LAST)
        root.clipboard_clear()
        root.clipboard_append(selected)
    except tk.TclError:
        pass

def create_context_menu(widget):
    menu = tk.Menu(widget, tearoff=0)
    menu.add_command(label="Копировать", command=lambda: widget.event_generate("<<Copy>>"))
    menu.add_command(label="Вставить", command=lambda: widget.event_generate("<<Paste>>"))
    menu.add_command(label="Вырезать", command=lambda: widget.event_generate("<<Cut>>"))
    widget.bind("<Button-3>", lambda event: menu.tk_popup(event.x_root, event.y_root))

# Главное меню
menubar = tk.Menu(root)

file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="Открыть файл", command=open_file)
file_menu.add_command(label="Сохранить перевод", command=save_result)
file_menu.add_command(label="Очистить поля", command=clear_fields)
file_menu.add_separator()
file_menu.add_command(label="Выход", command=root.quit)
menubar.add_cascade(label="Файл", menu=file_menu)

settings_menu = tk.Menu(menubar, tearoff=0)
theme_menu = tk.Menu(settings_menu, tearoff=0)
theme_menu.add_radiobutton(label="Тёмная", variable=theme, value="dark", command=toggle_theme)
theme_menu.add_radiobutton(label="Светлая", variable=theme, value="light", command=toggle_theme)
settings_menu.add_cascade(label="Тема", menu=theme_menu)

font_menu = tk.Menu(settings_menu, tearoff=0)
font_menu.add_command(label="Увеличить шрифт", command=lambda: [
    FONT_SETTINGS.update({"size": FONT_SETTINGS["size"] + 1}),
    input_text.configure(font=(FONT_SETTINGS["family"], FONT_SETTINGS["size"])),
    output_text.configure(font=(FONT_SETTINGS["family"], FONT_SETTINGS["size"]))
])
settings_menu.add_cascade(label="Шрифт", menu=font_menu)
menubar.add_cascade(label="Настройки", menu=settings_menu)

about_menu = tk.Menu(menubar, tearoff=0)
about_menu.add_command(label="Информация", command=show_about)
menubar.add_cascade(label="О программе", menu=about_menu)

root.config(menu=menubar)
# === Блок 14: Инициализация интерфейса (визуальные элементы) ===

style = ttk.Style()
style.theme_use("default")
style.configure("Green.Horizontal.TProgressbar", background="#4caf50", troughcolor="#e0e0e0")
style.configure("Yellow.Horizontal.TProgressbar", background="#ffb300", troughcolor="#e0e0e0")
style.configure("Red.Horizontal.TProgressbar", background="#e53935", troughcolor="#e0e0e0")

progress_frame = ttk.Frame(root)
progress_frame.pack(fill="x", padx=10)
ttk.Label(progress_frame, text="Использование лимита:").pack(side="left")
limit_bar = ttk.Progressbar(progress_frame, length=300, maximum=2_000_000)
limit_bar.pack(side="left", padx=10)
limit_label = ttk.Label(progress_frame, text="0 / 2 000 000")
limit_label.pack(side="left")

frame = ttk.Frame(root)
frame.pack(pady=10, fill="x")
combo_from = ttk.Combobox(frame, values=list(LANGS.values()), width=15)
combo_to = ttk.Combobox(frame, values=list(LANGS.values()), width=15)
combo_engine = ttk.Combobox(frame, values=list(ENGINES.values()), width=15, textvariable=engine_var)

ttk.Label(frame, text="Исходный язык:").grid(row=0, column=0)
combo_from.grid(row=0, column=1)
ttk.Label(frame, text="Целевой язык:").grid(row=0, column=2)
combo_to.grid(row=0, column=3)
ttk.Label(frame, text="Движок:").grid(row=1, column=0)
combo_engine.grid(row=1, column=1)
combo_engine.bind("<<ComboboxSelected>>", lambda e: save_settings())

# Переключатель лимита
chk_limit = ttk.Checkbutton(
    frame,
    text="Учитывать лимит",
    variable=limit_enabled_var,
    command=save_settings
)
chk_limit.grid(row=1, column=2, padx=5)

ttk.Button(frame, text="Очистить поля", command=clear_fields).grid(row=1, column=3, padx=5)
ttk.Button(frame, text="Перевести и сохранить", command=translate_and_save).grid(row=1, column=4, padx=5)

paned = ttk.PanedWindow(root, orient=tk.VERTICAL)
paned.pack(fill="both", expand=True, padx=10, pady=5)

# === Создание текстовых полей ===
input_text = tk.Text(paned, wrap="word", font=(FONT_SETTINGS["family"], FONT_SETTINGS["size"]))
paned.add(input_text, weight=1)

btn_simple = ttk.Button(paned, text="Простой перевод", command=run_translation)
paned.add(btn_simple)

output_text = tk.Text(paned, wrap="word", font=(FONT_SETTINGS["family"], FONT_SETTINGS["size"]))
paned.add(output_text, weight=1)

# === Привязка контекстного меню и горячих клавиш — строго здесь ===
create_context_menu(input_text)
create_context_menu(output_text)
output_text.bind("<Control-c>", copy_to_clipboard)

# === Блок 15: Запуск приложения ===

load_settings()
update_limit_bar()
toggle_theme()
root.mainloop()    