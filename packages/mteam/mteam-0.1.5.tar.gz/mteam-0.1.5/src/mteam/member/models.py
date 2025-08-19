from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class UserRole(str, Enum):
    """用户角色"""
    USER = "User"
    VIP = "VIP"
    MODERATOR = "Moderator"
    ADMIN = "Admin"

class UserStatus(str, Enum):
    """用户状态"""
    NORMAL = "Normal"
    PENDING = "Pending"
    BANNED = "Banned"

class RegisterForm(BaseModel):
    """注册表单"""
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str
    invitation_code: Optional[str] = None

class LoginForm(BaseModel):
    """登录表单"""
    username: str
    password: str
    two_factor_code: Optional[str] = None

class UserProfile(BaseModel):
    """用户资料"""
    id: int
    username: str
    email: EmailStr
    role: UserRole
    status: UserStatus
    join_time: datetime
    avatar_url: Optional[str] = None
    uploaded: int
    downloaded: int
    bonus_points: float
    invitations: int
    signature: Optional[str] = None

class ProfileUpdateForm(BaseModel):
    """资料更新表单"""
    avatar: Optional[str] = None
    signature: Optional[str] = None
    old_password: Optional[str] = None
    new_password: Optional[str] = None
    email: Optional[EmailStr] = None

class InvitationInfo(BaseModel):
    """邀请信息"""
    code: str
    created_at: datetime
    expires_at: datetime
    used_by: Optional[str] = None
    status: str 