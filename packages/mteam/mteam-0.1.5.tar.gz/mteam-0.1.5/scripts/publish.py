import os
import subprocess
import sys
from pathlib import Path

def run_command(command: str) -> bool:
    """运行命令并返回是否成功"""
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        return False

def clean_build_files():
    """清理旧的构建文件"""
    print("清理旧的构建文件...")
    paths_to_clean = [
        "dist",
        "build",
        "*.egg-info"
    ]
    for path in paths_to_clean:
        command = "rm -rf " + path
        if sys.platform == "win32":
            command = "rmdir /s /q " + path
        run_command(command)

def build_package():
    """构建包"""
    print("构建包...")
    return run_command("python -m build")

def upload_to_pypi():
    """上传到 PyPI"""
    print("上传到 PyPI...")
    return run_command("python -m twine upload dist/*")

def main():
    # 确保必要的工具已安装
    requirements = ["build", "twine"]
    for req in requirements:
        try:
            __import__(req)
        except ImportError:
            print(f"安装 {req}...")
            if not run_command(f"pip install {req}"):
                sys.exit(1)
    
    # 清理旧的构建文件
    clean_build_files()
    
    # 构建包
    if not build_package():
        sys.exit(1)
    
    # 确认上传
    response = input("构建完成。是否上传到 PyPI？(y/N) ").lower()
    if response != 'y':
        print("取消上传")
        sys.exit(0)
    
    # 上传到 PyPI
    if not upload_to_pypi():
        sys.exit(1)
    
    print("发布完成！")

if __name__ == "__main__":
    main() 