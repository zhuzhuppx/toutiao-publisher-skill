# Toutiao Publisher - 头条发布自动化

## 📌 一句话介绍

基于浏览器自动化的微头条发布工具，支持一键生成内容、智能去重、批量发布全流程自动化。

---

## 🚀 快速开始

### **方式一：直接运行（推荐新手）**

```bash
cd /app/working/workspaces/default

# 单篇发布（随机主题）
python -m active_skills.toutiao_publisher.main

# 指定主题发布
python -m active_skills.toutiao_publisher.main --topic "AI 科技"

# 批量发布 3 篇
python -m active_skills.toutiao_publisher.main --count 3
```

### **方式二：Python 代码调用**

```python
from active_skills.toutiao_publisher.main import ToutiaoPublisher

publisher = ToutiaoPublisher()

# 发布一篇 AI 科技文章
result = publisher.publish_article(topic="AI 科技", batch_size=1)

print(f"发布结果：{result}")
```

---

## 📋 使用场景

| 场景 | 命令示例 | 说明 |
|------|---------|------|
| 日常更新 | `--count 2` | 早晚各 1 篇 |
| 专题推广 | `--topic "AI 科技" --count 3` | 连续发布同一主题系列 |
| 测试验证 | `test_skill.py` | 运行自动化测试 |
| 查看历史 | `cat publish_history.json` | 已发文章列表 |

---

## ⚙️ 参数说明

| 参数 | 类型 | 默认值 | 可选值 | 说明 |
|------|------|--------|--------|------|
| `--topic` | string | None | 任意主题类别 | 指定发布主题，不填则随机 |
| `--count` | int | 1 | 1, 2, 3 | 批量发布数量（最多 3 篇） |

---

## 🎯 支持的发布主题

- ✅ **AI 科技** - 人工智能、大模型、工具推荐
- ✅ **理财知识** - 基金股票、保险配置、储蓄技巧
- ✅ **健康养生** - 运动健身、饮食调理、常见病
- ✅ **职场成长** - 面试求职、沟通技巧、升职加薪
- ✅ **亲子教育** - 学习习惯、兴趣培养、心理健康
- ✅ **情感关系** - 婚姻经营、两性相处、社交心理
- ✅ **生活妙招** - 家务整理、收纳技巧、省钱攻略
- ✅ **数码测评** - 手机电脑、智能家居、外设配件

---

## 🔧 常见问题

### Q: 启动时提示 `ProcessSingleton for your profile directory`？
**A**: 这是 Chrome 锁冲突导致的。执行以下命令清理：
```bash
pkill -9 chrome chromium
```

### Q: 发布的文章在哪里可以查看？
**A**: 
1. 登录头条号后台
2. 进入「作品管理」→「所有作品」
3. 按时间倒序找到最新发布的文章

### Q: 如何知道哪些主题已经发过了？
**A**: 查看 `publish_history.json` 文件：
```bash
cat /app/working/workspaces/default/publish_history.json
```

### Q: 为什么发布按钮点击没反应？
**A**: 
- 检查浏览器是否已登录头条账号
- 确认视口宽度设置为 1401px
- 尝试手动滚动页面触发自定义元素渲染

### Q: 可以自定义文案内容吗？
**A**: 当前版本为自动生成模式。如需自定义内容，可以修改 `main.py`中的 `_generate_content()` 方法。

---

## 📊 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| 单次发布耗时 | ~2-3 分钟 | 包含加载、生成、发布全流程 |
| 批量最大数量 | 3 篇 | 建议每次不超过此数 |
| 内容字数范围 | 200-350 字 | 符合头条爆款区间 |
| 主题池大小 | 52+ 话题 | 8 大类×6-7 个子话题 |

---

## 🛡️ 安全提醒

1. **不要频繁发布** - 每日建议不超过 6 篇，避免被判定为营销号
2. **定期清理缓存** - 每周删除一次浏览器 Profile 数据
3. **备份重要数据** - `publish_history.json` 可定期备份
4. **账号保护** - 不要在公共环境下运行脚本

---

## 📈 未来规划

- [ ] v5.1 - 多账号并发管理
- [ ] v5.2 - 数据分析报表生成
- [ ] v5.3 - 粉丝增长预测模型
- [ ] v5.4 - AI 内容质量评分系统

---

## 💬 反馈与支持

遇到问题或有改进建议？请通过以下方式联系我们：
- GitHub Issue: 提交问题描述
- 企业微信：CoPaw 技术频道
- 邮件：zhusiyuanhao@163.com

---

*最后更新时间：2026-03-30*  
*维护者：ZhuSiYuan*
