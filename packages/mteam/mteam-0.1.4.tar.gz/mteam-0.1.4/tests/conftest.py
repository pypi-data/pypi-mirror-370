import pytest
from dotenv import load_dotenv
import logging

# 在所有测试开始前加载环境变量
def pytest_configure(config):
    load_dotenv() 
      # 配置日志系统
    logging.basicConfig(
        level=logging.INFO,  # 设置日志级别为 INFO
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True  # 强制重新配置根日志记录器（Python 3.8+）
    )