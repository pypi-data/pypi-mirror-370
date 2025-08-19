# M-TEAM API 测试指南

## 环境配置

1. 复制环境变量模板：
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，填入实际的配置：
   ```text
   MTEAM_API_KEY=your_real_api_key_here
   MTEAM_BASE_URL=http://test2.m-team.cc/api
   ```

3. 安装测试依赖：
   ```bash
   pip install pytest python-dotenv
   ```

## 运行测试

1. 运行所有测试：
   ```bash
   pytest
   ```

2. 运行特定模块的测试：
   ```bash
   pytest tests/test_member.py
   pytest tests/test_torrent.py
   ```

3. 运行特定测试：
   ```bash
   pytest tests/test_member.py::test_login
   ```

4. 显示详细输出：
   ```bash
   pytest -v
   ```

## 测试覆盖范围

### 用户模块测试
- 注册新用户
- 用户登录
- 获取用户资料
- 更新用户资料

### 种子模块测试
- 搜索种子
- 获取种子详情
- 下载种子文件

## 注意事项

1. 确保 API 密钥有效且具有足够的权限
2. 测试环境应该使用测试服务器，避免影响生产环境
3. 某些测试可能需要特定的用户权限
4. 注意请求频率限制

## 常见问题

1. API 密钥无效
   - 检查 `.env` 文件中的 `MTEAM_API_KEY` 是否正确
   - 确认 API 密钥未过期

2. 请求失败
   - 检查网络连接
   - 确认 API 基础 URL 是否正确
   - 查看错误响应的具体信息

3. 测试超时
   - 可能是网络问题
   - 可能触发了频率限制
   - 尝试增加超时时间：`pytest --timeout=30` 

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate 