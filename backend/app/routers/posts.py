import json
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.models.database import get_db, Post, User
from app.models.schemas import PostCreate, PostUpdate, PostResponse, PostSummary, PaginatedResponse
from app.services.auth import get_current_user, get_current_admin_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/posts", tags=["文章"])


def serialize_post(post: Post, include_content: bool = True) -> dict:
    """将数据库 Post 对象转为响应字典"""
    tags = []
    if post.tags:
        try:
            tags = json.loads(post.tags)
        except (json.JSONDecodeError, TypeError):
            tags = []
    result = {
        "id": post.id,
        "title": post.title,
        "summary": post.summary,
        "cover_image": post.cover_image,
        "tags": tags,
        "published": post.published,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
    }
    if include_content:
        result["content"] = post.content
    return result


@router.get("", response_model=PaginatedResponse)
async def list_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    published: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """获取文章列表（未登录默认只返回已发布文章）"""
    query = db.query(Post)

    # 管理员可以查看所有文章，普通用户只看已发布的
    if current_user and current_user.role == "admin":
        if published is not None:
            query = query.filter(Post.published == published)
    else:
        query = query.filter(Post.published == True)

    total = query.count()
    total_pages = (total + limit - 1) // limit

    posts = query.order_by(Post.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "data": [serialize_post(p, include_content=False) for p in posts],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
    }


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: str, db: Session = Depends(get_db)):
    """获取单篇文章（只返回已发布的）"""
    post = db.query(Post).filter(Post.id == post_id, Post.published == True).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    return serialize_post(post)


@router.post("", response_model=PostResponse)
async def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建文章（需要管理员权限）"""
    post_data = post.model_dump()
    if post_data.get("tags"):
        post_data["tags"] = json.dumps(post_data["tags"], ensure_ascii=False)
    db_post = Post(**post_data)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return serialize_post(db_post)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    post: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新文章（需要管理员权限）"""
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="文章不存在")

    update_data = post.model_dump(exclude_unset=True)
    if "tags" in update_data and update_data["tags"] is not None:
        update_data["tags"] = json.dumps(update_data["tags"], ensure_ascii=False)
    for key, value in update_data.items():
        setattr(db_post, key, value)

    db.commit()
    db.refresh(db_post)
    return serialize_post(db_post)


@router.delete("/{post_id}")
async def delete_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除文章（需要管理员权限）"""
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="文章不存在")

    db.delete(db_post)
    db.commit()
    return {"message": "文章已删除"}
