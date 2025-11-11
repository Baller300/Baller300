# Quick Reference Card

## 🚀 Installation (One-Time Setup)
```bash
pip install -r requirements.txt
export SERPAPI_KEY="your_key"
export GEMINI_API_KEY="your_key"
python test_setup.py
```

## 💻 Basic Usage
```bash
# Interactive mode
python profile_finder.py

# Run examples
python example_usage.py
```

## 🔍 Common Commands

### Search for Profiles
```python
from profile_finder import profile_matcher

# Without face matching
results = profile_matcher("John Doe")

# With face matching
results = profile_matcher("John Doe", ref_image_path="photo.jpg")
```

### LinkedIn Search
```python
from profile_finder import search_linkedin_profile

# Basic search
results = search_linkedin_profile("John Doe")

# With company filter
results = search_linkedin_profile("John Doe", company="Google")
```

### Face Verification
```python
from profile_finder import verify_faces

verified, distance = verify_faces("image1.jpg", "image2.jpg")
print(f"Match: {verified}, Distance: {distance}")
```

### Detect Faces
```python
from profile_finder import detect_faces_in_image

faces = detect_faces_in_image("photo.jpg")
print(f"Found {len(faces)} faces")
```

## 📊 Output Files

### Location
- **CSV Reports**: `outputs/matches_{query}_{timestamp}.csv`
- **JSON Reports**: `outputs/matches_{query}_{timestamp}.json`
- **Images**: `downloads/{query}/{domain}/`

### CSV Columns
- rank, domain, title, link, snippet
- face_match, face_distance
- profile_name, profile_headline, profile_location
- downloaded_images

## ⚙️ Configuration

### Change Face Model
Edit `profile_finder.py`:
```python
model_name='Facenet512'  # Options: VGG-Face, Facenet, OpenFace, ArcFace
```

### Change Detector
```python
detector_backend='retinaface'  # Options: opencv, ssd, mtcnn, dlib
```

### Adjust Match Threshold
```python
threshold = 0.6  # Lower = stricter (range: 0.0-1.0)
```

## 🐛 Troubleshooting

### No faces detected
```bash
# Try different backend
detector_backend='mtcnn'  # or 'opencv', 'ssd'
```

### Rate limiting
```bash
# Increase delay in profile_finder.py
sleep(1.0)  # Change from 0.5 to 1.0
```

### Memory error
```bash
# Use lighter model
model_name='OpenFace'  # Instead of Facenet512
```

### Import errors
```bash
pip install --upgrade -r requirements.txt
```

## 📁 File Structure
```
profile-finder/
├── profile_finder.py      # Main script ⭐
├── requirements.txt       # Dependencies
├── test_setup.py         # Verify setup
├── example_usage.py      # Examples
├── PROJECT_README.md     # Main docs
├── USAGE.md             # Usage guide
├── INSTALL.md           # Installation
├── CHANGES.md           # Changelog
├── SUMMARY.md           # Overview
├── QUICK_REFERENCE.md   # This file
├── downloads/           # Downloaded images
└── outputs/             # Search results
```

## 🎯 Common Use Cases

### 1. Find LinkedIn Profile
```bash
python profile_finder.py
# Enter: "John Doe Microsoft"
# Skip image
```

### 2. Verify Profile with Photo
```bash
python profile_finder.py
# Enter: "Jane Smith"
# Image: /path/to/photo.jpg
```

### 3. Multi-Platform Search
```python
from profile_finder import search_social_media_profiles
results = search_social_media_profiles("Person Name")
```

### 4. Compare Two Photos
```python
from profile_finder import verify_faces
verified, dist = verify_faces("photo1.jpg", "photo2.jpg")
```

## 🔑 Environment Variables

### Required
```bash
SERPAPI_KEY=your_serpapi_key
GEMINI_API_KEY=your_gemini_key
```

### Check if Set
```bash
echo $SERPAPI_KEY
echo $GEMINI_API_KEY
```

### Set Permanently
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export SERPAPI_KEY="your_key"' >> ~/.bashrc
source ~/.bashrc
```

## 📊 API Limits

| Service | Free Tier | Paid |
|---------|-----------|------|
| SerpAPI | 100/month | $50/5000 |
| Gemini | Rate limited | Available |

## 🎨 Face Models Comparison

| Model | Speed | Accuracy | Size |
|-------|-------|----------|------|
| OpenFace | ⚡⚡⚡ | ⭐⭐⭐ | 30MB |
| Facenet | ⚡⚡ | ⭐⭐⭐⭐ | 90MB |
| Facenet512 | ⚡ | ⭐⭐⭐⭐⭐ | 90MB |
| VGG-Face | ⚡ | ⭐⭐⭐⭐ | 500MB |
| ArcFace | ⚡ | ⭐⭐⭐⭐⭐ | 150MB |

## 🔍 Detection Backends

| Backend | Speed | Accuracy | Use Case |
|---------|-------|----------|----------|
| opencv | ⚡⚡⚡ | ⭐⭐ | Fast, basic |
| ssd | ⚡⚡ | ⭐⭐⭐ | Balanced |
| mtcnn | ⚡⚡ | ⭐⭐⭐⭐ | Multi-stage |
| retinaface | ⚡ | ⭐⭐⭐⭐⭐ | Best accuracy |
| dlib | ⚡⚡ | ⭐⭐⭐ | Classic |

## 📝 Example Queries

### Good Queries
- ✅ "John Doe Software Engineer"
- ✅ "Jane Smith Google"
- ✅ "Person Name LinkedIn"
- ✅ "@username Instagram"

### Poor Queries
- ❌ "John" (too generic)
- ❌ "Software Engineer" (no name)
- ❌ "Person" (too vague)

## ⚠️ Important Notes

### Privacy
- Only search public information
- Get consent for photos
- Respect terms of service
- Comply with privacy laws

### Rate Limiting
- 0.5s delay between requests
- Don't exceed API quotas
- Respect robots.txt

### Accuracy
- Clear photos work best
- Front-facing preferred
- Good lighting helps
- Occlusion reduces accuracy

## 🆘 Quick Help

### Test Setup
```bash
python test_setup.py
```

### View Examples
```bash
python example_usage.py
```

### Check Logs
```bash
# Check console output for errors
# Look for [!] markers
```

### Reset
```bash
# Clear downloads
rm -rf downloads/*

# Clear outputs
rm -rf outputs/*

# Clear model cache
rm -rf ~/.deepface/weights
```

## 📚 Documentation

| File | Purpose |
|------|---------|
| PROJECT_README.md | Main documentation |
| INSTALL.md | Installation guide |
| USAGE.md | Detailed usage |
| CHANGES.md | What changed |
| SUMMARY.md | Quick overview |
| QUICK_REFERENCE.md | This file |

## 🎯 Success Checklist

- [ ] Dependencies installed
- [ ] API keys set
- [ ] test_setup.py passes
- [ ] Can run profile_finder.py
- [ ] Can search profiles
- [ ] Images download correctly
- [ ] Face detection works
- [ ] Results saved to outputs/

## 💡 Tips

1. **Use specific queries** for better results
2. **Provide clear photos** for face matching
3. **Check API quotas** regularly
4. **Start with small searches** (5-10 results)
5. **Review outputs/** folder for results
6. **Use lighter models** if memory limited
7. **Increase delays** if rate limited
8. **Read error messages** carefully

## 🔗 Quick Links

- SerpAPI: https://serpapi.com/
- Gemini API: https://makersuite.google.com/
- DeepFace: https://github.com/serengil/deepface

---

**Keep this file handy for quick reference!**
