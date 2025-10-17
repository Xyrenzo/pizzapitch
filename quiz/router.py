from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from auth.dependencies import get_current_user
from quiz.service import QuizService
from quiz.models import QuizResults
from config import TEMPLATES_DIR

router = APIRouter(prefix="/quiz", tags=["quiz"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# страницы с вопросами

@router.get('/questions', response_class=HTMLResponse)
def questions_page(request: Request, user_id: int = Depends(get_current_user)):
    progress = QuizService.get_quiz_progress(user_id)
    
    saved_answers = {}
    current_question = 0
    saved_results = None

    if progress:
        current_question = progress['current_question']
        saved_answers = progress['answers']
        saved_results = progress['results']

    return templates.TemplateResponse("questions.html", {
        "request": request,
        "user_id": user_id,
        "saved_answers": saved_answers,
        "saved_results": saved_results,
        "current_question": current_question
    })

@router.post('/process_results')
async def process_results(
    request: Request,
    user_id: int = Depends(get_current_user)
):
    try:
        body = await request.json()
        
        results = QuizResults(
            A=body.get('A', 0),
            B=body.get('B', 0),
            C=body.get('C', 0),
            D=body.get('D', 0)
        )

        answers_string = f"A:{results.A},B:{results.B},C:{results.C},D:{results.D}"
        QuizService.save_user_answers(user_id, answers_string, results.dict())
        QuizService.clear_quiz_progress(user_id)

        return {"status": "success", "results": results.dict()}

    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.get('/A', response_class=HTMLResponse)
def type_a_page(request: Request, user_id: int = Depends(get_current_user)):
    return templates.TemplateResponse("A.html", {
        "request": request,
        "user_id": user_id
    })

@router.get('/B', response_class=HTMLResponse)
def type_b_page(request: Request, user_id: int = Depends(get_current_user)):
    return templates.TemplateResponse("B.html", {
        "request": request,
        "user_id": user_id
    })

@router.get('/C', response_class=HTMLResponse)
def type_c_page(request: Request, user_id: int = Depends(get_current_user)):
    return templates.TemplateResponse("C.html", {
        "request": request,
        "user_id": user_id
    })

@router.get('/D', response_class=HTMLResponse)
def type_d_page(request: Request, user_id: int = Depends(get_current_user)):
    return templates.TemplateResponse("D.html", {
        "request": request,
        "user_id": user_id
    })

@router.post('/save_progress')
async def save_quiz_progress_endpoint(
    request: Request,
    user_id: int = Depends(get_current_user)
):
    try:
        body = await request.json()
        QuizService.save_quiz_progress(
            user_id=user_id,
            current_question=body.get('current_question', 0),
            answers=body.get('answers', {}),
            results=body.get('results')
        )
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.get('/get_progress')
async def get_quiz_progress_endpoint(
    request: Request,
    user_id: int = Depends(get_current_user)
):
    try:
        progress = QuizService.get_quiz_progress(user_id)
        return progress or {}
    except Exception as e:
        return {"error": str(e)}