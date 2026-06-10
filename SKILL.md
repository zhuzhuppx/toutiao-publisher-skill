# Toutiao Publisher Skill v9.0 — HTTP API 直接发布 + 流量优化策略

## 📋 功能概述

通过 HTTP API 直接发布微头条，无需浏览器自动化。

**两种方式：**
| 方式 | 适用场景 | 需要 |
|------|---------|------|
| 🏆 **API 直接调用**（推荐） | 日常发布 | Cookie 解密 + requests |
| 🔍 Playwright 浏览器注入 | 调试/验证/首次探索 | Playwright + 浏览器 |

---

## 🔧 前置条件

### 1. Chrome 用户数据目录（用于保存 Cookie）
已在服务器上以 `--user-data-dir=/tmp/chromium-debug` 启动过 Chrome 并完成扫码登录，Cookie 持久保存在 `/tmp/chromium-debug/Default/Cookies` 中。

> **Cookie 过期说明**：头条 Cookie 有效期较长（通常数天到数周），只要不频繁切换账号、不触发风控，可长期复用。若 Cookie 过期会收到 `{"code":100005,"message":"获取用户信息失败"}` 错误，需重新扫码。

### 2. 依赖包
```bash
# 核心依赖
pip install requests browser-cookie3
```

### 3. DBus 会话（Cookie 解密必需）
```bash
export DBUS_SESSION_BUS_ADDRESS=unix:path=/tmp/dbus-ucYCI7IqwW
```

---

## 🚀 方式一：HTTP API 直接发布（推荐）

### 完整脚本

```python
#!/usr/bin/env python3
"""直接 HTTP API 发布微头条"""
import os, json, requests
import browser_cookie3

# 1. 解密 Cookie
os.environ['DBUS_SESSION_BUS_ADDRESS'] = 'unix:path=/tmp/dbus-dqw1NcGgZq'
cj = browser_cookie3.chrome(cookie_file='/tmp/chromium-debug/Default/Cookies')

cookies_dict = {}
csrf_token = None
for c in cj:
    if 'toutiao' in c.domain:
        cookies_dict[c.name] = c.value
        if c.name == 'passport_csrf_token':
            csrf_token = c.value

# 2. 准备内容
content = """Spring Boot 项目启动慢？试试这 3 招：
1. 懒初始化：spring.main.lazy-initialization=true，启动时间缩短 60%
2. 排除多余自动配置：@SpringBootApplication(exclude = {...})
3. 用 -Dspring.profiles.active=dev 按需加载
#Java #SpringBoot #编程"""

# 3. 调用发布 API
url = "https://mp.toutiao.com/mp/agw/article/wtt"
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
        "claim_exclusive": "1",           # 头条首发
        "add_music_to_article_flag": "0",
        "tuwen_wtt_trans_flag": "0",
        "info_source": json.dumps({"source_type": -1})
    }, ensure_ascii=False),
    "is_fans_article": 2,
    "pre_upload": 1,
    "welfare_card": "",
    "entrance": "main"
}

resp = requests.post(url, headers=headers, cookies=cookies_dict, json=payload, timeout=30)

if resp.status_code == 200:
    data = resp.json()
    if data.get("code") == 0:
        thread_id = data["data"]["thread_id"]
        print(f"✅ 发布成功！thread_id: {thread_id}")
    else:
        print(f"❌ 发布失败: {resp.text}")
else:
    print(f"❌ HTTP 错误: {resp.status_code} - {resp.text}")
```

### API 参数详解

| 参数 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `content` | ✅ | string | 微头条正文，200-350 字最佳 |
| `image_list` | ✅ | array | 图片数组，无图传 `[]` |
| `extra` | ✅ | string(JSON) | 附加选项，JSON 字符串 |
| `is_fans_article` | ✅ | int | `2` = 普通发布 |
| `pre_upload` | ✅ | int | `1` |
| `entrance` | ✅ | string | `"main"` |

### extra 字段详解

```python
{
    "claim_exclusive": "1",           # "1"=头条首发, "0"=非首发
    "add_music_to_article_flag": "0",  # "1"=添加音乐
    "tuwen_wtt_trans_flag": "0",       # 图文转微头条
    "info_source": '{"source_type": -1}'  # 信息来源(-1=原创)
}
```

### Cookie 关键字段

| Cookie 名 | 用途 |
|-----------|------|
| `sessionid` / `sid_tt` | 登录会话标识 |
| `passport_csrf_token` | CSRF 令牌（❕必须作为 `X-CSRFToken` 请求头） |
| `csrf_session_id` | 备用 CSRF 令牌 |
| `uid_tt` | 用户 ID |

---

## 🔍 方式二：Playwright 浏览器注入（调试用）

当 API 调用失效、需调试页面状态或首次探索时使用。

### 完整流程

