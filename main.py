from fastapi import FastAPI, Request
from database.connection import init_db
from auth.router import router as auth_router
from quiz.router import router as quiz_router
from chat.router import router as chat_router
from results.router import router as results_router
from reviews.router import router as reviews_router
from fastapi.middleware.cors import CORSMiddleware
from config import STATIC_DIR, IMAGES_DIR
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

init_db()


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/img", StaticFiles(directory=IMAGES_DIR), name="images")

@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    user_id = None
    user_id = request.query_params.get('user_id')
    return templates.TemplateResponse(
        "404.html",
        {
            "request": request,
            "user_id": user_id  
        },
        status_code=404
    )

app.include_router(auth_router)
app.include_router(quiz_router)
app.include_router(chat_router)
app.include_router(results_router)
app.include_router(reviews_router)
