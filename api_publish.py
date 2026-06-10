#!/usr/bin/env python3
"""
头条微头条 HTTP API 直接发布脚本 v1.0
用法：
  export DBUS_SESSION_BUS_ADDRESS=unix:path=/tmp/dbus-dqw1NcGgZq
  python3 api_publish.py                      # 使用默认内容
  python3 api_publish.py "你的微头条内容..."  # 自定义内容
"""
import os, sys, json, datetime, browser_cookie3
import requests

# ===== 配置 =====
COOKIE_DB = '/tmp/chromium-debug/Default/Cookies'
API_URL = "https://mp.toutiao.com/mp/agw/article/wtt"
PUBLISH_LOG = os.path.join(os.path.dirname(__file__), "publish_history.json")

# ===== Cookie 解密 =====
def get_cookies_and_csrf():
    dbus_addr = os.environ.get('DBUS_SESSION_BUS_ADDRESS', '')
    if not dbus_addr:
        os.environ['DBUS_SESSION_BUS_ADDRESS'] = 'unix:path=/tmp/dbus-rV5MzDZHDR'
    cj = browser_cookie3.chrome(cookie_file=COOKIE_DB)
    cookies = {}
    csrf = None
    for c in cj:
        if 'toutiao' in c.domain:
            cookies[c.name] = c.value
            if c.name == 'passport_csrf_token':
                csrf = c.value
    return cookies, csrf

# ===== 发布 =====
def publish(content, cookies, csrf_token):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/147.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "X-CSRFToken": csrf_token or "",
        "Origin": "https://mp.toutiao.com",
        "Referer": "https://mp.toutiao.com/profile_v4/weitoutiao/publish",
    }
    payload = {
        "content": content,
        "image_list": [],
        "extra": json.dumps({
            "claim_exclusive": "1",
            "add_music_to_article_flag": "0",
            "tuwen_wtt_trans_flag": "0",
            "info_source": json.dumps({"source_type": -1})
        }, ensure_ascii=False),
        "is_fans_article": 2,
        "pre_upload": 1,
        "welfare_card": "",
        "entrance": "main"
    }
    resp = requests.post(API_URL, headers=headers, cookies=cookies, json=payload, timeout=30)
    return resp.status_code, resp.json()

# ===== 记录日志 =====
def log_publish(content, result):
    history = {"history": []}
    if os.path.exists(PUBLISH_LOG):
        try:
            with open(PUBLISH_LOG) as f:
                history = json.load(f)
        except: pass
    record = {
        "timestamp": datetime.datetime.now().isoformat(),
        "content": content[:100],
        "result": result
    }
    history["history"].append(record)
    with open(PUBLISH_LOG, 'w') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# ===== 默认内容 =====
DEFAULT_CONTENT = """Spring Boot 项目启动慢？试试这 3 招：
1. 懒初始化：spring.main.lazy-initialization=true，启动时间缩短 60%
2. 排除多余自动配置：@SpringBootApplication(exclude = {...})
3. 用 -Dspring.profiles.active=dev 按需加载
#Java #SpringBoot #编程"""

# ===== 主入口 =====
if __name__ == '__main__':
    content = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CONTENT
    print(f"📝 内容长度: {len(content)} 字")
    print("🔑 获取 Cookie...")
    cookies, csrf = get_cookies_and_csrf()
    print(f"   Cookie: {len(cookies)} 个")
    print(f"   CSRF:   {csrf}")
    print("🚀 发布中...")
    status, data = publish(content, cookies, csrf)
    if status == 200 and data.get("code") == 0:
        tid = data["data"]["thread_id"]
        print(f"✅ 发布成功！thread_id: {tid}")
        log_publish(content, data)
    else:
        print(f"❌ 失败: HTTP {status} | {data}")
        log_publish(content, {"error": f"HTTP {status}", "response": data})
