from pydantic import BaseModel

class QuizResults(BaseModel):
    A: int
    B: int
    C: int
    D: int