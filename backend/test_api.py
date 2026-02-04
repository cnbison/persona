#!/usr/bin/env python3
"""
后端API测试脚本
"""
import sys
import requests

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(f"   服务: {response.json()['service']}")
            print(f"   版本: {response.json()['version']}")
            print(f"   数据库: {response.json()['database']}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def test_root():
    """测试根路径"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ 根路径访问正常")
            return True
        else:
            print(f"❌ 根路径访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 根路径连接失败: {e}")
        return False

def test_docs():
    """测试API文档"""
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API文档可访问: http://localhost:8000/docs")
            return True
        else:
            print(f"❌ API文档访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API文档连接失败: {e}")
        return False

if __name__ == "__main__":
    print("🧪 测试后端API...")
    print()

    results = []
    results.append(test_root())
    results.append(test_health())
    results.append(test_docs())

    print()
    if all(results):
        print("🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("⚠️  部分测试失败")
        sys.exit(1)
