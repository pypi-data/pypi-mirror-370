#!/usr/bin/env python3
"""
一键发布脚本 - 直接发布到正式PyPI
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, check=True):
    """运行命令并处理错误"""
    print(f"运行命令: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("输出:", result.stdout)
    if result.stderr:
        print("错误:", result.stderr)
    
    if check and result.returncode != 0:
        print(f"命令失败: {command}")
        return False
    
    return True

def clean_build():
    """清理构建文件"""
    print("🧹 清理构建文件...")
    dirs_to_remove = ['build', 'dist', '*.egg-info']
    for dir_pattern in dirs_to_remove:
        for path in Path('.').glob(dir_pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"已删除: {path}")
            elif path.is_file():
                path.unlink()
                print(f"已删除: {path}")

def build_package():
    """构建包"""
    print("🔨 构建包...")
    return run_command("python -m build")

def check_package():
    """检查包"""
    print("✅ 检查包...")
    return run_command("python -m twine check dist/*")

def upload_to_pypi():
    """上传到正式PyPI"""
    print("🚀 上传到正式PyPI...")
    return run_command("python -m twine upload dist/*")

def test_install():
    """测试安装"""
    print("🧪 测试安装...")
    return run_command("pip install python-sbx")

def main():
    """主函数"""
    print("🎯 一键发布到正式PyPI")
    print("=" * 50)
    
    # 检查必要的工具
    try:
        import build
        import twine
    except ImportError:
        print("📦 安装必要的工具...")
        run_command("pip install build twine")
    
    # 检查配置文件
    if not os.path.exists('.pypirc'):
        print("❌ 错误: 找不到 .pypirc 配置文件")
        print("请确保配置文件存在并包含正确的token")
        sys.exit(1)
    
    print("✅ 找到 .pypirc 配置文件")
    
    # 清理旧的构建文件
    clean_build()
    
    # 构建包
    print("\n📦 开始构建包...")
    if not build_package():
        print("❌ 构建失败，退出")
        sys.exit(1)
    print("✅ 包构建成功!")
    
    # 检查包
    print("\n🔍 检查包...")
    if not check_package():
        print("❌ 包检查失败，退出")
        sys.exit(1)
    print("✅ 包检查通过!")
    
    # 上传到正式PyPI
    print("\n🚀 开始上传到正式PyPI...")
    if not upload_to_pypi():
        print("❌ 上传失败，退出")
        sys.exit(1)
    print("✅ 上传成功!")
    
    # 等待一下让PyPI处理
    print("\n⏳ 等待PyPI处理...")
    import time
    time.sleep(10)
    
    # 测试安装
    print("\n🧪 测试安装...")
    if not test_install():
        print("❌ 测试安装失败")
        print("可能的原因:")
        print("1. PyPI还在处理上传的包")
        print("2. 包配置有问题")
        print("3. 网络连接问题")
        print("\n建议等待几分钟后手动测试:")
        print("pip install python-sbx")
    else:
        print("✅ 测试安装成功!")
        print("\n🎉 发布完成!")
        print("=" * 50)
        print("用户可以通过以下命令安装你的包:")
        print("pip install python-sbx")
        print("\n运行命令:")
        print("python-sbx")
    
    print("\n" + "=" * 50)
    print("发布流程结束")

if __name__ == "__main__":
    main()
