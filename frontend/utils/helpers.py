import streamlit as st
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import logging
import re
import hashlib
import json
from utils.constants import *

logger = logging.getLogger(__name__)


# =====================================================
# FORMATTING FUNCTIONS
# =====================================================

def format_currency(
    amount: float,
    currency: str = CURRENCY_USD,
    decimals: Optional[int] = None
) -> str:
    """
    Format amount as currency with symbol
    
    Args:
        amount: Amount to format
        currency: Currency code (USD, EUR, VND, etc.)
        decimals: Number of decimal places (auto if None)
        
    Returns:
        Formatted currency string
        
    Examples:
        >>> format_currency(1234.56, "USD")
        "$1,234.56"
        >>> format_currency(1234.56, "VND")
        "₫1,235"
        >>> format_currency(1234.56, "EUR", decimals=1)
        "€1,234.6"
    
    NOTE FOR BACKEND:
    Backend should return amounts as float, not formatted strings.
    Frontend handles all display formatting.
    """
    symbol = CURRENCY_SYMBOLS.get(currency, "$")
    
    # VND doesn't use decimals
    if decimals is None:
        decimals = 0 if currency == CURRENCY_VND else 2
    
    if decimals == 0:
        return f"{symbol}{amount:,.0f}"
    else:
        return f"{symbol}{amount:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format as percentage
    
    Args:
        value: Value to format (0-100 or 0-1)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
        
    Examples:
        >>> format_percentage(85.3)
        "85.3%"
        >>> format_percentage(0.853)  # Auto-detect 0-1 range
        "85.3%"
    """
    # Auto-detect if value is 0-1 range
    if 0 <= value <= 1:
        value = value * 100
    
    return f"{value:.{decimals}f}%"


def format_number(value: Union[int, float], decimals: int = 0) -> str:
    """
    Format number with thousands separator
    
    Args:
        value: Number to format
        decimals: Number of decimal places
        
    Returns:
        Formatted number string
        
    Examples:
        >>> format_number(1234567)
        "1,234,567"
        >>> format_number(1234.5678, decimals=2)
        "1,234.57"
    """
    if decimals == 0:
        return f"{value:,.0f}"
    else:
        return f"{value:,.{decimals}f}"


def format_datetime(
    dt: Union[datetime, str],
    format: str = DATETIME_FORMAT_DISPLAY
) -> str:
    """
    Format datetime object or ISO string
    
    Args:
        dt: Datetime object or ISO string
        format: Output format string
        
    Returns:
        Formatted datetime string
        
    Examples:
        >>> format_datetime("2026-02-21T10:30:00")
        "Feb 21, 2026 10:30 AM"
        >>> format_datetime(datetime.now(), "%Y-%m-%d")
        "2026-02-21"
    
    NOTE FOR BACKEND:
    Backend should ALWAYS return datetimes in ISO 8601 format:
    "2026-02-21T10:30:00Z" or "2026-02-21T10:30:00+00:00"
    """
    if isinstance(dt, str):
        try:
            # Parse ISO format
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except:
            return dt  # Return as-is if can't parse
    
    try:
        return dt.strftime(format)
    except:
        return str(dt)


def time_ago(dt: Union[datetime, str]) -> str:
    """
    Convert datetime to human-readable "time ago" format
    
    Args:
        dt: Datetime object or ISO string
        
    Returns:
        Human-readable time ago string
        
    Examples:
        >>> time_ago(datetime.now() - timedelta(minutes=5))
        "5 minutes ago"
        >>> time_ago(datetime.now() - timedelta(days=2))
        "2 days ago"
    """
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except:
            return "unknown"
    
    now = datetime.now()
    if dt.tzinfo:
        from datetime import timezone
        now = datetime.now(timezone.utc)
    
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "just now"


# =====================================================
# COLOR & STYLING FUNCTIONS
# =====================================================

def get_risk_color(risk_score: int) -> str:
    """
    Get color based on risk score (0-100)
    
    Args:
        risk_score: Risk score (0-100)
        
    Returns:
        Hex color code
        
    Examples:
        >>> get_risk_color(25)
        "#00d68f"  # Green
        >>> get_risk_color(50)
        "#ffab00"  # Yellow
        >>> get_risk_color(85)
        "#ff5252"  # Red
    
    NOTE FOR BACKEND:
    Backend calculates risk_score (0-100 integer).
    Frontend handles all color mapping for display.
    """
    from config import config
    
    if risk_score < config.RISK_THRESHOLD_LOW:
        return COLOR_SUCCESS
    elif risk_score < config.RISK_THRESHOLD_MEDIUM:
        return COLOR_WARNING
    else:
        return COLOR_DANGER


def get_status_emoji(status: str) -> str:
    """
    Get emoji for status
    
    Args:
        status: Status string (APPROVED, PENDING, BLOCKED, etc.)
        
    Returns:
        Emoji character
        
    NOTE FOR BACKEND:
    Backend returns status as string constant.
    Must use exact strings from constants.py
    """
    return STATUS_ICONS.get(status, "❓")


def get_severity_emoji(severity: str) -> str:
    """Get emoji for severity level"""
    return SEVERITY_ICONS.get(severity, "⚪")


def get_status_color(status: str) -> str:
    """
    Get color for status
    
    Args:
        status: Status string
        
    Returns:
        CSS color class name
    """
    color_map = {
        STATUS_APPROVED: "success",
        STATUS_PENDING: "warning",
        STATUS_BLOCKED: "danger",
        STATUS_REVIEW: "warning",
        STATUS_ERROR: "danger"
    }
    return color_map.get(status, "info")


# =====================================================
# TEXT PROCESSING
# =====================================================

def truncate_text(
    text: str,
    max_length: int = 50,
    suffix: str = "..."
) -> str:
    """
    Truncate text to max length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
        
    Examples:
        >>> truncate_text("This is a very long text", 10)
        "This is..."
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
        
    Examples:
        >>> sanitize_filename("My Invoice (1).pdf")
        "My_Invoice_1.pdf"
        >>> sanitize_filename("invoice@#$%.pdf")
        "invoice.pdf"
    
    NOTE FOR BACKEND:
    Backend should also sanitize filenames before storing.
    Use same logic to ensure consistency.
    """
    # Remove unsafe characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    return filename


def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """
    Extract keywords from text (simple implementation)
    
    Args:
        text: Input text
        max_keywords: Maximum number of keywords
        
    Returns:
        List of keywords
    """
    # Remove special characters
    text = re.sub(r'[^\w\s]', '', text.lower())
    # Split into words
    words = text.split()
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
    keywords = [w for w in words if w not in stop_words and len(w) > 3]
    # Return unique keywords
    return list(dict.fromkeys(keywords))[:max_keywords]


# =====================================================
# MATH & CALCULATION
# =====================================================

def safe_divide(
    numerator: float,
    denominator: float,
    default: float = 0.0
) -> float:
    """
    Safe division avoiding divide by zero
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division fails
        
    Returns:
        Result or default
        
    Examples:
        >>> safe_divide(10, 2)
        5.0
        >>> safe_divide(10, 0)
        0.0
        >>> safe_divide(10, 0, default=1.0)
        1.0
    """
    try:
        return numerator / denominator if denominator != 0 else default
    except:
        return default


def calculate_percentage_change(
    old_value: float,
    new_value: float
) -> float:
    """
    Calculate percentage change
    
    Args:
        old_value: Old value
        new_value: New value
        
    Returns:
        Percentage change
        
    Examples:
        >>> calculate_percentage_change(100, 120)
        20.0
        >>> calculate_percentage_change(100, 80)
        -20.0
    """
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100


def round_to_nearest(value: float, nearest: float = 0.01) -> float:
    """
    Round to nearest value
    
    Args:
        value: Value to round
        nearest: Round to nearest this value
        
    Returns:
        Rounded value
        
    Examples:
        >>> round_to_nearest(1.234, 0.01)
        1.23
        >>> round_to_nearest(1234, 100)
        1200
    """
    return round(value / nearest) * nearest


# =====================================================
# VALIDATION HELPERS
# =====================================================

def is_valid_email(email: str) -> bool:
    """
    Validate email format (simple check)
    
    Args:
        email: Email address
        
    Returns:
        True if valid format
        
    Examples:
        >>> is_valid_email("user@example.com")
        True
        >>> is_valid_email("invalid-email")
        False
    """
    return bool(re.match(REGEX_EMAIL, email))


def is_safe_filename(filename: str) -> bool:
    """
    Check if filename is safe (no path traversal)
    
    Args:
        filename: Filename to check
        
    Returns:
        True if safe
    """
    # Check for path traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        return False
    # Check against safe pattern
    return bool(re.match(REGEX_SAFE_FILENAME, filename))


# =====================================================
# LOGGING & DEBUGGING
# =====================================================

def log_action(
    action: str,
    details: Optional[Dict[str, Any]] = None,
    level: str = "INFO"
):
    """
    Log user action
    
    Args:
        action: Action name
        details: Additional details
        level: Log level (INFO, WARNING, ERROR)
        
    Examples:
        >>> log_action("process_invoice", {"invoice_id": "INV-001"})
        >>> log_action("login_failed", {"email": "user@example.com"}, level="WARNING")
    
    NOTE FOR BACKEND:
    Backend should have separate audit logging system.
    This is for frontend debugging only.
    """
    user = st.session_state.get('user_email', 'anonymous')
    log_msg = f"User: {user} | Action: {action}"
    
    if details:
        # Sanitize sensitive data
        safe_details = {k: v for k, v in details.items() if k not in ['password', 'token']}
        log_msg += f" | Details: {safe_details}"
    
    if level == "INFO":
        logger.info(log_msg)
    elif level == "WARNING":
        logger.warning(log_msg)
    elif level == "ERROR":
        logger.error(log_msg)
    else:
        logger.debug(log_msg)


def debug_print(data: Any, label: str = "Debug"):
    """
    Pretty print debug data (only in debug mode)
    
    Args:
        data: Data to print
        label: Label for debug output
    """
    from config import config
    
    if config.DEBUG:
        st.sidebar.write(f"**{label}:**")
        st.sidebar.json(data if isinstance(data, dict) else str(data))


# =====================================================
# UI HELPERS
# =====================================================

def show_toast(
    message: str,
    type: str = "info",
    icon: Optional[str] = None
):
    """
    Show toast notification
    
    Args:
        message: Message to display
        type: Type (success, error, warning, info)
        icon: Optional icon emoji
        
    Examples:
        >>> show_toast("Invoice processed!", "success", "✅")
        >>> show_toast("Rate limit exceeded", "warning", "⚠️")
    """
    if icon:
        message = f"{icon} {message}"
    
    if type == "success":
        st.success(message)
    elif type == "error":
        st.error(message)
    elif type == "warning":
        st.warning(message)
    else:
        st.info(message)


def render_metric_card(
    title: str,
    value: str,
    delta: Optional[str] = None,
    delta_positive: bool = True,
    help_text: Optional[str] = None,
    icon: Optional[str] = None
):
    """
    Render a styled metric card
    
    Args:
        title: Metric title
        value: Metric value
        delta: Delta value (e.g., "+5%")
        delta_positive: Whether delta is good (green) or bad (red)
        help_text: Tooltip text
        icon: Optional icon emoji
        
    Examples:
        >>> render_metric_card("Accuracy", "99.2%", "+0.2%", icon="🎯")
        >>> render_metric_card("Errors", "12", "+3", delta_positive=False, icon="❌")
    """
    delta_class = "" if delta_positive else "negative"
    help_icon = f'<span title="{help_text}" style="cursor: help;">ℹ️</span>' if help_text else ""
    icon_html = f'<span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>' if icon else ""
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{icon_html}{title} {help_icon}</div>
        <div class="metric-value">{value}</div>
        {f'<div class="metric-delta {delta_class}">{delta}</div>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)


def create_download_link(
    data: Union[str, bytes],
    filename: str,
    mime_type: str = "text/plain"
) -> str:
    """
    Create download link for data
    
    Args:
        data: Data to download
        filename: Filename
        mime_type: MIME type
        
    Returns:
        Streamlit download button
        
    Examples:
        >>> create_download_link("csv_data", "export.csv", "text/csv")
    """
    import base64
    
    if isinstance(data, str):
        data = data.encode()
    
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}">Download {filename}</a>'
    return href


# =====================================================
# DATA PROCESSING
# =====================================================

def merge_dicts(*dicts: Dict) -> Dict:
    """
    Merge multiple dictionaries (later values override earlier)
    
    Args:
        *dicts: Dictionaries to merge
        
    Returns:
        Merged dictionary
        
    Examples:
        >>> merge_dicts({"a": 1}, {"b": 2}, {"a": 3})
        {"a": 3, "b": 2}
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result


