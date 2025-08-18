from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

class TorrentStatus(str, Enum):
    """种子状态"""
    NORMAL = "normal"
    PENDING = "pending"
    DELETED = "deleted"

class TorrentCategory(str, Enum):
    """种子分类"""
    MOVIE = "movie"
    TV = "tv"
    DOCUMENTARY = "documentary"
    ANIME = "anime"
    MUSIC = "music"
    MV = "mv"
    GAME = "game"
    SOFTWARE = "software"
    SPORTS = "sports"
    OTHER = "other"

class TorrentSearch(BaseModel):
    """种子搜索参数"""
    page_number: int = Field(1, ge=1, le=1000, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    keyword: Optional[str] = Field(None, description="搜索关键词")
    categories: Optional[List[TorrentCategory]] = Field(None, description="分类列表")
    imdb_id: Optional[str] = Field(None, description="IMDB ID")
    douban_id: Optional[str] = Field(None, description="豆瓣 ID")
    status: Optional[TorrentStatus] = Field(None, description="种子状态")

class TorrentDetail(BaseModel):
    """种子详细信息"""
    id: int
    title: str
    description: str
    category: TorrentCategory
    size: int
    uploader_id: int
    uploader_name: str
    upload_time: datetime
    seeders: int
    leechers: int
    completed: int
    status: TorrentStatus
    imdb_id: Optional[str] = None
    douban_id: Optional[str] = None
    tags: List[str] = []

class TorrentUploadForm(BaseModel):
    """种子上传表单"""
    title: str = Field(..., description="标题")
    description: str = Field(..., description="描述")
    category: TorrentCategory = Field(..., description="分类")
    anonymous: bool = Field(False, description="是否匿名")
    imdb_id: Optional[str] = Field(None, description="IMDB ID")
    douban_id: Optional[str] = Field(None, description="豆瓣 ID")
    tags: List[str] = Field(default_factory=list, description="标签") 