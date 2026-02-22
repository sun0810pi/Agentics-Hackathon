import requests
import streamlit as st
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta
from config import config
from utils.constants import *
from utils.helpers import log_action

logger = logging.getLogger(__name__)


class APIClient:
    """
    Backend API client
    
    Handles all HTTP requests to FastAPI backend with:
    - JWT token management
    - Automatic retries
    - Response caching
    - Error handling
    """
    
    def __init__(self):
        """Initialize API client"""
        self.base_url = config.get_backend_url()
        self.timeout = config.get_backend_timeout()
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': f'{config.APP_NAME}/{config.APP_VERSION}'
        })
        
        logger.info(f"API Client initialized with base URL: {self.base_url}")
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers with JWT token
        
        Returns:
            Dict with Authorization header if logged in
        """
        headers = {}
        
        # Get access token from session
        access_token = st.session_state.get('access_token')
        
        if access_token and access_token != 'demo_access_token':
            headers['Authorization'] = f'Bearer {access_token}'
        
        return headers
    
    def _handle_response(
        self,
        response: requests.Response,
        endpoint: str
    ) -> Dict[str, Any]:
        """
        Handle API response
        
        Args:
            response: Response object
            endpoint: Endpoint name for logging
            
        Returns:
            Parsed JSON response
            
        Raises:
            APIError: If response indicates error
        """
        try:
            # Check status code
            if response.status_code == 200:
                return response.json()
            
            elif response.status_code == 401:
                # Unauthorized - clear session
                logger.warning(f"Unauthorized request to {endpoint}")
                st.session_state.logged_in = False
                raise Exception("Session expired. Please login again.")
            
            elif response.status_code == 429:
                # Rate limited
                logger.warning(f"Rate limited on {endpoint}")
                raise Exception("Rate limit exceeded. Please try again later.")
            
            elif response.status_code >= 500:
                # Server error
                logger.error(f"Server error on {endpoint}: {response.status_code}")
                raise Exception("Backend server error. Please try again later.")
            
            else:
                # Other error
                error_msg = response.json().get('detail', 'Unknown error')
                logger.error(f"API error on {endpoint}: {error_msg}")
                raise Exception(error_msg)
        
        except requests.exceptions.JSONDecodeError:
            logger.error(f"Invalid JSON response from {endpoint}")
            raise Exception("Invalid response from server")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check backend health
        
        Returns:
            Dict with health status
        """
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=5
            )
            
            return self._handle_response(response, "health_check")
        
        except requests.exceptions.Timeout:
            logger.warning("Health check timeout")
            return {
                'status': 'timeout',
                'mode': 'unknown'
            }
        
        except requests.exceptions.ConnectionError:
            logger.warning("Health check connection error")
            return {
                'status': 'unavailable',
                'mode': 'unknown'
            }
        
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {
                'status': 'error',
                'mode': 'unknown'
            }
    
    def analyze_invoice(
        self,
        file_bytes: bytes,
        filename: str,
        mode: str = MODE_FULL,
        auto_approve_threshold: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze invoice with backend
        
        Args:
            file_bytes: File content as bytes
            filename: Original filename
            mode: Processing mode (full, fast, demo)
            auto_approve_threshold: Auto-approve threshold
            
        Returns:
            Dict with processing result
        """
        try:
            # Prepare files
            files = {
                'file': (filename, file_bytes, 'application/octet-stream')
            }
            
            # Prepare data
            data = {
                'mode': mode,
                'auto_approve_threshold': auto_approve_threshold
            }
            
            # Get auth headers
            headers = self._get_auth_headers()
            
            # Make request
            logger.info(f"Analyzing invoice: {filename} (mode: {mode})")
            
            response = self.session.post(
                f"{self.base_url}/api/analyze",
                files=files,
                data=data,
                headers=headers,
                timeout=self.timeout
            )
            
            result = self._handle_response(response, "analyze_invoice")
            
            # Log action
            log_action('analyze_invoice', {
                'filename': filename,
                'mode': mode,
                'decision': result.get('decision')
            })
            
            return result
        
        except requests.exceptions.Timeout:
            logger.error(f"Analyze timeout for {filename}")
            return {
                'success': False,
                'error': 'Request timeout. Please try again.'
            }
        
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error analyzing {filename}")
            return {
                'success': False,
                'error': 'Cannot connect to backend. Using demo mode.'
            }
        
        except Exception as e:
            logger.error(f"Error analyzing {filename}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get dashboard metrics
        
        Returns:
            Dict with metrics data
        """
        try:
            headers = self._get_auth_headers()
            
            response = self.session.get(
                f"{self.base_url}/api/metrics",
                headers=headers,
                timeout=10
            )
            
            return self._handle_response(response, "get_metrics")
        
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_agents(self) -> Dict[str, Any]:
        """
        Get list of agents with status
        
        Returns:
            Dict with agents list
        """
        try:
            headers = self._get_auth_headers()
            
            response = self.session.get(
                f"{self.base_url}/api/agents",
                headers=headers,
                timeout=10
            )
            
            return self._handle_response(response, "list_agents")
        
        except Exception as e:
            logger.error(f"Error listing agents: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_invoices(
        self,
        limit: int = 100,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get invoices from backend
        
        Args:
            limit: Maximum number of invoices
            status: Filter by status (APPROVED, PENDING, BLOCKED)
            start_date: Filter by start date (YYYY-MM-DD)
            end_date: Filter by end date (YYYY-MM-DD)
            
        Returns:
            Dict with invoices list
        """
        try:
            headers = self._get_auth_headers()
            
            # Build query params
            params = {'limit': limit}
            if status:
                params['status'] = status
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date
            
            response = self.session.get(
                f"{self.base_url}/api/invoices",
                params=params,
                headers=headers,
                timeout=15
            )
            
            return self._handle_response(response, "get_invoices")
        
        except Exception as e:
            logger.error(f"Error getting invoices: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_fraud_scenarios(self) -> Dict[str, Any]:
        """
        Get active fraud scenarios
        
        Returns:
            Dict with fraud scenarios
        """
        try:
            headers = self._get_auth_headers()
            
            response = self.session.get(
                f"{self.base_url}/api/fraud-scenarios",
                headers=headers,
                timeout=10
            )
            
            return self._handle_response(response, "get_fraud_scenarios")
        
        except Exception as e:
            logger.error(f"Error getting fraud scenarios: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_audit_logs(
        self,
        limit: int = 100,
        action: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get audit logs
        
        Args:
            limit: Maximum number of logs
            action: Filter by action type
            
        Returns:
            Dict with audit logs
        """
        try:
            headers = self._get_auth_headers()
            
            params = {'limit': limit}
            if action:
                params['action'] = action
            
            response = self.session.get(
                f"{self.base_url}/api/audit-logs",
                params=params,
                headers=headers,
                timeout=10
            )
            
            return self._handle_response(response, "get_audit_logs")
        
        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_xray_traces(
        self,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get X-Ray traces for observability
        
        Args:
            limit: Maximum number of traces
            
        Returns:
            Dict with X-Ray traces
        """
        try:
            headers = self._get_auth_headers()
            
            response = self.session.get(
                f"{self.base_url}/api/xray-traces",
                params={'limit': limit},
                headers=headers,
                timeout=10
            )
            
            return self._handle_response(response, "get_xray_traces")
        
        except Exception as e:
            logger.error(f"Error getting X-Ray traces: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_attack(
        self,
        attack_type: str,
        payload: str
    ) -> Dict[str, Any]:
        """
        Test attack simulation (for Security page demo)
        
        Args:
            attack_type: Type of attack (sql_injection, xss, etc.)
            payload: Attack payload
            
        Returns:
            Dict with attack test result
        """
        try:
            headers = self._get_auth_headers()
            
            data = {
                'attack_type': attack_type,
                'payload': payload
            }
            
            response = self.session.post(
                f"{self.base_url}/api/test-attack",
                json=data,
                headers=headers,
                timeout=10
            )
            
            return self._handle_response(response, "test_attack")
        
        except Exception as e:
            logger.error(f"Error testing attack: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance with caching
@st.cache_resource
def get_api_client() -> APIClient:
    """
    Get cached API client instance
    
    Returns:
        APIClient instance
    """
    return APIClient()


# Convenience functions
def check_backend_health() -> bool:
    """
    Quick health check
    
    Returns:
        True if backend is healthy
    """
    client = get_api_client()
    health = client.health_check()
    return health.get('status') == 'healthy'


def is_backend_available() -> bool:
    """
    Check if backend is available
    
    Returns:
        True if backend responds
    """
    try:
        client = get_api_client()
        health = client.health_check()
        return health.get('status') in ['healthy', 'degraded']
    except:
        return False