def deep_get(dictionary: Dict, keys: str, default: Any = None) -> Any:
    """
    Get nested dictionary value using dot notation
    
    Args:
        dictionary: Dictionary to search
        keys: Dot-separated keys (e.g., "user.profile.name")
        default: Default value if not found
        
    Returns:
        Value or default
        
    Examples:
        >>> data = {"user": {"profile": {"name": "John"}}}
        >>> deep_get(data, "user.profile.name")
        "John"
        >>> deep_get(data, "user.profile.age", default=0)
        0
    """
    keys_list = keys.split('.')
    value = dictionary
    
    for key in keys_list:
        try:
            value = value[key]
        except (KeyError, TypeError):
            return default
    
    return value


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """
    Flatten nested dictionary
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key (used in recursion)
        sep: Separator for keys
        
    Returns:
        Flattened dictionary
        
    Examples:
        >>> flatten_dict({"a": {"b": {"c": 1}}})
        {"a.b.c": 1}
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


# =====================================================
# HASH & CRYPTO
# =====================================================

def generate_hash(data: str, algorithm: str = "sha256") -> str:
    """
    Generate hash of data
    
    Args:
        data: Data to hash
        algorithm: Hash algorithm (md5, sha1, sha256)
        
    Returns:
        Hex hash string
        
    Examples:
        >>> generate_hash("test data")
        "916f0027a575074ce72a331777c3478d6513f786a591bd892da1a577bf2335f9"
    
    NOTE: This is for non-security purposes (cache keys, etc.)
    Do NOT use for password hashing!
    """
    if algorithm == "md5":
        return hashlib.md5(data.encode()).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(data.encode()).hexdigest()
    else:
        return hashlib.sha256(data.encode()).hexdigest()


def generate_short_id(length: int = 8) -> str:
    """
    Generate short random ID
    
    Args:
        length: ID length
        
    Returns:
        Random ID string
        
    Examples:
        >>> generate_short_id(8)
        "a3f9d2e1"
    """
    import secrets
    return secrets.token_hex(length // 2)


# =====================================================
# CACHE HELPERS
# =====================================================

def get_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate cache key from arguments
    
    Args:
        prefix: Key prefix
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Cache key string
        
    Examples:
        >>> get_cache_key("metrics", user_id=123, date="2026-02-21")
        "metrics:user_id=123:date=2026-02-21"
    """
    parts = [prefix]
    
    for arg in args:
        parts.append(str(arg))
    
    for key, value in sorted(kwargs.items()):
        parts.append(f"{key}={value}")
    
    return ":".join(parts)


