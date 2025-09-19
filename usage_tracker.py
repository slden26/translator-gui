import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime

USAGE_PATH = "usage.json"

def load_usage():
    if os.path.exists(USAGE_PATH):
        with open(USAGE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"month": datetime.now().strftime("%Y-%m"), "used": 0}

def save_usage(char_count):
    usage = load_usage()
    current_month = datetime.now().strftime("%Y-%m")
    if usage["month"] != current_month:
        usage = {"month": current_month, "used": 0}
    usage["used"] += char_count
    with open(USAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(usage, f, ensure_ascii=False, indent=2)

def show_usage():
    usage = load_usage()
    info = (
        f"Статистика перевода:\n\n"
        f"Месяц: {usage['month']}\n"
        f"Использовано символов: {usage['used']:,}\n"
        f"Лимит (пример): 2 000 000 символов\n"
        f"Остаток: {max(0, 2_000_000 - usage['used']):,}"
    )
    messagebox.showinfo("Статистика", info)

# 🧪 Пример использования
def simulate_translation():
    sample_text = "Это пример текста для перевода."
    char_count = len(sample_text)
    save_usage(char_count)
    show_usage()

# 🖼️ Мини-GUI
root = tk.Tk()
root.title("Тест учёта символов")
root.geometry("300x150")

btn = tk.Button(root, text="Симулировать перевод", command=simulate_translation)
btn.pack(pady=20)

stats_btn = tk.Button(root, text="Показать статистику", command=show_usage)
stats_btn.pack()

root.mainloop()