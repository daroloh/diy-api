from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse, PlainTextResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
import random
import asyncio
from datetime import datetime
from utils.errors import get_error_details, generate_request_id, get_current_timestamp
from schemas import ErrorResponse, SlowResponse, RateLimitResponse

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/simulate", tags=["API Failure Simulations"])

# In-memory storage for rate limiting (use Redis in production)
request_counts = {}

@router.get("/status", 
           summary="Simulate HTTP Status Codes",
           description="Returns any HTTP status code with detailed error information and debugging tips.")
def simulate_status(code: int = 400, include_headers: bool = True):
    """
    Simulate various HTTP status codes for testing error handling.
    
    - **code**: HTTP status code to return (400, 401, 403, 404, 422, 429, 500, 502, 503, 504)
    - **include_headers**: Include debugging headers in response
    """
    if code < 200 or code > 599:
        raise HTTPException(400, "Status code must be between 200-599")
    
    title, message, fix = get_error_details(code)
    
    response_data = {
        "error": title,
        "code": code,
        "message": message,
        "fix": fix,
        "timestamp": get_current_timestamp(),
        "request_id": generate_request_id(),
        "debug_info": {
            "endpoint": "/simulate/status",
            "parameters": {"code": code, "include_headers": include_headers},
            "common_causes": get_common_causes(code)
        }
    }
    
    headers = {}
    if include_headers:
        headers.update({
            "x-debug-mode": "true",
            "x-request-id": response_data["request_id"],
            "x-error-type": title.lower().replace(" ", "_")
        })
        
        # Add specific headers for certain error types
        if code == 429:
            headers["retry-after"] = "60"
            headers["x-ratelimit-limit"] = "100"
            headers["x-ratelimit-remaining"] = "0"
        elif code == 401:
            headers["www-authenticate"] = "Bearer"
    
    return JSONResponse(
        status_code=code,
        content=response_data,
        headers=headers
    )

@router.get("/invalid-json",
           summary="Return Malformed JSON",
           description="Returns intentionally broken JSON to test JSON parsing error handling.")
def simulate_invalid_json(error_type: str = "missing_comma"):
    """
    Simulate various types of invalid JSON responses.
    
    - **error_type**: Type of JSON error (missing_comma, unclosed_brace, invalid_escape, trailing_comma)
    """
    json_errors = {
        "missing_comma": '{"status": "error" "message": "Missing comma between properties"}',
        "unclosed_brace": '{"status": "error", "message": "Unclosed brace"',
        "invalid_escape": '{"status": "error", "message": "Invalid escape \\q sequence"}',
        "trailing_comma": '{"status": "error", "message": "Trailing comma",}',
        "unquoted_key": '{status: "error", "message": "Unquoted key"}',
        "single_quotes": "{'status': 'error', 'message': 'Single quotes instead of double'}"
    }
    
    if error_type not in json_errors:
        error_type = "missing_comma"
    
    headers = {
        "content-type": "application/json",
        "x-debug-mode": "true",
        "x-json-error-type": error_type,
        "x-expected-error": "JSON parse error"
    }
    
    return PlainTextResponse(
        json_errors[error_type], 
        status_code=200,
        headers=headers
    )

@router.get("/slow",
           summary="Simulate Slow Response",
           description="Intentionally delay response to test timeout handling and loading states.")
async def simulate_slow(seconds: int = 5, jitter: bool = False):
    """
    Simulate slow API responses for timeout testing.
    
    - **seconds**: Delay in seconds (max 30)
    - **jitter**: Add random jitter to delay time
    """
    if seconds > 30:
        raise HTTPException(400, "Maximum delay is 30 seconds")
    
    actual_delay = seconds
    if jitter:
        actual_delay = seconds + random.uniform(-1, 2)
        actual_delay = max(0.1, actual_delay)  # Ensure positive delay
    
    start_time = time.time()
    await asyncio.sleep(actual_delay)
    end_time = time.time()
    
    return {
        "status": "success",
        "message": f"Response delayed for {actual_delay:.2f} seconds",
        "delay_seconds": actual_delay,
        "requested_delay": seconds,
        "actual_elapsed": round(end_time - start_time, 2),
        "jitter_applied": jitter,
        "timestamp": get_current_timestamp(),
        "debug_info": {
            "use_case": "Test client timeout handling and loading states",
            "tip": "Implement progressive timeout values: connection timeout (5s), read timeout (30s)"
        }
    }

@router.get("/timeout",
           summary="Simulate Request Timeout", 
           description="Never returns a response to test client timeout handling.")
async def simulate_timeout(hang_time: int = 60):
    """
    Simulate a request that never completes (hangs forever).
    Client must implement timeout to handle this.
    
    - **hang_time**: How long to hang before timing out (max 120 seconds)
    """
    hang_time = min(hang_time, 120)  # Cap at 2 minutes for server resources
    
    # This will hang until the client times out or server kills the connection
    await asyncio.sleep(hang_time)
    
    # This should rarely be reached due to client/server timeouts
    return {
        "status": "timeout_expired",
        "message": f"Request hung for {hang_time} seconds",
        "tip": "If you see this response, your client timeout is longer than {hang_time}s"
    }

@router.get("/rate-limit",
           summary="Simulate Rate Limiting",
           description="Enforce rate limits and return 429 responses after limit exceeded.")
