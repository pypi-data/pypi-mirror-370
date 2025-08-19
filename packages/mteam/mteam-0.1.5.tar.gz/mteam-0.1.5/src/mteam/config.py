import os
from typing import Optional

def get_api_key() -> Optional[str]:
    """
    从环境变量获取 API 密钥
    
    Returns:
        str | None: API 密钥，如果环境变量未设置则返回 None
    """
    return os.getenv("MTEAM_API_KEY")

def get_base_url() -> str:
    """
    从环境变量获取基础 URL
    
    Returns:
        str: API 基础 URL，默认为测试环境
    """
    return os.getenv("MTEAM_BASE_URL", "https://api.m-team.cc/api") 