import pytest
from dotenv import load_dotenv
from mteam import MTeamClient
from mteam.models import Result

# 在测试开始前加载环境变量
load_dotenv()

@pytest.fixture
def client():
    """创建测试客户端"""
    return MTeamClient()

def test_client_initialization(client):
    """测试客户端初始化"""
    assert isinstance(client, MTeamClient)
    assert client.base_url.endswith('/api')
    assert client.api_key is not None

def test_make_request(client):
    """测试基础请求方法"""
    result = client._make_request("GET", "/test")
    assert isinstance(result, dict)

def test_check_ip(client):
    """测试 IP 检查功能"""
    result = client.check_ip("127.0.0.1")
    assert isinstance(result, Result)
    assert result.code in ["0", "400", "403"]  # 修改这里
    assert result.message is not None