def simulate_rate_limit(
    request: Request,
    limit: int = 3, 
    window: int = 60,
    reset_counts: bool = False
):
    """
    Simulate rate limiting with configurable limits.
    
    - **limit**: Number of requests allowed per window
    - **window**: Time window in seconds  
    - **reset_counts**: Reset the rate limit counter for this IP
    """
    client_ip = get_remote_address(request)
    current_time = time.time()
    
    # Reset counts if requested
    if reset_counts:
        request_counts.pop(client_ip, None)
        return {
            "status": "reset",
            "message": f"Rate limit counter reset for {client_ip}",
            "limit": limit,
            "window": window
        }
    
    # Initialize or get existing count data
    if client_ip not in request_counts:
        request_counts[client_ip] = {"count": 0, "window_start": current_time}
    
    count_data = request_counts[client_ip]
    
    # Reset window if expired
    if current_time - count_data["window_start"] > window:
        count_data["count"] = 0
        count_data["window_start"] = current_time
    
    # Check if limit exceeded
    if count_data["count"] >= limit:
        time_remaining = window - (current_time - count_data["window_start"])
        
        headers = {
            "retry-after": str(int(time_remaining) + 1),
            "x-ratelimit-limit": str(limit),
            "x-ratelimit-remaining": "0",
            "x-ratelimit-reset": str(int(count_data["window_start"] + window)),
            "x-debug-mode": "true"
        }
        
        response_data = {
            "error": "Too Many Requests",
            "code": 429,
            "message": f"Rate limit of {limit} requests per {window} seconds exceeded",
            "retry_after": int(time_remaining) + 1,
            "limit": limit,
            "remaining": 0,
            "window": window,
            "debug_info": {
                "current_count": count_data["count"],
                "window_start": count_data["window_start"],
                "client_ip": client_ip,
                "tip": "Implement exponential backoff: wait 1s, then 2s, then 4s, etc."
            }
        }
        
        return JSONResponse(
            status_code=429,
            content=response_data,
            headers=headers
        )
    
    # Increment count and return success
    count_data["count"] += 1
    remaining = limit - count_data["count"]
    
    headers = {
        "x-ratelimit-limit": str(limit),
        "x-ratelimit-remaining": str(remaining),
        "x-ratelimit-reset": str(int(count_data["window_start"] + window))
    }
    
    return JSONResponse(
        content={
            "status": "success",
            "message": "Request processed successfully",
            "rate_limit_info": {
                "limit": limit,
                "remaining": remaining,
                "window": window,
                "current_count": count_data["count"]
            }
        },
        headers=headers
    )

@router.get("/random",
           summary="Random API Failure",
           description="Returns a random error response to simulate unpredictable API behavior.")
def simulate_random(exclude_codes: str = ""):
    """
    Simulate random API failures for chaos testing.
    
    - **exclude_codes**: Comma-separated list of status codes to exclude (e.g., "500,503")
    """
    possible_codes = [400, 401, 403, 404, 422, 429, 500, 502, 503, 504]
    
    # Remove excluded codes
    if exclude_codes:
        try:
            excluded = [int(code.strip()) for code in exclude_codes.split(",")]
            possible_codes = [code for code in possible_codes if code not in excluded]
        except ValueError:
            pass  # Ignore invalid exclude_codes format
    
    if not possible_codes:
        possible_codes = [500]  # Fallback
    
    random_code = random.choice(possible_codes)
    
    # Add some randomness to response time
    if random.random() < 0.3:  # 30% chance of slow response
        time.sleep(random.uniform(0.5, 2.0))
    
    return simulate_status(random_code, include_headers=True)

@router.get("/network-error",
           summary="Simulate Network Issues",
           description="Simulate various network-level problems.")
async def simulate_network_error(error_type: str = "connection_reset"):
    """
    Simulate network-level errors.
    
    - **error_type**: Type of network error (connection_reset, dns_failure, ssl_error)
    """
    if error_type == "connection_reset":
        # Abruptly close connection (simulate connection reset)
        raise HTTPException(500, "Connection reset by peer")
    elif error_type == "dns_failure":
        return JSONResponse(
            status_code=502,
            content={
                "error": "Bad Gateway",
                "code": 502,
                "message": "DNS resolution failed for upstream service",
                "fix": "Check network connectivity and DNS settings",
                "debug_info": {
                    "error_type": "dns_resolution_failure",
                    "common_causes": ["Network connectivity issues", "DNS server problems", "Firewall blocking DNS"]
                }
            }
        )
    elif error_type == "ssl_error":
        return JSONResponse(
            status_code=502,
            content={
                "error": "SSL/TLS Error",
                "code": 502, 
                "message": "SSL certificate verification failed",
                "fix": "Check SSL certificate validity and chain",
                "debug_info": {
                    "error_type": "ssl_verification_failure",
                    "common_causes": ["Expired certificate", "Self-signed certificate", "Certificate chain issues"]
                }
            }
        )
    else:
        raise HTTPException(400, "Unknown network error type")

def get_common_causes(code: int) -> list:
    """Get common causes for HTTP status codes"""
    causes_map = {
        400: ["Invalid JSON syntax", "Missing required fields", "Invalid data types"],
        401: ["Missing API key", "Invalid credentials", "Expired token"],
        403: ["Insufficient permissions", "Account suspended", "IP blocked"],
        404: ["Wrong endpoint URL", "Resource deleted", "Typo in path"],
        422: ["Validation errors", "Business logic violations", "Invalid field values"],
        429: ["Too many requests", "Rate limit exceeded", "Burst limit reached"],
        500: ["Server bug", "Database connection error", "Unhandled exception"],
        502: ["Upstream server error", "Load balancer issues", "Network problems"],
        503: ["Server maintenance", "Overloaded server", "Temporary outage"],
        504: ["Slow upstream response", "Network timeout", "Processing timeout"]
    }
    return causes_map.get(code, ["Unknown cause"])

# Add rate limit error handler
router.state.limiter = limiter
router.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)