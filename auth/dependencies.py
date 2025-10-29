
from fastapi import Request, HTTPException, Depends
from typing import Optional
from database.repositories import SessionRepository
import secrets

def get_client_ip(request: Request) -> str:
    return request.client.host

async def get_current_user(request: Request) -> int:
    ip_address = get_client_ip(request)
    
    
    user_id = request.query_params.get('user_id')
    
    
    if not user_id:
        try:
            body = await request.json()
            user_id = body.get('user_id')
        except:
            pass
    
    if not user_id:
        raise HTTPException(status_code=403, detail="User ID required")
    
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=403, detail="Invalid user ID")

    if not SessionRepository.verify_access(user_id, ip_address):
        raise HTTPException(status_code=403, detail="Access denied")

    return user_id


def generate_oauth_state() -> str:
    return secrets.token_urlsafe(32)