from database.repositories import UserRepository, SessionRepository
from typing import Optional

class AuthService:
    @staticmethod
    def register_user(username: str, email: str, password: str, ip_address: str) -> int:
        user_id = UserRepository.create_user(username, email, password)
        SessionRepository.create_session(user_id, ip_address)
        return user_id

    @staticmethod
    def login_user(email: str, password: str, ip_address: str) -> Optional[int]:
        user = UserRepository.get_user_by_credentials(email, password)
        if user:
            user_id = user[0]
            SessionRepository.create_session(user_id, ip_address)
            return user_id
        return None