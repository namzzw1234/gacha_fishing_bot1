# utils/database.py
# 🎃 ~ Sổ phép thuật lưu trữ linh hồn thợ câu ~ 🕯️

import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")

def load_json(filename):
    """
    🎃 Hàm triệu hồi dữ liệu từ sổ phép thuật JSON
    """
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"⚰️ File {filename} không tồn tại trong sổ phép thuật!")
        return {}
    with open(path, "r", encoding="utf8") as f:
        print(f"🕯️ Đang triệu hồi dữ liệu từ {filename}...")
        return json.load(f)

def save_json(filename, data):
    """
    🦇 Hàm niêm phong dữ liệu vào sổ phép thuật JSON
    """
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"🪄 Đã niêm phong dữ liệu vào {filename}.")