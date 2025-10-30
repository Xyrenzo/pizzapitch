from database.repositories import QuizRepository
from typing import Dict, Any, Optional

class QuizService:
    @staticmethod
    def save_quiz_progress(user_id: int, current_question: int, answers: dict, results: dict = None):
        QuizRepository.save_quiz_progress(user_id, current_question, answers, results)

    @staticmethod
    def get_quiz_progress(user_id: int) -> Optional[Dict[str, Any]]:
        return QuizRepository.get_quiz_progress(user_id)

    @staticmethod
    def clear_quiz_progress(user_id: int):
        QuizRepository.clear_quiz_progress(user_id)

    @staticmethod
    def save_user_answers(user_id: int, answers: str, results: dict):
        QuizRepository.save_answers(user_id, answers, results)

    @staticmethod
    def get_user_answers(user_id: int):
        result = QuizRepository.get_latest_results(user_id)
        if result:
            return result[0], eval(result[1])
        return None, None