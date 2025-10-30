from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
import math
from datetime import datetime, timedelta

from auth.dependencies import get_current_user
from database.repositories import ReviewRepository
from config import TEMPLATES_DIR, STATIC_DIR
from fastapi.staticfiles import StaticFiles

router = APIRouter(tags=["reviews"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


class ReviewCreate(BaseModel):
    rating: int
    comment: Optional[str] = ""

@router.get('/reviews', response_class=HTMLResponse)
def reviews_page(
    request: Request, 
    user_id: int = Depends(get_current_user)
):
    return templates.TemplateResponse("reviews.html", {
        "request": request,
        "user_id": user_id
    })

@router.get('/api/reviews')
async def get_reviews(
    request: Request,
    sort: str = "newest",
    user_id: int = Depends(get_current_user)
):
    try:
        reviews = ReviewRepository.get_all_reviews(sort)
        average_rating = ReviewRepository.get_average_rating()
        reviews_count = ReviewRepository.get_reviews_count()
        
        
        for review in reviews:
            review['time_ago'] = format_time_ago(review['created_at'])
            
            
            review['user_has_liked'] = ReviewRepository.has_user_liked(
                review['id'], user_id
            )
        
        
        user_review = ReviewRepository.get_review_by_user(user_id)
        if user_review:
            user_review['time_ago'] = format_time_ago(user_review['created_at'])
        
        return {
            'success': True,
            'reviews': reviews,
            'average_rating': average_rating,
            'reviews_count': reviews_count,
            'user_review': user_review
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/api/reviews')
async def create_review(
    request: Request,
    review_data: ReviewCreate,
    user_id: int = Depends(get_current_user)
):
    try:
        
        existing_review = ReviewRepository.get_review_by_user(user_id)
        if existing_review:
            raise HTTPException(status_code=400, detail="Вы уже оставили отзыв")
        
        if not 1 <= review_data.rating <= 5:
            raise HTTPException(status_code=400, detail="Рейтинг должен быть от 1 до 5")
        
        success = ReviewRepository.create_review(
            user_id, 
            review_data.rating, 
            review_data.comment
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Не удалось создать отзыв")
            
        return {"success": True}
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/api/reviews/{review_id}/like')
async def like_review(
    request: Request,
    review_id: int,
    user_id: int = Depends(get_current_user)
):
    try:
        success = ReviewRepository.like_review(review_id, user_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/api/reviews/{review_id}/unlike')
async def unlike_review(
    request: Request,
    review_id: int,
    user_id: int = Depends(get_current_user)
):
    try:
        success = ReviewRepository.unlike_review(review_id, user_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete('/api/reviews/user')
async def delete_user_review(
    request: Request,
    user_id: int = Depends(get_current_user)
):
    try:
        success = ReviewRepository.delete_review(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Отзыв не найден")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def format_time_ago(timestamp):
    """Форматирование времени в человекочитаемый вид с учетом локального времени"""
    if isinstance(timestamp, str):
        
        if 'Z' in timestamp:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            timestamp = timestamp.astimezone()
        else:
            timestamp = datetime.fromisoformat(timestamp)
    
    
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=None)
        now = datetime.now()
    else:
        now = datetime.now().astimezone()
    
    diff = now - timestamp
    
    if diff < timedelta(minutes=1):
        return "только что"
    elif diff < timedelta(hours=1):
        minutes = math.floor(diff.seconds / 60)
        return f"{minutes} минут назад"
    elif diff < timedelta(days=1):
        hours = math.floor(diff.seconds / 3600)
        return f"{hours} часов назад"
    elif diff < timedelta(days=30):
        days = diff.days
        return f"{days} дней назад"
    else:
        return timestamp.strftime("%d.%m.%Y в %H:%M")