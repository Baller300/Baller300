#!/usr/bin/env python3
"""
Test script to verify the setup and dependencies for profile_finder.py
"""

import sys
import os

def test_imports():
    """Test if all required packages can be imported."""
    print("🔍 Testing imports...")
    
    required_packages = {
        'requests': 'requests',
        'pandas': 'pandas',
        'PIL': 'Pillow',
        'imagehash': 'imagehash',
        'bs4': 'beautifulsoup4',
        'google.generativeai': 'google-generativeai',
        'deepface': 'deepface',
        'cv2': 'opencv-python',
    }
    
    failed = []
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError as e:
            print(f"  ✗ {package} - {e}")
            failed.append(package)
    
    if failed:
        print(f"\n❌ Missing packages: {', '.join(failed)}")
        print(f"Install with: pip install {' '.join(failed)}")
        return False
    
    print("\n✅ All packages imported successfully!")
    return True

def test_environment_variables():
    """Test if required environment variables are set."""
    print("\n🔍 Testing environment variables...")
    
    required_vars = ['SERPAPI_KEY', 'GEMINI_API_KEY']
    missing = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✓ {var} is set")
        else:
            print(f"  ✗ {var} is NOT set")
            missing.append(var)
    
    if missing:
        print(f"\n⚠️ Missing environment variables: {', '.join(missing)}")
        print("\nSet them with:")
        for var in missing:
            print(f"  export {var}='your_key_here'")
        return False
    
    print("\n✅ All environment variables are set!")
    return True

def test_deepface():
    """Test DeepFace functionality."""
    print("\n🔍 Testing DeepFace...")
    
    try:
        from deepface import DeepFace
        print("  ✓ DeepFace imported")
        
        # Test available models
        models = ['VGG-Face', 'Facenet', 'Facenet512', 'OpenFace', 'DeepFace', 'ArcFace']
        print(f"  ℹ Available models: {', '.join(models)}")
        
        # Test available backends
        backends = ['opencv', 'ssd', 'dlib', 'mtcnn', 'retinaface']
        print(f"  ℹ Available backends: {', '.join(backends)}")
        
        print("\n✅ DeepFace is ready!")
        print("  ⚠️ Note: Models will be downloaded on first use (~100MB)")
        return True
        
    except Exception as e:
        print(f"  ✗ DeepFace test failed: {e}")
        return False

def test_directories():
    """Test if output directories can be created."""
    print("\n🔍 Testing directory creation...")
    
    dirs = ['downloads', 'outputs']
    
    for dir_name in dirs:
        try:
            os.makedirs(dir_name, exist_ok=True)
            print(f"  ✓ {dir_name}/ directory ready")
        except Exception as e:
            print(f"  ✗ Failed to create {dir_name}/: {e}")
            return False
    
    print("\n✅ Directories created successfully!")
    return True

def main():
    """Run all tests."""
    print("="*60)
    print("Profile Finder - Setup Test")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Environment Variables", test_environment_variables()))
    results.append(("DeepFace", test_deepface()))
    results.append(("Directories", test_directories()))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! You're ready to use profile_finder.py")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
