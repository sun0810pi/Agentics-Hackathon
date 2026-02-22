# =====================================================
# STATUS CONSTANTS
# =====================================================
STATUS_APPROVED = "APPROVED"
STATUS_PENDING = "PENDING"
STATUS_BLOCKED = "BLOCKED"
STATUS_REVIEW = "REVIEW"
STATUS_ERROR = "ERROR"
STATUS_SUCCESS = "SUCCESS"

# =====================================================
# DECISION TYPES
# =====================================================
DECISION_APPROVE = "APPROVE"
DECISION_REVIEW = "REVIEW"
DECISION_BLOCK = "BLOCK"
DECISION_ERROR = "ERROR"

# =====================================================
# AGENT MODES
# =====================================================
MODE_FULL = "full"
MODE_FAST = "fast"
MODE_DEMO = "demo"

# =====================================================
# SEVERITY LEVELS
# =====================================================
SEVERITY_CRITICAL = "CRITICAL"
SEVERITY_HIGH = "HIGH"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_LOW = "LOW"
SEVERITY_INFO = "INFO"

# =====================================================
# CURRENCY CODES
# =====================================================
CURRENCY_USD = "USD"
CURRENCY_EUR = "EUR"
CURRENCY_VND = "VND"
CURRENCY_GBP = "GBP"
CURRENCY_JPY = "JPY"

CURRENCY_SYMBOLS = {
    CURRENCY_USD: "$",
    CURRENCY_EUR: "€",
    CURRENCY_VND: "₫",
    CURRENCY_GBP: "£",
    CURRENCY_JPY: "¥"
}

# =====================================================
# DATE FORMATS
# =====================================================
DATE_FORMAT_ISO = "%Y-%m-%d"
DATETIME_FORMAT_ISO = "%Y-%m-%d %H:%M:%S"
DATETIME_FORMAT_DISPLAY = "%b %d, %Y %I:%M %p"
DATETIME_FORMAT_SHORT = "%Y-%m-%d %H:%M"

# =====================================================
# CHART COLORS
# =====================================================
COLOR_SUCCESS = "#00d68f"
COLOR_WARNING = "#ffab00"
COLOR_DANGER = "#ff5252"
COLOR_INFO = "#4A9EFF"
COLOR_NEUTRAL = "#a0aec0"
COLOR_PRIMARY = "#4A9EFF"
COLOR_SECONDARY = "#718096"

# Color scales
COLORS_RISK = ["#00d68f", "#ffab00", "#ff5252"]  # Low → Medium → High
COLORS_HEATMAP = ["#0a0e1a", "#4A9EFF", "#00d68f"]

# =====================================================
# ICON MAPPINGS
# =====================================================
STATUS_ICONS = {
    STATUS_APPROVED: "✅",
    STATUS_PENDING: "⏳",
    STATUS_BLOCKED: "❌",
    STATUS_REVIEW: "⚠️",
    STATUS_ERROR: "🔴",
    STATUS_SUCCESS: "✅"
}

SEVERITY_ICONS = {
    SEVERITY_CRITICAL: "🔴",
    SEVERITY_HIGH: "🟠",
    SEVERITY_MEDIUM: "🟡",
    SEVERITY_LOW: "🟢",
    SEVERITY_INFO: "ℹ️"
}

AGENT_TIER_ICONS = {
    "Core Detection": "🎯",
    "ML Intelligence": "🧠",
    "Merchant Success": "💼",
    "Security": "🛡️"
}

# =====================================================
# ATTACK TYPES (for demo)
# =====================================================
ATTACK_SQL_INJECTION = "SQL Injection"
ATTACK_XSS = "Cross-Site Scripting (XSS)"
ATTACK_PATH_TRAVERSAL = "Path Traversal"
ATTACK_COMMAND_INJECTION = "Command Injection"
ATTACK_CSRF = "Cross-Site Request Forgery"
ATTACK_XXE = "XML External Entity"
ATTACK_SSRF = "Server-Side Request Forgery"

