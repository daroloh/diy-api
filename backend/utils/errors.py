from typing import Dict, Tuple
from datetime import datetime
import uuid

def get_error_details(code: int) -> Tuple[str, str, str]:
    """Get error title, message, and fix suggestions for HTTP status codes"""
    error_catalog = {
        400: (
            "Bad Request",
            "The request contains invalid syntax or cannot be fulfilled.",
            "Check your request body, query parameters, and ensure all required fields are present and properly formatted."
        ),
        401: (
            "Unauthorized", 
            "Authentication credentials are missing or invalid.",
            "Include a valid API key in the 'x-api-key' header or check your authentication token."
        ),
        403: (
            "Forbidden",
            "You don't have permission to access this resource.",
            "Verify your account has the necessary permissions or contact support to upgrade your access level."
        ),
        404: (
            "Not Found",
            "The requested endpoint or resource does not exist.",
            "Check the URL path and ensure you're calling the correct endpoint. Verify the resource ID exists."
        ),
        422: (
            "Unprocessable Entity",
            "The request body contains invalid or missing required fields.",
            "Validate your JSON payload against the API schema. Check field types and required properties."
        ),
        429: (
            "Too Many Requests",
            "Rate limit exceeded. You've sent too many requests in a given time period.",
            "Implement exponential backoff in your client. Check the 'Retry-After' header for the wait time."
        ),
        500: (
            "Internal Server Error",
            "An unexpected error occurred on the server side.",
            "This is likely a temporary issue. Try again in a few moments or contact support if it persists."
        ),
        502: (
            "Bad Gateway",
            "The server received an invalid response from an upstream server.",
            "This indicates a temporary server issue. Retry your request with exponential backoff."
        ),
        503: (
            "Service Unavailable",
            "The service is temporarily unavailable, often due to maintenance or overload.",
            "Wait a few minutes and try again. Check the service status page for maintenance announcements."
        ),
        504: (
            "Gateway Timeout",
            "The server didn't receive a response from an upstream server in time.",
            "Reduce request complexity or try again later. Consider implementing client-side timeouts."
        )
    }
    
    if code not in error_catalog:
        return (
            "Unknown Error",
            f"HTTP status code {code} was returned.",
            "Refer to HTTP status code documentation for this specific error."
        )
    
    return error_catalog[code]

def generate_request_id() -> str:
    """Generate a unique request ID for tracking"""
    return f"req_{uuid.uuid4().hex[:12]}"

def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.utcnow().isoformat() + "Z"