```python
#!/usr/bin/env python3
import asyncio, os, json
import browser_cookie3
from playwright.async_api import async_playwright

# 1. 解密 Cookie
os.environ['DBUS_SESSION_BUS_ADDRESS'] = 'unix:path=/tmp/dbus-dqw1NcGgZq'
cj = browser_cookie3.chrome(cookie_file='/tmp/chromium-debug/Default/Cookies')
cookies = {c.name: c.value for c in cj if 'toutiao' in c.domain}

# 2. 注入 Cookie 到 Playwright
pw_cookies = []
for name, value in cookies.items():
    pw_cookies.append({
        'name': name, 'value': value,
        'domain': '.mp.toutiao.com', 'path': '/',
        'httpOnly': False, 'secure': True, 'sameSite': 'Lax'
    })

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1400, 'height': 900}
        )
        page = await context.new_page()

        # 关键：先访问根域名（允许重定向），再注入 Cookie
        await page.goto("https://mp.toutiao.com", wait_until="domcontentloaded")
        await context.add_cookies(pw_cookies)

        # 导航到发布页
        await page.goto("https://mp.toutiao.com/profile_v4/weitoutiao/publish",
                        wait_until="networkidle")
        await asyncio.sleep(3)

        # 3. 填充内容（ProseMirror 编辑器）
        editor = page.locator('[contenteditable="true"]')
        await editor.click()
        await editor.fill("")
        await page.type('[contenteditable="true"]', "你的微头条内容...", delay=10)

        # 4. 处理发文助手遮罩（如果出现）
        try:
            mask = page.locator('.arco-drawal-mask, [class*="drawer"], [class*="Drawer"]')
            if await mask.is_visible(timeout=3000):
                await page.evaluate("""
                    () => {
                        document.querySelectorAll('.arco-drawer-mask, [class*="mask"]')
                            .forEach(el => el.remove());
                    }
                """)
        except:
            pass

        # 5. 勾选"头条首发"
        await page.evaluate("""
            () => document.querySelector('[class*="checkbox"]')?.click()
        """)

        # 6. 点击发布
        await page.evaluate("""
            () => {
                const btn = document.querySelector('button:has-text("发布")');
                if (btn) {
                    btn.scrollIntoView();
                    btn.click();
                }
            }
        """)

        # 7. 等待发布结果
        await asyncio.sleep(8)
        print(f"最终 URL: {page.url}")

asyncio.run(main())
```

---

## 🧠 Cookie 解密原理

Chrome >= v127 加密 Cookie 存储方式：
- 文件：`Default/Cookies`（SQLite 数据库）
- Cookie 值在 `encrypted_value` 列中，AES-256-GCM（v10 格式）加密
- 加密密钥存储在系统 keyring 中

### 解密流程

```
Chrome → Cookie SQLite (encrypted_value BLOB)
                                 ↓
                              libsecret (AES key)
                                 ↓
                         browser_cookie3 自动解密
                                 ↓
                             明文 Cookie
```

关键点：
1. `browser_cookie3.chrome(cookie_file=...)` 自动调用 libsecret 解密
2. 需要 `DBUS_SESSION_BUS_ADDRESS` 环境变量指向运行中的 dbus-daemon
3. 不需要安装 gnome-keyring-daemon，DBus 服务本身就能解密

---

## ⚠️ 错误码对照

| code | message | 原因 | 解决 |
|------|---------|------|------|
| 0 | - | ✅ 成功 | - |
| 100005 | 获取用户信息失败 | Cookie 过期/无效 | 重新扫码登录 |
| 7050 | 保存失败 | Payload 格式错误或 CSRF 缺失 | 检查 payload 结构 + CSRF 头 |
| 10xxx | - | 内容违规 | 调整措辞，移除敏感词 |

---

## 📝 内容策略 v9.0（流量优化版）

### 🎯 核心原则：流量优先，干货次之

头条算法更倾向推荐有争议、有情绪、有互动的内容。纯干货只有搜到的人才会看。

### 📊 内容配比

| 内容类型 | 比例 | 定位 | 目的 |
|---------|:----:|------|------|
| 有争议的技术观点 | 40% | 抛出反常识/争议观点 | 引发评论争论，算法加权 |
| 热点+技术结合 | 30% | 追热点时事+技术视角解读 | 蹭热点流量池 |
| 实用技术干货 | 20% | 纯干货分享 | 建立专业形象 |
| AI 生图经验 | 10% | AI 生图实战 | 账号定位差异化 |

### 🔥 标题公式（最重要！）

