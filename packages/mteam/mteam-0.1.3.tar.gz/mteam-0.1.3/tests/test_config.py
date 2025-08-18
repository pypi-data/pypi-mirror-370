import os
import pytest
from dotenv import load_dotenv
from mteam.config import get_base_url, get_api_key

load_dotenv()

def test_env_variables():
    """测试环境变量是否正确加载"""
    assert os.getenv("MTEAM_BASE_URL") == "https://api.m-team.cc/api"
    assert os.getenv("MTEAM_API_KEY") is not None
    
def test_config_functions():
    """测试配置函数是否正确获取环境变量"""
    assert get_base_url() == "https://api.m-team.cc/api"
    assert get_api_key() is not None 