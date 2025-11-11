# Installation Guide

Complete step-by-step installation guide for the Smart Profile Finder.

## Prerequisites

### System Requirements
- **Operating System**: Linux, macOS, or Windows
- **Python**: Version 3.8 or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: ~500MB for dependencies and models
- **Internet**: Required for API calls and model downloads

### Required Accounts
1. **SerpAPI Account** (for Google search)
   - Sign up: https://serpapi.com/
   - Free tier: 100 searches/month
   - Paid plans: Starting at $50/month for 5,000 searches

2. **Google AI Studio Account** (for Gemini API)
   - Sign up: https://makersuite.google.com/
   - Free tier: Available
   - Get API key: https://makersuite.google.com/app/apikey

## Installation Steps

### Step 1: Check Python Version
```bash
python --version
# or
python3 --version
```

Should show Python 3.8 or higher. If not, install/upgrade Python:
- **Ubuntu/Debian**: `sudo apt install python3.10`
- **macOS**: `brew install python@3.10`
- **Windows**: Download from https://www.python.org/downloads/

### Step 2: Create Project Directory
```bash
mkdir profile-finder
cd profile-finder
```

### Step 3: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

Your prompt should now show `(venv)` prefix.

### Step 4: Copy Project Files
Copy all project files to the `profile-finder` directory:
- `profile_finder.py`
- `requirements.txt`
- `test_setup.py`
- `example_usage.py`
- All documentation files

### Step 5: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- `deepface` - Face detection and recognition
- `opencv-python` - Image processing
- `tf-keras` - Deep learning backend
- `requests` - HTTP requests
- `beautifulsoup4` - Web scraping
- `pandas` - Data handling
- `Pillow` - Image manipulation
- `imagehash` - Perceptual hashing
- `google-generativeai` - Gemini AI
- `retina-face` - Face detection backend

**Note**: First installation may take 5-10 minutes as it downloads all packages.

### Step 6: Set Environment Variables

#### Option A: Export in Terminal (Temporary)
```bash
export SERPAPI_KEY="your_serpapi_key_here"
export GEMINI_API_KEY="your_gemini_api_key_here"
```

#### Option B: Add to Shell Profile (Permanent)
```bash
# For bash (~/.bashrc or ~/.bash_profile)
echo 'export SERPAPI_KEY="your_serpapi_key_here"' >> ~/.bashrc
echo 'export GEMINI_API_KEY="your_gemini_api_key_here"' >> ~/.bashrc
source ~/.bashrc

# For zsh (~/.zshrc)
echo 'export SERPAPI_KEY="your_serpapi_key_here"' >> ~/.zshrc
echo 'export GEMINI_API_KEY="your_gemini_api_key_here"' >> ~/.zshrc
source ~/.zshrc
```

#### Option C: Create .env File (Recommended)
```bash
cat > .env << EOF
SERPAPI_KEY=your_serpapi_key_here
GEMINI_API_KEY=your_gemini_api_key_here
EOF
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

And add to the top of `profile_finder.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Step 7: Verify Installation
```bash
python test_setup.py
```

Expected output:
```
🔍 Testing imports...
  ✓ requests
  ✓ pandas
  ✓ Pillow
  ✓ imagehash
  ✓ beautifulsoup4
  ✓ google-generativeai
  ✓ deepface
  ✓ opencv-python

✅ All packages imported successfully!

🔍 Testing environment variables...
  ✓ SERPAPI_KEY is set
  ✓ GEMINI_API_KEY is set

✅ All environment variables are set!

🔍 Testing DeepFace...
  ✓ DeepFace imported
  ℹ Available models: VGG-Face, Facenet, Facenet512, OpenFace, DeepFace, ArcFace
  ℹ Available backends: opencv, ssd, dlib, mtcnn, retinaface

✅ DeepFace is ready!

🔍 Testing directory creation...
  ✓ downloads/ directory ready
  ✓ outputs/ directory ready

✅ Directories created successfully!

🎉 All tests passed! You're ready to use profile_finder.py
```

### Step 8: First Run (Model Download)
On first run, DeepFace will download AI models (~100MB):

```bash
python profile_finder.py
```

