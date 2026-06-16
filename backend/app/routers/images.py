import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from PIL import Image as PILImage
from typing import Optional

from app.config import get_settings
from app.models.database import get_db, Image, User
from app.models.schemas import ImageResponse, PaginatedResponse
from app.services.auth import get_current_admin_user

settings = get_settings()

router = APIRouter(prefix="/images", tags=["图片"])


def create_thumbnail(image_path: str, thumbnail_path: str, size: tuple = (300, 300)):
    """创建缩略图"""
    with PILImage.open(image_path) as img:
        img.thumbnail(size)
        img.save(thumbnail_path)


@router.get("", response_model=PaginatedResponse)
async def list_images(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取图片列表"""
    query = db.query(Image)

    total = query.count()
    total_pages = (total + limit - 1) // limit

    images = query.order_by(Image.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "data": images,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
    }


@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(image_id: str, db: Session = Depends(get_db)):
    """获取单张图片"""
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="图片不存在")
    return image


@router.post("", response_model=ImageResponse)
async def upload_image(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """上传图片（需要管理员权限）"""
    # 验证文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只支持图片文件")

    # 验证文件大小
    file_size = 0
    file_content = await file.read()
    file_size = len(file_content)

    if file_size > settings.max_file_size:
        raise HTTPException(status_code=400, detail="文件大小超过限制")

    # 生成文件名
    file_ext = os.path.splitext(file.filename)[1]
    file_name = f"{uuid.uuid4()}{file_ext}"
    thumbnail_name = f"thumb_{file_name}"

    # 创建上传目录
    os.makedirs(settings.upload_dir, exist_ok=True)

    # 保存原图
    file_path = os.path.join(settings.upload_dir, file_name)
    with open(file_path, "wb") as f:
        f.write(file_content)

    # 创建缩略图
    thumbnail_path = os.path.join(settings.upload_dir, thumbnail_name)
    try:
        create_thumbnail(file_path, thumbnail_path)
    except Exception:
        thumbnail_path = None

    # 获取图片尺寸
    try:
        with PILImage.open(file_path) as img:
            width, height = img.size
    except Exception:
        width, height = None, None

    # 保存到数据库
    db_image = Image(
        url=f"/uploads/{file_name}",
        thumbnail=f"/uploads/{thumbnail_name}" if thumbnail_path else None,
        title=title or file.filename,
        width=width,
        height=height,
    )

    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    return db_image


@router.delete("/{image_id}")
async def delete_image(
    image_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除图片（需要管理员权限）"""
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="图片不存在")

    # 删除文件
    if image.url:
        file_path = os.path.join(settings.upload_dir, os.path.basename(image.url))
        if os.path.exists(file_path):
            os.remove(file_path)

    if image.thumbnail:
        thumb_path = os.path.join(settings.upload_dir, os.path.basename(image.thumbnail))
        if os.path.exists(thumb_path):
            os.remove(thumb_path)

    # 从数据库删除
    db.delete(image)
    db.commit()

    return {"message": "图片已删除"}
