import pytest
from dotenv import load_dotenv
from mteam import MTeamClient
from mteam.subtitle import (
    SubtitleSearch,
    SubtitleUploadForm,
    SubtitleLanguage
)
from datetime import datetime
import logging
# 在测试开始前加载环境变量
load_dotenv()

@pytest.fixture
def client():
    """创建测试客户端"""
    return MTeamClient()

def test_search_subtitles(client):
    """测试搜索字幕"""
    search = SubtitleSearch(
        keyword="测试",
        language_id=1,  # 假设1是简体中文
        page_size=10
    )
    result = client.subtitle.search(search)
    assert result.code == 0
    assert result.message.upper() == "SUCCESS"
    assert len(result.data.data) < 10

def test_get_languages(client):
    """测试获取支持的语言列表"""
    result = client.subtitle.get_languages()
    assert result.code == 0
    assert result.message.upper() == "SUCCESS"
    assert len(result.data) > 0
    # 确保返回的语言列表包含基本语言
    languages = [lang.value for lang in result.data]
    assert SubtitleLanguage.CHINESE_SIMPLIFIED.value in languages

# def test_upload_subtitle(client, tmp_path):
#     """测试上传字幕"""
#     # 创建一个临时字幕文件
#     subtitle_file = tmp_path / "test.srt"
#     subtitle_file.write_text("""
# 1
# 00:00:01,000 --> 00:00:04,000
# 这是一个测试字幕
#     """)
    
#     form = SubtitleUploadForm(
#         title="测试字幕",
#         torrent_id=884344,  # 使用一个存在的种子ID
#         language_id=1,  # 假设1是简体中文
#         anonymous=False
#     )
    
#     with open(subtitle_file, 'rb') as f:
#         result = client.subtitle.upload(form, f)
#         assert result.code == 0
#         assert result.message.upper() == "SUCCESS"
#         assert result.data is not None

def test_download_subtitle(client):
    """测试下载字幕"""
    # 使用一个测试凭证
    credential = "c2lkPTU3MDgyJnNpZ249YWM3NWQxNTNmODYwM2UxM2Y4NTlmN2Q3ODM4ZmMyMTQmdD0xNzU1NDM2MDQ5JnVpZD0zMjUxMDY%3D"
    save_path = "/tmp/test.srt"
    
    # 下载字幕
    result_path = client.subtitle.download(
        credential=credential,
        save_path=save_path
    )
    # 验证返回的路径与请求的保存路径相同
    assert result_path == save_path
    
    # 验证文件是否存在和大小
    import os
    assert os.path.exists(save_path)
    assert os.path.getsize(save_path) > 0

def test_delete_subtitle(client):
    """测试删除字幕"""
    # 注意：这个测试需要上传者权限
    # 假设ID为1的字幕存在且当前用户有权限删除
    result = client.subtitle.delete(subtitle_id=1)
    assert result.code == 0
    assert result.message.upper() == "SUCCESS"

@pytest.mark.parametrize("language", [
    SubtitleLanguage.CHINESE_SIMPLIFIED,
    SubtitleLanguage.CHINESE_TRADITIONAL,
    SubtitleLanguage.ENGLISH,
    SubtitleLanguage.JAPANESE
])
def test_search_by_language(client, language):
    """测试按语言搜索字幕"""
    search = SubtitleSearch(
        keyword="测试",
        language_id=language.value,
        page_size=5
    )
    result = client.subtitle.search(search)
    assert result.code == 0
    assert result.message.upper() == "SUCCESS"
    
    # 验证返回的字幕语言正确
    if result.data:
        for subtitle in result.data:
            assert subtitle.language == language.value 

def test_generate_download_link(client):
    """测试生成字幕下载链接"""
    # 使用一个已知存在的字幕ID
    subtitle_id = 1
    result = client.subtitle.generate_download_link(subtitle_id)
    
    assert result.code == 0
    assert result.message.upper() == "SUCCESS"
    assert result.data is not None
    assert isinstance(result.data, str)
    # 验证返回的是一个有效的下载链接
    assert len(result.data) > 20

def test_get_subtitle_list(client):
    """测试获取种子的字幕列表"""
    torrent_id = 869244
    result = client.subtitle.get_subtitle_list(torrent_id)
    
    assert result.code == 0
    assert result.message.upper() == "SUCCESS"
    assert isinstance(result.data, list)
    
    # 如果有字幕，验证字幕信息的结构
    if result.data:
        subtitle = result.data[0]
        
        # 验证必要字段
        assert isinstance(subtitle.id, str)
        assert isinstance(subtitle.name, str)
        assert isinstance(subtitle.filename, str)
        assert isinstance(subtitle.torrent, str)
        assert isinstance(subtitle.size, str)
        assert isinstance(subtitle.lang, str)
        assert isinstance(subtitle.ext, str)
        assert isinstance(subtitle.hits, str)
        assert isinstance(subtitle.created_date, datetime)
        assert isinstance(subtitle.last_modified_date, datetime)
        
        # 验证字段值的合理性
        assert len(subtitle.id) > 0
        assert len(subtitle.name) > 0
        assert subtitle.torrent == str(torrent_id)
        assert int(subtitle.size) >= 0
        assert int(subtitle.hits) >= 0
        assert subtitle.ext in ['srt', 'ass', 'ssa'] 