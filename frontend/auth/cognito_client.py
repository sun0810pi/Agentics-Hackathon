import boto3
from typing import Dict, Any, Optional
import streamlit as st
from config import config
import logging

logger = logging.getLogger(__name__)


class CognitoClient:
    """
    AWS Cognito authentication client
    
    Handles all authentication operations:
    - Login/Signup
    - Token management
    - Password reset
    - Email verification
    """
    
    def __init__(self):
        """Initialize Cognito client"""
        # Get Cognito config
        cognito_config = config.get_cognito_config()
        
        self.user_pool_id = cognito_config.get("user_pool_id", "")
        self.client_id = cognito_config.get("client_id", "")
        self.region = cognito_config.get("region", "us-east-1")
        
        # Check if configured
        self.is_configured = bool(self.user_pool_id and self.client_id)
        
        if self.is_configured:
            try:
                # Initialize boto3 client
                self.client = boto3.client(
                    'cognito-idp',
                    region_name=self.region
                )
                logger.info("Cognito client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Cognito client: {e}")
                self.is_configured = False
                self.client = None
        else:
            self.client = None
            logger.warning("Cognito not configured - using demo mode")
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Login with email and password
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Dict with:
                - success: bool
                - access_token: str (if success)
                - id_token: str (if success)
                - refresh_token: str (if success)
                - expires_in: int (if success)
                - error: str (if failed)
        """
        if not self.is_configured:
            # Demo mode - use demo users
            return self._demo_login(email, password)
        
        try:
            # Authenticate with Cognito
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password
                }
            )
            
            # Extract tokens
            auth_result = response['AuthenticationResult']
            
            logger.info(f"User {email} logged in successfully")
            
            return {
                'success': True,
                'access_token': auth_result['AccessToken'],
                'id_token': auth_result['IdToken'],
                'refresh_token': auth_result['RefreshToken'],
                'expires_in': auth_result['ExpiresIn']
            }
        
        except self.client.exceptions.NotAuthorizedException:
            logger.warning(f"Failed login attempt for {email}")
            return {
                'success': False,
                'error': 'Invalid email or password'
            }
        
        except self.client.exceptions.UserNotFoundException:
            return {
                'success': False,
                'error': 'User not found'
            }
        
        except Exception as e:
            logger.error(f"Login error: {e}")
            return {
                'success': False,
                'error': f'Login failed: {str(e)}'
            }
    
    def _demo_login(self, email: str, password: str) -> Dict[str, Any]:
        """Demo login (when Cognito not configured)"""
        demo_users = config.DEMO_USERS
        
        if email in demo_users:
            user = demo_users[email]
            if user['password'] == password:
                return {
                    'success': True,
                    'access_token': 'demo_access_token',
                    'id_token': 'demo_id_token',
                    'refresh_token': 'demo_refresh_token',
                    'expires_in': 3600
                }
        
        return {
            'success': False,
            'error': 'Invalid email or password'
        }
    
    def signup(self, email: str, password: str, name: str) -> Dict[str, Any]:
        """
        Register new user
        
        Args:
            email: User email
            password: User password
            name: User full name
            
        Returns:
            Dict with success/error
        """
        if not self.is_configured:
            return {
                'success': False,
                'error': 'Signup not available in demo mode'
            }
        
        try:
            response = self.client.sign_up(
                ClientId=self.client_id,
                Username=email,
                Password=password,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                    {'Name': 'name', 'Value': name}
                ]
            )
            
            logger.info(f"User {email} signed up successfully")
            
            return {
                'success': True,
                'message': 'Account created! Check your email for verification code.'
            }
        
        except self.client.exceptions.UsernameExistsException:
            return {
                'success': False,
                'error': 'Email already registered'
            }
        
        except self.client.exceptions.InvalidPasswordException as e:
            return {
                'success': False,
                'error': str(e)
            }
        
        except Exception as e:
            logger.error(f"Signup error: {e}")
            return {
                'success': False,
                'error': f'Signup failed: {str(e)}'
            }
    
    def verify_email(self, email: str, code: str) -> Dict[str, Any]:
        """
        Verify email with code
        
        Args:
            email: User email
            code: Verification code from email
            
        Returns:
            Dict with success/error
        """
        if not self.is_configured:
            return {
                'success': False,
                'error': 'Email verification not available in demo mode'
            }
        
        try:
            self.client.confirm_sign_up(
                ClientId=self.client_id,
                Username=email,
                ConfirmationCode=code
            )
            
            logger.info(f"Email verified for {email}")
            
            return {
                'success': True,
                'message': 'Email verified! You can now login.'
            }
        
        except self.client.exceptions.CodeMismatchException:
            return {
                'success': False,
                'error': 'Invalid verification code'
            }
        
        except Exception as e:
            logger.error(f"Email verification error: {e}")
            return {
                'success': False,
                'error': f'Verification failed: {str(e)}'
            }
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information from access token
        
        Args:
            access_token: Cognito access token
            
        Returns:
            Dict with user info or error
        """
        if not self.is_configured:
            # Demo mode - return demo user info
            return {
                'success': True,
                'email': st.session_state.get('user_email', 'demo@agentflow.ai'),
                'name': st.session_state.get('user_name', 'Demo User'),
                'email_verified': True
            }
        
        try:
            response = self.client.get_user(
                AccessToken=access_token
            )
            
            # Parse user attributes
            user_attrs = {
                attr['Name']: attr['Value']
                for attr in response['UserAttributes']
            }
            
            return {
                'success': True,
                'email': user_attrs.get('email'),
                'name': user_attrs.get('name'),
                'email_verified': user_attrs.get('email_verified') == 'true'
            }
        
        except Exception as e:
            logger.error(f"Get user info error: {e}")
            return {
                'success': False,
                'error': f'Failed to get user info: {str(e)}'
            }
    
    def logout(self, access_token: str) -> Dict[str, Any]:
        """
        Logout user (revoke token)
        
        Args:
            access_token: Cognito access token
            
        Returns:
            Dict with success/error
        """
        if not self.is_configured:
            return {'success': True}
        
        try:
            self.client.global_sign_out(
                AccessToken=access_token
            )
            
            logger.info("User logged out successfully")
            
            return {'success': True}
        
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return {
                'success': False,
                'error': f'Logout failed: {str(e)}'
            }
    
    def forgot_password(self, email: str) -> Dict[str, Any]:
        """
        Initiate password reset
        
        Args:
            email: User email
            
        Returns:
            Dict with success/error
        """
        if not self.is_configured:
            return {
                'success': False,
                'error': 'Password reset not available in demo mode'
            }
        
        try:
            self.client.forgot_password(
                ClientId=self.client_id,
                Username=email
            )
            
            logger.info(f"Password reset initiated for {email}")
            
            return {
                'success': True,
                'message': 'Password reset code sent to your email'
            }
        
        except Exception as e:
            logger.error(f"Forgot password error: {e}")
            return {
                'success': False,
                'error': f'Failed to send reset code: {str(e)}'
            }
    
    def reset_password(
        self,
        email: str,
        code: str,
        new_password: str
    ) -> Dict[str, Any]:
        """
        Reset password with code
        
        Args:
            email: User email
            code: Reset code from email
            new_password: New password
            
        Returns:
            Dict with success/error
        """
        if not self.is_configured:
            return {
                'success': False,
                'error': 'Password reset not available in demo mode'
            }
        
        try:
            self.client.confirm_forgot_password(
                ClientId=self.client_id,
                Username=email,
                ConfirmationCode=code,
                Password=new_password
            )
            
            logger.info(f"Password reset successful for {email}")
            
            return {
                'success': True,
                'message': 'Password reset successful! You can now login.'
            }
        
        except Exception as e:
            logger.error(f"Reset password error: {e}")
            return {
                'success': False,
                'error': f'Password reset failed: {str(e)}'
            }


# Singleton instance
@st.cache_resource
def get_cognito_client() -> CognitoClient:
    """Get cached Cognito client instance"""
    return CognitoClient()