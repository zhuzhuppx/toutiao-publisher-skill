#!/usr/bin/env python3
"""记录本次发布的图片URI到image_usage.json"""
import json, datetime, os

USAGE_FILE = os.path.join(os.path.dirname(__file__), "image_usage.json")

# 刚发的9张图image_uri（从publish_9grid输出可知）
uris = [
    "tos-cn-i-ezhpy3drpa/f7123913f8e04e5fa34a3e110a8b56d7",
    "tos-cn-i-ezhpy3drpa/9ca1593678a746bbb896cb84a000732e",
    "tos-cn-i-ezhpy3drpa/786f6adfcc824f31bb039a404107de62",
    "tos-cn-i-ezhpy3drpa/84ab5cf305a54538b2fa78c3a139a7ad",
    "tos-cn-i-ezhpy3drpa/20e31f866e47409099ecb763993f0ca0",
    "tos-cn-i-ezhpy3drpa/626117b11a3444928bf19d1e4e1dda96",
    "tos-cn-i-ezhpy3drpa/97a44813355c4ee88bc802f4aee5d12f",
    "tos-cn-i-ezhpy3drpa/6eade4274762431f9a07f1fad6162f27",
    "tos-cn-i-ezhpy3drpa/6a3b1ab8be0446e4890ee5329d87ef37",
]

# 读取已有记录
usage = {"images": []}
if os.path.exists(USAGE_FILE):
    try:
        with open(USAGE_FILE) as f:
            usage = json.load(f)
    except:
        pass

today = datetime.date.today().isoformat()
for uri in uris:
    usage["images"].append({
        "image_uri": uri,
        "date": today,
        "thread_id": "1867599766011020"
    })

with open(USAGE_FILE, 'w') as f:
    json.dump(usage, f, ensure_ascii=False, indent=2)

print(f'[✓] 已记录 {len(uris)} 张图片到 {USAGE_FILE}')
