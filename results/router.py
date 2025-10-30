from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth.dependencies import get_current_user
from results.service import ResultsService
from database.repositories import UserRepository, SessionRepository
from config import TEMPLATES_DIR, STATIC_DIR
from fastapi.staticfiles import StaticFiles

router = APIRouter(tags=["results"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
router.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@router.get('/results', response_class=HTMLResponse)
def results_page(request: Request, user_id: int = Depends(get_current_user)):
    return templates.TemplateResponse("results.html", {
        "request": request,
        "user_id": user_id
    })

@router.get('/get_user_results')
async def get_user_results(
    request: Request,
    user_id: int = Depends(get_current_user)
):
    try:
        results = ResultsService.get_user_results(user_id)
        if results:
            return results
        else:
            return {"error": "No results found"}
    except Exception as e:
        return {"error": str(e)}

@router.get('/all', response_class=HTMLResponse)
def all_types_page(request: Request, user_id: int = Depends(get_current_user)):
    return templates.TemplateResponse("all.html", {
        "request": request,
        "user_id": user_id
    })

@router.get('/get_users')
def get_users():
    try:
        users = UserRepository.get_all_users()
        return {"users": [{"id": u[0], "username": u[1], "email": u[2], "password": u[3]} for u in users]}
    except Exception as e:
        return {"error": str(e)}

@router.get('/get_sessions')
def get_sessions():
    try:
        sessions = SessionRepository.get_all_sessions()
        return {"sessions": [{"id": s[0], "user_id": s[1], "ip_address": s[2], "created_at": s[3]} for s in sessions]}
    except Exception as e:
        return {"error": str(e)}