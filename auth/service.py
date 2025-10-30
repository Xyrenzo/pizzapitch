import random
import smtplib
from email.mime.text import MIMEText
from database.repositories import UserRepository, SessionRepository
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import httpx
import secrets
import json

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

BASE_URL = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")

verification_codes = {}
oauth_states = {}

class AuthService:
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
    @staticmethod
    def register_user(username: str, email: str, password: str, ip_address: str) -> int:
        user_id = UserRepository.create_user(username, email, password)
        SessionRepository.create_session(user_id, ip_address)
        AuthService.send_verification_code(email)
        return user_id

    @staticmethod
    def send_verification_code(email: str):
        code = ''.join(str(random.randint(0, 9)) for _ in range(6))
        verification_codes[email] = {
            "code": code,
            "expires": datetime.utcnow() + timedelta(minutes=10)
        }

        msg = MIMEText(f"Ваш код подтверждения: {code}")
        msg["Subject"] = "Подтверждение почты"
        msg["From"] = "noreply@yourapp.com"
        msg["To"] = email

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.send_message(msg)
        except Exception as e:
            print("Ошибка отправки email:", e)

    @staticmethod
    def verify_code(email: str, code: str) -> bool:
        data = verification_codes.get(email)
        if not data:
            return False
        if datetime.utcnow() > data["expires"]:
            del verification_codes[email]
            return False
        if data["code"] != code:
            return False
        del verification_codes[email]
        return True

    @staticmethod
    def login_user(email: str, password: str, ip_address: str) -> Optional[int]:
        user = UserRepository.get_user_by_credentials(email, password)
        if user:
            user_id = user[0]
            SessionRepository.create_session(user_id, ip_address)
            return user_id
        return None

    
    @staticmethod
    def generate_oauth_state(provider: str) -> str:
        state = secrets.token_urlsafe(32)
        oauth_states[state] = {
            "provider": provider,
            "created": datetime.utcnow(),
            "expires": datetime.utcnow() + timedelta(minutes=10)
        }
        return state

    @staticmethod
    def validate_oauth_state(state: str, provider: str = None) -> bool:
        data = oauth_states.get(state)
        if not data:
            return False
        
        if datetime.utcnow() > data["expires"]:
            del oauth_states[state]
            return False
        
        if provider and data.get("provider") != provider:
            return False
        del oauth_states[state]
        return True

    @staticmethod
    async def google_oauth_callback(code: str) -> Dict[str, Any]:
        try:
            redirect_uri = f"{BASE_URL}/auth/google/callback"
            
            async with httpx.AsyncClient() as client:
                token_response = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": GOOGLE_CLIENT_ID,
                        "client_secret": GOOGLE_CLIENT_SECRET,
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": redirect_uri
                    }
                )
                
                print(f"Token response status: {token_response.status_code}")
                print(f"Token response: {token_response.text}")
                
                if token_response.status_code != 200:
                    return {"error": f"Failed to get access token: {token_response.text}"}
                
                token_data = token_response.json()
                access_token = token_data["access_token"]
                
                
                user_response = await client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                print(f"User info response status: {user_response.status_code}")
                
                if user_response.status_code != 200:
                    return {"error": f"Failed to get user info: {user_response.text}"}
                
                user_data = user_response.json()
                print(f"User data: {user_data}")
                
                return {
                    "email": user_data["email"],
                    "name": user_data.get("name", user_data["email"].split('@')[0]),
                    "provider": "google",
                    "provider_id": user_data["id"]
                }
                
        except Exception as e:
            print(f"Google OAuth error: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    async def github_oauth_callback(code: str) -> Dict[str, Any]:
        try:
            
            async with httpx.AsyncClient() as client:
                
                token_response = await client.post(
                    "https://github.com/login/oauth/access_token",
                    headers={"Accept": "application/json"},
                    data={
                        "client_id": GITHUB_CLIENT_ID,
                        "client_secret": GITHUB_CLIENT_SECRET,
                        "code": code,
                        "redirect_uri": "https://pizzapitch.onrender.com/auth/github/callback" 
                    }
                )
                
                print(f"GitHub token response status: {token_response.status_code}")
                print(f"GitHub token response: {token_response.text}")
                
                if token_response.status_code != 200:
                    return {"error": f"Failed to get access token: {token_response.text}"}
                
                token_data = token_response.json()
                access_token = token_data["access_token"]
                
                
                user_response = await client.get(
                    "https://api.github.com/user",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                print(f"GitHub user info response status: {user_response.status_code}")
                
                if user_response.status_code != 200:
                    return {"error": f"Failed to get user info: {user_response.text}"}
                
                user_data = user_response.json()
                print(f"GitHub user data: {user_data}")
                
                
                emails_response = await client.get(
                    "https://api.github.com/user/emails",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if emails_response.status_code != 200:
                    return {"error": f"Failed to get user emails: {emails_response.text}"}
                
                emails_data = emails_response.json()
                primary_email = next((email["email"] for email in emails_data if email["primary"] and email["verified"]), None)
                
                if not primary_email:
                    primary_email = next((email["email"] for email in emails_data if email["verified"]), None)
                
                return {
                    "email": primary_email or user_data.get("email", ""),
                    "name": user_data.get("name", user_data.get("login", "")),
                    "provider": "github",
                    "provider_id": str(user_data["id"])
                }
                
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def oauth_login(user_data: Dict[str, Any], ip_address: str) -> int:
        email = user_data["email"]
        name = user_data["name"]
        provider = user_data["provider"]
        provider_id = user_data["provider_id"]
    
        user = UserRepository.get_user_by_oauth(provider, provider_id)
    
        if user:
            user_id = user[0]
        else:
        
            user = UserRepository.get_user_by_email(email)
        
            if user:
                user_id = user[0]
            
                UserRepository.save_oauth_info(user_id, provider, provider_id)
            else:
            
            
                random_password = secrets.token_urlsafe(16)
                user_id = UserRepository.create_user(name, email, random_password)
            
            
                UserRepository.save_oauth_info(user_id, provider, provider_id)
    
    
        SessionRepository.create_session(user_id, ip_address)
        return user_id