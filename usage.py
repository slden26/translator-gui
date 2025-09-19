import json
from datetime import datetime
from tkinter import messagebox

USAGE_PATH = "usage.json"
MAX_LIMIT = 2_000_000
WARNING_THRESHOLD = int(0.9 * MAX_LIMIT)

def load_usage():
    try:
        with open(USAGE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"month": datetime.now().strftime("%Y-%m"), "used": 0}

def save_usage(char_count, engine_name):
    if engine_name.lower() != "microsoft":
        return  # лимит учитывается только для Microsoft

    usage = load_usage()
    current_month = datetime.now().strftime("%Y-%m")

    if usage.get("month") != current_month:
        usage = {"month": current_month, "used": 0}

    usage["used"] += char_count
    if usage["used"] > MAX_LIMIT:
        usage["used"] = MAX_LIMIT

    with open(USAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(usage, f, ensure_ascii=False, indent=2)

    if usage["used"] >= WARNING_THRESHOLD:
        messagebox.showwarning(
            "Лимит почти исчерпан",
            f"Вы использовали {usage['used']:,} символов из {MAX_LIMIT:,}."
        )