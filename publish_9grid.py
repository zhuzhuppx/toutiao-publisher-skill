#!/usr/bin/env python3
"""九宫格微头条发布 - 一次上传9张 + API发布"""
import os, sys, json, asyncio, requests
from playwright.async_api import async_playwright

API_URL = "https://mp.toutiao.com/mp/agw/article/wtt"
CDP_URL = 'http://localhost:9222'
IMG_DIR = '/tmp/baidu_imgs'

async def main():
    img_files = sorted([f for f in os.listdir(IMG_DIR) 
                       if f.endswith('.jpg') and f != 'sweet_jp_girls.zip'])[:9]
    img_paths = [os.path.join(IMG_DIR, f) for f in img_files]
    print(f'[*] 准备上传 {len(img_paths)} 张图片...')

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        page = browser.contexts[0].pages[-1]

        await page.goto('https://mp.toutiao.com/profile_v4/weitoutiao/publish',
                         wait_until='domcontentloaded')
        await page.wait_for_timeout(3000)
        await page.evaluate('() => document.querySelectorAll("[class*=drawer]").forEach(e => e.remove())')

        # 监听所有上传响应
        image_uris = []
        def on_upload_response(response):
            if 'spice/image' in response.url and response.status == 200:
                async def get():
                    data = await response.json()
                    uri = data.get('data', {}).get('image_uri', '')
                    if uri and uri not in image_uris:
                        image_uris.append(uri)
                        print(f'  [+] 上传成功 ({len(image_uris)}/{len(img_paths)})')
                asyncio.ensure_future(get())
        page.on('response', on_upload_response)

        # 尝试一次性上传多个文件
        await page.evaluate('() => { document.querySelector("button.syl-toolbar-button")?.click(); }')
        await page.wait_for_timeout(800)
        
        # 用 set_input_files 传入文件列表（支持 multiple）
        file_input = page.locator('input[type="file"]').first
        await file_input.set_input_files(img_paths)
        print('[*] 文件已提交，等待上传完成...')
        
        # 等待所有图片上传完成
        for _ in range(30):
            await page.wait_for_timeout(1000)
            if len(image_uris) >= len(img_paths):
                break
            print(f'  ...已上传 {len(image_uris)}/{len(img_paths)}')

        print(f'\n[*] 成功上传 {len(image_uris)}/{len(img_paths)} 张')

        if not image_uris:
            print('[!] 全部上传失败')
            await browser.close()
            return

        # 提取Cookie
        cookies_list = await page.context.cookies()
        cookies = {c['name']: c['value'] for c in cookies_list if 'toutiao' in c['domain']}
        csrf = cookies.get('passport_csrf_token', '')

        # 发布
        content = '日系甜美清新九宫格来啦！🌸 每一张都是治愈系，你最心动哪一张？评论区告诉我！👇 #日系 #清新 #甜妹 #治愈系'

        extra = json.dumps({
            'claim_exclusive': '1', 'add_music_to_article_flag': '0',
            'tuwen_wtt_trans_flag': '0',
            'info_source': json.dumps({'source_type': -1}, ensure_ascii=False)
        }, ensure_ascii=False)

        payload = {
            'content': content,
            'image_list': image_uris[:9],
            'extra': extra,
            'is_fans_article': 2, 'pre_upload': 1, 'welfare_card': '', 'entrance': 'main'
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/147.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf,
            'Origin': 'https://mp.toutiao.com',
            'Referer': 'https://mp.toutiao.com/profile_v4/weitoutiao/publish',
        }

        resp = requests.post(API_URL, headers=headers, cookies=cookies,
                           data=json.dumps(payload, ensure_ascii=False), timeout=30)
        result = resp.json()
        print(f'\n[Publish] HTTP {resp.status_code}, code={result.get("code")}, msg={result.get("message")}')
        if result.get('code') == 0:
            tid = result['data']['thread_id']
            print(f'[✓] 九宫格发布成功! thread_id: {tid}')
        else:
            print(f'[✗] 失败: {result.get("message")}')

        await browser.close()

asyncio.run(main())
