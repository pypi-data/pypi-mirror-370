"""
Standalone Example Implementation

This module provides a complete example of how to implement the MCP Security Framework
in a standalone application, including all abstract method implementations.

The example demonstrates:
- Standalone application with security framework
- Real-world authentication and authorization
- Rate limiting implementation
- Certificate-based authentication
- Production-ready security features
- Comprehensive error handling

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from mcp_security_framework.core.security_manager import SecurityManager
from mcp_security_framework.core.auth_manager import AuthManager
from mcp_security_framework.core.ssl_manager import SSLManager
from mcp_security_framework.core.permission_manager import PermissionManager
from mcp_security_framework.core.rate_limiter import RateLimiter
from mcp_security_framework.schemas.config import SecurityConfig, AuthConfig, SSLConfig
from mcp_security_framework.schemas.models import AuthResult, AuthStatus, AuthMethod
from mcp_security_framework.constants import (
    DEFAULT_CLIENT_IP, DEFAULT_SECURITY_HEADERS, AUTH_METHODS,
    ErrorCodes, HTTP_UNAUTHORIZED, HTTP_FORBIDDEN, HTTP_TOO_MANY_REQUESTS
)


class StandaloneExample:
    """
    Complete Standalone Example with Security Framework Implementation
    
    This class demonstrates a production-ready standalone application
    with comprehensive security features including:
    - Multi-method authentication (API Key, JWT, Certificate)
    - Role-based access control
    - Rate limiting with Redis backend
    - SSL/TLS configuration
    - Comprehensive logging and monitoring
    - Command-line interface
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize standalone example with security configuration.
        
        Args:
            config_path: Path to security configuration file
        """
        self.config = self._load_config(config_path)
        self.security_manager = SecurityManager(self.config)
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
    
    def _load_config(self, config_path: Optional[str]) -> SecurityConfig:
        """
        Load security configuration from file or create default.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            SecurityConfig: Loaded configuration
        """
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            return SecurityConfig(**config_data)
        
        # Create production-ready default configuration
        return SecurityConfig(
            auth=AuthConfig(
                enabled=True,
                methods=[AUTH_METHODS["API_KEY"], AUTH_METHODS["JWT"], AUTH_METHODS["CERTIFICATE"]],
                api_keys={
                    "admin_key_123": {"username": "admin", "roles": ["admin", "user"]},
                    "user_key_456": {"username": "user", "roles": ["user"]},
                    "readonly_key_789": {"username": "readonly", "roles": ["readonly"]}
                },
                jwt_secret="your-super-secret-jwt-key-change-in-production",
                jwt_algorithm="HS256",
                jwt_expiry_hours=24,
                public_paths=["/health", "/metrics"],
                security_headers=DEFAULT_SECURITY_HEADERS
            ),
            ssl=SSLConfig(
                enabled=True,
                cert_file="certs/server.crt",
                key_file="certs/server.key",
                ca_cert_file="certs/ca.crt",
                verify_mode="CERT_REQUIRED",
                min_version="TLSv1.2"
            ),
            rate_limit={
                "enabled": True,
                "default_requests_per_minute": 60,
                "default_requests_per_hour": 1000,
                "burst_limit": 2,
                "window_size_seconds": 60,
                "storage_backend": "redis",
                "redis_config": {
                    "host": "localhost",
                    "port": 6379,
                    "db": 0,
                    "password": None
                },
                "exempt_paths": ["/health", "/metrics"],
                "exempt_roles": ["admin"]
            },
            permissions={
                "enabled": True,
                "roles_file": "config/roles.json",
                "default_role": "user",
                "hierarchy_enabled": True
            },
            logging={
                "enabled": True,
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_path": "logs/security.log",
                "max_file_size": 10,
                "backup_count": 5,
                "console_output": True,
                "json_format": False
            }
        )
    
    def _setup_logging(self):
        """Setup logging configuration."""
        if self.config.logging.enabled:
            logging.basicConfig(
                level=getattr(logging, self.config.logging.level),
                format=self.config.logging.format,
                handlers=[
                    logging.FileHandler(self.config.logging.file_path) if self.config.logging.file_path else logging.NullHandler(),
                    logging.StreamHandler() if self.config.logging.console_output else logging.NullHandler()
                ]
            )
    
    def authenticate_user(self, credentials: Dict[str, Any]) -> AuthResult:
        """
        Authenticate user with provided credentials.
        
        Args:
            credentials: User credentials (api_key, jwt_token, or certificate)
            
        Returns:
            AuthResult: Authentication result
        """
        try:
            if "api_key" in credentials:
                return self.security_manager.auth_manager.authenticate_api_key(credentials["api_key"])
            elif "jwt_token" in credentials:
                return self.security_manager.auth_manager.authenticate_jwt_token(credentials["jwt_token"])
            elif "certificate" in credentials:
                return self.security_manager.auth_manager.authenticate_certificate(credentials["certificate"])
            else:
                return AuthResult(
                    is_valid=False,
                    status=AuthStatus.FAILED,
                    username=None,
                    roles=[],
                    auth_method=None,
                    error_code=ErrorCodes.AUTHENTICATION_ERROR,
                    error_message="No valid credentials provided"
                )
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            return AuthResult(
                is_valid=False,
                status=AuthStatus.FAILED,
                username=None,
                roles=[],
                auth_method=None,
                error_code=ErrorCodes.AUTHENTICATION_ERROR,
                error_message=str(e)
            )
    
    def check_permissions(self, user_roles: List[str], required_permissions: List[str]) -> bool:
        """
        Check if user has required permissions.
        
        Args:
            user_roles: User roles
            required_permissions: Required permissions
            
        Returns:
            bool: True if user has required permissions
        """
        try:
            return self.security_manager.permission_manager.validate_access(
                user_roles, required_permissions
            )
        except Exception as e:
            self.logger.error(f"Permission check failed: {str(e)}")
            return False
    
    def check_rate_limit(self, identifier: str) -> bool:
        """
        Check if request is within rate limits.
        
        Args:
            identifier: Request identifier (IP, user ID, etc.)
            
        Returns:
            bool: True if request is within rate limits
        """
        try:
            return self.security_manager.rate_limiter.check_rate_limit(identifier)
        except Exception as e:
            self.logger.error(f"Rate limit check failed: {str(e)}")
            return True  # Allow request if rate limiting fails
    
    def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a secure request with full security validation.
        
        Args:
            request_data: Request data including credentials and action
            
        Returns:
            Dict[str, Any]: Response data
        """
        try:
            # Extract request components
            credentials = request_data.get("credentials", {})
            action = request_data.get("action", "")
            resource = request_data.get("resource", "")
            identifier = request_data.get("identifier", DEFAULT_CLIENT_IP)
            
            # Step 1: Rate limiting check
            if not self.check_rate_limit(identifier):
                return {
                    "success": False,
                    "error": "Rate limit exceeded",
                    "error_code": ErrorCodes.RATE_LIMIT_EXCEEDED_ERROR,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Step 2: Authentication
            auth_result = self.authenticate_user(credentials)
            if not auth_result.is_valid:
                return {
                    "success": False,
                    "error": "Authentication failed",
                    "error_code": auth_result.error_code,
                    "error_message": auth_result.error_message,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Step 3: Authorization
            required_permissions = self._get_required_permissions(action, resource)
            if not self.check_permissions(auth_result.roles, required_permissions):
                return {
                    "success": False,
                    "error": "Insufficient permissions",
                    "error_code": ErrorCodes.PERMISSION_DENIED_ERROR,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Step 4: Process the action
            result = self._execute_action(action, resource, request_data.get("data", {}))
            
            # Step 5: Log security event
            self._log_security_event("request_processed", {
                "username": auth_result.username,
                "action": action,
                "resource": resource,
                "success": True,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return {
                "success": True,
                "data": result,
                "user": {
                    "username": auth_result.username,
                    "roles": auth_result.roles,
                    "auth_method": auth_result.auth_method
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Request processing failed: {str(e)}")
            return {
                "success": False,
                "error": "Internal server error",
                "error_code": ErrorCodes.GENERAL_ERROR,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _get_required_permissions(self, action: str, resource: str) -> List[str]:
        """
        Get required permissions for action and resource.
        
        Args:
            action: Action to perform
            resource: Resource to access
            
        Returns:
            List[str]: Required permissions
        """
        # Define permission mappings
        permission_mappings = {
            "read": ["read"],
            "write": ["read", "write"],
            "delete": ["read", "write", "delete"],
            "admin": ["admin"],
            "create": ["read", "write"],
            "update": ["read", "write"]
        }
        
        return permission_mappings.get(action, ["read"])
    
    def _execute_action(self, action: str, resource: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the requested action.
        
        Args:
            action: Action to perform
            resource: Resource to access
            data: Action data
            
        Returns:
            Dict[str, Any]: Action result
        """
        # Simulate different actions
        if action == "read":
            return {"resource": resource, "data": {"example": "data"}}
        elif action == "write":
            return {"resource": resource, "data": data, "status": "written"}
        elif action == "delete":
            return {"resource": resource, "status": "deleted"}
        elif action == "create":
            return {"resource": resource, "data": data, "status": "created"}
        elif action == "update":
            return {"resource": resource, "data": data, "status": "updated"}
        else:
            return {"error": f"Unknown action: {action}"}
    
    def _log_security_event(self, event_type: str, details: Dict[str, Any]):
        """
        Log security event.
        
        Args:
            event_type: Type of security event
            details: Event details
        """
        try:
            self.logger.info(
                f"Security event: {event_type}",
                extra={
                    "event_type": event_type,
                    "timestamp": details.get("timestamp"),
                    "username": details.get("username"),
                    "action": details.get("action"),
                    "resource": details.get("resource"),
                    "success": details.get("success"),
                    **details
                }
            )
        except Exception as e:
            self.logger.error(f"Failed to log security event: {str(e)}")
    
    def generate_api_key(self, username: str, roles: List[str]) -> str:
        """
        Generate API key for user.
        
        Args:
            username: Username
            roles: User roles
            
        Returns:
            str: Generated API key
        """
        try:
            api_key = self.security_manager.auth_manager.generate_api_key()
            # Store the API key (in production, this would be in a database)
            self.config.auth.api_keys[api_key] = {
                "username": username,
                "roles": roles
            }
            return api_key
        except Exception as e:
            self.logger.error(f"Failed to generate API key: {str(e)}")
            raise
    
    def create_jwt_token(self, username: str, roles: List[str], expiry_hours: int = 24) -> str:
        """
        Create JWT token for user.
        
        Args:
            username: Username
            roles: User roles
            expiry_hours: Token expiry in hours
            
        Returns:
            str: Generated JWT token
        """
        try:
            user_data = {
                "username": username,
                "roles": roles,
                "exp": datetime.utcnow() + timedelta(hours=expiry_hours)
            }
            return self.security_manager.auth_manager.create_jwt_token(user_data)
        except Exception as e:
            self.logger.error(f"Failed to create JWT token: {str(e)}")
            raise
    
    def validate_certificate(self, certificate_path: str) -> bool:
        """
        Validate certificate.
        
        Args:
            certificate_path: Path to certificate file
            
        Returns:
            bool: True if certificate is valid
        """
        try:
            return self.security_manager.ssl_manager.validate_certificate(certificate_path)
        except Exception as e:
            self.logger.error(f"Certificate validation failed: {str(e)}")
            return False
    
    def get_security_status(self) -> Dict[str, Any]:
        """
        Get security framework status.
        
        Returns:
            Dict[str, Any]: Security status information
        """
        return {
            "ssl_enabled": self.config.ssl.enabled,
            "auth_enabled": self.config.auth.enabled,
            "rate_limiting_enabled": self.config.rate_limit.enabled,
            "permissions_enabled": self.config.permissions.enabled,
            "logging_enabled": self.config.logging.enabled,
            "auth_methods": self.config.auth.methods,
            "timestamp": datetime.utcnow().isoformat()
        }


# Example usage and testing
class StandaloneExampleTest:
    """Test class for standalone example functionality."""
    
    @staticmethod
    def test_authentication():
        """Test authentication functionality."""
        example = StandaloneExample()
        
        # Test API key authentication
        credentials = {"api_key": "admin_key_123"}
        auth_result = example.authenticate_user(credentials)
        assert auth_result.is_valid
        assert auth_result.username == "admin"
        assert "admin" in auth_result.roles
        
        print("✅ API Key authentication test passed")
    
    @staticmethod
    def test_permissions():
        """Test permission checking."""
        example = StandaloneExample()
        
        # Test admin permissions
        admin_roles = ["admin"]
        user_roles = ["user"]
        readonly_roles = ["readonly"]
        
        # Admin should have all permissions
        assert example.check_permissions(admin_roles, ["read", "write", "delete"])
        
        # User should have read and write permissions
        assert example.check_permissions(user_roles, ["read", "write"])
        
        # Readonly should only have read permission
        assert example.check_permissions(readonly_roles, ["read"])
        assert not example.check_permissions(readonly_roles, ["write"])
        
        print("✅ Permission checking test passed")
    
    @staticmethod
    def test_rate_limiting():
        """Test rate limiting functionality."""
        example = StandaloneExample()
        
        # Test rate limiting
        identifier = "test_user"
        for i in range(5):
            is_allowed = example.check_rate_limit(identifier)
            print(f"Request {i+1}: {'Allowed' if is_allowed else 'Blocked'}")
        
        print("✅ Rate limiting test completed")
    
    @staticmethod
    def test_request_processing():
        """Test complete request processing."""
        example = StandaloneExample()
        
        # Test successful request
        request_data = {
            "credentials": {"api_key": "admin_key_123"},
            "action": "read",
            "resource": "data",
            "identifier": "test_user"
        }
        
        result = example.process_request(request_data)
        assert result["success"]
        assert "data" in result
        
        print("✅ Request processing test passed")
    
    @staticmethod
    def test_api_key_generation():
        """Test API key generation."""
        example = StandaloneExample()
        
        api_key = example.generate_api_key("test_user", ["user"])
        assert len(api_key) > 0
        
        # Test the generated key
        credentials = {"api_key": api_key}
        auth_result = example.authenticate_user(credentials)
        assert auth_result.is_valid
        assert auth_result.username == "test_user"
        
        print("✅ API key generation test passed")


if __name__ == "__main__":
    # Run tests
    print("Running Standalone Example Tests...")
    StandaloneExampleTest.test_authentication()
    StandaloneExampleTest.test_permissions()
    StandaloneExampleTest.test_rate_limiting()
    StandaloneExampleTest.test_request_processing()
    StandaloneExampleTest.test_api_key_generation()
    
    # Example usage
    print("\nExample Usage:")
    example = StandaloneExample()
    
    # Generate API key for new user
    api_key = example.generate_api_key("new_user", ["user"])
    print(f"Generated API key: {api_key}")
    
    # Process a request
    request_data = {
        "credentials": {"api_key": api_key},
        "action": "read",
        "resource": "user_data",
        "identifier": "192.168.1.100"
    }
    
    result = example.process_request(request_data)
    print(f"Request result: {result}")
    
    # Get security status
    status = example.get_security_status()
    print(f"Security status: {status}")