# =====================================================
# STREAMLIT HELPERS
# =====================================================

def init_session_state(defaults: Dict[str, Any]):
    """
    Initialize session state with defaults
    
    Args:
        defaults: Dictionary of default values
        
    Examples:
        >>> init_session_state({
        ...     "user_email": None,
        ...     "logged_in": False,
        ...     "theme": "dark"
        ... })
    """
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_session_state():
    """Clear all session state variables"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def get_session_value(key: str, default: Any = None) -> Any:
    """
    Get value from session state
    
    Args:
        key: Session key
        default: Default value
        
    Returns:
        Session value or default
    """
    return st.session_state.get(key, default)


def set_session_value(key: str, value: Any):
    """Set value in session state"""
    st.session_state[key] = value


# =====================================================
# ERROR HANDLING
# =====================================================

class AgentFlowError(Exception):
    """Base exception for AgentFlow"""
    pass


class ValidationError(AgentFlowError):
    """Validation error"""
    pass


class APIError(AgentFlowError):
    """API error"""
    pass


class AuthenticationError(AgentFlowError):
    """Authentication error"""
    pass


def handle_error(error: Exception, show_details: bool = False):
    """
    Handle error and show user-friendly message
    
    Args:
        error: Exception object
        show_details: Whether to show technical details
        
    Examples:
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     handle_error(e)
    """
    from config import config
    
    # Log error
    logger.error(f"Error: {type(error).__name__}: {str(error)}")
    
    # Show user-friendly message
    if isinstance(error, ValidationError):
        st.error(f"❌ Validation Error: {str(error)}")
    elif isinstance(error, APIError):
        st.error(f"❌ API Error: {str(error)}")
    elif isinstance(error, AuthenticationError):
        st.error(f"❌ Authentication Error: {str(error)}")
    else:
        st.error(f"❌ An error occurred: {str(error) if show_details or config.DEBUG else 'Please try again'}")
    
    # Show details in debug mode
    if config.DEBUG and show_details:
        st.exception(error)


# =====================================================
# EXPORT
# =====================================================

__all__ = [
    # Formatting
    'format_currency',
    'format_percentage',
    'format_number',
    'format_datetime',
    'time_ago',
    
    # Colors & Styling
    'get_risk_color',
    'get_status_emoji',
    'get_severity_emoji',
    'get_status_color',
    
    # Text
    'truncate_text',
    'sanitize_filename',
    'extract_keywords',
    
    # Math
    'safe_divide',
    'calculate_percentage_change',
    'round_to_nearest',
    
    # Validation
    'is_valid_email',
    'is_safe_filename',
    
    # Logging
    'log_action',
    'debug_print',
    
    # UI
    'show_toast',
    'render_metric_card',
    'create_download_link',
    
    # Data
    'merge_dicts',
    'deep_get',
    'flatten_dict',
    
    # Hash
    'generate_hash',
    'generate_short_id',
    
    # Cache
    'get_cache_key',
    
    # Session
    'init_session_state',
    'clear_session_state',
    'get_session_value',
    'set_session_value',
    
    # Errors
    'AgentFlowError',
    'ValidationError',
    'APIError',
    'AuthenticationError',
    'handle_error'
]

def apply_theme():
    """Inject theme CSS vào page hiện tại. Gọi ở đầu mỗi page file."""
    import streamlit as st
    from config import config
    try:
        from themes.dark import DARK_THEME
        from themes.light import LIGHT_THEME
        theme = st.session_state.get('theme', 'dark')
        css = DARK_THEME if theme == 'dark' else LIGHT_THEME
        st.markdown(css, unsafe_allow_html=True)
    except Exception:
        pass