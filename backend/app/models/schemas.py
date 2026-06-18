from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# 用户相关
class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: str
    avatar: Optional[str] = None
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# 认证相关
class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# 文章相关
class PostCreate(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    tags: Optional[list[str]] = None
    published: bool = False

    class Config:
        from_attributes = True


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    tags: Optional[list[str]] = None
    published: Optional[bool] = None

    class Config:
        from_attributes = True


class PostSummary(BaseModel):
    """文章列表摘要（不含 content）"""
    id: str
    title: str
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    tags: list[str] = []
    published: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PostResponse(PostSummary):
    """文章详情（含 content）"""
    content: str


# 图片相关
class ImageResponse(BaseModel):
    id: str
    url: str
    thumbnail: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 分页响应
class PaginatedResponse(BaseModel):
    data: list
    total: int
    page: int
    limit: int
    total_pages: int


# 统计相关
class DailyVisit(BaseModel):
    date: str
    count: int


class StatsResponse(BaseModel):
    total_visits: int
    today_visits: int
    total_posts: int
    published_posts: int
    total_images: int
    running_days: int
    daily_visits: list[DailyVisit] = []
    years: list[int] = []  # 有数据的年份列表