# Attack payloads (for demonstration only!)
ATTACK_PAYLOADS = {
    ATTACK_SQL_INJECTION: [
        "1' OR '1'='1",
        "admin'--",
        "1; DROP TABLE users--",
        "' UNION SELECT * FROM users--"
    ],
    ATTACK_XSS: [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
        "<svg/onload=alert('XSS')>"
    ],
    ATTACK_PATH_TRAVERSAL: [
        "../../../etc/passwd",
        "....//....//....//etc/passwd",
        "..%252f..%252f..%252fetc/passwd"
    ],
    ATTACK_COMMAND_INJECTION: [
        "; ls -la",
        "| cat /etc/passwd",
        "`whoami`",
        "$(rm -rf /)"
    ]
}

# =====================================================
# FILE TYPES & EXTENSIONS
# =====================================================
FILE_TYPE_PDF = "pdf"
FILE_TYPE_PNG = "png"
FILE_TYPE_JPG = "jpg"
FILE_TYPE_JPEG = "jpeg"

MIME_TYPES = {
    FILE_TYPE_PDF: "application/pdf",
    FILE_TYPE_PNG: "image/png",
    FILE_TYPE_JPG: "image/jpeg",
    FILE_TYPE_JPEG: "image/jpeg"
}

# =====================================================
# API ENDPOINTS
# =====================================================
ENDPOINT_HEALTH = "/health"
ENDPOINT_ANALYZE = "/api/analyze"
ENDPOINT_METRICS = "/api/metrics"
ENDPOINT_AGENTS = "/api/agents"
ENDPOINT_INVOICES = "/api/invoices"
ENDPOINT_FRAUD_SCENARIOS = "/api/fraud-scenarios"
ENDPOINT_AUDIT_LOGS = "/api/audit-logs"

# =====================================================
# REGEX PATTERNS
# =====================================================
REGEX_EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
REGEX_PHONE = r'^\+?1?\d{9,15}$'
REGEX_SAFE_FILENAME = r'^[a-zA-Z0-9._-]+$'
REGEX_INVOICE_NUMBER = r'^INV-\d{4}-\d{4}$'

# =====================================================
# ERROR MESSAGES
# =====================================================
ERROR_INVALID_EMAIL = "Invalid email format"
ERROR_INVALID_PASSWORD = "Password must be at least 8 characters with uppercase, lowercase, number, and special character"
ERROR_FILE_TOO_LARGE = "File size exceeds maximum allowed"
ERROR_INVALID_FILE_TYPE = "Invalid file type"
ERROR_NETWORK_ERROR = "Network error - please check your connection"
ERROR_BACKEND_UNAVAILABLE = "Backend service unavailable"
ERROR_AUTHENTICATION_FAILED = "Authentication failed"
ERROR_UNAUTHORIZED = "You don't have permission to access this resource"
ERROR_RATE_LIMIT_EXCEEDED = "Rate limit exceeded - please try again later"

# =====================================================
# SUCCESS MESSAGES
# =====================================================
SUCCESS_LOGIN = "Login successful!"
SUCCESS_LOGOUT = "Logged out successfully"
SUCCESS_UPLOAD = "File uploaded successfully"
SUCCESS_PROCESS = "Invoice processed successfully"
SUCCESS_SAVE = "Saved successfully"

# =====================================================
# INFO MESSAGES
# =====================================================
INFO_DEMO_MODE = "🎬 Demo Mode - Using simulated data"
INFO_HYBRID_MODE = "🚀 Hybrid Mode - Connected to backend"
INFO_PRODUCTION_MODE = "🔥 Production Mode - Live system"
INFO_BACKEND_UNAVAILABLE = "⚠️ Backend unavailable - using local processing"

# =====================================================
# CHART DEFAULTS
# =====================================================
CHART_HEIGHT_DEFAULT = 400
CHART_HEIGHT_SMALL = 300
CHART_HEIGHT_LARGE = 600

CHART_TEMPLATE = "plotly_dark"
CHART_FONT_FAMILY = "sans-serif"