Models will be downloaded to `~/.deepface/weights/`:
- `retinaface.h5` (~30MB) - Face detection
- `facenet512_weights.h5` (~90MB) - Face recognition
- Other models as needed

This is a one-time download. Subsequent runs will be faster.

## Platform-Specific Instructions

### Ubuntu/Debian Linux
```bash
# Install system dependencies
sudo apt update
sudo apt install python3-pip python3-venv
sudo apt install libgl1-mesa-glx libglib2.0-0  # For OpenCV

# Continue with Step 3 above
```

### macOS
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.10

# Continue with Step 3 above
```

### Windows
1. Install Python from https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH" during installation
2. Open Command Prompt or PowerShell
3. Continue with Step 3 above

**Windows-specific notes**:
- Use `python` instead of `python3`
- Use `venv\Scripts\activate` to activate virtual environment
- May need Visual C++ Build Tools for some packages

### Amazon Linux 2023 (Sandbox Environment)
```bash
# Install Python and pip
sudo dnf install python3 python3-pip -y

# Install system dependencies
sudo dnf install mesa-libGL glib2 -y

# Continue with Step 3 above
```

## Troubleshooting

### Issue: "pip: command not found"
```bash
# Install pip
python -m ensurepip --upgrade
```

### Issue: "No module named 'cv2'"
```bash
# Reinstall opencv-python
pip uninstall opencv-python
pip install opencv-python-headless
```

### Issue: "TensorFlow not found"
```bash
# Install TensorFlow
pip install tensorflow>=2.15.0
```

### Issue: "Permission denied"
```bash
# Use --user flag
pip install --user -r requirements.txt
```

### Issue: "SSL Certificate Error"
```bash
# Use trusted host
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Issue: Models not downloading
```bash
# Manually create directory
mkdir -p ~/.deepface/weights

# Check internet connection
ping google.com

# Try with different backend
# Edit profile_finder.py and change detector_backend to 'opencv'
```

### Issue: "Memory Error"
```bash
# Reduce batch size or use lighter model
# Edit profile_finder.py:
# Change model_name='Facenet512' to model_name='OpenFace'
```

## Verification Checklist

Before using the tool, verify:

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip list`)
- [ ] SERPAPI_KEY environment variable set
- [ ] GEMINI_API_KEY environment variable set
- [ ] test_setup.py passes all tests
- [ ] downloads/ and outputs/ directories exist
- [ ] Internet connection working
- [ ] Sufficient disk space (~500MB)

## Next Steps

After successful installation:

1. **Read Documentation**
   ```bash
   cat USAGE.md
   cat PROJECT_README.md
   ```

2. **Run Examples**
   ```bash
   python example_usage.py
   ```

3. **Try Basic Search**
   ```bash
   python profile_finder.py
   # Enter a person's name when prompted
   ```

4. **Test with Reference Image**
   - Prepare a clear photo (JPG or PNG)
   - Run: `python profile_finder.py`
   - Provide image path when prompted

## Updating

To update to the latest version:

```bash
# Pull latest code
git pull

# Update dependencies
pip install --upgrade -r requirements.txt

# Clear model cache if needed
rm -rf ~/.deepface/weights
```

## Uninstallation

To completely remove:

```bash
# Deactivate virtual environment
deactivate

# Remove project directory
cd ..
rm -rf profile-finder

# Remove model cache
rm -rf ~/.deepface

# Remove environment variables from shell profile
# Edit ~/.bashrc or ~/.zshrc and remove export lines
```

## Support

If you encounter issues:

1. Check this guide thoroughly
2. Run `python test_setup.py` for diagnostics
3. Check error messages in console
4. Verify API keys are correct
5. Ensure internet connection is stable
6. Check API quotas (SerpAPI, Gemini)

## Additional Resources

- **DeepFace Documentation**: https://github.com/serengil/deepface
- **SerpAPI Documentation**: https://serpapi.com/docs
- **Gemini API Documentation**: https://ai.google.dev/docs
- **Python Virtual Environments**: https://docs.python.org/3/tutorial/venv.html
- **pip Documentation**: https://pip.pypa.io/en/stable/

---

**Installation Time**: ~10-15 minutes (including model downloads)  
**Difficulty**: Beginner to Intermediate  
**Support**: See PROJECT_README.md for contact information
