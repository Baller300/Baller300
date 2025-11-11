# Smart Profile Finder with Face Detection

A powerful Python tool that searches for social media profiles (LinkedIn, Instagram, Facebook, Twitter) and uses **DeepFace** AI for face detection and verification to match profiles with reference images.

## 🌟 Features

### Core Capabilities
- 🔍 **Multi-Platform Search**: Automatically searches LinkedIn, Instagram, Facebook, Twitter
- 🎯 **AI Face Detection**: Uses DeepFace with RetinaFace detector for accurate face detection
- 🤖 **Face Verification**: Compares reference photos with discovered profile images
- 📊 **Profile Data Extraction**: Extracts names, bios, headlines, locations, profile images
- 🖼️ **Image Downloading**: Automatically downloads profile pictures and page images
- 🧠 **AI Analysis**: Uses Google Gemini to analyze and summarize findings
- 📈 **Detailed Reports**: Generates CSV and JSON reports with match confidence scores

### Technical Highlights
- **Face Detection**: RetinaFace (state-of-the-art accuracy)
- **Face Recognition**: Facenet512 (can switch to VGG-Face, ArcFace, etc.)
- **Search Engine**: SerpAPI for reliable Google search results
- **AI Analysis**: Google Gemini 2.5 Pro for intelligent summarization
- **Rate Limiting**: Built-in delays to avoid blocking
- **Error Handling**: Comprehensive error handling and logging

## 📋 Requirements

### Python Version
- Python 3.8 or higher

### API Keys (Required)
1. **SerpAPI Key**: For Google search results
   - Sign up at https://serpapi.com/
   - Free tier: 100 searches/month

2. **Google Gemini API Key**: For AI analysis
   - Get from https://makersuite.google.com/app/apikey
   - Free tier available

### Dependencies
See `requirements.txt` for full list:
- `deepface` - Face detection and recognition
- `opencv-python` - Image processing
- `requests` - HTTP requests
- `beautifulsoup4` - Web scraping
- `pandas` - Data handling
- `google-generativeai` - Gemini AI
- And more...

## 🚀 Installation

### 1. Clone or Download
```bash
git clone <repository-url>
cd profile-finder
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables
```bash
export SERPAPI_KEY="your_serpapi_key_here"
export GEMINI_API_KEY="your_gemini_api_key_here"
```

Or create a `.env` file:
```
SERPAPI_KEY=your_serpapi_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Test Setup
```bash
python test_setup.py
```

## 💻 Usage

### Basic Usage
```bash
python profile_finder.py
```

### Interactive Mode
```
Enter person name/info: John Doe
Reference image path (optional): /path/to/photo.jpg
```

### Example Queries
- `"John Doe Software Engineer"`
- `"Jane Smith Google"`
- `"@username"`
- `"Person Name Company"`

### Programmatic Usage
```python
from profile_finder import profile_matcher

# Search with face matching
results = profile_matcher(
    query="John Doe",
    ref_image_path="reference.jpg",
    num_results=10
)

# Process results
for result in results:
    if result['face_match']:
        print(f"Match found: {result['title']}")
        print(f"Distance: {result['face_distance']}")
```

## 📁 Project Structure

```
profile-finder/
├── profile_finder.py      # Main script
├── requirements.txt       # Python dependencies
├── test_setup.py         # Setup verification script
├── example_usage.py      # Usage examples
├── USAGE.md             # Detailed usage guide
├── CHANGES.md           # Changelog and improvements
├── PROJECT_README.md    # This file
├── downloads/           # Downloaded images (created automatically)
│   └── {query}/
│       └── {domain}/
└── outputs/             # Search results (created automatically)
    ├── matches_{query}_{timestamp}.csv
    └── matches_{query}_{timestamp}.json
```

## 🎯 How It Works

### 1. Search Phase
- Searches Google using SerpAPI for profiles matching the query
- Targets specific platforms: LinkedIn, Instagram, Facebook, Twitter
- Fetches up to 10 results per platform

### 2. Data Extraction Phase
- Visits each profile URL
- Extracts structured data (name, bio, headline, location)
- Downloads profile images and page images
- Organizes images by domain

### 3. Face Matching Phase (Optional)
- Detects faces in reference image using RetinaFace
- Extracts face embeddings using Facenet512
- Compares reference face with downloaded profile images
- Calculates similarity distance (threshold: 0.6)
- Marks profiles with matching faces

### 4. Analysis Phase
- Summarizes all findings
- Uses Gemini AI to analyze profile consistency
- Identifies likely matches across platforms
- Generates detailed CSV and JSON reports

## 📊 Output Files

### CSV Report
`outputs/matches_{query}_{timestamp}.csv`

