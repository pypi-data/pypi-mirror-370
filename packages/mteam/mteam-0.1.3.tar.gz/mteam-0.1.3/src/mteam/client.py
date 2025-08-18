from typing import Optional, Dict, Any
import httpx
import json
from .config import get_api_key, get_base_url
from .exceptions import APIError
from .torrent.client import TorrentClient
from .member.client import MemberClient
from .subtitle.client import SubtitleClient
from .models import Result
import os   
import logging

logger = logging.getLogger(__name__)

class MTeamClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 10.0,
        verify_ssl: bool = True,
        headers: Optional[Dict[str, str]] = None,
        follow_redirects: bool = True,
        http_client: Optional[httpx.Client] = None
    ):
        """
        初始化 MTeam 客户端

        Args:
            base_url: API 基础 URL（可选，默认从环境变量读取）
            api_key: API 密钥（可选，默认从环境变量读取）
            timeout: 请求超时时间（秒）
            verify_ssl: 是否验证 SSL 证书
            headers: 自定义请求头
            follow_redirects: 是否跟随重定向
            http_client: 自定义 httpx 客户端
        """
        self.base_url = (base_url or get_base_url()).rstrip('/')
        self.api_key = api_key or get_api_key()
        
        # 配置默认请求头
        self.headers = {
            # "Content-Type": "application/json",
            "x-api-key": self.api_key
        }
        # 合并自定义请求头
        if headers:
            self.headers.update(headers)
        
        # 使用提供的客户端或创建新的
        if http_client:
            self.client = http_client
        else:
            self.client = httpx.Client(
                timeout=timeout,
                headers=self.headers,
                verify=verify_ssl,
                follow_redirects=follow_redirects
            )
            
        # 初始化各个模块的客户端
        self.torrent = TorrentClient(self)
        self.member = MemberClient(self)
        self.subtitle = SubtitleClient(self)

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出时关闭客户端"""
        self.client.close()

    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求

        Args:
            method: HTTP 方法
            endpoint: API 端点
            data: 请求体数据
            **kwargs: 其他请求参数
        """
        url = f"{self.base_url}{endpoint}"    
        try:
            response = self.client.request(method=method, url=url, **kwargs)
            response.raise_for_status()
            result = response.json()
            
            # 检查 API 响应状态
            if result.get("message", "").upper() != "SUCCESS":
                raise APIError(
                    f"API 错误: {result.get('message')}",
                    status_code=response.status_code
                )
                
            # 如果是debug模式, 打印结果为json
            if os.getenv("DEBUG") == "true":
                logger.info(json.dumps(result, indent=4))
            return result
            
        except httpx.HTTPStatusError as e:
            raise APIError(
                f"HTTP {e.response.status_code}: {e.response.text}",
                status_code=e.response.status_code
            )
        except httpx.HTTPError as e:
            raise APIError(f"HTTP 请求错误: {str(e)}")

    def check_ip(self, ip: str) -> Result:
        """
        检查 IP 地址
        
        Args:
            ip: IP 地址
        """
        return Result(**self._make_request(
            "GET",
            "/system/check-ip",
            params={"ip": ip}
        )) 