#!/usr/bin/env python3
"""
LandPPT Application Runner

This script starts the LandPPT FastAPI application with proper configuration.
"""

import uvicorn
import sys
import os
import asyncio
from dotenv import load_dotenv

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_modules = [
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('jinja2', 'jinja2'),
        ('sqlalchemy', 'sqlalchemy'),
        ('langchain', 'langchain'),
        ('langchain_text_splitters', 'langchain-text-splitters'),
    ]
    
    missing = []
    for import_name, package_name in required_modules:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)
    
    if missing:
        print("❌ 缺少必要的依赖，请先安装：")
        print(f"   pip install {' '.join(missing)}")
        print()
        return False
    return True

def check_env_file():
    """Check if .env file exists and provide guidance"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    env_example_path = os.path.join(os.path.dirname(__file__), '.env.example')
    
    if not os.path.exists(env_path):
        if os.path.exists(env_example_path):
            print("⚠️  未检测到 .env 文件，正在复制模板...")
            import shutil
            shutil.copy(env_example_path, env_path)
            print(f"✅ 已创建 .env 文件，请编辑它配置 API 密钥")
            print()
        else:
            print("⚠️  未找到 .env.example 模板文件")
            print()

def main():
    """Main entry point for running the application"""

    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # Check .env file
    check_env_file()
    
    # Load environment variables with error handling
    try:
        load_dotenv()
    except PermissionError as e:
        print(f"⚠️  警告: 无法加载 .env 文件 (权限错误): {e}")
        print("   将使用系统环境变量...")
    except Exception as e:
        print(f"⚠️  警告: 无法加载 .env 文件: {e}")
        print("   将使用系统环境变量...")

    # Get configuration from environment variables with defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() in ("true", "1", "yes", "on")
    debug = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes", "on")
    log_level = os.getenv("LOG_LEVEL", "info").lower()

    # Enable debug mode
    if debug:
        log_level = "debug"
        reload = True
        print("🐛 Debug 模式已启用")
        print("   - 自动重载: 开启")
        print("   - 日志级别: debug")
        print()

    # Configuration
    config = {
        "app": "landppt.main:app",
        "host": host,
        "port": port,
        "reload": reload,
        "log_level": log_level,
        "access_log": True,
    }
    
    print("🚀 正在启动 LandPPT 服务器...")
    print("=" * 60)
    print(f"📍 地址: http://localhost:{config['port']}")
    print(f"📚 API 文档: http://localhost:{config['port']}/docs")
    print(f"🌐 Web 界面: http://localhost:{config['port']}/web")
    print("=" * 60)
    
    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动错误: {e}")
        print("\n💡 提示:")
        print("   1. 确保已安装所有依赖: pip install -e .")
        print("   2. 检查 .env 文件中的 API 密钥配置")
        print("   3. 查看日志获取更多详细信息")
        sys.exit(1)

if __name__ == "__main__":
    main()
