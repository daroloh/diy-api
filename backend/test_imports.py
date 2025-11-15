"""
Test script to verify the API Failure Simulator works correctly.
Run this from the backend directory after installing dependencies.
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Test imports
    from main import app
    from routers.simulate import router
    from utils.errors import get_error_details
    from schemas import ErrorResponse
    
    print("✅ All imports successful!")
    
    # Test error catalog
    title, message, fix = get_error_details(401)
    print(f"✅ Error catalog working: {title}")
    
    # Test FastAPI app creation
    print(f"✅ FastAPI app created: {app.title}")
    print(f"✅ Router included: {len(app.routes)} routes total")
    
    print("\n🎉 API Failure Simulator is ready to run!")
    print("\nTo start the server:")
    print("uvicorn main:app --reload --port 8000")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you've installed the dependencies: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Error: {e}")