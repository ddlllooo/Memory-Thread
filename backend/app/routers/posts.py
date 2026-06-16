from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.models.database import get_db, Post, User
from app.models.schemas import PostCreate, PostUpdate, PostResponse, PaginatedResponse
from app.services.auth import get_current_admin_user

router = APIRouter(prefix="/posts", tags=["文章"])


@router.get("", response_model=PaginatedResponse)
async def list_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    published: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """获取文章列表"""
    query = db.query(Post)

    if published is not None:
        query = query.filter(Post.published == published)

    total = query.count()
    total_pages = (total + limit - 1) // limit

    posts = query.order_by(Post.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "data": posts,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
    }


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: str, db: Session = Depends(get_db)):
    """获取单篇文章"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    return post


@router.post("", response_model=PostResponse)
async def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建文章（需要管理员权限）"""
    db_post = Post(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


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

    update_data = post.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_post, key, value)

    db.commit()
    db.refresh(db_post)
    return db_post


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
