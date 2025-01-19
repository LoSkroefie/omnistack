import pytest
from datetime import datetime, timedelta
import jwt
from auth.auth_service import (
    AuthService,
    User,
    SubscriptionManager
)

@pytest.fixture
def auth_service():
    return AuthService("test-secret-key")

@pytest.fixture
def subscription_manager():
    return SubscriptionManager()

@pytest.fixture
async def test_user(auth_service):
    return await auth_service.create_user(
        email="test@example.com",
        password="test123",
        full_name="Test User"
    )

class TestAuthService:
    async def test_create_user(self, auth_service):
        user = await auth_service.create_user(
            email="new@example.com",
            password="password123"
        )
        assert isinstance(user, User)
        assert user.email == "new@example.com"
        assert user.api_key is not None
    
    async def test_create_duplicate_user(self, auth_service, test_user):
        with pytest.raises(Exception):
            await auth_service.create_user(
                email="test@example.com",
                password="password123"
            )
    
    async def test_authenticate_user(self, auth_service, test_user):
        user = await auth_service.authenticate_user(
            email="test@example.com",
            password="test123"
        )
        assert user is not None
        assert user.email == test_user.email
    
    async def test_authenticate_invalid_password(
        self,
        auth_service,
        test_user
    ):
        user = await auth_service.authenticate_user(
            email="test@example.com",
            password="wrong-password"
        )
        assert user is None
    
    def test_create_access_token(self, auth_service, test_user):
        token = auth_service.create_access_token(test_user)
        assert isinstance(token, str)
        
        # Verify token
        payload = jwt.decode(
            token,
            auth_service.secret_key,
            algorithms=["HS256"]
        )
        assert payload["sub"] == test_user.email
    
    def test_create_token_with_expiry(self, auth_service, test_user):
        expires_delta = timedelta(minutes=15)
        token = auth_service.create_access_token(
            test_user,
            expires_delta
        )
        
        payload = jwt.decode(
            token,
            auth_service.secret_key,
            algorithms=["HS256"]
        )
        assert "exp" in payload
    
    def test_verify_token(self, auth_service, test_user):
        token = auth_service.create_access_token(test_user)
        user = auth_service.verify_token(token)
        assert user is not None
        assert user.email == test_user.email
    
    def test_verify_invalid_token(self, auth_service):
        user = auth_service.verify_token("invalid-token")
        assert user is None
    
    def test_verify_expired_token(self, auth_service, test_user):
        expires_delta = timedelta(seconds=-1)
        token = auth_service.create_access_token(
            test_user,
            expires_delta
        )
        
        with pytest.raises(jwt.ExpiredSignatureError):
            auth_service.verify_token(token)
    
    def test_verify_api_key(self, auth_service, test_user):
        user = auth_service.verify_api_key(test_user.api_key)
        assert user is not None
        assert user.email == test_user.email
    
    def test_verify_invalid_api_key(self, auth_service):
        user = auth_service.verify_api_key("invalid-key")
        assert user is None
    
    def test_refresh_api_key(self, auth_service, test_user):
        old_key = test_user.api_key
        new_key = auth_service.refresh_api_key(test_user)
        
        assert new_key != old_key
        assert auth_service.verify_api_key(new_key) == test_user
        assert auth_service.verify_api_key(old_key) is None

class TestSubscriptionManager:
    def test_check_limits_free_tier(
        self,
        subscription_manager,
        test_user
    ):
        test_user.subscription_tier = "free"
        assert subscription_manager.check_limits(
            test_user,
            "basic_analysis"
        )
        assert not subscription_manager.check_limits(
            test_user,
            "advanced_optimization"
        )
    
    def test_check_limits_pro_tier(
        self,
        subscription_manager,
        test_user
    ):
        test_user.subscription_tier = "pro"
        assert subscription_manager.check_limits(
            test_user,
            "basic_analysis"
        )
        assert subscription_manager.check_limits(
            test_user,
            "advanced_optimization"
        )
    
    def test_check_file_size_limits(
        self,
        subscription_manager,
        test_user
    ):
        test_user.subscription_tier = "free"
        assert subscription_manager.check_limits(
            test_user,
            "basic_analysis",
            file_size=500_000
        )
        assert not subscription_manager.check_limits(
            test_user,
            "basic_analysis",
            file_size=2_000_000
        )
    
    def test_upgrade_subscription(
        self,
        subscription_manager,
        test_user
    ):
        assert subscription_manager.upgrade_subscription(
            test_user,
            "pro"
        )
        assert test_user.subscription_tier == "pro"
    
    def test_upgrade_to_invalid_tier(
        self,
        subscription_manager,
        test_user
    ):
        assert not subscription_manager.upgrade_subscription(
            test_user,
            "invalid-tier"
        )
        assert test_user.subscription_tier == "free"
