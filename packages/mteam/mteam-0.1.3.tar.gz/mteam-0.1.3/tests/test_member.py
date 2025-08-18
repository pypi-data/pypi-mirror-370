import pytest
from dotenv import load_dotenv
from mteam import MTeamClient
from mteam.member import RegisterForm, LoginForm, ProfileUpdateForm

# 在测试开始前加载环境变量
load_dotenv()

@pytest.fixture
def client():
    """创建测试客户端"""
    return MTeamClient()

@pytest.fixture
def test_user():
    """测试用户数据"""
    return {
        "username": os.getenv("TEST_USERNAME", "test_user"),
        "password": os.getenv("TEST_PASSWORD", "test_password"),
        "email": os.getenv("TEST_EMAIL", "test@example.com")
    }

def test_register(client, test_user):
    """测试用户注册"""
    form = RegisterForm(
        username=test_user["username"],
        email=test_user["email"],
        password=test_user["password"],
        confirm_password=test_user["password"]
    )
    result = client.member.register(form)
    assert result.code == 0

def test_login(client, test_user):
    """测试用户登录"""
    form = LoginForm(
        username=test_user["username"],
        password=test_user["password"]
    )
    result = client.member.login(form)
    assert result.code == 0

def test_get_profile(client):
    """测试获取用户资料"""
    result = client.member.get_profile()
    assert result.code == 0
    assert result.data is not None

def test_update_profile(client):
    """测试更新用户资料"""
    form = ProfileUpdateForm(
        signature="测试签名"
    )
    result = client.member.update_profile(form)
    assert result.code == 0 