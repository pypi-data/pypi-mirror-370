from typing import List, Optional
from ..models import Result
from .models import (
    RegisterForm,
    LoginForm,
    UserProfile,
    ProfileUpdateForm,
    InvitationInfo,
    UserRole,
    UserStatus
)

class MemberClient:
    """用户相关 API 客户端"""
    
    def __init__(self, base_client):
        self._client = base_client
    
    def register(self, form: RegisterForm) -> Result:
        """
        注册新用户
        
        Args:
            form: 注册表单
        """
        return Result(**self._client._make_request(
            "POST",
            "/member/register",
            json=form.model_dump()
        ))
    
    def login(self, form: LoginForm) -> Result:
        """
        用户登录
        
        Args:
            form: 登录表单
        """
        return Result(**self._client._make_request(
            "POST",
            "/member/login",
            json=form.model_dump()
        ))
    
    def logout(self) -> Result:
        """退出登录"""
        return Result(**self._client._make_request(
            "POST",
            "/member/logout"
        ))
    
    def get_profile(self, user_id: Optional[int] = None) -> Result[UserProfile]:
        """
        获取用户资料
        
        Args:
            user_id: 用户ID，不传则获取当前用户资料
        """
        endpoint = f"/member/profile/{user_id}" if user_id else "/member/profile"
        return Result[UserProfile](**self._client._make_request(
            "GET",
            endpoint
        ))
    
    def update_profile(self, form: ProfileUpdateForm) -> Result[UserProfile]:
        """
        更新用户资料
        
        Args:
            form: 更新表单
        """
        return Result[UserProfile](**self._client._make_request(
            "POST",
            "/member/profile/update",
            json=form.model_dump()
        ))
    
    def get_invitations(self) -> Result[List[InvitationInfo]]:
        """获取邀请码列表"""
        return Result[List[InvitationInfo]](**self._client._make_request(
            "GET",
            "/member/invitations"
        ))
    
    def generate_invitation(self) -> Result[InvitationInfo]:
        """生成新的邀请码"""
        return Result[InvitationInfo](**self._client._make_request(
            "POST",
            "/member/invitation/generate"
        ))
    
    def verify_email(self, code: str) -> Result:
        """
        验证邮箱
        
        Args:
            code: 验证码
        """
        return Result(**self._client._make_request(
            "POST",
            "/member/verify-email",
            params={"code": code}
        ))
    
    def reset_password(self, email: str) -> Result:
        """
        请求重置密码
        
        Args:
            email: 注册邮箱
        """
        return Result(**self._client._make_request(
            "POST",
            "/member/reset-password",
            params={"email": email}
        )) 