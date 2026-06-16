from pydantic import BaseModel, EmailStr
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
class PostBase(BaseModel):
    title: str
    content: str
    excerpt: Optional[str] = None
    published: bool = False


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    published: Optional[bool] = None


class PostResponse(PostBase):
    id: str
    cover_image_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 图片相关
class ImageBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class ImageCreate(ImageBase):
    pass


class ImageResponse(ImageBase):
    id: str
    url: str
    thumbnail: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    post_id: Optional[str] = None
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
