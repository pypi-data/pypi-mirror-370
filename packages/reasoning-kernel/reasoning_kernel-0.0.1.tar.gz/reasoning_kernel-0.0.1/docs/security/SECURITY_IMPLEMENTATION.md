# Security Implementation Guide

This document provides comprehensive security implementation guidance for the MSA Reasoning Kernel.

## 🛡️ Security Architecture Overview

The Reasoning Kernel implements defense-in-depth security with multiple layers:

1. **Input Validation Layer** - Sanitizes and validates all user inputs
2. **Authentication Layer** - Secure API key management and verification  
3. **Authorization Layer** - Role-based access control
4. **Transport Security** - HTTPS and secure headers
5. **Application Security** - Circuit breakers and rate limiting
6. **Data Security** - Encrypted credentials and secure storage

## 🚨 Critical Security Fixes Implemented

### 🔥 CRITICAL: Hardcoded Credentials Security Issue Resolved

**Issue**: Production API keys were previously exposed in configuration files.

**Resolution**: Implemented comprehensive credential management system:

1. ✅ **Removed all hardcoded credentials** from configuration files
2. ✅ **Created secure credential management** with bcrypt hashing
3. ✅ **Implemented .env.template system** with placeholders only
4. ✅ **Enhanced .gitignore** to prevent future credential exposure
5. ✅ **Added startup credential validation** for production deployments

**Secure Configuration Pattern**:

```bash
# .env.template (safe - contains only placeholders)
DAYTONA_API_KEY=your_daytona_api_key_here
AZURE_OPENAI_API_KEY=your_azure_openai_key_here
GOOGLE_AI_API_KEY=your_google_ai_key_here
REDIS_PASSWORD=your_secure_password_here
```

**Production Deployment**:

- All sensitive values loaded from secure environment variables
- API keys validated and hashed using bcrypt
- No plaintext credentials stored in code or configuration files

## 🔐 Security Components

### Credential Manager (`reasoning_kernel/security/credential_manager.py`)

Provides secure credential handling:

```python
from reasoning_kernel.security.credential_manager import (
    get_secure_config,
    hash_api_key_secure,
    verify_api_key_secure
)

# Load and validate configuration
config = get_secure_config()
print(f"Validation status: {config['validation']['valid']}")

# Secure API key hashing
api_key = "rk_EXAMPLE_KEY_FOR_DOCUMENTATION_ONLY"
hashed = hash_api_key_secure(api_key)
is_valid = verify_api_key_secure(api_key, hashed)
```

### Input Validation (`reasoning_kernel/models/requests.py`)

Enhanced request validation with security features:

```python
from reasoning_kernel.models.requests import MSAReasoningRequest
from pydantic import ValidationError

# Security validation automatically applied
try:
    request = MSAReasoningRequest(
        scenario="Analyze this <script>alert('xss')</script> scenario"
    )
    print("Request processed safely")
except ValidationError as e:
    print(f"Dangerous content blocked: {e}")
```

### Security Validation Tool (`tools/security_validator.py`)

Comprehensive security checking:

```bash
# Run security validation
python tools/security_validator.py

# Output:
🛡️  Reasoning Kernel Security Validation
✅ All required credentials are configured
✅ .env contains placeholder values (secure)
✅ .gitignore has security patterns
```

## 🔑 API Key Security

### Format Specification

- **Prefix**: `rk_` (reasoning kernel)
- **Length**: 35 characters total
- **Encoding**: Base64url safe characters
- **Pattern**: `^rk_[A-Za-z0-9_-]{32}$`

### Generation and Validation

```python
from reasoning_kernel.security.credential_manager import api_key_manager

# Generate secure API key
new_key = api_key_manager.generate_api_key()
print(f"Generated: {new_key}")

# Validate format
is_valid = api_key_manager.is_valid_format(new_key)
print(f"Valid format: {is_valid}")

# Secure hashing for storage (uses bcrypt)
hashed = api_key_manager.hash_api_key(new_key)
print(f"Hashed: {hashed[:20]}...")

# Verification
verified = api_key_manager.verify_api_key(new_key, hashed)
print(f"Verification: {verified}")
```