| 公式 | 示例 | 原理 |
|------|------|------|
| `千万别{做X}！{Y}年经验的血泪教训` | 千万别这样拆分微服务！5 年踩坑总结 | 恐惧+好奇心 |
| `{数字}个{主题}，{效果}` | 3 个 Spring Boot 配置，让接口快 10 倍 | 数字明确+效果可量化 |
| `我{做了啥}，结果{反差}` | 我用 AI 审查代码 3 个月，团队差点崩了 | 故事化+反差 |
| `{热点事件}，程序员怎么看？` | 茅台又涨价，程序员却笑了 | 蹭热点+身份代入 |
| `停止{错误做法}！试试这{数字}招` | 停止 SELECT *！这 5 个优化立竿见影 | 否定+解决方案 |
| `{技术}过时了？{新技术}才是未来` | Spring Boot 过时了？K8s+GraalVM 才是未来 | 争议引发辩论 |

### ✍️ 正文结构优化

```
{标题式开头 - 一句话抓眼球，直接抛出观点/问题}

{核心论点展开 - 2-4 个要点，每个要点有数据/故事支撑}

{反方/争议点 - 主动提出"有人可能会说..."，然后反驳}

{互动钩子 - 强引导："你赞成吗？评论区见分晓"}

{标签 - 3 个，包含 1 个大流量标签 + 1 个精准标签}
```

### 🖼️ 配图策略（重要）

有配图的微头条推荐权重更高。建议：
- 每篇配 1-3 张图
- 类型：代码截图 / 数据表格图 / AI 生成配图
- 图片需先上传至头条图床，获取 `image_uri` 后填入 `image_list`

**图片上传流程：**
1. 打开浏览器发布页 `https://mp.toutiao.com/profile_v4/weitoutiao/publish`
2. 点击工具栏「图片」按钮，在弹出的文件选择器中选取本地图片
3. 上传成功后，拦截响应 `POST /spice/image`，返回 JSON 中包含 `data.image_uri`
4. 将 `image_uri` 值（如 `tos-cn-i-ezhpy3drpa/xxx...`）填入 publish payload 的 `image_list` 字段

**⚠️ 关键发现**：`image_list` 字段必须使用 **`image_uri`**（短格式），**不要**使用 `image_url`（完整 URL）。使用 `image_url` 会导致 `code:303 "微头条为空"` 错误。

**示例 payload（含图片）：**
```json
{
  "content": "...",
  "image_list": ["tos-cn-i-ezhpy3drpa/47b34ce6f2e04a47b9b6058a45164f7b"],
  "extra": "{\"claim_exclusive\":\"1\",...}",
  ...
}
```

### 💬 互动引导技巧

1. **开篇埋争议**：第一句就抛出让人想反驳的观点
2. **结尾强引导**：不要"你怎么看"，用"你赞成吗？评论区见！"
3. **评论区自导自演**：发完后自己先评论第一条带节奏
4. **制造对立**：制造"新手 vs 老手"、"大厂 vs 小厂"的对比

### ⏰ 发布节奏

- 每天最多 2 条，间隔 6 小时以上
- 最佳发布时间：早 8-9 点、午 12-13 点、晚 19-21 点
- 周四/五发干货，周一/三发争议话题，周末发轻松热点

### 🔗 热点追踪流程

1. 打开头条热搜榜 `https://tophub.today/` 看今日热点
2. 筛选与技术/程序员相关的话题
3. 用程序员视角写热点解读（蹭流量池）
4. 标题必含热点关键词

### 📝 模板库

```
🔥【争议观点型】
{反常识观点}，说点得罪人的大实话。
...
你可能觉得我在胡说，但干过{数字}年的人都知道这是真的。
你赞成还是反对？评论区说说你的看法！

🔥【故事分享型】
我做了{数字}个月{某事}，结果{反转结果}。
{具体经历+数据}
最后说一句：{核心观点}
有同感的评论区扣 1

🔥【热点解读型】
{今日热点事件}
作为一个{角色}，我想说几句：
{技术视角分析}
{标签}
```

```
skills/toutiao_publisher/
├── SKILL.md              ← 本文件 (v9.1)
├── api_publish.py        ← HTTP API 发布脚本（纯文字版）
├── api_publish_img.py    ← HTTP API 发布脚本（支持图片，推荐）
└── publish_history.json  ← 发布日志
```

## ✅ 验证发布结果

发布成功后访问：
```
https://mp.toutiao.com/profile_v4/weitoutiao
```
列表中应出现新文章，内容与发布内容一致。

---

## 🔄 版本历史

| 版本 | 核心方法 | 状态 |
|------|---------|------|
| v1-v6 | CDP 浏览器自动化 | ❌ 已淘汰 |
| v7.0-v7.2 | CDP + 手动操作 | ❌ 已淘汰 |
| **v8.0** | **HTTP API 直接调用** | ❌ 旧版本 |
| **v9.1** | **API + 图片上传（image_uri 修正）** | ✅ **当前版本** |
| v9.0 | 流量优化+争议标题+配图+互动引导 | ❌ 旧版本 |
| v8.0 | HTTP API 直接调用 | ❌ 旧版本 |

---

*最后更新时间：2026-06-10*
*版本：v9.1 (API + 图片上传 image_uri 修正)*
*账号：老猿人 (Java + AI 生图)*
