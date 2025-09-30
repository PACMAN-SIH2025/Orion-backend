"""
Supabase Client Configuration
Handles Supabase authentication and database operations.
"""

from functools import lru_cache
from supabase import create_client, Client
from core.config import get_settings

settings = get_settings()

@lru_cache()
def get_supabase_client() -> Client:
    """Get Supabase client instance."""
    return create_client(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_anon_key
    )

@lru_cache()
def get_supabase_admin_client() -> Client:
    """Get Supabase admin client instance with service role key."""
    return create_client(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_service_role_key
    )

# Supabase service functions
class SupabaseService:
    """Service for Supabase operations."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.admin_client = get_supabase_admin_client()
    
    async def sign_up_user(self, email: str, password: str, user_metadata: dict = None):
        """Sign up a new user."""
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_metadata or {}
                }
            })
            return response
        except Exception as e:
            raise Exception(f"Signup failed: {str(e)}")
    
    async def sign_in_user(self, email: str, password: str):
        """Sign in an existing user."""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return response
        except Exception as e:
            raise Exception(f"Signin failed: {str(e)}")
    
    async def get_user_from_token(self, access_token: str):
        """Get user information from access token."""
        try:
            response = self.client.auth.get_user(access_token)
            return response
        except Exception as e:
            raise Exception(f"Token validation failed: {str(e)}")
    
    async def sign_out_user(self, access_token: str):
        """Sign out user."""
        try:
            response = self.client.auth.sign_out(access_token)
            return response
        except Exception as e:
            raise Exception(f"Signout failed: {str(e)}")
    
    async def reset_password(self, email: str):
        """Send password reset email."""
        try:
            response = self.client.auth.reset_password_email(email)
            return response
        except Exception as e:
            raise Exception(f"Password reset failed: {str(e)}")
    
    async def update_user_metadata(self, access_token: str, metadata: dict):
        """Update user metadata."""
        try:
            response = self.client.auth.update_user(
                access_token,
                {"data": metadata}
            )
            return response
        except Exception as e:
            raise Exception(f"Update user failed: {str(e)}")

# Global service instance
supabase_service = SupabaseService()