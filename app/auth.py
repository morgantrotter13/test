"""
Authentication module for Google OAuth and JWT tokens.
"""
from datetime import datetime, timedelta
from typing import Optional
import os
import jwt
import httpx
from fastapi import HTTPException, Depends, Header
from sqlalchemy.orm import Session
from app.database import get_db, User

# JWT Settings
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable must be set")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 1 week

# Google OAuth Settings
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")


def create_access_token(user_id: int, email: str) -> str:
    """Create a JWT access token."""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def verify_google_token(token: str) -> dict:
    """Verify Google OAuth token and get user info."""
    print(f"🔍 Verifying Google token...")
    try:
        # Get user info from Google
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            print(f"🔍 Google API response: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Google API error: {response.text}")
                raise HTTPException(status_code=401, detail="Invalid Google token")
            
            user_info = response.json()
            print(f"✅ Got user info: {user_info.get('email')}")
            return user_info
    except httpx.RequestError as e:
        print(f"❌ Network error calling Google: {e}")
        raise HTTPException(status_code=500, detail=f"Could not verify Google token: {str(e)}")


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user from JWT token in Authorization header."""
    if not authorization:
        return None
    
    try:
        # Extract token from "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
        
        payload = verify_token(token)
        user = db.query(User).filter(User.id == payload["user_id"]).first()
        return user
    except (ValueError, HTTPException):
        return None


def require_auth(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Require authentication - raises 401 if not authenticated."""
    user = get_current_user(authorization, db)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def get_or_create_user(db: Session, google_user: dict) -> User:
    """Get existing user or create new one from Google user info."""
    user = db.query(User).filter(User.google_id == google_user["sub"]).first()
    
    if user:
        # Update last login
        user.last_login = datetime.utcnow()
        user.name = google_user.get("name", user.name)
        user.picture = google_user.get("picture", user.picture)
        db.commit()
    else:
        # Create new user
        user = User(
            email=google_user["email"],
            name=google_user.get("name", ""),
            picture=google_user.get("picture", ""),
            google_id=google_user["sub"],
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user


def get_user_from_token(token: str, db: Session) -> Optional[User]:
    """Get user from token without raising exceptions. Returns None if invalid."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = db.query(User).filter(User.id == payload["user_id"]).first()
        return user
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
