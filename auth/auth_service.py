from typing import Dict, Optional
import jwt
from datetime import datetime, timedelta
from passlib.hash import bcrypt
from fastapi import HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import uuid

class User(BaseModel):
    id: str
    email: str
    hashed_password: str
    full_name: Optional[str] = None
    api_key: Optional[str] = None
    subscription_tier: str = "free"
    created_at: datetime
    last_login: Optional[datetime] = None

class AuthService:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        self._users: Dict[str, User] = {}
        self._api_keys: Dict[str, str] = {}
    
    async def create_user(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None
    ) -> User:
        """Create a new user account."""
        if email in self._users:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        user_id = str(uuid.uuid4())
        api_key = self._generate_api_key()
        
        user = User(
            id=user_id,
            email=email,
            hashed_password=self._hash_password(password),
            full_name=full_name,
            api_key=api_key,
            created_at=datetime.utcnow()
        )
        
        self._users[email] = user
        self._api_keys[api_key] = email
        
        return user
    
    async def authenticate_user(
        self,
        email: str,
        password: str
    ) -> Optional[User]:
        """Authenticate user credentials."""
        user = self._users.get(email)
        if not user:
            return None
        
        if not self._verify_password(password, user.hashed_password):
            return None
        
        user.last_login = datetime.utcnow()
        return user
    
    def create_access_token(
        self,
        user: User,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token."""
        if expires_delta is None:
            expires_delta = timedelta(minutes=30)
        
        expire = datetime.utcnow() + expires_delta
        
        to_encode = {
            "sub": user.email,
            "exp": expire,
            "type": "access"
        }
        
        return jwt.encode(
            to_encode,
            self.secret_key,
            algorithm="HS256"
        )
    
    def verify_token(self, token: str) -> Optional[User]:
        """Verify JWT token and return user."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=["HS256"]
            )
            email = payload.get("sub")
            if email is None:
                return None
            return self._users.get(email)
        except jwt.PyJWTError:
            return None
    
    def verify_api_key(self, api_key: str) -> Optional[User]:
        """Verify API key and return user."""
        email = self._api_keys.get(api_key)
        if email is None:
            return None
        return self._users.get(email)
    
    def refresh_api_key(self, user: User) -> str:
        """Generate new API key for user."""
        if user.api_key:
            del self._api_keys[user.api_key]
        
        new_api_key = self._generate_api_key()
        user.api_key = new_api_key
        self._api_keys[new_api_key] = user.email
        
        return new_api_key
    
    def _generate_api_key(self) -> str:
        """Generate unique API key."""
        return f"omsk_{uuid.uuid4().hex}"
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return bcrypt.hash(password)
    
    def _verify_password(
        self,
        plain_password: str,
        hashed_password: str
    ) -> bool:
        """Verify password against hash."""
        return bcrypt.verify(plain_password, hashed_password)

class SubscriptionManager:
    def __init__(self):
        self.plans = {
            "free": {
                "requests_per_day": 100,
                "max_file_size": 1_000_000,  # 1MB
                "features": ["basic_analysis"]
            },
            "pro": {
                "requests_per_day": 1000,
                "max_file_size": 10_000_000,  # 10MB
                "features": [
                    "basic_analysis",
                    "advanced_optimization",
                    "priority_support"
                ]
            },
            "enterprise": {
                "requests_per_day": float("inf"),
                "max_file_size": 100_000_000,  # 100MB
                "features": [
                    "basic_analysis",
                    "advanced_optimization",
                    "priority_support",
                    "custom_models",
                    "dedicated_support"
                ]
            }
        }
    
    def check_limits(
        self,
        user: User,
        feature: str,
        file_size: Optional[int] = None
    ) -> bool:
        """Check if user's subscription allows the operation."""
        plan = self.plans.get(user.subscription_tier)
        if not plan:
            return False
        
        if feature not in plan["features"]:
            return False
        
        if file_size and file_size > plan["max_file_size"]:
            return False
        
        return True
    
    def upgrade_subscription(
        self,
        user: User,
        new_tier: str
    ) -> bool:
        """Upgrade user's subscription tier."""
        if new_tier not in self.plans:
            return False
        
        user.subscription_tier = new_tier
        return True
