#!/usr/bin/env python3
"""快速带图发布 — 从浏览器直取 cookie + 上传图片 + API 发布"""
import os, sys, json, asyncio, requests
from playwright.async_api import async_playwright

API_URL = "https://mp.toutiao.com/mp/agw/article/wtt"
CDP_URL = 'http://localhost:9222'

async def main(content, image_path):
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        page = browser.contexts[0].pages[-1]

        # 1. 上传图片
        await page.goto('https://mp.toutiao.com/profile_v4/weitoutiao/publish',
                         wait_until='domcontentloaded')
        await page.wait_for_timeout(3000)
        await page.evaluate('() => document.querySelectorAll("[class*=drawer]").forEach(e => e.remove())')

        upload_result = {}
        def on_response(response):
            if 'spice/image' in response.url and response.status == 200:
                async def get():
                    data = await response.json()
                    upload_result['data'] = data
                asyncio.ensure_future(get())
        page.on('response', on_response)

        await page.evaluate('() => { document.querySelector("button.syl-toolbar-button")?.click(); }')
        await page.wait_for_timeout(1000)
        file_input = page.locator('input[type="file"]').first
        await file_input.set_input_files(image_path)
        await page.wait_for_timeout(5000)

        img_uri = upload_result.get('data', {}).get('data', {}).get('image_uri', '')
        print(f'[✓] 图片上传: image_uri = {img_uri}')

        # 2. 从浏览器拿 cookie
        cookies_list = await page.context.cookies()
        cookies = {c['name']: c['value'] for c in cookies_list if 'toutiao' in c['domain']}
        csrf = cookies.get('passport_csrf_token', '')
        print(f'[✓] Cookie: {len(cookies)} 个, CSRF: {csrf[:20]}...')

        # 3. 发布
        extra = json.dumps({
            'claim_exclusive': '1', 'add_music_to_article_flag': '0',
            'tuwen_wtt_trans_flag': '0',
            'info_source': json.dumps({'source_type': -1}, ensure_ascii=False)
        }, ensure_ascii=False)

        payload = {
            'content': content,
            'image_list': [img_uri] if img_uri else [],
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
            print(f'[✓] 带图发布成功! thread_id: {tid}')
        else:
            print(f'[✗] 失败')

        await browser.close()

if __name__ == '__main__':
    content = sys.argv[1] if len(sys.argv) > 1 else '做了10年Java开发，今天说句得罪人的大实话：90%的项目根本不需要微服务。单体架构能扛到百万用户，微服务的复杂度却能把团队拖垮。技术选型不是选最火的，而是选最合适的。你站微服务还是单体？评论区说说你的理由！'
    image = sys.argv[2] if len(sys.argv) > 2 else '/tmp/tech_image.png'
    asyncio.run(main(content, image))
