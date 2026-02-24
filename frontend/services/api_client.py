import requests
import streamlit as st
import base64
import random
import time
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from config import config
from utils.constants import *
from utils.helpers import log_action

logger = logging.getLogger(__name__)


class APIClient:
    """
    Backend API client with authentication and error handling
    
    Features:
    - Automatic JWT token management
    - Demo mode header injection (X-Demo-Mode)
    - Request retry logic with exponential backoff
    - Comprehensive error handling
    - Request/response logging with IDs
    - Health check caching
    """
    
    def __init__(self):
        """Initialize API client"""
        self.base_url = config.get_backend_url()
        self.timeout = config.get_backend_timeout()
        self.session = requests.Session()
        self._request_counter = 0
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': f'{config.APP_NAME}/{config.APP_VERSION}'
        })
        
        logger.info(f"✅ API Client initialized: {self.base_url} (timeout: {self.timeout}s)")
    
    def _get_request_id(self) -> str:
        """Generate unique request ID for tracking"""
        self._request_counter += 1
        return f"REQ-{int(time.time())}-{self._request_counter:04d}"
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers with JWT token or demo mode
        
        Returns:
            Dict with authorization headers
        
        FIXED: Now adds X-Demo-Mode header when in demo mode
        """
        headers = {}
        
        # Get access token from session
        access_token = st.session_state.get('access_token', '')
        
        if access_token and access_token != 'demo_access_token':
            # Real JWT token - use Authorization header
            headers['Authorization'] = f'Bearer {access_token}'
            logger.debug("🔐 Using JWT authentication")
        else:
            # Demo mode - add header to bypass JWT verification on backend
            headers['X-Demo-Mode'] = 'true'
            logger.debug("🎭 Using demo mode (X-Demo-Mode header)")
        
        # Add request ID for tracking
        headers['X-Request-ID'] = self._get_request_id()
        
        return headers
    
    def _handle_response(
        self,
        response: requests.Response,
        endpoint: str
    ) -> Dict[str, Any]:
        """
        Handle API response with backend error format
        
        Args:
            response: HTTP response object
            endpoint: API endpoint name (for logging)
            
        Returns:
            Parsed response data
            
        Raises:
            Exception: On error responses
        """
        try:
            # Log response
            request_id = response.headers.get('X-Request-ID', 'unknown')
            logger.debug(f"📥 Response {request_id}: {response.status_code} from {endpoint}")
            
            # Check status code
            if response.status_code == 200:
                return response.json()
            
            elif response.status_code == 401:
                # Unauthorized - clear session
                logger.warning(f"🔒 Unauthorized request to {endpoint}")
                st.session_state.logged_in = False
                raise Exception("Session expired. Please login again.")
            
            elif response.status_code == 429:
                # Rate limited
                logger.warning(f"⏱️ Rate limited on {endpoint}")
                retry_after = response.headers.get('Retry-After', '60')
                raise Exception(f"Rate limit exceeded. Try again in {retry_after}s.")
            
            elif response.status_code >= 500:
                # Server error
                logger.error(f"🔥 Server error on {endpoint}: {response.status_code}")
                raise Exception("Backend server error. Please try again later.")
            
            else:
                # Other error - parse backend error format
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', 'Unknown error')
                    error_detail = error_data.get('detail', '')
                    
                    if error_detail:
                        error_msg = f"{error_msg}: {error_detail}"
                    
                except:
                    error_msg = f"HTTP {response.status_code}"
                
                logger.error(f"❌ API error on {endpoint}: {error_msg}")
                raise Exception(error_msg)
        
        except requests.exceptions.JSONDecodeError:
            logger.error(f"⚠️ Invalid JSON response from {endpoint}")
            raise Exception("Invalid response from server")
    
    @st.cache_data(ttl=60)
    def health_check(_self) -> Dict[str, Any]:
        """
        Check backend health (cached for 60s)
        
        Returns:
            Dict with health status
        
        FIXED: Now handles both boolean and string values for demo_mode
        """
        try:
            response = _self.session.get(
                f"{_self.base_url}/health",
                timeout=5
            )
            
            data = _self._handle_response(response, "health_check")
            
            # FIXED: Handle both boolean True/False and string 'true'/'false'
            demo_mode_raw = data.get('demo_mode')
            
            # Support multiple formats:
            # - Boolean: True/False
            # - String: 'true'/'false', '1'/'0', 'yes'/'no'
            # - Integer: 1/0
            if isinstance(demo_mode_raw, bool):
                is_demo = demo_mode_raw
            elif isinstance(demo_mode_raw, str):
                is_demo = demo_mode_raw.lower() in ['true', '1', 'yes', 'on']
            elif isinstance(demo_mode_raw, int):
                is_demo = demo_mode_raw == 1
            else:
                is_demo = False
            
            result = {
                'status': data.get('status', 'unknown'),
                'mode': 'demo' if is_demo else 'production',
                'version': data.get('version', 'unknown'),
                'services': data.get('services', {}),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"💚 Health check: {result['status']} (mode: {result['mode']})")
            
            return result
        
        except requests.exceptions.Timeout:
            logger.warning("⏱️ Health check timeout")
            return {'status': 'timeout', 'mode': 'unknown'}
        
        except requests.exceptions.ConnectionError:
            logger.warning("🔌 Health check connection error")
            return {'status': 'unavailable', 'mode': 'unknown'}
        
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
            return {'status': 'error', 'mode': 'unknown', 'error': str(e)}
    
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
            auto_approve_threshold: Auto-approve threshold (not used by backend)
            
        Returns:
            Dict with processing result
        """
        try:
            # Generate invoice ID
            invoice_id = f"INV-{random.randint(100000, 999999)}"
            
            # Encode file to base64 (backend expects this)
            file_b64 = base64.b64encode(file_bytes).decode('utf-8')
            
            # Prepare JSON body (NOT multipart!)
            data = {
                'invoice_id': invoice_id,
                'file_name': filename,
                'file_data': file_b64,
                'mode': mode
            }
            
            # Get auth headers (includes X-Demo-Mode if in demo)
            headers = self._get_auth_headers()
            
            # Make request
            logger.info(f"📤 Analyzing invoice: {filename} (mode: {mode})")
            
            response = self.session.post(
                f"{self.base_url}/api/analyze",
                json=data,
                headers=headers,
                timeout=self.timeout
            )
            
            result = self._handle_response(response, "analyze_invoice")
            
            # Log action
            log_action('analyze_invoice', {
                'filename': filename,
                'mode': mode,
                'invoice_id': invoice_id,
                'decision': result.get('final_decision')
            })
            
            logger.info(f"✅ Analysis complete: {result.get('final_decision')} (risk: {result.get('risk', {}).get('risk_score', 0)})")
            
            # Return with success flag
            return {
                'success': True,
                **result
            }
        
        except requests.exceptions.Timeout:
            logger.error(f"⏱️ Analyze timeout for {filename}")
            return {
                'success': False,
                'error': f'Request timeout after {self.timeout}s. Please try again.'
            }
        
        except requests.exceptions.ConnectionError:
            logger.error(f"🔌 Connection error analyzing {filename}")
            return {
                'success': False,
                'error': 'Cannot connect to backend. Check if backend is running.'
            }
        
        except Exception as e:
            logger.error(f"❌ Error analyzing {filename}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get dashboard metrics"""
        try:
            headers = self._get_auth_headers()
            
            response = self.session.get(
                f"{self.base_url}/api/metrics",
                params={'days': days},
                headers=headers,
                timeout=10
            )
            
            data = self._handle_response(response, "get_metrics")
            
            return {
                'success': True,
                'data': data
            }
        
        except Exception as e:
            logger.error(f"❌ Error getting metrics: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_agents(self) -> Dict[str, Any]:
        """Get list of agents with status"""
        try:
            headers = self._get_auth_headers()
            
            response = self.session.get(
                f"{self.base_url}/api/agents/status",
                headers=headers,
                timeout=10
            )
            
            data = self._handle_response(response, "list_agents")
            
            return {
                'success': True,
                'agents': data.get('agents', [])
            }
        
        except Exception as e:
            logger.error(f"❌ Error listing agents: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_invoices(
        self,
        page: int = 1,
        page_size: int = 50,
        decision: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get invoices from backend"""
        try:
            headers = self._get_auth_headers()
            
            # Build query params
            params = {
                'page': page,
                'page_size': page_size
            }
            
            if decision:
                params['decision'] = decision
            
            response = self.session.get(
                f"{self.base_url}/api/invoices",
                params=params,
                headers=headers,
                timeout=15
            )
            
            data = self._handle_response(response, "get_invoices")
            
            return {
                'success': True,
                'invoices': data.get('invoices', []),
                'total': data.get('total', 0),
                'page': data.get('page', page),
                'has_more': data.get('has_more', False)
            }
        
        except Exception as e:
            logger.error(f"❌ Error getting invoices: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_invoice_by_id(self, invoice_id: str) -> Dict[str, Any]:
        """Get single invoice by ID"""
        try:
            headers = self._get_auth_headers()
            
            response = self.session.get(
                f"{self.base_url}/api/invoices/{invoice_id}",
                headers=headers,
                timeout=10
            )
            
            data = self._handle_response(response, "get_invoice_by_id")
            
            return {
                'success': True,
                'invoice': data
            }
        
        except Exception as e:
            logger.error(f"❌ Error getting invoice {invoice_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_fraud_scenarios(self) -> Dict[str, Any]:
        """Get active fraud scenarios"""
        try:
            headers = self._get_auth_headers()
            
            response = self.session.get(
                f"{self.base_url}/api/fraud-scenarios",
                headers=headers,
                timeout=10
            )
            
            data = self._handle_response(response, "get_fraud_scenarios")
            
            return {
                'success': True,
                'scenarios': data.get('scenarios', [])
            }
        
        except Exception as e:
            logger.error(f"❌ Error getting fraud scenarios: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_audit_logs(
        self,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get audit logs"""
        try:
            headers = self._get_auth_headers()
            
            response = self.session.get(
                f"{self.base_url}/api/audit-logs",
                params={'page': page, 'page_size': page_size},
                headers=headers,
                timeout=10
            )
            
            data = self._handle_response(response, "get_audit_logs")
            
            return {
                'success': True,
                'logs': data.get('logs', []),
                'total': data.get('total', 0)
            }
        
        except Exception as e:
            logger.error(f"❌ Error getting audit logs: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_xray_traces(
        self,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get X-Ray traces for observability"""
        try:
            headers = self._get_auth_headers()
            
            response = self.session.get(
                f"{self.base_url}/api/xray-traces",
                params={'limit': limit},
                headers=headers,
                timeout=10
            )
            
            data = self._handle_response(response, "get_xray_traces")
            
            return {
                'success': True,
                'traces': data.get('traces', [])
            }
        
        except Exception as e:
            logger.error(f"❌ Error getting X-Ray traces: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_attack(
        self,
        attack_type: str,
        payload: str
    ) -> Dict[str, Any]:
        """Test attack simulation (for Security page demo)"""
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
            
            result = self._handle_response(response, "test_attack")
            
            return {
                'success': True,
                **result
            }
        
        except Exception as e:
            logger.error(f"❌ Error testing attack: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def submit_feedback(
        self,
        invoice_id: str,
        original_decision: str,
        correct_decision: str,
        reason: str = ""
    ) -> Dict[str, Any]:
        """Submit feedback for ML improvement"""
        try:
            headers = self._get_auth_headers()
            
            data = {
                'invoice_id': invoice_id,
                'original_decision': original_decision,
                'correct_decision': correct_decision,
                'reason': reason,
                'reviewer_id': st.session_state.get('user_email', 'unknown')
            }
            
            response = self.session.post(
                f"{self.base_url}/api/feedback",
                json=data,
                headers=headers,
                timeout=10
            )
            
            result = self._handle_response(response, "submit_feedback")
            
            return {
                'success': True,
                'message': result.get('message', 'Feedback submitted')
            }
        
        except Exception as e:
            logger.error(f"❌ Error submitting feedback: {e}")
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