Contains:
- Rank, domain, title, link, snippet
- Face match status (True/False)
- Face distance (lower = better match)
- Profile data (name, bio, headline, location)
- Downloaded image paths

### JSON Report
`outputs/matches_{query}_{timestamp}.json`

Contains:
- Complete structured data
- Nested profile information
- Face verification results
- All metadata

### Downloaded Images
`downloads/{query}/{domain}/`

Organized by:
- Query name
- Domain (linkedin.com, instagram.com, etc.)
- Image type (profile.jpg, img_1.jpg, etc.)

## 🔧 Configuration

### Change Face Detection Model
Edit `profile_finder.py`:
```python
# In get_face_embedding() function
model_name='Facenet512'  # Default

# Options:
# 'VGG-Face', 'Facenet', 'Facenet512', 'OpenFace', 
# 'DeepFace', 'DeepID', 'ArcFace', 'Dlib'
```

### Change Detection Backend
```python
# In detect_faces_in_image() function
detector_backend='retinaface'  # Default

# Options:
# 'opencv', 'ssd', 'dlib', 'mtcnn', 'retinaface', 'mediapipe'
```

### Adjust Face Match Threshold
```python
# In verify_faces() function
threshold = 0.6  # Lower = stricter matching
```

## 🧪 Testing

### Run Setup Tests
```bash
python test_setup.py
```

Checks:
- ✓ All dependencies installed
- ✓ Environment variables set
- ✓ DeepFace functionality
- ✓ Directory creation

### Run Examples
```bash
python example_usage.py
```

Demonstrates:
- Basic profile search
- Face matching
- LinkedIn-specific search
- Multi-platform search
- Face verification
- Face detection
- Profile data extraction

## 📖 Documentation

- **USAGE.md**: Detailed usage guide with examples
- **CHANGES.md**: Comparison with old implementation
- **example_usage.py**: Code examples for all features

## ⚠️ Important Notes

### Privacy & Ethics
- Only searches publicly available information
- Respects robots.txt and terms of service
- Do not use for stalking or harassment
- Comply with GDPR and data protection laws
- Get consent before using someone's photos

### Rate Limiting
- Built-in 0.5s delay between requests
- SerpAPI has monthly quotas
- Some platforms may block excessive requests

### Accuracy
- Face matching depends on image quality
- Best results with front-facing, well-lit photos
- Multiple angles may reduce accuracy
- Occlusion (glasses, masks) may affect results

### Limitations
- Public profiles only (no private/protected accounts)
- JavaScript-heavy sites may not load fully
- Some platforms actively block scrapers
- API quotas apply (SerpAPI, Gemini)

## 🐛 Troubleshooting

### No faces detected
- Ensure image is clear and face is visible
- Try different detector backend (mtcnn, ssd)
- Check image format (JPG, PNG supported)

### Rate limiting errors
- Increase sleep time between requests
- Reduce number of results per query
- Check SerpAPI quota

### Profile extraction fails
- Some platforms block scraping
- Use official APIs when available
- Check internet connection

### Memory issues
- DeepFace downloads models on first run (~100MB)
- Models cached in `~/.deepface/weights/`
- Ensure sufficient disk space

## 🔄 Comparison with Old Version

### Key Improvements
- ✅ **95-98% accuracy** (vs 85-90% with face_recognition)
- ✅ **7+ face detection models** (vs 1)
- ✅ **5+ detection backends** (vs 1)
- ✅ **Easier installation** (no C++ compilation needed)
- ✅ **Better integration** (automated workflow)
- ✅ **Enhanced features** (profile extraction, multi-platform)
- ✅ **Modern codebase** (actively maintained)

See `CHANGES.md` for detailed comparison.

## 📝 License

This project is for educational purposes. Please respect:
- Platform terms of service
- Privacy laws (GDPR, CCPA, etc.)
- Ethical use guidelines
- API usage limits

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📧 Support

For issues or questions:
1. Check documentation (USAGE.md, CHANGES.md)
2. Run test_setup.py to verify installation
3. Review error messages in console
4. Check API keys and quotas
5. Ensure internet connection

## 🙏 Acknowledgments

- **DeepFace**: Face detection and recognition
- **SerpAPI**: Google search results
- **Google Gemini**: AI analysis
- **OpenCV**: Image processing
- **BeautifulSoup**: Web scraping

## 📚 References

- DeepFace: https://github.com/serengil/deepface
- SerpAPI: https://serpapi.com/
- Google Gemini: https://ai.google.dev/
- RetinaFace: https://arxiv.org/abs/1905.00641
- Facenet: https://arxiv.org/abs/1503.03832

---

**Version**: 2.0  
**Last Updated**: November 2025  
**Author**: Uday Kashyap  
**Status**: Active Development
