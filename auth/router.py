from fastapi import APIRouter, Request, Form, Depends, Response
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from auth.service import AuthService
from auth.dependencies import get_client_ip
from config import TEMPLATES_DIR, STATIC_DIR
from fastapi.staticfiles import StaticFiles
from auth.service import BASE_URL


router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
router.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

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
        return RedirectResponse(url=f"/verify?email={email}&user_id={user_id}", status_code=303)
    except Exception as e:
        return {"error": str(e)}

@router.get('/verify', response_class=HTMLResponse)
def verify_page(request: Request, email: str, user_id: int):
    return templates.TemplateResponse("verify.html", {"request": request, "email": email, "user_id": user_id})

@router.post('/verify_code')
def verify_code(email: str = Form(...), code: str = Form(...), user_id: int = Form(...)):
    if AuthService.verify_code(email, code):
        return JSONResponse({"success": True, "redirect_url": f"/questions?user_id={user_id}"})
    return JSONResponse({"success": False, "message": "Неверный или просроченный код"})

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
            return RedirectResponse(url=f"/questions?user_id={user_id}", status_code=303)
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

@router.post('/resend_code')
def resend_code(email: str = Form(...)):
    try:
        AuthService.send_verification_code(email)
        return JSONResponse({"success": True})
    except Exception as e:
        return JSONResponse({"success": False, "message": str(e)})


@router.get('/auth/google')
def google_auth():
    state = AuthService.generate_oauth_state("google")
    
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={AuthService.GOOGLE_CLIENT_ID}&"
        f"response_type=code&"
        f"scope=openid%20email%20profile&"
        f"redirect_uri={BASE_URL}/auth/google/callback&"
        f"state={state}&"
        f"access_type=offline"
    )
    return RedirectResponse(google_auth_url)

@router.get('/auth/google/callback')
async def google_callback(request: Request, code: str = None, state: str = None, error: str = None):
    try:
        ip_address = get_client_ip(request)
        
        if error:
            return JSONResponse({"error": f"OAuth error: {error}"}, status_code=400)
        
        if not code:
            return JSONResponse({"error": "Missing code parameter"}, status_code=400)
        
        if not state:
            return JSONResponse({"error": "No state parameter received"}, status_code=400)
        
        
        if not AuthService.validate_oauth_state(state, "google"):
            return JSONResponse({"error": "Invalid or expired state"}, status_code=400)
        
        
        user_data = await AuthService.google_oauth_callback(code)
        
        if "error" in user_data:
            return JSONResponse({"error": user_data["error"]}, status_code=400)
        
        
        user_id = AuthService.oauth_login(user_data, ip_address)
        
        return RedirectResponse(url=f"/questions?user_id={user_id}", status_code=303)
        
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

@router.get('/auth/github')
def github_auth():
    state = AuthService.generate_oauth_state("github")
    
    github_auth_url = (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={AuthService.GITHUB_CLIENT_ID}&"
        f"scope=user:email&"
        f"state={state}"
    )
    return RedirectResponse(github_auth_url)

@router.get('/auth/github/callback')
async def github_callback(request: Request, code: str = None, state: str = None, error: str = None):
    try:
        ip_address = get_client_ip(request)
        
        if error:
            return JSONResponse({"error": f"OAuth error: {error}"}, status_code=400)
        
        if not code:
            return JSONResponse({"error": "Missing code parameter"}, status_code=400)
        
        if not state:
            return JSONResponse({"error": "No state parameter received"}, status_code=400)
        
        
        if not AuthService.validate_oauth_state(state, "github"):
            return JSONResponse({"error": "Invalid or expired state"}, status_code=400)
        
        
        user_data = await AuthService.github_oauth_callback(code)
        
        if "error" in user_data:
            return JSONResponse({"error": user_data["error"]}, status_code=400)
        
        
        user_id = AuthService.oauth_login(user_data, ip_address)
        
        return RedirectResponse(url=f"/questions?user_id={user_id}", status_code=303)
        
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)