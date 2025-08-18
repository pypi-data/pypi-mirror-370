import pytest
from dotenv import load_dotenv
from mteam import MTeamClient
from mteam.torrent import TorrentSearch, TorrentCategory

# 在测试开始前加载环境变量
load_dotenv()

@pytest.fixture
def client():
    """创建测试客户端"""
    return MTeamClient()

def test_search_torrents(client):
    """测试搜索种子"""
    search = TorrentSearch(
        keyword="测试",
        categories=[TorrentCategory.MOVIE],
        page_size=10
    )
    result = client.torrent.search(search)
    assert result.code == 0
    assert result.message.upper() == "SUCCESS"
    assert len(result.data) <= 10

def test_get_torrent_detail(client):
    """测试获取种子详情"""
    result = client.torrent.get_detail(884344)
    assert result.code == 0
    assert result.message.upper() == "SUCCESS" 