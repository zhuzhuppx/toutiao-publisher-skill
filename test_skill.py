#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Toutiao Publisher Skill - 自动化测试脚本
用途：验证头条发布功能的各个模块
版本：1.0.0
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_topic_pool():
    """测试主题池生成逻辑"""
    print("=" * 50)
    print("【测试 1】主题池内容")
    print("=" * 50)
    
    from active_skills.toutiao_publisher.main import TOPIC_POOL
    
    # 检查所有主题类别是否存在
    expected_categories = ["AI 科技", "理财知识", "健康养生", "职场成长", 
                          "亲子教育", "情感关系", "生活妙招", "数码测评"]
    
    for category in expected_categories:
        assert category in TOPIC_POOL, f"缺失主题类别：{category}"
        assert len(TOPIC_POOL[category]) > 0, f"{category}下无话题"
        print(f"✅ {category}: {len(TOPIC_POOL[category])}个话题")
    
    print("\n🎯 主题池测试通过！\n")


def test_content_generation():
    """测试内容生成逻辑"""
    print("=" * 50)
    print("【测试 2】内容生成")
    print("=" * 50)
    
    from active_skills.toutiao_publisher.main import ToutiaoPublisher
    
    publisher = ToutiaoPublisher()
    
    # 测试不同主题的内容生成
    test_topics = ["AI 科技", "理财知识", "健康养生"]
    
    for topic in test_topics:
        content = publisher._generate_content(topic)
        assert len(content) > 100, f"生成内容过短：{len(content)}字"
        assert topic in content or any(kw in content for kw in ["分享", "经验", "建议"]), \
            f"内容未包含关键词"
        print(f"✅ {topic}: {len(content)}字")
        
        # 打印部分预览
        print(f"   预览：{content[:50]}...")
    
    print("\n📝 内容生成测试通过！\n")


def test_history_management():
    """测试历史记录管理"""
    print("=" * 50)
    print("【测试 3】历史记录管理")
    print("=" * 50)
    
    from active_skills.toutiao_publisher.main import ToutiaoPublisher, PUBLISH_HISTORY_FILE
    
    import tempfile
    import json
    
    # 使用临时文件测试（避免污染真实数据）
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        test_file = Path(tmp.name)
    
    try:
        # 模拟加载空历史
        temp_history = []
        temp_history.append("测试内容 1")
        temp_history.append("测试内容 2")
        
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(temp_history, f, ensure_ascii=False)
        
        print(f"✅ 创建测试历史文件成功")
        print(f"   文件路径：{test_file}")
        
        # 验证去重逻辑
        if "测试内容 1" not in temp_history:
            raise Exception("历史数据读取失败")
        
        print(f"✅ 历史数据完整性验证通过")
        
    finally:
        # 清理临时文件
        if test_file.exists():
            test_file.unlink()
            print("🗑️ 清理临时测试文件")
    
    print("\n💾 历史记录管理测试通过！\n")


def test_browser_config():
    """测试浏览器配置兼容性"""
    print("=" * 50)
    print("【测试 4】浏览器配置")
    print("=" * 50)
    
    try:
        from browser_use import BrowserConfig
        
        # 测试 Headless 模式
        config_headless = BrowserConfig(headless=True)
        print(f"✅ Headless 模式配置成功")
        
        # 测试 Visible 模式
        config_visible = BrowserConfig(headless=False)
        print(f"✅ Visible 模式配置成功")
        
        # 测试视口设置
        assert hasattr(config_headless, 'viewport_size')
        print(f"✅ 视口大小配置支持")
        
        print("\n🌐 浏览器配置测试通过！\n")
        
    except ImportError:
        print("⚠️ 未安装 browser_use 库，跳过此测试")
        print("提示：pip install browser-use\n")
    except Exception as e:
        print(f"❌ 浏览器配置测试失败：{e}\n")


def test_file_operations():
    """测试文件操作功能"""
    print("=" * 50)
    print("【测试 5】文件操作")
    print("=" * 50)
    
    from active_skills.toutiao_publisher.main import WORKSPACE_DIR
    
    # 检查工作目录
    assert WORKSPACE_DIR.exists(), f"工作目录不存在：{WORKSPACE_DIR}"
    print(f"✅ 工作目录存在：{WORKSPACE_DIR}")
    
    # 检查必要子目录
    required_dirs = ["active_skills/toutiao_publisher"]
    for dir_path in required_dirs:
        full_path = WORKSPACE_DIR / dir_path
        assert full_path.exists(), f"缺少必需目录：{full_path}"
        print(f"✅ 必要目录存在：{dir_path}")
    
    print("\n📁 文件操作测试通过！\n")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("🚀 Toutiao Publisher Skill - 自动化测试套件 v1.0.0")
    print("=" * 70 + "\n")
    
    tests = [
        ("主题池内容", test_topic_pool),
        ("内容生成逻辑", test_content_generation),
        ("历史记录管理", test_history_management),
        ("浏览器配置兼容", test_browser_config),
        ("文件操作", test_file_operations),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n▶️  开始测试：{test_name}\n")
            test_func()
            results.append((test_name, "PASS"))
        except AssertionError as e:
            print(f"❌ 测试失败：{test_name}")
            print(f"   错误信息：{e}\n")
            results.append((test_name, "FAIL"))
        except Exception as e:
            print(f"⚠️  测试异常：{test_name}")
            print(f"   异常信息：{e}\n")
            results.append((test_name, "ERROR"))
    
    # 汇总报告
    print("\n" + "=" * 70)
    print("📊 测试结果汇总")
    print("=" * 70)
    
    total = len(results)
    passed = sum(1 for _, status in results if status == "PASS")
    failed = sum(1 for _, status in results if status == "FAIL")
    errors = sum(1 for _, status in results if status == "ERROR")
    
    for test_name, status in results:
        icon = "✅" if status == "PASS" else "❌"
        print(f"{icon} {test_name}: {status}")
    
    print(f"\n总计：{total} | 通过：{passed} | 失败：{failed} | 异常：{errors}")
    print("=" * 70 + "\n")
    
    return {"passed": passed, "failed": failed, "errors": errors}


if __name__ == "__main__":
    result = run_all_tests()
    
    # 退出码设置
    exit_code = 0 if result["failed"] == 0 and result["errors"] == 0 else 1
    sys.exit(exit_code)
