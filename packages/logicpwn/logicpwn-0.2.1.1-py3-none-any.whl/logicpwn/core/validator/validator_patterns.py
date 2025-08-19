"""
Vulnerability patterns and regexes for LogicPwn response validation.
Enhanced with critical security vulnerability detection patterns.
"""

class VulnerabilityPatterns:
    """Pre-defined patterns for common vulnerability detection."""
    
    # SQL Injection patterns (Enhanced)
    SQL_INJECTION = [
        r"SQL syntax.*MySQL",
        r"Warning.*mysql_",
        r"valid MySQL result",
        r"ORA-[0-9]{4,5}",
        r"Microsoft.*ODBC.*SQL",
        r"PostgreSQL.*ERROR",
        r"SQLite.*error",
        r"SQL syntax.*MariaDB",
        r"mysql_fetch_array",
        r"mysql_num_rows",
        r"pg_query\(\)",
        r"sqlite3\.OperationalError",
        r"ORA-00933",
        r"syntax error.*near",
        r"quoted string not properly terminated"
    ]
    
    # XSS patterns (Enhanced)
    XSS_INDICATORS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"onerror\s*=",
        r"onload\s*=",
        r"onclick\s*=",
        r"onmouseover\s*=",
        r"onsubmit\s*=",
        r"onfocus\s*=",
        r"onblur\s*=",
        r"eval\s*\(",
        r"document\.cookie",
        r"window\.location",
        r"alert\s*\(",
        r"confirm\s*\(",
        r"prompt\s*\("
    ]
    
    # Directory traversal patterns (Enhanced)
    DIRECTORY_TRAVERSAL = [
        r"root:.*:0:0:",
        r"\[boot loader\]",
        r"<DIR>\s+\.\.",
        r"/etc/passwd",
        r"/var/www/",
        r"C:\\Windows\\",
        r"\.\.[\\/]",
        r"etc[\\/]shadow",
        r"boot\.ini",
        r"windows[\\/]system32",
        r"proc[\\/]version",
        r"\.\.[\\/]\.\.[\\/]",
        r"php\.ini"
    ]
    
    # SSRF (Server-Side Request Forgery) patterns
    SSRF_INDICATORS = [
        r"localhost",
        r"127\.0\.0\.1",
        r"0\.0\.0\.0",
        r"::1",
        r"metadata\.google",
        r"169\.254\.169\.254",  # AWS metadata
        r"metadata\.azure",
        r"metadata\.digitalocean",
        r"consul\.service",
        r"kubernetes\.default",
        r"internal[\.\-_]",
        r"admin[\.\-_]",
        r"test[\.\-_]",
        r"staging[\.\-_]",
        r"dev[\.\-_]",
        r"192\.168\.",
        r"10\.\d+\.",
        r"172\.(1[6-9]|2\d|3[01])\.",
        r"file://",
        r"dict://",
        r"gopher://",
        r"ldap://",
        r"ftp://"
    ]
    
    # Command Injection patterns
    COMMAND_INJECTION = [
        r"uid=\d+.*gid=\d+",  # Unix id command output
        r"root:.*:0:0:",      # /etc/passwd content
        r"bin[\\/]sh",
        r"cmd\.exe",
        r"powershell",
        r"whoami",
        r"ipconfig",
        r"ifconfig",
        r"netstat",
        r"ps aux",
        r"tasklist",
        r"Windows.*Microsoft",
        r"Linux.*GNU",
        r"Darwin.*Kernel",
        r"Volume.*Serial Number",
        r"Directory of C:",
        r"total \d+",  # ls -la output
        r"/bin/bash",
        r"/usr/bin",
        r"command not found",
        r"No such file or directory",
        r"Permission denied",
        r"cannot execute"
    ]
    
    # CSRF (Cross-Site Request Forgery) detection patterns
    CSRF_INDICATORS = [
        r"csrf[_\-]?token",
        r"_token",
        r"authenticity[_\-]?token",
        r"csrfmiddlewaretoken",
        r"__RequestVerificationToken",
        r"form[_\-]?token",
        r"security[_\-]?token",
        r"anti[_\-]?csrf",
        r"state[_\-]?token",
        r"nonce",
        r"challenge",
        r"verification[_\-]?code"
    ]
    
    # Authentication bypass patterns (Enhanced)
    AUTH_BYPASS = [
        r"admin.*panel",
        r"privileged.*access",
        r"unauthorized.*admin",
        r"bypass.*authentication",
        r"administrator.*dashboard",
        r"root.*access",
        r"super.*user",
        r"elevated.*privileges",
        r"admin.*console",
        r"management.*interface"
    ]
    
    # Information disclosure patterns (Enhanced)
    INFO_DISCLOSURE = [
        r"stack trace",
        r"debug.*information",
        r"internal.*error",
        r"version.*information",
        r"database.*error",
        r"Exception.*at",
        r"Traceback.*most recent",
        r"Fatal error.*in",
        r"Warning.*in.*line",
        r"Notice.*in.*line",
        r"Call Stack:",
        r"Source File:",
        r"Line Number:",
        r"Error Type:",
        r"Server Error in",
        r"Application Error",
        r"System\.Exception",
        r"NullPointerException",
        r"ArrayIndexOutOfBounds",
        r"ClassNotFoundException"
    ]
    
    # Local File Inclusion (LFI) patterns
    LFI_INDICATORS = [
        r"include\s*\(",
        r"require\s*\(",
        r"include_once\s*\(",
        r"require_once\s*\(",
        r"Warning.*include",
        r"Warning.*require",
        r"failed to open stream",
        r"No such file or directory.*include",
        r"Permission denied.*include"
    ]
    
    # Remote File Inclusion (RFI) patterns
    RFI_INDICATORS = [
        r"allow_url_include",
        r"allow_url_fopen",
        r"Warning.*URL file-access",
        r"failed to open stream.*HTTP",
        r"getaddrinfo failed",
        r"Connection refused.*include"
    ]
    
    # XXE (XML External Entity) patterns
    XXE_INDICATORS = [
        r"<!DOCTYPE.*\[",
        r"<!ENTITY.*>",
        r"ENTITY.*SYSTEM",
        r"xml.*entity",
        r"SimpleXML.*Entity",
        r"libxml.*entity",
        r"Entity.*not defined"
    ]
    
    # Business Logic patterns
    BUSINESS_LOGIC = [
        r"negative.*price",
        r"invalid.*quantity",
        r"insufficient.*funds",
        r"credit.*limit.*exceeded",
        r"out.*of.*stock",
        r"inventory.*error",
        r"payment.*failed",
        r"transaction.*declined",
        r"order.*limit.*exceeded",
        r"discount.*invalid"
    ]
    
    # Timing Attack indicators
    TIMING_ATTACK = [
        r"sleep\s*\(",
        r"benchmark\s*\(",
        r"waitfor.*delay",
        r"pg_sleep\s*\(",
        r"dbms_pipe\.receive_message",
        r"setTimeout\s*\(",
        r"time\.sleep\s*\("
    ]
    
    # Open Redirect patterns
    OPEN_REDIRECT = [
        r"Location:\s*https?://",
        r"redirect.*url=https?://",
        r"Location:\s*/\/",
        r"window\.location.*=.*http",
        r"document\.location.*=.*http"
    ] 