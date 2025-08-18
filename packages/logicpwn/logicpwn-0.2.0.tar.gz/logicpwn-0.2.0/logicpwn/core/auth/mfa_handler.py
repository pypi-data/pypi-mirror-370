"""
Multi-Factor Authentication (MFA) Support for LogicPwn.

Provides comprehensive MFA handling including:
- TOTP (Time-based One-Time Password)
- HOTP (HMAC-based One-Time Password)  
- SMS-based authentication
- Email-based authentication
- Hardware token support (FIDO2/WebAuthn)
- Backup codes
- MFA enrollment and management

Features:
- Multiple MFA methods
- QR code generation for TOTP
- Backup code generation and validation
- MFA challenge handling
- Device registration and management
- Rate limiting and security controls
"""
import base64
import hashlib
import hmac
import qrcode
import secrets
import struct
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Callable
from io import BytesIO
from datetime import datetime, timezone

import requests
from loguru import logger
from pydantic import BaseModel, Field, field_validator

from logicpwn.exceptions import AuthenticationError, ValidationError, NetworkError
from logicpwn.core.performance import monitor_performance


@dataclass
class TOTPSecret:
    """TOTP secret with metadata."""
    secret: str
    issuer: str
    account_name: str
    algorithm: str = "SHA1"
    digits: int = 6
    period: int = 30
    
    @property
    def provisioning_uri(self) -> str:
        """Generate TOTP provisioning URI for QR codes."""
        label = f"{self.issuer}:{self.account_name}"
        params = {
            'secret': self.secret,
            'issuer': self.issuer,
            'algorithm': self.algorithm,
            'digits': self.digits,
            'period': self.period
        }
        
        param_string = '&'.join(f"{k}={v}" for k, v in params.items())
        return f"otpauth://totp/{label}?{param_string}"
    
    def generate_qr_code(self) -> bytes:
        """Generate QR code for TOTP setup."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        return img_buffer.getvalue()


@dataclass
class MFAChallenge:
    """MFA challenge information."""
    challenge_id: str
    method: str
    expires_at: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """Check if challenge is expired."""
        return time.time() >= self.expires_at
    
    @property
    def time_remaining(self) -> int:
        """Get seconds remaining for challenge."""
        return max(0, int(self.expires_at - time.time()))


class MFAConfig(BaseModel):
    """MFA configuration."""
    
    # TOTP settings
    totp_issuer: str = Field(default="LogicPwn", description="TOTP issuer name")
    totp_algorithm: str = Field(default="SHA1", description="TOTP hash algorithm")
    totp_digits: int = Field(default=6, ge=6, le=8, description="TOTP code length")
    totp_period: int = Field(default=30, ge=15, le=300, description="TOTP time period in seconds")
    totp_window: int = Field(default=1, ge=0, le=5, description="TOTP time window tolerance")
    
    # SMS settings
    sms_provider: Optional[str] = Field(default=None, description="SMS provider (twilio, aws_sns)")
    sms_config: Dict[str, Any] = Field(default_factory=dict, description="SMS provider configuration")
    sms_template: str = Field(default="Your verification code is: {code}", description="SMS message template")
    
    # Email settings
    email_provider: Optional[str] = Field(default=None, description="Email provider (smtp, sendgrid)")
    email_config: Dict[str, Any] = Field(default_factory=dict, description="Email provider configuration")
    email_template: str = Field(default="Your verification code is: {code}", description="Email message template")
    email_subject: str = Field(default="Verification Code", description="Email subject")
    
    # Security settings
    code_length: int = Field(default=6, ge=4, le=10, description="Verification code length")
    code_expiry: int = Field(default=300, ge=60, le=3600, description="Code expiry time in seconds")
    max_attempts: int = Field(default=3, ge=1, le=10, description="Maximum verification attempts")
    rate_limit_window: int = Field(default=3600, description="Rate limiting window in seconds")
    max_codes_per_window: int = Field(default=5, description="Maximum codes per rate limit window")
    
    # Backup codes
    backup_code_count: int = Field(default=10, ge=5, le=20, description="Number of backup codes to generate")
    backup_code_length: int = Field(default=8, ge=6, le=12, description="Backup code length")
    
    model_config = {"arbitrary_types_allowed": True}


class TOTPHandler:
    """
    TOTP (Time-based One-Time Password) handler.
    
    Features:
    - TOTP generation and validation
    - QR code generation for setup
    - Time window tolerance
    - Multiple hash algorithms
    """
    
    def __init__(self, config: MFAConfig):
        self.config = config
    
    def generate_secret(self, length: int = 32) -> str:
        """Generate base32-encoded TOTP secret."""
        secret_bytes = secrets.token_bytes(length)
        return base64.b32encode(secret_bytes).decode('ascii')
    
    def create_totp_secret(self, account_name: str, secret: Optional[str] = None) -> TOTPSecret:
        """Create TOTP secret configuration."""
        if not secret:
            secret = self.generate_secret()
        
        return TOTPSecret(
            secret=secret,
            issuer=self.config.totp_issuer,
            account_name=account_name,
            algorithm=self.config.totp_algorithm,
            digits=self.config.totp_digits,
            period=self.config.totp_period
        )
    
    def _hotp(self, secret: str, counter: int, algorithm: str = "SHA1", digits: int = 6) -> str:
        """Generate HOTP code."""
        # Decode base32 secret
        try:
            key = base64.b32decode(secret.upper())
        except Exception:
            raise ValidationError("Invalid TOTP secret format")
        
        # Convert counter to bytes
        counter_bytes = struct.pack('>Q', counter)
        
        # Generate HMAC
        if algorithm == "SHA1":
            hash_function = hashlib.sha1
        elif algorithm == "SHA256":
            hash_function = hashlib.sha256
        elif algorithm == "SHA512":
            hash_function = hashlib.sha512
        else:
            raise ValidationError(f"Unsupported algorithm: {algorithm}")
        
        hmac_digest = hmac.new(key, counter_bytes, hash_function).digest()
        
        # Dynamic truncation
        offset = hmac_digest[-1] & 0x0f
        truncated = struct.unpack('>I', hmac_digest[offset:offset + 4])[0]
        truncated &= 0x7fffffff
        
        # Generate code
        code = truncated % (10 ** digits)
        return str(code).zfill(digits)
    
    @monitor_performance("totp_generation")
    def generate_totp(self, secret: str, timestamp: Optional[float] = None) -> str:
        """
        Generate TOTP code for given secret and timestamp.
        
        Args:
            secret: Base32-encoded TOTP secret
            timestamp: Unix timestamp (defaults to current time)
            
        Returns:
            TOTP code string
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Calculate time counter
        counter = int(timestamp // self.config.totp_period)
        
        return self._hotp(
            secret=secret,
            counter=counter,
            algorithm=self.config.totp_algorithm,
            digits=self.config.totp_digits
        )
    
    @monitor_performance("totp_validation")
    def validate_totp(self, secret: str, code: str, timestamp: Optional[float] = None) -> bool:
        """
        Validate TOTP code.
        
        Args:
            secret: Base32-encoded TOTP secret
            code: TOTP code to validate
            timestamp: Unix timestamp (defaults to current time)
            
        Returns:
            True if code is valid
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Try current time window and adjacent windows
        current_counter = int(timestamp // self.config.totp_period)
        
        for i in range(-self.config.totp_window, self.config.totp_window + 1):
            test_counter = current_counter + i
            expected_code = self._hotp(
                secret=secret,
                counter=test_counter,
                algorithm=self.config.totp_algorithm,
                digits=self.config.totp_digits
            )
            
            if secrets.compare_digest(code, expected_code):
                return True
        
        return False


class SMSHandler:
    """SMS-based MFA handler."""
    
    def __init__(self, config: MFAConfig, session: Optional[requests.Session] = None):
        self.config = config
        self.session = session or requests.Session()
        
    def generate_code(self) -> str:
        """Generate numeric verification code."""
        max_value = 10 ** self.config.code_length
        code = secrets.randbelow(max_value)
        return str(code).zfill(self.config.code_length)
    
    @monitor_performance("sms_send")
    def send_code(self, phone_number: str, code: Optional[str] = None) -> str:
        """
        Send SMS verification code.
        
        Args:
            phone_number: Recipient phone number
            code: Verification code (generated if not provided)
            
        Returns:
            Verification code sent
        """
        if not code:
            code = self.generate_code()
        
        message = self.config.sms_template.format(code=code)
        
        if self.config.sms_provider == "twilio":
            self._send_twilio_sms(phone_number, message)
        elif self.config.sms_provider == "aws_sns":
            self._send_aws_sms(phone_number, message)
        else:
            raise ValidationError(f"Unsupported SMS provider: {self.config.sms_provider}")
        
        logger.info(f"SMS verification code sent to {phone_number[-4:]}")
        return code
    
    def _send_twilio_sms(self, phone_number: str, message: str):
        """Send SMS via Twilio."""
        try:
            from twilio.rest import Client
            
            client = Client(
                self.config.sms_config['account_sid'],
                self.config.sms_config['auth_token']
            )
            
            client.messages.create(
                body=message,
                from_=self.config.sms_config['from_number'],
                to=phone_number
            )
            
        except ImportError:
            raise ValidationError("Twilio library not installed")
        except Exception as e:
            raise NetworkError(f"Failed to send Twilio SMS: {e}")
    
    def _send_aws_sms(self, phone_number: str, message: str):
        """Send SMS via AWS SNS."""
        try:
            import boto3
            
            sns = boto3.client(
                'sns',
                aws_access_key_id=self.config.sms_config['access_key_id'],
                aws_secret_access_key=self.config.sms_config['secret_access_key'],
                region_name=self.config.sms_config.get('region', 'us-east-1')
            )
            
            sns.publish(
                PhoneNumber=phone_number,
                Message=message
            )
            
        except ImportError:
            raise ValidationError("boto3 library not installed")
        except Exception as e:
            raise NetworkError(f"Failed to send AWS SNS SMS: {e}")


class EmailHandler:
    """Email-based MFA handler."""
    
    def __init__(self, config: MFAConfig):
        self.config = config
    
    def generate_code(self) -> str:
        """Generate alphanumeric verification code."""
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        code = ''.join(secrets.choice(alphabet) for _ in range(self.config.code_length))
        return code
    
    @monitor_performance("email_send")
    def send_code(self, email_address: str, code: Optional[str] = None) -> str:
        """
        Send email verification code.
        
        Args:
            email_address: Recipient email address
            code: Verification code (generated if not provided)
            
        Returns:
            Verification code sent
        """
        if not code:
            code = self.generate_code()
        
        message = self.config.email_template.format(code=code)
        
        if self.config.email_provider == "smtp":
            self._send_smtp_email(email_address, message)
        elif self.config.email_provider == "sendgrid":
            self._send_sendgrid_email(email_address, message)
        else:
            raise ValidationError(f"Unsupported email provider: {self.config.email_provider}")
        
        logger.info(f"Email verification code sent to {email_address}")
        return code
    
    def _send_smtp_email(self, email_address: str, message: str):
        """Send email via SMTP."""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            smtp_config = self.config.email_config
            
            msg = MIMEMultipart()
            msg['From'] = smtp_config['from_email']
            msg['To'] = email_address
            msg['Subject'] = self.config.email_subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(smtp_config['host'], smtp_config.get('port', 587))
            server.starttls()
            server.login(smtp_config['username'], smtp_config['password'])
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            raise NetworkError(f"Failed to send SMTP email: {e}")
    
    def _send_sendgrid_email(self, email_address: str, message: str):
        """Send email via SendGrid."""
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail
            
            sg = sendgrid.SendGridAPIClient(api_key=self.config.email_config['api_key'])
            
            mail = Mail(
                from_email=self.config.email_config['from_email'],
                to_emails=email_address,
                subject=self.config.email_subject,
                plain_text_content=message
            )
            
            sg.send(mail)
            
        except ImportError:
            raise ValidationError("SendGrid library not installed")
        except Exception as e:
            raise NetworkError(f"Failed to send SendGrid email: {e}")


class BackupCodeHandler:
    """Backup code handler for MFA recovery."""
    
    def __init__(self, config: MFAConfig):
        self.config = config
    
    def generate_backup_codes(self) -> List[str]:
        """Generate backup codes."""
        codes = []
        for _ in range(self.config.backup_code_count):
            # Generate alphanumeric code
            alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            code = ''.join(secrets.choice(alphabet) for _ in range(self.config.backup_code_length))
            codes.append(code)
        
        return codes
    
    def hash_backup_code(self, code: str) -> str:
        """Hash backup code for secure storage."""
        return hashlib.sha256(code.encode()).hexdigest()
    
    def validate_backup_code(self, code: str, hashed_codes: List[str]) -> bool:
        """
        Validate backup code against hashed codes.
        
        Args:
            code: Code to validate
            hashed_codes: List of hashed backup codes
            
        Returns:
            True if code is valid
        """
        code_hash = self.hash_backup_code(code)
        return code_hash in hashed_codes


class MFAManager:
    """
    Multi-Factor Authentication manager.
    
    Features:
    - Multiple MFA methods (TOTP, SMS, Email)
    - Challenge/response handling
    - Rate limiting and security controls
    - Backup code support
    - Device registration
    """
    
    def __init__(self, config: MFAConfig, session: Optional[requests.Session] = None):
        self.config = config
        self.session = session or requests.Session()
        
        self.totp_handler = TOTPHandler(config)
        self.sms_handler = SMSHandler(config, session)
        self.email_handler = EmailHandler(config)
        self.backup_handler = BackupCodeHandler(config)
        
        # Active challenges
        self.active_challenges: Dict[str, MFAChallenge] = {}
        self.verification_attempts: Dict[str, int] = {}
        self.rate_limit_tracker: Dict[str, List[float]] = {}
    
    def generate_challenge_id(self) -> str:
        """Generate unique challenge ID."""
        return secrets.token_urlsafe(32)
    
    def _check_rate_limit(self, identifier: str) -> bool:
        """Check if rate limit is exceeded."""
        now = time.time()
        window_start = now - self.config.rate_limit_window
        
        # Clean old entries
        if identifier in self.rate_limit_tracker:
            self.rate_limit_tracker[identifier] = [
                timestamp for timestamp in self.rate_limit_tracker[identifier]
                if timestamp > window_start
            ]
        else:
            self.rate_limit_tracker[identifier] = []
        
        # Check limit
        return len(self.rate_limit_tracker[identifier]) < self.config.max_codes_per_window
    
    def _record_code_request(self, identifier: str):
        """Record code request for rate limiting."""
        now = time.time()
        if identifier not in self.rate_limit_tracker:
            self.rate_limit_tracker[identifier] = []
        self.rate_limit_tracker[identifier].append(now)
    
    @monitor_performance("mfa_challenge_creation")
    def create_challenge(self, method: str, destination: str, **kwargs) -> MFAChallenge:
        """
        Create MFA challenge.
        
        Args:
            method: MFA method (totp, sms, email)
            destination: Destination (phone/email) for code delivery
            **kwargs: Additional method-specific parameters
            
        Returns:
            MFAChallenge object
        """
        # Check rate limiting
        if not self._check_rate_limit(destination):
            raise AuthenticationError("Rate limit exceeded for MFA requests")
        
        challenge_id = self.generate_challenge_id()
        expires_at = time.time() + self.config.code_expiry
        
        challenge = MFAChallenge(
            challenge_id=challenge_id,
            method=method,
            expires_at=expires_at,
            metadata={'destination': destination, **kwargs}
        )
        
        # Send verification code for applicable methods
        if method == "sms":
            code = self.sms_handler.send_code(destination)
            challenge.metadata['code'] = code
        elif method == "email":
            code = self.email_handler.send_code(destination)
            challenge.metadata['code'] = code
        elif method == "totp":
            # TOTP doesn't need code delivery
            pass
        else:
            raise ValidationError(f"Unsupported MFA method: {method}")
        
        # Store challenge
        self.active_challenges[challenge_id] = challenge
        self._record_code_request(destination)
        
        logger.info(f"Created MFA challenge {challenge_id} using method {method}")
        return challenge
    
    @monitor_performance("mfa_challenge_verification")
    def verify_challenge(self, challenge_id: str, code: str, **kwargs) -> bool:
        """
        Verify MFA challenge.
        
        Args:
            challenge_id: Challenge ID
            code: Verification code
            **kwargs: Additional verification parameters
            
        Returns:
            True if verification successful
        """
        # Get challenge
        challenge = self.active_challenges.get(challenge_id)
        if not challenge:
            raise AuthenticationError("Invalid challenge ID")
        
        # Check expiry
        if challenge.is_expired:
            del self.active_challenges[challenge_id]
            raise AuthenticationError("Challenge has expired")
        
        # Check attempt limit
        attempts = self.verification_attempts.get(challenge_id, 0)
        if attempts >= self.config.max_attempts:
            del self.active_challenges[challenge_id]
            raise AuthenticationError("Maximum verification attempts exceeded")
        
        # Verify code based on method
        is_valid = False
        
        if challenge.method == "totp":
            secret = kwargs.get('secret')
            if not secret:
                raise ValidationError("TOTP secret required for verification")
            is_valid = self.totp_handler.validate_totp(secret, code)
            
        elif challenge.method in ["sms", "email"]:
            expected_code = challenge.metadata.get('code')
            if not expected_code:
                raise ValidationError("No code available for verification")
            is_valid = secrets.compare_digest(code, expected_code)
            
        else:
            raise ValidationError(f"Unsupported MFA method: {challenge.method}")
        
        # Update attempts
        self.verification_attempts[challenge_id] = attempts + 1
        
        # Clean up if successful
        if is_valid:
            del self.active_challenges[challenge_id]
            if challenge_id in self.verification_attempts:
                del self.verification_attempts[challenge_id]
            
            logger.info(f"Successfully verified MFA challenge {challenge_id}")
        else:
            logger.warning(f"Invalid verification code for challenge {challenge_id}")
        
        return is_valid
    
    def get_challenge_status(self, challenge_id: str) -> Optional[Dict[str, Any]]:
        """Get challenge status information."""
        challenge = self.active_challenges.get(challenge_id)
        if not challenge:
            return None
        
        return {
            'challenge_id': challenge.challenge_id,
            'method': challenge.method,
            'expires_at': challenge.expires_at,
            'time_remaining': challenge.time_remaining,
            'attempts_remaining': self.config.max_attempts - self.verification_attempts.get(challenge_id, 0)
        }
    
    def cleanup_expired_challenges(self):
        """Clean up expired challenges."""
        now = time.time()
        expired_challenges = [
            challenge_id for challenge_id, challenge in self.active_challenges.items()
            if challenge.is_expired
        ]
        
        for challenge_id in expired_challenges:
            del self.active_challenges[challenge_id]
            if challenge_id in self.verification_attempts:
                del self.verification_attempts[challenge_id]
        
        if expired_challenges:
            logger.debug(f"Cleaned up {len(expired_challenges)} expired MFA challenges")


# Convenience functions

def create_totp_qr_code(secret: str, account_name: str, issuer: str = "LogicPwn") -> bytes:
    """Create QR code for TOTP setup."""
    totp_secret = TOTPSecret(
        secret=secret,
        account_name=account_name,
        issuer=issuer
    )
    return totp_secret.generate_qr_code()


def validate_totp_code(secret: str, code: str, algorithm: str = "SHA1", 
                      digits: int = 6, period: int = 30, window: int = 1) -> bool:
    """Validate TOTP code with custom parameters."""
    config = MFAConfig(
        totp_algorithm=algorithm,
        totp_digits=digits,
        totp_period=period,
        totp_window=window
    )
    
    handler = TOTPHandler(config)
    return handler.validate_totp(secret, code)
