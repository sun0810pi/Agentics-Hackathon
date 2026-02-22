import streamlit as st
from typing import Dict, Any, Optional, List
from services.api_client import get_api_client, is_backend_available
from services.demo_data import get_demo_data_generator
from config import config
import logging

logger = logging.getLogger(__name__)


class DataProvider:
    """
    Smart data provider that switches between demo and real data
    
    Strategy:
    1. Check if backend is available
    2. If available → use real data from backend
    3. If unavailable → use demo data generator
    4. Cache results for performance
    """
    
    def __init__(self):
        """Initialize data provider"""
        self.api_client = get_api_client()
        self.demo_generator = get_demo_data_generator()
        
        # Check demo mode setting
        self.demo_mode = config.get_demo_mode() == "demo"
        
        # Check backend availability (cached for 1 minute)
        self.backend_available = not self.demo_mode and self._check_backend()
        
        logger.info(f"Data Provider initialized (demo_mode={self.demo_mode}, backend_available={self.backend_available})")
    
    def _check_backend(self) -> bool:
        """
        Check if backend is available
        
        Returns:
            True if backend responds
        """
        return is_backend_available()
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """
        Get dashboard metrics
        
        Returns:
            Dict with metrics:
            - total_processed: int
            - total_approved: int
            - total_blocked: int
            - total_pending: int
            - accuracy: float (percentage)
            - automation_rate: float (percentage)
            - avg_latency_ms: int
            - fraud_prevented_usd: int
            - uptime_pct: float
            - agents_active: int
        """
        if self.backend_available:
            try:
                logger.debug("Fetching metrics from backend")
                result = self.api_client.get_metrics()
                
                if result.get('success'):
                    return result.get('data', {})
                else:
                    logger.warning(f"Backend metrics error: {result.get('error')}")
            
            except Exception as e:
                logger.error(f"Error fetching backend metrics: {e}")
        
        # Fallback to demo data
        logger.debug("Using demo metrics")
        return self.demo_generator.generate_dashboard_metrics()
    
    def get_invoices(
        self,
        limit: int = 100,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get invoices
        
        Args:
            limit: Maximum number of invoices
            status: Filter by status
            start_date: Filter by start date
            end_date: Filter by end date
            
        Returns:
            List of invoice dicts
        """
        if self.backend_available:
            try:
                logger.debug(f"Fetching {limit} invoices from backend")
                result = self.api_client.get_invoices(
                    limit=limit,
                    status=status,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if result.get('success'):
                    return result.get('invoices', [])
                else:
                    logger.warning(f"Backend invoices error: {result.get('error')}")
            
            except Exception as e:
                logger.error(f"Error fetching backend invoices: {e}")
        
        # Fallback to demo data
        logger.debug(f"Using demo invoices (count={limit})")
        invoices = self.demo_generator.generate_invoices(limit)
        
        # Apply filters
        if status:
            invoices = [inv for inv in invoices if inv['status'] == status]
        
        return invoices
    
    def get_fraud_scenarios(self) -> List[Dict[str, Any]]:
        """
        Get active fraud scenarios
        
        Returns:
            List of fraud scenario dicts
        """
        if self.backend_available:
            try:
                logger.debug("Fetching fraud scenarios from backend")
                result = self.api_client.get_fraud_scenarios()
                
                if result.get('success'):
                    return result.get('scenarios', [])
                else:
                    logger.warning(f"Backend fraud scenarios error: {result.get('error')}")
            
            except Exception as e:
                logger.error(f"Error fetching backend fraud scenarios: {e}")
        
        # Fallback to demo data
        logger.debug("Using demo fraud scenarios")
        return self.demo_generator.generate_fraud_scenarios()
    
    def get_agent_metrics(self) -> List[Dict[str, Any]]:
        """
        Get agent performance metrics
        
        Returns:
            List of agent metric dicts
        """
        if self.backend_available:
            try:
                logger.debug("Fetching agent metrics from backend")
                result = self.api_client.list_agents()
                
                if result.get('success'):
                    return result.get('agents', [])
                else:
                    logger.warning(f"Backend agent metrics error: {result.get('error')}")
            
            except Exception as e:
                logger.error(f"Error fetching backend agent metrics: {e}")
        
        # Fallback to demo data
        logger.debug("Using demo agent metrics")
        return self.demo_generator.generate_agent_metrics()
    
    def get_time_series(
        self,
        days: int = 30,
        metric: str = "processed"
    ) -> List[Dict[str, Any]]:
        """
        Get time series data for charts
        
        Args:
            days: Number of days
            metric: Metric type (processed, approved, blocked, etc.)
            
        Returns:
            List of time series points
        """
        if self.backend_available:
            try:
                logger.debug(f"Fetching time series from backend (days={days}, metric={metric})")
                # TODO: Add backend endpoint for time series
                # For now, use demo data
            except Exception as e:
                logger.error(f"Error fetching backend time series: {e}")
        
        # Use demo data
        logger.debug(f"Using demo time series (days={days})")
        return self.demo_generator.generate_time_series(days)
    
    def get_audit_logs(
        self,
        limit: int = 100,
        action: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get audit logs
        
        Args:
            limit: Maximum number of logs
            action: Filter by action type
            
        Returns:
            List of audit log dicts
        """
        if self.backend_available:
            try:
                logger.debug(f"Fetching audit logs from backend (limit={limit})")
                result = self.api_client.get_audit_logs(limit=limit, action=action)
                
                if result.get('success'):
                    return result.get('logs', [])
                else:
                    logger.warning(f"Backend audit logs error: {result.get('error')}")
            
            except Exception as e:
                logger.error(f"Error fetching backend audit logs: {e}")
        
        # Fallback to demo data
        logger.debug("Using demo audit logs")
        return self.demo_generator.generate_audit_logs(limit)
    
    def get_xray_traces(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get X-Ray traces
        
        Args:
            limit: Maximum number of traces
            
        Returns:
            List of X-Ray trace dicts
        """
        if self.backend_available:
            try:
                logger.debug(f"Fetching X-Ray traces from backend (limit={limit})")
                result = self.api_client.get_xray_traces(limit=limit)
                
                if result.get('success'):
                    return result.get('traces', [])
                else:
                    logger.warning(f"Backend X-Ray traces error: {result.get('error')}")
            
            except Exception as e:
                logger.error(f"Error fetching backend X-Ray traces: {e}")
        
        # Fallback to demo data
        logger.debug("Using demo X-Ray traces")
        return self.demo_generator.generate_xray_traces(limit)
    
    def process_invoice(
        self,
        file_bytes: bytes,
        filename: str,
        mode: str = "full",
        auto_approve_threshold: int = 30
    ) -> Dict[str, Any]:
        """
        Process invoice (main workflow)
        
        Args:
            file_bytes: File content
            filename: Original filename
            mode: Processing mode (full, fast, demo)
            auto_approve_threshold: Auto-approve threshold
            
        Returns:
            Processing result dict
        """
        if self.backend_available and mode != "demo":
            try:
                logger.info(f"Processing invoice via backend: {filename}")
                result = self.api_client.analyze_invoice(
                    file_bytes=file_bytes,
                    filename=filename,
                    mode=mode,
                    auto_approve_threshold=auto_approve_threshold
                )
                
                if not result.get('success') and result.get('success') is not None:
                    logger.warning(f"Backend processing failed: {result.get('error')}")
                    # Don't fallback to demo for actual file processing
                    return result
                
                return result
            
            except Exception as e:
                logger.error(f"Error processing invoice: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }
        
        # Demo mode - simulate processing
        logger.info(f"Processing invoice in demo mode: {filename}")
        return self.demo_generator.simulate_invoice_processing(
            filename=filename,
            mode=mode
        )


# Singleton instance
@st.cache_resource
def get_data_provider() -> DataProvider:
    """
    Get cached data provider instance
    
    Returns:
        DataProvider instance
    """
    return DataProvider()


# Convenience functions
def get_dashboard_metrics() -> Dict[str, Any]:
    """Get dashboard metrics"""
    provider = get_data_provider()
    return provider.get_dashboard_metrics()


def get_invoices(limit: int = 100, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get invoices"""
    provider = get_data_provider()
    return provider.get_invoices(limit=limit, status=status)


def get_fraud_scenarios() -> List[Dict[str, Any]]:
    """Get fraud scenarios"""
    provider = get_data_provider()
    return provider.get_fraud_scenarios()


def get_agent_metrics() -> List[Dict[str, Any]]:
    """Get agent metrics"""
    provider = get_data_provider()
    return provider.get_agent_metrics()


def process_invoice(
    file_bytes: bytes,
    filename: str,
    mode: str = "full",
    auto_approve_threshold: int = 30
) -> Dict[str, Any]:
    """Process invoice"""
    provider = get_data_provider()
    return provider.process_invoice(
        file_bytes=file_bytes,
        filename=filename,
        mode=mode,
        auto_approve_threshold=auto_approve_threshold
    )