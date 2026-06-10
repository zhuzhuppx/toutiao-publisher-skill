#!/usr/bin/env python3
"""
头条微头条 HTTP API 发布脚本 v1.1 — 支持图片
用法：
  export DBUS_SESSION_BUS_ADDRESS=unix:path=/tmp/dbus-xxx
  python3 api_publish_img.py                          # 使用默认内容+图片
  python3 api_publish_img.py "你的内容"               # 自定义内容+自动上传图片
  python3 api_publish_img.py "内容" "/path/to/img.png" # 自定义内容+自定义图片
"""
import os, sys, json, datetime, asyncio
import requests
from playwright.async_api import async_playwright

# ===== 配置 =====
COOKIE_DB = '/tmp/chromium-debug/Default/Cookies'
API_URL = "https://mp.toutiao.com/mp/agw/article/wtt"
PUBLISH_LOG = os.path.join(os.path.dirname(__file__), "publish_history.json")
CDP_URL = 'http://localhost:9222'

# ===== 图片上传（通过浏览器 Playwright） =====
async def upload_image_async(image_path):
    """
    通过浏览器 CDP 上传图片，返回 image_uri
    """
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        page = browser.contexts[0].pages[-1]
        
        # 打开发布页
        await page.goto('https://mp.toutiao.com/profile_v4/weitoutiao/publish', 
                         wait_until='domcontentloaded')
        await page.wait_for_timeout(3000)
        
        # 移除弹窗遮罩
        await page.evaluate('() => document.querySelectorAll("[class*=drawer]").forEach(e => e.remove())')
        await page.wait_for_timeout(500)
        
        # 监听上传响应
        upload_result = {}
        def on_response(response):
            if 'spice/image' in response.url and response.status == 200:
                async def get():
                    data = await response.json()
                    upload_result['data'] = data
                asyncio.ensure_future(get())
        page.on('response', on_response)
        
        # 点击图片按钮
        await page.evaluate('() => { document.querySelector("button.syl-toolbar-button")?.click(); }')
        await page.wait_for_timeout(1000)
        
        # 上传图片
        file_input = page.locator('input[type="file"]').first
        await file_input.set_input_files(image_path)
        await page.wait_for_timeout(5000)
        
        # 获取 image_uri
        data = upload_result.get('data', {}).get('data', {})
        img_uri = data.get('image_uri', '')
        
        await browser.close()
        return img_uri

def upload_image(image_path):
    """同步包装"""
    return asyncio.run(upload_image_async(image_path))

# ===== 获取 Cookie（browser-cookie3 方式） =====
def get_cookies_and_csrf():
    import browser_cookie3
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
def publish(content, cookies, csrf_token, image_uri=''):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/147.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "X-CSRFToken": csrf_token or "",
        "Origin": "https://mp.toutiao.com",
        "Referer": "https://mp.toutiao.com/profile_v4/weitoutiao/publish",
    }
    payload = {
        "content": content,
        "image_list": [image_uri] if image_uri else [],
        "extra": json.dumps({
            "claim_exclusive": "1",
            "add_music_to_article_flag": "0",
            "tuwen_wtt_trans_flag": "0",
            "info_source": json.dumps({"source_type": -1}, ensure_ascii=False)
        }, ensure_ascii=False),
        "is_fans_article": 2,
        "pre_upload": 1,
        "welfare_card": "",
        "entrance": "main"
    }
    resp = requests.post(API_URL, headers=headers, cookies=cookies,
                        json=payload, timeout=30)
    return resp.status_code, resp.json()

# ===== 记录日志 =====
def log_publish(content, image_uri, result):
    history = {"history": []}
    if os.path.exists(PUBLISH_LOG):
        try:
            with open(PUBLISH_LOG) as f:
                history = json.load(f)
        except: pass
    record = {
        "timestamp": datetime.datetime.now().isoformat(),
        "content": content[:100],
        "has_image": bool(image_uri),
        "result": result
    }
    history["history"].append(record)
    with open(PUBLISH_LOG, 'w') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# ===== 默认内容（带争议标题） =====
DEFAULT_CONTENT = '做了10年Java开发，今天说句大实话：微服务架构真的被过度神话了。90%的项目用单体架构完全够用，强行拆分反而引入分布式事务、服务调用链路、部署复杂度等问题。技术选型不是选最火的，而是选最合适的。你们项目组也在拆微服务吗？效果怎么样？欢迎评论区聊聊。'
DEFAULT_IMAGE = '/tmp/tech_image.png'

# ===== 主入口 =====
if __name__ == '__main__':
    content = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CONTENT
    image_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_IMAGE
    
    # 上传图片
    print(f"[*] 上传图片: {image_path} ...")
    img_uri = upload_image(image_path) if os.path.exists(image_path) else ''
    if img_uri:
        print(f"[✓] 图片上传成功! image_uri: {img_uri}")
    else:
        print("[!] 无图片或上传失败，纯文字发布")
    
    # 获取 Cookie
    print("[*] 获取 Cookie ...")
    cookies, csrf = get_cookies_and_csrf()
    print(f"[✓] Cookie: {len(cookies)} 个, CSRF: {csrf[:20]}...")
    
    # 发布
    print(f"[*] 发布微头条 (含图片: {bool(img_uri)})...")
    code, result = publish(content, cookies, csrf, img_uri)
    
    if code == 200 and result.get('code') == 0:
        tid = result['data']['thread_id']
        print(f"[✓] 发布成功! thread_id: {tid}")
        if img_uri:
            print(f"[✓] 含图片发布: {img_uri[:40]}...")
    else:
        print(f"[✗] 发布失败: HTTP {code}, code={result.get('code')}, msg={result.get('message')}")
    
    log_publish(content, img_uri, result)
    print(f"[*] 日志已记录到 {PUBLISH_LOG}")
