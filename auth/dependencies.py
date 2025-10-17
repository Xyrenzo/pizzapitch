from fastapi import Request, HTTPException, Depends
from typing import Optional
from database.repositories import SessionRepository

# часть реалтзуемой логики логина и регистрации

def get_client_ip(request: Request) -> str:
    return request.client.host

async def get_current_user(
    request: Request, 
    user_id: Optional[int] = None
) -> int:
    ip_address = get_client_ip(request)

    if user_id is None:
        user_id = request.query_params.get('user_id')
        if not user_id:
            raise HTTPException(status_code=403, detail="User ID required")
        user_id = int(user_id)

    if not SessionRepository.verify_access(user_id, ip_address):
        raise HTTPException(status_code=403, detail="Access denied")

    return user_id