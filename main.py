from fastapi import FastAPI
from database.connection import init_db
from auth.router import router as auth_router
from quiz.router import router as quiz_router
from chat.router import router as chat_router
from results.router import router as results_router
from reviews.router import router as reviews_router
from fastapi.middleware.cors import CORSMiddleware
from config import STATIC_DIR, IMAGES_DIR
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


init_db()


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/img", StaticFiles(directory=IMAGES_DIR), name="images")


app.include_router(auth_router)
app.include_router(quiz_router)
app.include_router(chat_router)
app.include_router(results_router)
app.include_router(reviews_router)