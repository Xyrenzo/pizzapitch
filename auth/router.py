from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from auth.service import AuthService
from auth.dependencies import get_client_ip
from config import TEMPLATES_DIR

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# маршрутизация клиента в регистрационную страницу или в страницу логина

@router.get('/')
def root(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post('/register')
def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    try:
        ip_address = get_client_ip(request)
        user_id = AuthService.register_user(username, email, password, ip_address)
        return RedirectResponse(url=f"/quiz/questions?user_id={user_id}", status_code=303)
    except Exception as e:
        return {"error": str(e)}

@router.post('/login')
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    try:
        ip_address = get_client_ip(request)
        user_id = AuthService.login_user(email, password, ip_address)
        
        if user_id:
            return RedirectResponse(url=f"/quiz/questions?user_id={user_id}", status_code=303)
        else:
            return {"error": "Invalid email or password."}
    except Exception as e:
        return {"error": str(e)}

@router.get('/login', response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get('/register', response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})