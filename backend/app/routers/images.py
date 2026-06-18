import os
import uuid
import logging
from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import Optional
from PIL import Image as PILImage

from app.config import get_settings
from app.models.database import get_db, Image, User
from app.models.schemas import ImageResponse, PaginatedResponse
from app.services.auth import get_current_admin_user

logger = logging.getLogger(__name__)
settings = get_settings()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"}
ALLOWED_MIME_PREFIXES = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/bmp", "image/svg+xml"}

router = APIRouter(prefix="/images", tags=["图片"])


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


@router.post("", response_model=ImageResponse)
async def upload_image(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """上传图片（需要管理员权限）"""
    if not file.content_type or file.content_type not in ALLOWED_MIME_PREFIXES:
        raise HTTPException(status_code=400, detail="只支持图片文件")

    file_content = await file.read()
    if len(file_content) > settings.max_file_size:
        raise HTTPException(status_code=400, detail="文件大小超过限制")

    # 验证扩展名白名单
    file_ext = os.path.splitext(file.filename)[1].lower() if file.filename else ".png"
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式: {file_ext}")

    # 通过 Pillow 验证图片文件（SVG 跳过，因为 Pillow 不支持）
    if file_ext != ".svg":
        try:
            img = PILImage.open(BytesIO(file_content))
            img.verify()
        except Exception:
            raise HTTPException(status_code=400, detail="无效的图片文件")

    file_name = f"{uuid.uuid4()}{file_ext}"

    os.makedirs(settings.upload_dir, exist_ok=True)

    file_path = os.path.join(settings.upload_dir, file_name)
    with open(file_path, "wb") as f:
        f.write(file_content)
    logger.info(f"图片上传成功: {file_name}")

    db_image = Image(
        url=f"/uploads/{file_name}",
        thumbnail=f"/uploads/{file_name}",
        title=title or file.filename,
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

    if image.url:
        file_path = os.path.join(settings.upload_dir, os.path.basename(image.url))
        if os.path.exists(file_path):
            os.remove(file_path)

    db.delete(image)
    db.commit()

    return {"message": "图片已删除"}
