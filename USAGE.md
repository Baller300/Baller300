# Smart Profile Finder - Usage Guide

## Overview
This tool searches for social media profiles (LinkedIn, Instagram, Facebook, Twitter) and uses **DeepFace** for face detection and verification to match profiles with a reference image.

## Features

### 🎯 Core Capabilities
- **Face Detection & Verification**: Uses DeepFace with RetinaFace detector and Facenet512 model
- **Multi-Platform Search**: LinkedIn, Instagram, Facebook, Twitter/X
- **Profile Data Extraction**: Extracts names, bios, headlines, profile images
- **Image Downloading**: Downloads profile pictures and page images
- **Face Matching**: Compares reference image with discovered profiles
- **AI Analysis**: Uses Google Gemini to analyze and summarize results

### 🔧 Technical Details
- **Face Detection Backend**: RetinaFace (more accurate than dlib)
- **Face Recognition Model**: Facenet512 (can be changed to VGG-Face, ArcFace, etc.)
- **Verification Threshold**: Distance < 0.6 for face matching
- **Rate Limiting**: 0.5s delay between requests

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
export SERPAPI_KEY="your_serpapi_key_here"
export GEMINI_API_KEY="your_gemini_api_key_here"
```

Or create a `.env` file:
```
SERPAPI_KEY=your_serpapi_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

## Usage

### Basic Usage
```bash
python profile_finder.py
```

### Interactive Mode
```
Enter person name/info: John Doe Software Engineer
Reference image path (optional): /path/to/photo.jpg
```

### Example Queries
- `"John Doe LinkedIn"`
- `"Jane Smith Instagram"`
- `"@username Twitter"`
- `"John Doe Microsoft Engineer"`

## How It Works

### 1. Search Phase
- Searches Google using SerpAPI for profiles matching the query
- Prioritizes LinkedIn, Instagram, Facebook, Twitter domains
- Fetches up to 10 results per platform

### 2. Data Extraction Phase
- Visits each profile URL
- Extracts profile data (name, bio, headline, location)
- Downloads profile images and page images
- Saves images to `downloads/{query}/{domain}/`

### 3. Face Matching Phase (if reference image provided)
- Detects faces in reference image using RetinaFace
- Extracts face embeddings using Facenet512
- Compares reference face with downloaded profile images
- Marks profiles with matching faces (distance < 0.6)

### 4. Analysis Phase
- Summarizes all findings
- Uses Gemini AI to analyze profile consistency
- Identifies likely matches across platforms
- Generates detailed report

## Output Files

### CSV Report
`outputs/matches_{query}_{timestamp}.csv`
- Rank, domain, title, link, snippet
- Face match status and distance
- Profile data (name, bio, etc.)
- Downloaded image paths

### JSON Report
`outputs/matches_{query}_{timestamp}.json`
- Detailed structured data
- Complete profile information
- Face verification results

### Downloaded Images
`downloads/{query}/{domain}/`
- Profile images
- Page images
- Organized by domain

## Face Detection Models

### Available Models
You can change the model in the code:

```python
# In get_face_embedding() function
model_name='Facenet512'  # Default (best accuracy)
# Options: 'VGG-Face', 'Facenet', 'Facenet512', 'OpenFace', 'DeepFace', 'DeepID', 'ArcFace', 'Dlib'
```

### Detection Backends
```python
# In detect_faces_in_image() function
detector_backend='retinaface'  # Default (most accurate)
# Options: 'opencv', 'ssd', 'dlib', 'mtcnn', 'retinaface', 'mediapipe'
```

## Troubleshooting

### No faces detected
- Ensure image is clear and face is visible
- Try different detector backend (mtcnn, ssd)
- Check image file format (JPG, PNG supported)

### Rate limiting errors
- Increase sleep time between requests
- Use fewer results per query
- Check SerpAPI quota

### Profile data extraction fails
- Some platforms block scraping
- Use official APIs when available
- Respect robots.txt and terms of service

### Memory issues
- DeepFace downloads models on first run (~100MB)
- Models are cached in `~/.deepface/weights/`
- Ensure sufficient disk space

## Privacy & Ethics

⚠️ **Important Considerations**:
- Only search for publicly available information
- Respect privacy and terms of service
- Do not use for stalking or harassment
- Comply with GDPR and data protection laws
- Get consent before using someone's photos

## API Keys

### SerpAPI
- Sign up at https://serpapi.com/
- Free tier: 100 searches/month
- Paid plans available

### Google Gemini
- Get API key from https://makersuite.google.com/app/apikey
- Free tier available
- Used for result analysis

## Advanced Usage

### Custom Search
```python
from profile_finder import search_linkedin_profile, search_social_media_profiles

# Search specific platform
linkedin_results = search_linkedin_profile("John Doe", company="Google")
instagram_results = search_social_media_profiles("John Doe", platform="instagram")
```

### Face Verification Only
```python
from profile_finder import verify_faces

verified, distance = verify_faces("reference.jpg", "profile.jpg")
print(f"Match: {verified}, Distance: {distance}")
```

### Batch Processing
```python
queries = ["Person 1", "Person 2", "Person 3"]
for query in queries:
    profile_matcher(query, ref_image_path="reference.jpg")
```

## Performance Tips

1. **Use specific queries**: Include company, location, or username
2. **Provide clear reference images**: Front-facing, good lighting
3. **Limit results**: Start with 5-10 results per platform
4. **Cache results**: Save and reuse downloaded images
5. **Use faster models**: OpenFace is faster than Facenet512

## Limitations

- **Public profiles only**: Cannot access private/protected accounts
- **Rate limits**: SerpAPI and platforms have request limits
- **Accuracy**: Face matching depends on image quality
- **Dynamic content**: JavaScript-heavy sites may not load fully
- **Anti-scraping**: Some platforms actively block scrapers

## Support

For issues or questions:
1. Check error messages in console
2. Verify API keys are set correctly
3. Ensure all dependencies are installed
4. Check internet connection
5. Review platform terms of service