## 🛡️ Input Security

### Dangerous Pattern Detection

The system blocks these patterns:

- **Code Execution**: `eval()`, `exec()`, `__import__()`, `compile()`
- **File Access**: `open()`, `file()`, `input()`
- **System Access**: `os.`, `sys.`, `subprocess`
- **XSS Patterns**: `<script>`, `javascript:`, `vbscript:`
- **Template Injection**: `${}`, `{{}}`

### HTML Sanitization

All inputs are sanitized using a custom implementation:

```python
from reasoning_kernel.models.requests import sanitize_html_content

# Examples
sanitize_html_content("<script>alert(1)</script>Hello")  # Returns: "Hello"
sanitize_html_content("Safe <b>bold</b> text")  # Returns: "Safe &lt;b&gt;bold&lt;/b&gt; text"
```

### Context Validation

Nested object depth and structure validation:

```python
# Maximum context depth: 5 levels
valid_context = {
    "level1": {
        "level2": {
            "level3": {
                "level4": {
                    "level5": "allowed"
                }
            }
        }
    }
}

# This would be rejected (6+ levels)
invalid_context = {
    "level1": {
        "level2": {
            "level3": {
                "level4": {
                    "level5": {
                        "level6": "rejected"
                    }
                }
            }
        }
    }
}
```

## 🔍 Security Testing

### Test Coverage

Comprehensive test suite with 17 security scenarios:

```bash
# Run security validation tests
python -m pytest tests/test_security_validation.py -v

# Results:
✅ test_validate_no_dangerous_patterns_safe
✅ test_validate_no_dangerous_patterns_dangerous  
✅ test_sanitize_html_content
✅ test_validate_context_depth_valid
✅ test_validate_context_depth_too_deep
✅ test_valid_request
✅ test_scenario_too_short
✅ test_scenario_too_long
✅ test_scenario_dangerous_patterns
✅ test_invalid_session_id
✅ test_valid_session_id
✅ test_invalid_mode
✅ test_invalid_priority
✅ test_execution_time_too_low
✅ test_execution_time_too_high
✅ test_context_validation_safe
✅ test_context_validation_dangerous

17 passed in 0.09s
```

### Security Validation Script

Regular security checks:

```bash
python tools/security_validator.py
```

Example output:

```
🛡️  Reasoning Kernel Security Validation
============================================================
🔒 Security Configuration Validation
==================================================
✅ All required credentials are configured
ℹ️  Optional credentials not configured: ['ANTHROPIC_API_KEY']

📊 Configuration Summary:
   - Required credentials: 3/3 configured
   - Optional credentials: 3/4 configured

🔍 File Security Analysis
==============================
📄 Checking .env...
   ✅ .env contains placeholder values (secure)
   ✅ .gitignore has security patterns

🔑 API Key Security Tests
==============================
   ✅ rk_aaaaaaa...aaaaaaaaaa: Valid format
   ❌ sk_invalid_key: Invalid format
   ❌ rk_short: Invalid format
   ❌ : Invalid format
   ❌ rk_aaaaaaa...aaaaaaaaa!: Invalid format

🎯 Security Recommendations:
   1. Never commit .env files with real credentials
   2. Use environment variables in production
   3. Rotate API keys regularly
   4. Monitor for credential leaks
   5. Use proper API key hashing in production

✅ Security validation completed!
```

## 🚀 Production Security

### Environment Setup

```bash
# Production environment variables
export AZURE_OPENAI_API_KEY="prod-azure-key"
export DAYTONA_API_KEY="prod-daytona-key"
export REDIS_PASSWORD="secure-redis-password"
export API_KEY_SECRET="random-256-bit-secret"
export ENVIRONMENT="production"
export DEVELOPMENT="false"
export ALLOWED_ORIGINS="https://your-domain.com"
```

