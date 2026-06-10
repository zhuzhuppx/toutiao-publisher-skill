#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Toutiao Publisher - 微头条发布自动化脚本 v5.0（演示模式）
功能：内容生成 + 历史记录管理（浏览器自动化需手动配合）
作者：ZhuSiYuan
版本：1.0.1
最后更新：2026-03-30
"""

import os
import json
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

WORKSPACE_DIR = Path("/app/working/workspaces/default")
PUBLISH_HISTORY_FILE = WORKSPACE_DIR / "publish_history.json"

# 主题池配置
TOPIC_POOL = {
    "AI 科技": [
        "如何用 AI 提升工作效率？这 5 个小技巧你必须知道",
        "大模型时代来了！普通人如何抓住风口变现？",
        "ChatGPT 之外的 10 个免费 AI 工具推荐",
        "AI 绘画入门教程：从零开始创作你的第一幅数字艺术",
        "别再手动做表格了！AI 自动生成 Excel 的神器分享"
    ],
    "理财知识": [
        "月薪 5000 如何攒下第一个 10 万？我的储蓄秘诀",
        "基金定投小白必看：选基避坑指南",
        "家庭资产配置四步法，让钱生钱不迷茫",
        "国债逆回购：闲置资金也能赚收益的理财神器",
        "保险配置攻略：如何用最少的预算获得最佳保障"
    ],
    "健康养生": [
        "久坐族必备！办公室 5 分钟拉伸动作，缓解肩颈疼痛",
        "护眼食谱 TOP10：经常盯屏幕的人一定要看",
        "失眠怎么办？4 个助眠小技巧让你一觉到天亮",
        "减肥不是节食！科学减脂的饮食结构解析",
        "冬季进补误区：这些食物越吃越虚"
    ],
    "职场成长": [
        "简历优化秘籍：HR 一眼相中的 3 个关键要素",
        "向上汇报的艺术：如何让领导记住你的成绩",
        "时间管理革命：番茄工作法的正确打开方式",
        "面试被问'你有什么缺点'？这个回答绝对加分",
        "升职加薪潜规则：比能力更重要的是这些软技能"
    ],
    "亲子教育": [
        "培养孩子阅读习惯，这 5 个方法亲测有效",
        "游戏化学习：让孩子爱上写作业的小技巧",
        "孩子情绪爆发时，爸妈应该怎么做？",
        "兴趣班太多反而伤娃？理性选择的判断标准",
        "陪读妈妈自救指南：如何平衡工作与育儿"
    ],
    "情感关系": [
        "婚姻经营的真相：好的关系是共同成长的结果",
        "夫妻吵架后，这样做能快速修复感情",
        "边界感是什么？成年人的必修课",
        "信任危机怎么破？重建关系的三个步骤",
        "两性沟通密码：听懂对方的潜台词"
    ],
    "生活妙招": [
        "断舍离实战：一年扔掉 100 件无用物品",
        "冰箱收纳公式：这样摆东西拿取超方便",
        "购物清单模板：再也不买浪费的东西",
        "省钱攻略：这样买日用品立省 30%",
        "小空间大利用：出租屋改造灵感分享"
    ],
    "数码测评": [
        "旗舰机选购指南：这几款最值得入手",
        "蓝牙耳机怎么选？参数党告诉你答案",
        "桌面改造计划：提升幸福感的神器推荐",
        "智能门锁安全吗？实测告诉你真实体验",
        "投影仪 vs 电视：小户型该选哪个？"
    ]
}


class ToutiaoPublisher:
    """头条号发布者核心类（演示模式）"""
    
    def __init__(self):
        pass  # 不再保存状态，每次从文件加载
        
    def _load_history(self) -> List[str]:
        """加载已发布记录"""
        if PUBLISH_HISTORY_FILE.exists():
            with open(PUBLISH_HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_to_history(self, content: str):
        """保存发布记录到 JSON"""
        history = self._load_history()
        # 去重检查
        if content not in history:
            history.append(content)
            with open(PUBLISH_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
    def _generate_content(self, topic: str, max_words: int = 350) -> str:
        """根据主题生成内容"""
        topics = TOPIC_POOL.get(topic, [])
        title = random.choice(topics)
        
        content_templates = [
            f"【{title}】\n\n今天想和大家聊聊这个话题...\n\n最近发现很多小伙伴对{topic}存在误解。\n其实只要掌握以下几个关键点，就能轻松应对：\n\n✨ 要点一：明确目标，制定清晰计划\n✨ 要点二：坚持执行，保持耐心\n✨ 要点三：定期复盘，及时调整策略\n\n📌 我的建议是：先从一个小目标开始，循序渐进。\n\n💬 你们有什么经验或困惑吗？欢迎评论区留言交流~\n\n# {topic} #经验分享 #个人成长",
            
            f"大家好！今天要分享的是关于{topic}的心得体会。\n\n看到最近这个话题讨论很热烈，我也来谈谈自己的看法：\n\n🔍 **现状分析**\n目前很多人对{topic}的认知还停留在表面...\n\n💡 **实用建议**\n1️⃣ 第一步：打好基础，了解核心概念\n2️⃣ 第二步：多实践，积累经验\n3️⃣ 第三步：持续学习，跟上趋势\n\n🎯 **我的观点**\n{topic}不是遥不可及的，每个人都可以通过努力掌握它。\n关键在于找到适合自己的方法和节奏。\n\n🤝 希望大家都能在这个领域有所收获！有什么疑问可以留言哦~\n\n#{topic} #干货分享 #成长日记"
        ]
        
        content = random.choice(content_templates)
        
        # 字数控制
        if len(content) > max_words:
            content = content[:max_words] + "..."
            
        return content
    
    def publish_article_demo(self, topic: str = None, batch_size: int = 1) -> Dict[str, Any]:
        """演示模式发布流程
        
        Args:
            topic: 指定主题，None 则随机选择
            batch_size: 批量发布数量（最多 3）
            
        Returns:
            发布结果汇总 dict
        """
        results = []
        
        print("\n" + "=" * 60)
        print("🚀 头条发布 - 演示模式")
        print("=" * 60 + "\n")
        
        for i in range(batch_size):
            print(f"\n{'='*60}")
            print(f"📝 第 {i+1}/{batch_size} 篇准备中...")
            print('=' * 60)
            
            try:
                # 随机选题
                if topic is None:
                    topic = random.choice(list(TOPIC_POOL.keys()))
                
                # 生成内容
                content = self._generate_content(topic)
                
                # 显示待发布内容
                print(f"\n📌 主题：{topic}")
                print(f"📊 字数：{len(content)}字")
                print(f"\n📄 正文内容:\n{'-'*40}\n{content}\n{'-'*40}\n")
                
                # 保存到草稿文件
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                draft_file = WORKSPACE_DIR / f"{timestamp}_发布草稿_{i+1}.txt"
                with open(draft_file, 'w', encoding='utf-8') as f:
                    f.write(f"主题：{topic}\n\n内容：\n{content}")
                
                print(f"\n💾 已保存到：{draft_file}")
                
                # 提示用户操作
                print(f"\n👉 草稿已保存，请自行复制发布:")
                print(f"   - 文件：{draft_file}")
                print(f"   - 网址：https://mp.toutiao.com/publish/manage/manage/?type=3")
                print(f"   - 建议：早晚各 1 篇 (8:00 / 20:00)\n")
                
                # 自动继续下一轮（演示模式）
                
                # 保存记录到结果列表
                record = {
                    "index": i + 1,
                    "topic": topic,
                    "status": "ready_for_manual_publish",
                    "draft_file": str(draft_file),
                    "content_length": len(content)
                }
                results.append(record)
                
                # 记录历史
                self._save_to_history(content)
                
                print(f"✅ 第{i+1}篇准备完成！主题：{topic}")
                
            except Exception as e:
                results.append({
                    "index": i + 1,
                    "topic": topic,
                    "status": "failed",
                    "error": str(e)
                })
                print(f"❌ 第{i+1}篇处理失败：{e}")
        
        summary = {
            "total": len(results),
            "success": sum(1 for r in results if r["status"] != "failed"),
            "results": results
        }
        
        print("\n" + "=" * 60)
        print("📊 发布准备汇总")
        print("=" * 60)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        print("\n✨ 提示：所有草稿已保存在工作目录，请及时复制发布！\n")
        
        return summary


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="头条号微头条发布工具 (演示模式)")
    parser.add_argument("--topic", type=str, default=None, help="指定发布主题，如'AI 科技'")
    parser.add_argument("--count", type=int, default=1, choices=[1, 2, 3], help="准备篇数（最多 3 篇）")
    args = parser.parse_args()
    
    publisher = ToutiaoPublisher()
    result = publisher.publish_article_demo(topic=args.topic, batch_size=args.count)
    
    return result


if __name__ == "__main__":
    main()
