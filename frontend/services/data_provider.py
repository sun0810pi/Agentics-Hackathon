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
    WITH FIELD MAPPING for backend compatibility
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
        """Check if backend is available"""
        return is_backend_available()
    
    def _map_backend_response(self, backend_data: Dict[str, Any]) -> Dict[str, Any]:
        if not backend_data:
            return {}
        
        # Extract nested risk data
        risk_data = backend_data.get('risk', {})
        
        return {
            'invoice_id': backend_data.get('invoice_id'),
            'decision': backend_data.get('final_decision'),  # ← map field
            'risk_score': risk_data.get('risk_score', 0),    # ← extract nested
            'risk_level': risk_data.get('risk_level', 'UNKNOWN'),
            'confidence': backend_data.get('final_confidence', 0.0),
            'agent_results': backend_data.get('agent_results', []),
            'total_duration_ms': backend_data.get('total_duration_ms', 0),
            'agents_run': backend_data.get('agents_run', 0),
            'agents_succeeded': backend_data.get('agents_succeeded', 0),
            'agents_failed': backend_data.get('agents_failed', 0),
            'fraud_indicators': backend_data.get('fraud_indicators', {}),
            'security': backend_data.get('security', {}),
            'ml_insights': backend_data.get('ml_insights', {}),
            'extracted': backend_data.get('extracted', {}),
            'pii_report': backend_data.get('pii_report', {}),
            'trace_id': backend_data.get('trace_id'),
            'metadata': backend_data  # Keep full response for debugging
        }
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get dashboard metrics with backend fallback"""
        if self.backend_available:
            try:
                logger.debug("Fetching metrics from backend")
                result = self.api_client.get_metrics()
                
                if result.get('success'):
                    # Backend metrics already in correct format
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
        page: int = 1
    ) -> List[Dict[str, Any]]:
        """Get invoices with pagination"""
        if self.backend_available:
            try:
                logger.debug(f"Fetching invoices from backend (page={page})")
                result = self.api_client.get_invoices(
                    page=page,
                    page_size=limit,
                    decision=status
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
    
    def get_invoice_by_id(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Get single invoice by ID"""
        if self.backend_available:
            try:
                result = self.api_client.get_invoice_by_id(invoice_id)
                
                if result.get('success'):
                    return result.get('invoice')
            
            except Exception as e:
                logger.error(f"Error fetching invoice {invoice_id}: {e}")
        
        return None
    
    def get_fraud_scenarios(self) -> List[Dict[str, Any]]:
        """Get active fraud scenarios"""
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
        """Get agent performance metrics"""
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
        """Get time series data for charts"""
        # Always use demo data for now (backend doesn't have this endpoint yet)
        logger.debug(f"Using demo time series (days={days})")
        return self.demo_generator.generate_time_series(days)
    
    def get_audit_logs(
        self,
        limit: int = 100,
        page: int = 1
    ) -> List[Dict[str, Any]]:
        """Get audit logs"""
        if self.backend_available:
            try:
                logger.debug(f"Fetching audit logs from backend (page={page})")
                result = self.api_client.get_audit_logs(page=page, page_size=limit)
                
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
        """Get X-Ray traces"""
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
        if self.backend_available and mode != "demo":
            try:
                logger.info(f"Processing invoice via backend: {filename}")
                result = self.api_client.analyze_invoice(
                    file_bytes=file_bytes,
                    filename=filename,
                    mode=mode,
                    auto_approve_threshold=auto_approve_threshold
                )
                
                if result.get('success'):
                    # Map backend response to frontend format
                    mapped = self._map_backend_response(result)
                    mapped['success'] = True
                    return mapped
                else:
                    # Return error
                    return {
                        'success': False,
                        'error': result.get('error', 'Unknown error')
                    }
            
            except Exception as e:
                logger.error(f"Error processing invoice: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }
        
        # Demo mode - simulate processing
        logger.info(f"Processing invoice in demo mode: {filename}")
        demo_result = self.demo_generator.simulate_invoice_processing(
            filename=filename,
            mode=mode
        )
        demo_result['success'] = True
        return demo_result


# Singleton instance
@st.cache_resource
def get_data_provider() -> DataProvider:
    """Get cached data provider instance"""
    return DataProvider()


# Convenience functions with error handling
def get_dashboard_metrics() -> Dict[str, Any]:
    """Get dashboard metrics"""
    try:
        provider = get_data_provider()
        return provider.get_dashboard_metrics()
    except Exception as e:
        logger.error(f"Error in get_dashboard_metrics: {e}")
        return {}


def get_invoices(limit: int = 100, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get invoices"""
    try:
        provider = get_data_provider()
        return provider.get_invoices(limit=limit, status=status)
    except Exception as e:
        logger.error(f"Error in get_invoices: {e}")
        return []


def get_fraud_scenarios() -> List[Dict[str, Any]]:
    """Get fraud scenarios"""
    try:
        provider = get_data_provider()
        return provider.get_fraud_scenarios()
    except Exception as e:
        logger.error(f"Error in get_fraud_scenarios: {e}")
        return []


def get_agent_metrics() -> List[Dict[str, Any]]:
    """Get agent metrics"""
    try:
        provider = get_data_provider()
        return provider.get_agent_metrics()
    except Exception as e:
        logger.error(f"Error in get_agent_metrics: {e}")
        return []


def process_invoice(
    file_bytes: bytes,
    filename: str,
    mode: str = "full",
    auto_approve_threshold: int = 30
) -> Dict[str, Any]:
    """Process invoice"""
    try:
        provider = get_data_provider()
        return provider.process_invoice(
            file_bytes=file_bytes,
            filename=filename,
            mode=mode,
            auto_approve_threshold=auto_approve_threshold
        )
    except Exception as e:
        logger.error(f"Error in process_invoice: {e}")
        return {
            'success': False,
            'error': str(e)
        }