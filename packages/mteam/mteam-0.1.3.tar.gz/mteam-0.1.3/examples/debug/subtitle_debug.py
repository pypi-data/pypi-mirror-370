import logging
from dotenv import load_dotenv
from mteam import MTeamClient
from mteam.subtitle import SubtitleSearch, SubtitleLanguage

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

def debug_subtitle_list():
    """调试字幕列表功能"""
    # 使用自定义配置创建客户端
    client = MTeamClient(
        timeout=30.0,  # 更长的超时时间
        verify_ssl=False,  # 禁用 SSL 验证
        headers={
            "User-Agent": "MTeam-SDK/1.0"  # 自定义 User-Agent
        }
    )
    
    # 使用上下文管理器
    with MTeamClient() as client:
        torrent_id = '869244'
        result = client.subtitle.get_subtitle_list(torrent_id)
        logger.info(f"Response code: {result.code}")
        logger.info(f"Response message: {result.message}")
        
        if result.data:
            for subtitle in result.data:
                logger.info("=" * 50)
                logger.info(f"字幕ID: {subtitle.id}")
                logger.info(f"标题: {subtitle.name}")
                logger.info(f"文件名: {subtitle.filename}")
                logger.info(f"种子ID: {subtitle.torrent}")
                logger.info(f"大小: {subtitle.size}")
                logger.info(f"语言: {subtitle.lang}")
                logger.info(f"格式: {subtitle.ext}")
                logger.info(f"下载次数: {subtitle.hits}")
                logger.info(f"作者: {subtitle.author or '匿名'}")
                logger.info(f"创建时间: {subtitle.created_date}")
                logger.info(f"修改时间: {subtitle.last_modified_date}")

def debug_subtitle_generate_download_link(   ):
    """调试字幕搜索功能"""
    client = MTeamClient(api_key="")
    subtitle_id = 57082
    result = client.subtitle.generate_download_link(subtitle_id)
    logger.info(f"Response code: {result.code}")
    logger.info(f"Response message: {result.message}")
    logger.info(f"Response data: {result.data}")
    

if __name__ == "__main__":
    # 在这里选择要调试的功能
    debug_subtitle_generate_download_link()
    debug_subtitle_list()
