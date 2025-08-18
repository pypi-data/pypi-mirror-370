from typing import List, Optional, BinaryIO
from ..models import Result
from .models import (
    TorrentSearch,
    TorrentDetail,
    TorrentUploadForm,
    TorrentCategory,
    TorrentStatus
)

class TorrentClient:
    """种子相关 API 客户端"""
    
    def __init__(self, base_client):
        self._client = base_client
    
    def search(self, params: TorrentSearch) -> Result[List[TorrentDetail]]:
        """
        搜索种子
        
        Args:
            params: 搜索参数
        """
        return Result[List[TorrentDetail]](**self._client._make_request(
            "POST",
            "/torrent/search",
            json=params.model_dump()
        ))
    
    def get_detail(self, torrent_id: int) -> Result[TorrentDetail]:
        """
        获取种子详情
        
        Args:
            torrent_id: 种子ID
        """
        return Result[TorrentDetail](**self._client._make_request(
            "GET",
            f"/torrent/{torrent_id}"
        ))
    
    def upload(self, form: TorrentUploadForm, torrent_file: BinaryIO) -> Result[TorrentDetail]:
        """
        上传种子
        
        Args:
            form: 上传表单
            torrent_file: .torrent 文件对象
        """
        files = {'file': torrent_file}
        return Result[TorrentDetail](**self._client._make_request(
            "POST",
            "/torrent/upload",
            data=form.model_dump(),
            files=files
        ))
    
    def download(self, torrent_id: int) -> Result[bytes]:
        """
        下载种子文件
        
        Args:
            torrent_id: 种子ID
        """
        return Result[bytes](**self._client._make_request(
            "GET",
            f"/torrent/download/{torrent_id}"
        ))
    
    def edit(self, torrent_id: int, form: TorrentUploadForm) -> Result[TorrentDetail]:
        """
        编辑种子信息
        
        Args:
            torrent_id: 种子ID
            form: 编辑表单
        """
        return Result[TorrentDetail](**self._client._make_request(
            "POST",
            f"/torrent/edit/{torrent_id}",
            json=form.model_dump()
        ))
    
    def delete(self, torrent_id: int) -> Result:
        """
        删除种子
        
        Args:
            torrent_id: 种子ID
        """
        return Result(**self._client._make_request(
            "POST",
            f"/torrent/delete/{torrent_id}"
        ))
    
    def get_categories(self) -> Result[List[TorrentCategory]]:
        """获取所有种子分类"""
        return Result[List[TorrentCategory]](**self._client._make_request(
            "GET",
            "/torrent/categories"
        )) 