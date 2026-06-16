import hashlib
from datetime import datetime, date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.models.database import get_db, Visit, Post, Image
from app.models.schemas import StatsResponse, DailyVisit

router = APIRouter(prefix="/stats", tags=["统计"])


@router.post("/visit")
async def record_visit(request: Request, db: Session = Depends(get_db)):
    """记录一次页面访问"""
    ip = request.client.host if request.client else "unknown"
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()
    ua = request.headers.get("user-agent", "")
    path = request.headers.get("referer", "/")

    visit = Visit(path=path, ip_hash=ip_hash, user_agent=ua)
    db.add(visit)
    db.commit()
    return {"message": "ok"}


@router.get("", response_model=StatsResponse)
async def get_stats(
    year: Optional[int] = Query(None, description="年份，不传则为当前年"),
    db: Session = Depends(get_db),
):
    """获取站点统计数据"""
    total_visits = db.query(func.count(Visit.id)).scalar() or 0

    today_start = datetime.combine(date.today(), datetime.min.time())
    today_visits = (
        db.query(func.count(Visit.id))
        .filter(Visit.created_at >= today_start)
        .scalar()
        or 0
    )

    total_posts = db.query(func.count(Post.id)).scalar() or 0
    published_posts = (
        db.query(func.count(Post.id)).filter(Post.published == True).scalar() or 0
    )
    total_images = db.query(func.count(Image.id)).scalar() or 0

    first_post_date = db.query(func.min(Post.created_at)).scalar()
    if first_post_date:
        running_days = max(1, (datetime.utcnow() - first_post_date).days + 1)
    else:
        running_days = 1

    # 有数据的年份列表
    year_rows = (
        db.query(extract("year", Visit.created_at).label("y"))
        .group_by("y")
        .all()
    )
    years = sorted([int(r.y) for r in year_rows if r.y], reverse=True)
    if not years:
        years = [date.today().year]

    # 指定年份的每日访问量
    target_year = year or date.today().year
    start_date = date(target_year, 1, 1)
    end_date = date(target_year, 12, 31)
    days_in_year = (end_date - start_date).days + 1

    rows = (
        db.query(
            func.date(Visit.created_at).label("d"),
            func.count(Visit.id).label("cnt"),
        )
        .filter(
            Visit.created_at >= datetime.combine(start_date, datetime.min.time()),
            Visit.created_at < datetime.combine(end_date + timedelta(days=1), datetime.min.time()),
        )
        .group_by("d")
        .all()
    )
    visit_map = {str(r.d): r.cnt for r in rows}

    daily_visits = []
    for i in range(days_in_year):
        d = start_date + timedelta(days=i)
        ds = d.isoformat()
        daily_visits.append(DailyVisit(date=ds, count=visit_map.get(ds, 0)))

    return StatsResponse(
        total_visits=total_visits,
        today_visits=today_visits,
        total_posts=total_posts,
        published_posts=published_posts,
        total_images=total_images,
        running_days=running_days,
        daily_visits=daily_visits,
        years=years,
    )
