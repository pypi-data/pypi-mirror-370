# M-TEAM API SDK

M-TEAM API 的 Python SDK，提供了简单易用的接口封装。

## 安装

```bash
pip install mteam
```

## 快速开始

1. 配置环境变量
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API 密钥：
```
MTEAM_API_KEY=your_api_key_here
MTEAM_BASE_URL=http://test2.m-team.cc/api
```

2. 基本使用
```python
from mteam import MTeamClient

# 创建客户端实例
client = MTeamClient()

# 搜索种子
from mteam.torrent import TorrentSearch, TorrentCategory
search = TorrentSearch(
    keyword="测试",
    categories=[TorrentCategory.MOVIE],
    page_size=10
)
result = client.torrent.search(search)

# 获取用户资料
profile = client.member.get_profile()
```

## 功能模块

### 用户模块
```python
from mteam.member import LoginForm, RegisterForm

# 用户登录
form = LoginForm(username="test", password="password")
result = client.member.login(form)

# 获取用户资料
profile = client.member.get_profile()
```

### 种子模块
```python
from mteam.torrent import TorrentSearch, TorrentCategory

# 搜索种子
search = TorrentSearch(keyword="测试")
results = client.torrent.search(search)

# 获取种子详情
torrent = client.torrent.get_detail(torrent_id=123)
```

### 字幕模块
```python
from mteam.subtitle import SubtitleSearch

# 搜索字幕
search = SubtitleSearch(keyword="测试")
subtitles = client.subtitle.search(search)

# 上传字幕
form = SubtitleUploadForm(
    title="测试字幕",
    torrent_id=123,
    language_id=1
)
result = client.subtitle.upload(form, "path/to/subtitle.srt")
```

## 测试

1. 安装测试依赖
```bash
pip install pytest python-dotenv
```

2. 运行测试
```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/test_member.py
pytest tests/test_torrent.py

# 运行单个测试
pytest tests/test_member.py::test_login

# 显示详细输出
pytest -v
```

## 注意事项

1. API 密钥安全
   - 不要在代码中硬编码 API 密钥
   - 使用环境变量或配置文件管理密钥
   - 不要将密钥提交到版本控制系统

2. 错误处理
   - 所有 API 调用都可能抛出 `APIError` 异常
   - 检查响应的 `code` 和 `message` 字段
   - 合理处理网络错误和超时

3. 请求限制
   - 注意 API 的请求频率限制
   - 合理设置超时时间
   - 必要时实现请求重试机制

## 常见问题

1. API 密钥无效
   - 检查 `.env` 文件中的 `MTEAM_API_KEY` 是否正确
   - 确认 API 密钥未过期

2. 请求失败
   - 检查网络连接
   - 确认 API 基础 URL 是否正确
   - 查看错误响应的具体信息

3. 类型错误
   - 确保传入参数符合类型要求
   - 使用 IDE 的类型提示功能
   - 参考 API 文档中的参数说明

## API 文档

完整的 API 文档请参考：[API 文档链接]

## 贡献指南

1. Fork 本仓库
2. 创建功能分支
3. 提交代码
4. 创建 Pull Request

## 许可证

MIT License 