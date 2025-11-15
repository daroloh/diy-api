# API Failure Simulator & Troubleshooting Playground

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](./LICENSE)

> **Perfect for API Support Engineers, Developers, and QA Teams**

An educational API that lets you intentionally break requests to learn how APIs behave under failure conditions. Simulate real-world API problems like rate limiting, timeouts, malformed responses, and various HTTP error codes.

## Why This Matters

Every API support engineer needs to understand:
- How APIs fail in production  
- HTTP status codes and error handling
- Rate limiting and retry strategies
- JSON parsing errors and malformed responses
- Network timeouts and connection issues
- Debugging customer API integration problems

This tool provides a **safe sandbox** to reproduce and understand these scenarios.

## Quick Start (Windows PowerShell)

### Prerequisites
- Python 3.8 or higher
- Git

### 1. Clone and Setup
```powershell
git clone https://github.com/daroloh/diy-api.git
cd diy-api
cd backend
```

### 2. Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Run the API
```powershell
uvicorn main:app --reload --port 8000
```

**API is now running at:** http://localhost:8000

- **Interactive Docs:** http://localhost:8000/ (Swagger UI)
- **Alternative Docs:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## API Endpoints

### Status Code Simulation
```http
GET /simulate/status?code=401&include_headers=true
```
**What it does:** Returns any HTTP status code with detailed error info and debugging tips.

### Try It With curl
```powershell
# Test 401 Unauthorized
curl -i "http://localhost:8000/simulate/status?code=401"

# Test 429 Rate Limited  
curl -i "http://localhost:8000/simulate/status?code=429"

# Test 500 Internal Server Error
curl -i "http://localhost:8000/simulate/status?code=500"
```

## Project Structure

```
diy-api/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── .env                   # Environment variables
│   ├── schemas.py             # Pydantic response models
│   ├── routers/
│   │   ├── __init__.py
│   │   └── simulate.py        # All simulation endpoints
│   └── utils/
│       ├── __init__.py
│       └── errors.py          # Error handling utilities
└── README.md                  # This file
```

## Portfolio Value

This project demonstrates:
- **API Design** - RESTful endpoints with proper HTTP semantics
- **Error Handling** - Comprehensive error responses and debugging info  
- **Rate Limiting** - Production-ready rate limiting implementation
- **Documentation** - Self-documenting API with Swagger/OpenAPI
- **Testing Mindset** - Understanding of failure modes and edge cases
- **Educational Focus** - Teaching tool that helps others learn

Perfect for **API Support Engineer** and **Developer Relations** roles!

---

**Built with love for the API community**