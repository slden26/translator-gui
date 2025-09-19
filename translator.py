import json
import requests
import os

try:
    from googletrans import Translator as GoogleTranslator
except ImportError:
    GoogleTranslator = None

def translate(text, src, tgt):
    # 🔧 Загружаем конфигурацию
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        return "[Ошибка: не удалось загрузить config.json]"

    engine = cfg.get("engine", "google").lower()
    print(f"[DEBUG] Выбран движок: {engine}")

    # 🌐 Google Translate
    if engine == "google":
        if not GoogleTranslator:
            return "[Ошибка: googletrans не установлен]"
        try:
            translator = GoogleTranslator()
            result = translator.translate(text, src=src, dest=tgt)
            return result.text
        except Exception as e:
            return f"[Google ошибка: {e}]"

    # 🧬 DeepL
    if engine == "deepl":
        key = cfg.get("deepl_key", "")
        if not key:
            return "[Ошибка: отсутствует ключ DeepL]"
        try:
            url = "https://api-free.deepl.com/v2/translate"
            data = {
                "auth_key": key,
                "text": text,
                "source_lang": src.upper(),
                "target_lang": tgt.upper()
            }
            response = requests.post(url, data=data)
            response.raise_for_status()
            return response.json()["translations"][0]["text"]
        except Exception as e:
            return f"[DeepL ошибка: {e}]"

    # 🛰️ Lingvanex
    if engine == "lingvanex":
        token = cfg.get("lingvanex_token", "")
        if not token:
            return "[Ошибка: отсутствует токен Lingvanex]"
        try:
            url = "https://api-b2b.backenster.com/b1/api/v3/translate"
            headers = {"Authorization": f"Bearer {token}"}
            payload = {
                "from": src,
                "to": tgt,
                "data": text,
                "platform": "api"
            }
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()["result"]
        except Exception as e:
            return f"[Lingvanex ошибка: {e}]"

    # 🔒 Локальный заглушка
    if engine == "local":
        return f"[{src}→{tgt}] {text}"

    # 🏢 Microsoft Translator
    if engine == "microsoft":
        key = cfg.get("subscription_key", "")
        region = cfg.get("region", "")
        if not key or not region:
            return "[Ошибка: отсутствует ключ Microsoft Translator]"
        try:
            endpoint = "https://api.cognitive.microsofttranslator.com"
            path = "/translate?api-version=3.0"
            params = f"&from={src}&to={tgt}"
            url = endpoint + path + params
            headers = {
                "Ocp-Apim-Subscription-Key": key,
                "Ocp-Apim-Subscription-Region": region,
                "Content-type": "application/json"
            }
            body = [{"text": text}]
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()
            return response.json()[0]["translations"][0]["text"]
        except Exception as e:
            return f"[Microsoft ошибка: {e}]"

    # ❌ Неизвестный движок
    return f"[Ошибка: неизвестный движок '{engine}']"