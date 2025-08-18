from typing import List, TypeVar, Generic, Optional, Any
from enum import Enum
from pydantic import BaseModel

class JoinType(str, Enum):
    """加入类型"""
    NORMAL = "normal"
    INVITE = "invite"
    APPLY = "apply"

T = TypeVar('T')

class Result(BaseModel, Generic[T]):
    """API 响应结果"""
    code: int
    message: str
    data: Optional[T] = None
    
    def __bool__(self) -> bool:
        """根据响应码判断请求是否成功"""
        return self.code == 0

class PaginatedData(BaseModel, Generic[T]):
    """分页数据结构"""
    pageNumber: str
    pageSize: str
    total: str
    totalPages: str
    data: List[T]


class RegisterForm(BaseModel):
    """注册表单"""
    username: str
    email: str
    password: str

class AlbumForm(BaseModel):
    """专辑表单"""
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    join_type: JoinType

class AlbumTorrentSearch(BaseModel):
    """专辑种子搜索参数"""
    album_id: int
    keyword: str

class AlbumTorrentJoinForm(BaseModel):
    """专辑种子加入表单"""
    album_id: int
    torrent_ids: List[int]

class AlbumTorrentRemoveForm(BaseModel):
    """专辑种子移除表单"""
    album_id: int
    torrent_ids: List[int] 