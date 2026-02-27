import re
from typing import Tuple, List, Optional, Any
import html
import bleach
from utils.constants import *


class InputValidator:
    """
    Security-focused input validator
    
    All validation methods return (is_valid, error_message) tuple.
    If is_valid is False, error_message explains why.
    """
    
    # =====================================================
    # EMAIL & PASSWORD VALIDATION
    # =====================================================
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email format
        
        Args:
            email: Email address to validate
            
        Returns:
            (is_valid, error_message)
            
        Examples:
            >>> validate_email("user@example.com")
            (True, "")
            >>> validate_email("invalid-email")
            (False, "Invalid email format")
        """
        if not email:
            return False, "Email is required"
        
        if len(email) > 254:  # RFC 5321
            return False, "Email too long (max 254 characters)"
        
        if not re.match(REGEX_EMAIL, email):
            return False, "Invalid email format"
        
        return True, ""
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Validate password strength
        
        Requirements (enforced by Cognito):
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        - At least one special character
        
        Args:
            password: Password to validate
            
        Returns:
            (is_valid, error_message)
            
        Examples:
            >>> validate_password("Test123!")
            (True, "")
            >>> validate_password("weak")
            (False, "Password must be at least 8 characters")
        
        NOTE FOR BACKEND:
        Backend uses AWS Cognito for password management.
        Cognito enforces these rules automatically.
        NEVER store passwords in plaintext!
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if len(password) > 128:
            return False, "Password too long (max 128 characters)"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, ""
    
    # =====================================================
    # TEXT SANITIZATION
    # =====================================================
    
    @staticmethod
    def sanitize_string(
        text: str,
        max_length: int = 1000,
        allow_html: bool = False
    ) -> str:
        """
        Sanitize user input string
        
        Prevents:
        - XSS attacks
        - Script injection
        - HTML injection (unless explicitly allowed)
        
        Args:
            text: Input text
            max_length: Maximum allowed length
            allow_html: Whether to allow safe HTML tags
            
        Returns:
            Sanitized text
            
        Examples:
            >>> sanitize_string("<script>alert('XSS')</script>")
            "&lt;script&gt;alert('XSS')&lt;/script&gt;"
            >>> sanitize_string("Hello <b>World</b>", allow_html=True)
            "Hello <b>World</b>"  # Only safe tags allowed
        
        NOTE FOR BACKEND:
        Backend should also sanitize before storing in database.
        Use prepared statements to prevent SQL injection.
        """
        if not text:
            return ""
        
        # Truncate to max length
        text = text[:max_length]
        
        if allow_html:
            # Allow only safe HTML tags
            allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'a', 'br']
            allowed_attrs = {'a': ['href', 'title']}
            text = bleach.clean(
                text,
                tags=allowed_tags,
                attributes=allowed_attrs,
                strip=True
            )
        else:
            # Remove all HTML tags
            text = bleach.clean(text, tags=[], strip=True)
        
        # Escape HTML entities
        text = html.escape(text)
        
        return text
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        r"""
        Sanitize filename for safe storage
        
        Prevents:
        - Path traversal attacks (../, ..\)
        - Command injection
        - Special characters that could break file systems
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
            
        Examples:
            >>> sanitize_filename("../../etc/passwd")
            "etc_passwd"
            >>> sanitize_filename("invoice (1).pdf")
            "invoice_1.pdf"
        
        NOTE FOR BACKEND:
        Backend should generate its own secure filenames (e.g., UUID).
        Never trust client-provided filenames for storage paths.
        """
        if not filename:
            return "unnamed"
        
        # Remove directory separators
        filename = filename.replace('/', '_').replace('\\', '_')
        
        # Remove parent directory references
        filename = filename.replace('..', '')
        
        # Remove unsafe characters (keep only alphanumeric, dots, dashes, underscores)
        filename = re.sub(r'[^\w\s.-]', '', filename)
        
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        
        # Remove multiple consecutive underscores
        filename = re.sub(r'_+', '_', filename)
        
        # Ensure not empty after sanitization
        if not filename or filename == '.':
            filename = "unnamed"
        
        return filename
    
    # =====================================================
    # FILE UPLOAD VALIDATION
    # =====================================================
    
    @staticmethod
    def validate_file_upload(
        file: Any,
        allowed_types: List[str],
        max_size_mb: int = 50
    ) -> Tuple[bool, str]:
        """
        Validate uploaded file
        
        Checks:
        1. File exists
        2. File size within limit
        3. File extension is allowed
        4. Filename is safe
        
        Args:
            file: Streamlit UploadedFile object
            allowed_types: List of allowed extensions (e.g., ['pdf', 'png'])
            max_size_mb: Maximum file size in MB
            
        Returns:
            (is_valid, error_message)
            
        Examples:
            >>> validate_file_upload(file, ['pdf', 'png'], 50)
            (True, "")
        
        NOTE FOR BACKEND:
        Backend MUST perform additional validation:
        1. Check magic bytes (file signature), not just extension
        2. Scan for viruses (optional but recommended)
        3. Validate file content structure
        4. Generate secure storage filename (don't use client filename)
        
        Example backend validation:
```python
        import magic
        
        # Check magic bytes
        mime = magic.from_buffer(file_bytes, mime=True)
        if mime not in ['application/pdf', 'image/png', 'image/jpeg']:
            raise ValueError("Invalid file type")
        
        # Optional: Virus scan with ClamAV
        import pyclamd
        cd = pyclamd.ClamdUnixSocket()
        if cd.scan_stream(file_bytes):
            raise ValueError("Virus detected")
```
        """
        # Check if file exists
        if file is None:
            return False, "No file provided"
        
        # Check file size
        file_size_mb = file.size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            return False, f"File too large: {file_size_mb:.1f}MB (max: {max_size_mb}MB)"
        
        # Check file extension
        if '.' not in file.name:
            return False, "File has no extension"
        
        file_ext = file.name.split('.')[-1].lower()
        if file_ext not in allowed_types:
            return False, f"Invalid file type: .{file_ext} (allowed: {', '.join(allowed_types)})"
        
        # Check filename safety
        if not InputValidator.is_safe_filename(file.name):
            return False, "Invalid filename (contains unsafe characters)"
        
        return True, ""
    
    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        """
        Check if filename is safe (no path traversal)
        
        Args:
            filename: Filename to check
            
        Returns:
            True if safe, False if potentially dangerous
            
        Examples:
            >>> is_safe_filename("invoice.pdf")
            True
            >>> is_safe_filename("../../etc/passwd")
            False
        """
        # Check for path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return False
        
        # Check for null bytes
        if '\x00' in filename:
            return False
        
        # Check against safe pattern (alphanumeric, dots, dashes, underscores)
        if not re.match(REGEX_SAFE_FILENAME, filename):
            return False
        
        return True
    
    # =====================================================
    # NUMERIC VALIDATION
    # =====================================================
    
    @staticmethod
    def validate_amount(
        amount: Any,
        min_value: float = 0,
        max_value: float = 1000000
    ) -> Tuple[bool, str]:
        """
        Validate monetary amount
        
        Args:
            amount: Amount to validate (string or number)
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            (is_valid, error_message)
            
        Examples:
            >>> validate_amount("1234.56")
            (True, "")
            >>> validate_amount("-100")
            (False, "Amount must be positive")
        """
        try:
            amount_float = float(amount)
        except (ValueError, TypeError):
            return False, "Invalid amount format"
        
        if amount_float < min_value:
            return False, f"Amount must be at least {min_value}"
        
        if amount_float > max_value:
            return False, f"Amount must not exceed {max_value}"
        
        # Check for reasonable decimal places (max 2 for currency)
        if '.' in str(amount):
            decimals = len(str(amount).split('.')[1])
            if decimals > 2:
                return False, "Amount can have at most 2 decimal places"
        
        return True, ""
    
    @staticmethod
    def validate_risk_score(score: Any) -> Tuple[bool, str]:
        """
        Validate risk score (0-100)
        
        Args:
            score: Risk score to validate
            
        Returns:
            (is_valid, error_message)
        """
        try:
            score_int = int(score)
        except (ValueError, TypeError):
            return False, "Invalid risk score format"
        
        if not 0 <= score_int <= 100:
            return False, "Risk score must be between 0 and 100"
        
        return True, ""
    
    # =====================================================
    # DATE VALIDATION
    # =====================================================
    
    @staticmethod
    def validate_date(date_str: str, format: str = "%Y-%m-%d") -> Tuple[bool, str]:
        """
        Validate date string
        
        Args:
            date_str: Date string to validate
            format: Expected date format
            
        Returns:
            (is_valid, error_message)
            
        Examples:
            >>> validate_date("2026-02-21")
            (True, "")
            >>> validate_date("21/02/2026")
            (False, "Invalid date format")
        
        NOTE FOR BACKEND:
        Backend should store dates in ISO 8601 format: YYYY-MM-DD
        """
        try:
            from datetime import datetime
            datetime.strptime(date_str, format)
            return True, ""
        except ValueError:
            return False, f"Invalid date format (expected: {format})"
    
    # =====================================================
    # ATTACK DETECTION (FOR DEMO PAGE)
    # =====================================================
    
    @staticmethod
    def detect_sql_injection(input_str: str) -> bool:
        """
        Detect potential SQL injection attempts
        
        ⚠️ THIS IS FOR DEMO PURPOSES ONLY! ⚠️
        Do NOT use blacklist detection in production!
        
        In production:
        - Backend uses parameterized queries (not validation)
        - This prevents SQL injection at the source
        
        Args:
            input_str: Input to check
            
        Returns:
            True if SQL injection pattern detected
            
        NOTE FOR BACKEND:
        NEVER use blacklist validation for SQL injection!
        ALWAYS use parameterized queries:
        
        ✅ CORRECT:
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        
        ❌ WRONG:
        cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
        """
        sql_patterns = [
            r"(\bOR\b.*?=.*?|'\s*OR\s*')",
            r"(\bUNION\b.*?\bSELECT\b)",
            r"(\bDROP\b.*?\bTABLE\b)",
            r"(;.*?--)",
            r"(/\*.*?\*/)",
            r"(\bEXEC\b|\bEXECUTE\b)",
            r"(xp_cmdshell)",
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def detect_xss(input_str: str) -> bool:
        """
        Detect potential XSS attempts
        
        ⚠️ THIS IS FOR DEMO PURPOSES ONLY! ⚠️
        Do NOT use blacklist detection in production!
        
        In production:
        - Sanitize all inputs (see sanitize_string)
        - Encode all outputs
        - Use Content Security Policy headers
        
        Args:
            input_str: Input to check
            
        Returns:
            True if XSS pattern detected
        """
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"onerror\s*=",
            r"onload\s*=",
            r"<img[^>]*onerror",
            r"<svg[^>]*onload",
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def detect_path_traversal(input_str: str) -> bool:
        """
        Detect potential path traversal attempts
        
        Args:
            input_str: Input to check
            
        Returns:
            True if path traversal pattern detected
        """
        traversal_patterns = [
            r"\.\./",
            r"\.\.",
            r"%2e%2e",
            r"/etc/passwd",
            r"c:\\windows",
        ]
        
        for pattern in traversal_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                return True
        
        return False
    
    # =====================================================
    # BATCH VALIDATION
    # =====================================================
    
    @staticmethod
    def validate_all(validations: List[Tuple[bool, str]]) -> Tuple[bool, List[str]]:
        """
        Validate multiple fields at once
        
        Args:
            validations: List of (is_valid, error_message) tuples
            
        Returns:
            (all_valid, list_of_errors)
            
        Examples:
            >>> results = [
            ...     validate_email("user@example.com"),
            ...     validate_password("Test123!"),
            ...     validate_amount("1234.56")
            ... ]
            >>> is_valid, errors = validate_all(results)
        """
        all_valid = all(v[0] for v in validations)
        errors = [v[1] for v in validations if not v[0]]
        return all_valid, errors


# =====================================================
# CONVENIENCE FUNCTIONS
# =====================================================

def validate_email(email: str) -> Tuple[bool, str]:
    """Convenience wrapper"""
    return InputValidator.validate_email(email)

def validate_password(password: str) -> Tuple[bool, str]:
    """Convenience wrapper"""
    return InputValidator.validate_password(password)

def sanitize_string(text: str, max_length: int = 1000) -> str:
    """Convenience wrapper"""
    return InputValidator.sanitize_string(text, max_length)

def validate_file_upload(file: Any, allowed_types: List[str], max_size_mb: int = 50) -> Tuple[bool, str]:
    """Convenience wrapper"""
    return InputValidator.validate_file_upload(file, allowed_types, max_size_mb)


# =====================================================
# EXPORT
# =====================================================

__all__ = [
    'InputValidator',
    'validate_email',
    'validate_password',
    'sanitize_string',
    'validate_file_upload'
]

def detect_sql_injection(input_str: str) -> bool:
    return InputValidator.detect_sql_injection(input_str)

def detect_xss(input_str: str) -> bool:
    return InputValidator.detect_xss(input_str)

def detect_path_traversal(input_str: str) -> bool:
    return InputValidator.detect_path_traversal(input_str)

def sanitize_filename(filename: str) -> str:
    return InputValidator.sanitize_filename(filename)