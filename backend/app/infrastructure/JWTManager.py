from typing import Optional
from datetime import datetime, timedelta, timezone
import jwt
from settings import settings

import logging

logger = logging.getLogger(__name__)

class JWTManager:

    @staticmethod
    def generate_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str):
        try:
            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return decoded
        except jwt.ExpiredSignatureError:
            logger.warning("Attempt to use an expired token")
            raise ValueError("Token expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Attempt to use an invalid token: {e}")
            raise ValueError("Invalid token")