### Security Headers

HTTP security headers are automatically applied:

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY  
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
Content-Security-Policy: default-src 'self'
```

### Rate Limiting

Per-API-key rate limiting:

```python
# Configuration constants
MAX_CONCURRENT_REQUESTS_PER_KEY = 10
API_KEY_DEFAULT_EXPIRY_DAYS = 365
```

## 📊 Security Monitoring

### Logging Configuration

Security events are logged:

```python
import logging

logger = logging.getLogger("reasoning_kernel.security")

# Examples of security logging
logger.warning(f"Invalid API key attempt from {client_ip}")
logger.error(f"Dangerous pattern detected: {pattern_type}")
logger.info(f"Successful API key validation for {key_prefix}")
```

### Health Checks

Monitor security status via API endpoints:

```bash
# Basic health check
curl -H "X-API-Key: your-key" /health

# Security status
curl -H "X-API-Key: your-key" /security/status

# Circuit breaker status
curl -H "X-API-Key: your-key" /circuit-breakers
```

## 🎯 Security Best Practices

### Development Guidelines

1. **Never commit real credentials**
   - Use `.env.template` for examples
   - Keep `.env` in `.gitignore`
   - Use placeholder values in documentation

2. **Input validation**
   - Always validate user inputs
   - Use provided security functions
   - Test with malicious inputs

3. **API key management**
   - Use proper key format (`rk_`)
   - Hash keys before storage
   - Implement key rotation

4. **Testing**
   - Run security tests regularly
   - Use security validation script
   - Test edge cases and attack scenarios

### Production Deployment

1. **Environment variables only**
   - No credential files in production
   - Use secure key management systems
   - Implement proper access controls

2. **Monitoring and logging**
   - Log all security events
   - Monitor for suspicious patterns
   - Set up alerting for security issues

3. **Network security**
   - Use HTTPS only
   - Implement proper firewall rules
   - Consider VPN/private networks

4. **Dependency management**
   - Keep dependencies updated
   - Monitor for security advisories
   - Use dependency scanning tools

## 🔐 Constants and Configuration

Security constants are centralized in `reasoning_kernel/core/constants.py`:

```python
# API Key Security
API_KEY_LENGTH = 32
API_KEY_PREFIX_LENGTH = 8
MAX_API_KEYS_PER_USER = 10
API_KEY_DEFAULT_EXPIRY_DAYS = 365
PASSWORD_MIN_LENGTH = 12

# Input Validation
MAX_SCENARIO_LENGTH = 10000
MIN_SCENARIO_LENGTH = 10
MAX_CONTEXT_DEPTH = 5
MAX_CONTEXT_KEYS = 50
MAX_CONTEXT_KEY_LENGTH = 100

# Rate Limiting
MAX_CONCURRENT_REQUESTS_PER_KEY = 10
DEFAULT_RATE_LIMIT_PER_MINUTE = 60
DEFAULT_RATE_LIMIT_PER_HOUR = 1000

# Security Patterns
PATTERN_SESSION_ID = r"^[a-zA-Z0-9_-]+$"
PATTERN_API_KEY = r"^[a-zA-Z0-9_-]+$"
```

## 🚨 Incident Response

If a security issue is discovered:

1. **Immediate Actions**
   - Rotate affected credentials
   - Block suspicious API keys
   - Enable enhanced logging

2. **Investigation**
   - Review access logs
   - Identify scope of compromise
   - Document timeline

3. **Remediation**
   - Fix security vulnerability
   - Update security documentation
   - Enhance monitoring

4. **Prevention**
   - Implement additional controls
   - Update security procedures
   - Conduct security training

---

**Security Status**: ✅ **SECURE** - All critical vulnerabilities have been addressed with comprehensive security measures implemented.
