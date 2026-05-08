"""
Authentication Service using Supabase Auth.

This service provides user authentication and authorization using Supabase Auth.
It handles user registration, login, session management, and profile creation.

Features:
- Email/password authentication
- JWT token management
- User profile management
- Session validation
"""

from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """
    Authentication service using Supabase Auth.
    
    Provides user registration, login, session management, and profile operations.
    Uses Supabase Auth for JWT-based authentication with Row Level Security.
    
    Attributes:
        supabase: Supabase client instance
    """
    
    def __init__(self, supabase: Client):
        """
        Initialize AuthService.
        
        Args:
            supabase: Supabase client instance
        
        Example:
            >>> from supabase import create_client
            >>> supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            >>> auth = AuthService(supabase)
        """
        self.supabase = supabase
    
    def sign_up(self, email: str, password: str, full_name: str = None) -> Dict[str, Any]:
        """
        Register a new user.
        
        Creates a new user in Supabase Auth and optionally creates a profile.
        
        Args:
            email: User email address
            password: User password (min 6 characters)
            full_name: Optional full name for profile
        
        Returns:
            Dictionary with user data and session
            
        Raises:
            Exception: If registration fails
            
        Example:
            >>> result = auth.sign_up("user@example.com", "password123", "John Doe")
            >>> print(result["user"]["id"])
        """
        try:
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name
                    } if full_name else {}
                }
            })
            
            # Create profile if user is created
            if response.user:
                self.create_profile(response.user.id, email, full_name)
                logger.info(f"User registered: {email}")
            
            return response.model_dump()
            
        except Exception as e:
            logger.error(f"Registration failed for {email}: {e}")
            raise
    
    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email address
            password: User password
        
        Returns:
            Dictionary with user data and session tokens
            
        Raises:
            Exception: If authentication fails
            
        Example:
            >>> result = auth.sign_in("user@example.com", "password123")
            >>> print(result["session"]["access_token"])
        """
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            logger.info(f"User logged in: {email}")
            return response.model_dump()
            
        except Exception as e:
            logger.error(f"Login failed for {email}: {e}")
            raise
    
    def sign_out(self) -> Dict[str, Any]:
        """
        Log out current user and invalidate session.
        
        Returns:
            Dictionary with response status
        
        Example:
            >>> result = auth.sign_out()
        """
        try:
            response = self.supabase.auth.sign_out()
            logger.info("User logged out")
            return response.model_dump()
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            raise
    
    def get_user(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get current user from JWT token.
        
        Args:
            token: JWT access token
        
        Returns:
            User data dictionary or None if invalid
            
        Example:
            >>> user = auth.get_user(access_token)
            >>> if user:
            ...     print(user["email"])
        """
        try:
            options = ClientOptions(auth_token=token)
            client = create_client(
                self.supabase.url,
                self.supabase.key,
                options=options
            )
            
            user_response = client.auth.get_user()
            if user_response.user:
                logger.debug("User validated successfully")
                return user_response.user.model_dump()
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None
    
    def create_profile(self, user_id: str, email: str, full_name: str = None) -> None:
        """
        Create a user profile in the profiles table.
        
        Args:
            user_id: User ID from auth.users
            email: User email
            full_name: Optional full name
        
        Example:
            >>> auth.create_profile("user-uuid", "user@example.com", "John Doe")
        """
        try:
            self.supabase.table("profiles").insert({
                "id": user_id,
                "email": email,
                "full_name": full_name
            }).execute()
            logger.info(f"Profile created for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to create profile: {e}")
            # Profile might already exist, which is OK
            if "duplicate key" not in str(e).lower():
                raise
    
    def update_profile(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user profile information.
        
        Args:
            user_id: User ID
            updates: Dictionary of fields to update
        
        Returns:
            Updated profile data
            
        Example:
            >>> result = auth.update_profile("user-uuid", {"full_name": "Jane Doe"})
        """
        try:
            response = self.supabase.table("profiles").update(updates).eq(
                "id", user_id
            ).execute()
            logger.info(f"Profile updated for user {user_id}")
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Failed to update profile: {e}")
            raise
    
    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile by ID.
        
        Args:
            user_id: User ID
        
        Returns:
            Profile data or None if not found
        """
        try:
            response = self.supabase.table("profiles").select("*").eq(
                "id", user_id
            ).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to get profile: {e}")
            return None
    
    def get_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """
        Get session information from session token.
        
        Args:
            session_token: Session token
        
        Returns:
            Session data or None if invalid
        """
        try:
            response = self.supabase.auth.get_session(session_token)
            if response.session:
                return response.session.model_dump()
            return None
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            return None
    
    def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token
        
        Returns:
            New session data
        
        Example:
            >>> new_session = auth.refresh_session(refresh_token)
            >>> print(new_session["access_token"])
        """
        try:
            response = self.supabase.auth.refresh_session(refresh_token)
            logger.debug("Session refreshed successfully")
            return response.model_dump()
        except Exception as e:
            logger.error(f"Failed to refresh session: {e}")
            raise
    
    def reset_password(self, email: str) -> Dict[str, Any]:
        """
        Request password reset email.
        
        Args:
            email: User email address
        
        Returns:
            Response status
        
        Example:
            >>> result = auth.reset_password("user@example.com")
        """
        try:
            response = self.supabase.auth.reset_password_for_email(
                email,
                options={"redirect_to": "https://yourapp.com/reset-password"}
            )
            logger.info(f"Password reset requested for {email}")
            return response.model_dump()
        except Exception as e:
            logger.error(f"Failed to request password reset: {e}")
            raise
    
    def change_password(self, new_password: str) -> Dict[str, Any]:
        """
        Change password for current user.
        
        Args:
            new_password: New password
        
        Returns:
            Response with user data
        
        Example:
            >>> result = auth.change_password("newpassword123")
        """
        try:
            response = self.supabase.auth.update_user({
                "password": new_password
            })
            logger.info("Password changed successfully")
            return response.model_dump()
        except Exception as e:
            logger.error(f"Failed to change password: {e}")
            raise
    
    def delete_user_account(self) -> Dict[str, Any]:
        """
        Delete current user account and all associated data.
        
        WARNING: This permanently deletes the user and all their data.
        
        Returns:
            Response status
        
        Example:
            >>> result = auth.delete_user_account()
        """
        try:
            response = self.supabase.auth.admin.delete_user(
                self.supabase.auth.get_user().user.id
            )
            logger.info("User account deleted")
            return response.model_dump()
        except Exception as e:
            logger.error(f"Failed to delete user account: {e}")
            raise
    
    def list_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all users (admin only).
        
        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
        
        Returns:
            List of user data dictionaries
        """
        try:
            response = self.supabase.auth.admin.list_users(
                page=1,
                per_page=limit
            )
            return [user.model_dump() for user in response.users]
        except Exception as e:
            logger.error(f"Failed to list users: {e}")
            raise
