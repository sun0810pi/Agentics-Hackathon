import time
from typing import Dict, Optional
import streamlit as st
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter
    
    Concept:
    - Each user has a "bucket" of tokens
    - Each request consumes tokens
    - Tokens regenerate over time
    - When bucket is empty → rate limited
    
    Example:
    - Bucket capacity: 10 tokens
    - Refill rate: 1 token per 6 seconds
    - Different endpoints cost different amounts
    """
    
    def __init__(
        self,
        capacity: int = 10,
        refill_rate: float = 1.0,  # tokens per second
        refill_interval: int = 60   # seconds
    ):
        """
        Initialize rate limiter
        
        Args:
            capacity: Maximum tokens in bucket
            refill_rate: Tokens added per second
            refill_interval: How often to refill (seconds)
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.refill_interval = refill_interval
        
        # Endpoint costs (in tokens)
        self.endpoint_costs = {
            '/api/analyze': 5,          # Expensive: full processing
            '/api/metrics': 1,           # Cheap: just data retrieval
            '/api/invoices': 2,          # Medium: database query
            '/api/fraud-scenarios': 2,
            '/api/agents': 1,
            '/api/audit-logs': 1,
            '/api/xray-traces': 1,
            '/api/test-attack': 3,       # Expensive: security test
        }
        
        # Initialize session state
        if 'rate_limiter' not in st.session_state:
            st.session_state.rate_limiter = {
                'tokens': capacity,
                'last_refill': time.time()
            }
    
    def _refill_tokens(self):
        """Refill tokens based on time elapsed"""
        state = st.session_state.rate_limiter
        now = time.time()
        elapsed = now - state['last_refill']
        
        # Calculate tokens to add
        tokens_to_add = elapsed * self.refill_rate
        
        # Add tokens (cap at capacity)
        state['tokens'] = min(
            self.capacity,
            state['tokens'] + tokens_to_add
        )
        
        state['last_refill'] = now
    
    def check_rate_limit(
        self,
        endpoint: str,
        user_id: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Check if request is allowed
        
        Args:
            endpoint: API endpoint being called
            user_id: User identifier (optional)
            
        Returns:
            (is_allowed, error_message)
            
        Examples:
            >>> limiter = RateLimiter()
            >>> allowed, msg = limiter.check_rate_limit('/api/analyze')
            >>> if not allowed:
            ...     st.error(msg)
        """
        # Refill tokens first
        self._refill_tokens()
        
        # Get cost for this endpoint
        cost = self.endpoint_costs.get(endpoint, 1)
        
        # Check if enough tokens
        state = st.session_state.rate_limiter
        
        if state['tokens'] >= cost:
            # Consume tokens
            state['tokens'] -= cost
            
            logger.debug(f"Rate limit OK: {endpoint} (cost={cost}, remaining={state['tokens']:.1f})")
            
            return True, None
        else:
            # Rate limited
            wait_time = self._calculate_wait_time(cost)
            
            error_msg = (
                f"Rate limit exceeded. Please wait {wait_time:.0f} seconds before trying again. "
                f"This helps prevent overloading the system."
            )
            
            logger.warning(f"Rate limited: {endpoint} (tokens={state['tokens']:.1f}, cost={cost})")
            
            return False, error_msg
    
    def _calculate_wait_time(self, required_tokens: float) -> float:
        """
        Calculate how long until enough tokens available
        
        Args:
            required_tokens: Tokens needed
            
        Returns:
            Wait time in seconds
        """
        state = st.session_state.rate_limiter
        tokens_needed = required_tokens - state['tokens']
        wait_time = tokens_needed / self.refill_rate
        return max(0, wait_time)
    
    def get_status(self) -> Dict[str, any]:
        """
        Get current rate limit status
        
        Returns:
            Dict with status info
        """
        self._refill_tokens()
        state = st.session_state.rate_limiter
        
        return {
            'tokens_available': round(state['tokens'], 1),
            'capacity': self.capacity,
            'percentage': round((state['tokens'] / self.capacity) * 100, 1),
            'refill_rate': self.refill_rate
        }
    
    def reset(self):
        """Reset rate limiter (admin function)"""
        st.session_state.rate_limiter = {
            'tokens': self.capacity,
            'last_refill': time.time()
        }
        logger.info("Rate limiter reset")


# Singleton instance
@st.cache_resource
def get_rate_limiter() -> RateLimiter:
    """
    Get cached rate limiter instance
    
    Returns:
        RateLimiter instance
    """
    return RateLimiter(
        capacity=10,      # 10 tokens
        refill_rate=0.167, # ~1 token per 6 seconds
        refill_interval=60
    )