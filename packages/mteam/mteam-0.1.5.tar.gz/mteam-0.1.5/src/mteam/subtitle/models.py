from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

class SubtitleLanguage(str, Enum):
    """字幕语言"""
    CHINESE_SIMPLIFIED = "chs"
    CHINESE_TRADITIONAL = "cht"
    ENGLISH = "eng"
    JAPANESE = "jpn"

class SubtitleUploadForm(BaseModel):
    """字幕上传表单"""
    title: str = Field(..., description="字幕标题")
    torrent_id: int = Field(..., description="关联种子ID")
    language_id: int = Field(..., description="字幕语言ID")
    anonymous: bool = Field(False, description="是否匿名")
    note: Optional[str] = Field(None, description="备注信息")

class SubtitleSearch(BaseModel):
    """字幕搜索参数"""
    page_number: int = Field(1, ge=1, le=1000, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    keyword: Optional[str] = Field(None, description="搜索关键词")
    language_id: Optional[int] = Field(None, description="语言ID")
    torrent_id: Optional[int] = Field(None, description="种子ID")

class SubtitleInfo(BaseModel):
    """字幕信息"""
    id: str
    name: str  # 字幕标题
    filename: str  # 文件名
    torrent: str  # 关联的种子ID
    size: str  # 文件大小
    lang: str  # 语言ID
    ext: str  # 文件扩展名
    hits: str  # 下载次数
    anonymous: bool = False  # 是否匿名
    author: Optional[str] = None  # 作者
    savePath: Optional[str] = None  # 保存路径
    createdDate: datetime  # 创建时间
    lastModifiedDate: datetime  # 最后修改时间

    class Config:
        orm_mode = True  # 关键：允许从字典转换为 Pydantic 模型
        allow_population_by_field_name = True  # 允许使用别名
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")
        } 
        