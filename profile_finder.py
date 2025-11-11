import os, re, json, requests, pandas as pd
from datetime import datetime
from PIL import Image
import imagehash
from io import BytesIO
from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote
import google.generativeai as genai
from deepface import DeepFace
import cv2
import numpy as np
from time import sleep

# ==== CONFIG ====
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not SERPAPI_KEY or not GEMINI_API_KEY:
    raise EnvironmentError("❌ Missing SERPAPI_KEY or GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-pro")

# ==== UTILITIES ====
def safe_filename(s):
    """Make string safe for filenames."""
    return re.sub(r'[\\/*?:"<>|]', "_", s)

def get_phash_from_url(url):
    """Compute perceptual hash from image URL."""
    try:
        img_data = requests.get(url, timeout=10).content
        img = Image.open(BytesIO(img_data)).convert("RGB")
        return imagehash.phash(img)
    except Exception:
        return None

def compare_phashes(p1, p2):
    """Return similarity ratio between two perceptual hashes."""
    if not p1 or not p2:
        return 0.0
    dist = p1 - p2
    return 1.0 - dist / (len(p1.hash) ** 2)

def download_images_from_page(url, dest_folder, limit=3):
    """Download up to `limit` public images from a given URL."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        html = requests.get(url, timeout=10, headers=headers).text
    except Exception as e:
        print(f"  [!] Failed to load {url}: {e}")
        return []

    soup = BeautifulSoup(html, "html.parser")
    imgs = [img.get("src") for img in soup.find_all("img") if img.get("src")]
    saved = []

    for img_url in imgs[:limit]:
        try:
            if img_url.startswith("//"):
                img_url = "https:" + img_url
            elif img_url.startswith("/"):
                parsed = urlparse(url)
                img_url = f"{parsed.scheme}://{parsed.netloc}{img_url}"

            img_data = requests.get(img_url, timeout=10, headers=headers).content
            fname = os.path.join(dest_folder, safe_filename(os.path.basename(img_url.split("?")[0])) or f"img_{len(saved)+1}.jpg")
            if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                fname += ".jpg"
            with open(fname, "wb") as f:
                f.write(img_data)
            saved.append(fname)
        except Exception:
            continue

    return saved

# ==== DEEPFACE UTILITIES ====
def detect_faces_in_image(image_path):
    """Detect faces in an image using DeepFace."""
    try:
        # Use RetinaFace for detection (more accurate)
        faces = DeepFace.extract_faces(
            img_path=image_path,
            detector_backend='retinaface',
            enforce_detection=False
        )
        return faces
    except Exception as e:
        print(f"  [!] Face detection error: {e}")
        return []

def get_face_embedding(image_path, model_name='Facenet512'):
    """Get face embedding using DeepFace."""
    try:
        embedding = DeepFace.represent(
            img_path=image_path,
            model_name=model_name,
            detector_backend='retinaface',
            enforce_detection=False
        )
        return embedding[0]['embedding'] if embedding else None
    except Exception as e:
        print(f"  [!] Embedding error: {e}")
        return None

def verify_faces(img1_path, img2_path, model_name='Facenet512'):
    """Verify if two images contain the same person using DeepFace."""
    try:
        result = DeepFace.verify(
            img1_path=img1_path,
            img2_path=img2_path,
            model_name=model_name,
            detector_backend='retinaface',
            enforce_detection=False
        )
        return result['verified'], result['distance']
    except Exception as e:
        print(f"  [!] Verification error: {e}")
        return False, 1.0

def find_similar_faces(reference_image, image_folder, threshold=0.6):
    """Find images with similar faces in a folder."""
    ref_embedding = get_face_embedding(reference_image)
    if ref_embedding is None:
        print("  [!] Could not extract face from reference image")
        return []
    
    similar_images = []
    for filename in os.listdir(image_folder):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            img_path = os.path.join(image_folder, filename)
            verified, distance = verify_faces(reference_image, img_path)
            
            if verified or distance < threshold:
                similar_images.append({
                    'path': img_path,
                    'distance': distance,
                    'verified': verified
                })
    
    return sorted(similar_images, key=lambda x: x['distance'])

# ==== SERPAPI FETCH ====
def fetch_profiles(query, num=10):
    """Fetch Google search results using SerpAPI."""
    params = {"engine": "google", "q": query, "num": num, "api_key": SERPAPI_KEY}
    
    resp = requests.get("https://serpapi.com/search.json", params=params)
    if resp.status_code != 200:
        print("SerpAPI error:", resp.text)
        return []

    data = resp.json()
    return data.get("organic_results", [])

def reverse_image_search(image_path):
    """Perform reverse image search using SerpAPI."""
    try:
        # Upload image and get search results
        with open(image_path, 'rb') as f:
            files = {'file': f}
            # Note: This is a simplified version. In production, you'd upload to a service
            # and use the URL with SerpAPI's Google Lens API
            print("  [i] Reverse image search requires image URL. Skipping for local files.")
            return []
    except Exception as e:
        print(f"  [!] Reverse image search error: {e}")
        return []

def search_linkedin_profile(name, company=None):
    """Search for LinkedIn profiles."""
    query = f'site:linkedin.com/in/ "{name}"'
    if company:
        query += f' "{company}"'
    
    return fetch_profiles(query, num=5)

def search_social_media_profiles(name, platform=None):
    """Search for social media profiles across platforms."""
    platforms = ['instagram', 'facebook', 'twitter', 'linkedin'] if not platform else [platform]
    all_results = []
    
    for plat in platforms:
        query = f'site:{plat}.com "{name}"'
        results = fetch_profiles(query, num=3)
        all_results.extend(results)
        sleep(0.5)  # Rate limiting
    
    return all_results

# ==== EXTRACT DATA FROM SOCIAL MEDIA ====
def extract_linkedin_data(url):
    """Extract data from LinkedIn profile (public view)."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {
            'url': url,
            'name': None,
            'headline': None,
            'location': None,
            'profile_image': None
        }
        
        # Try to extract name
        name_tag = soup.find('h1', {'class': lambda x: x and 'name' in x.lower()})
        if name_tag:
            data['name'] = name_tag.get_text(strip=True)
        
        # Try to extract headline
        headline_tag = soup.find('div', {'class': lambda x: x and 'headline' in x.lower()})
        if headline_tag:
            data['headline'] = headline_tag.get_text(strip=True)
        
        # Try to extract profile image
        img_tag = soup.find('img', {'class': lambda x: x and 'profile' in x.lower()})
        if img_tag and img_tag.get('src'):
            data['profile_image'] = img_tag['src']
        
        return data
    except Exception as e:
        print(f"  [!] LinkedIn extraction error: {e}")
        return None

def extract_instagram_data(username):
    """Extract data from Instagram profile (public view)."""
    try:
        url = f'https://www.instagram.com/{username}/'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {
            'url': url,
            'username': username,
            'name': None,
            'bio': None,
            'profile_image': None
        }
        
        # Try to extract from meta tags
        meta_description = soup.find('meta', {'property': 'og:description'})
        if meta_description:
            data['bio'] = meta_description.get('content', '')
        
        # Try to extract profile image
        meta_image = soup.find('meta', {'property': 'og:image'})
        if meta_image:
            data['profile_image'] = meta_image.get('content')
        
        return data
    except Exception as e:
        print(f"  [!] Instagram extraction error: {e}")
        return None

def extract_twitter_data(username):
    """Extract data from Twitter/X profile (public view)."""
    try:
        url = f'https://twitter.com/{username}'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {
            'url': url,
            'username': username,
            'name': None,
            'bio': None,
            'profile_image': None
        }
        
        # Try to extract from meta tags
        meta_title = soup.find('meta', {'property': 'og:title'})
        if meta_title:
            data['name'] = meta_title.get('content', '')
        
        meta_description = soup.find('meta', {'property': 'og:description'})
        if meta_description:
            data['bio'] = meta_description.get('content', '')
        
        meta_image = soup.find('meta', {'property': 'og:image'})
        if meta_image:
            data['profile_image'] = meta_image.get('content')
        
        return data
    except Exception as e:
        print(f"  [!] Twitter extraction error: {e}")
        return None

def download_profile_image(image_url, dest_path):
    """Download profile image from URL."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(image_url, headers=headers, timeout=10)
        with open(dest_path, 'wb') as f:
            f.write(response.content)
        return dest_path
    except Exception as e:
        print(f"  [!] Image download error: {e}")
        return None

# ==== CORE MATCHER ====
def profile_matcher(query, ref_image_path=None, num_results=10):
    """Main profile + image scraping logic with face detection."""
    print(f"\n🔍 Searching for: {query}")
    
    # Search LinkedIn first
    print("\n📊 Searching LinkedIn profiles...")
    linkedin_results = search_linkedin_profile(query)
    
    # Search other social media
    print("📱 Searching social media profiles...")
    social_results = search_social_media_profiles(query)
    
    # Combine results
    results = linkedin_results + social_results
    
    if not results:
        print("⚠️ No results found.")
        return []

    # Process reference image if provided
    ref_embedding = None
    ref_faces = []
    if ref_image_path and os.path.exists(ref_image_path):
        print(f"\n📸 Processing reference image...")
        ref_faces = detect_faces_in_image(ref_image_path)
        ref_embedding = get_face_embedding(ref_image_path)
        if ref_faces:
            print(f"  ✓ Detected {len(ref_faces)} face(s) in reference image")
        else:
            print("  ⚠️ No faces detected in reference image")

    all_data = []
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_img_dir = os.path.join("downloads", safe_filename(query))
    os.makedirs(base_img_dir, exist_ok=True)

    for i, r in enumerate(results):
        link = r.get("link")
        title = r.get("title", "")
        snippet = r.get("snippet", "")
        domain = urlparse(link).netloc.replace("www.", "")

        print(f"\n[{i+1}/{len(results)}] Processing: {domain}")
        
        dest_folder = os.path.join(base_img_dir, domain)
        os.makedirs(dest_folder, exist_ok=True)

        row = {
            "rank": i + 1,
            "domain": domain,
            "title": title,
            "link": link,
            "snippet": snippet,
            "downloaded_images": [],
            "face_match": False,
            "face_distance": None,
            "profile_data": {}
        }

        # Extract profile data based on platform
        if 'linkedin.com' in domain:
            profile_data = extract_linkedin_data(link)
            if profile_data:
                row['profile_data'] = profile_data
                # Download profile image
                if profile_data.get('profile_image'):
                    img_path = os.path.join(dest_folder, 'profile.jpg')
                    if download_profile_image(profile_data['profile_image'], img_path):
                        row['downloaded_images'].append(img_path)
        
        elif 'instagram.com' in domain:
            # Extract username from URL
            username = link.split('instagram.com/')[-1].strip('/')
            profile_data = extract_instagram_data(username)
            if profile_data:
                row['profile_data'] = profile_data
                if profile_data.get('profile_image'):
                    img_path = os.path.join(dest_folder, 'profile.jpg')
                    if download_profile_image(profile_data['profile_image'], img_path):
                        row['downloaded_images'].append(img_path)
        
        elif 'twitter.com' in domain or 'x.com' in domain:
            username = link.split('/')[-1].strip('/')
            profile_data = extract_twitter_data(username)
            if profile_data:
                row['profile_data'] = profile_data
                if profile_data.get('profile_image'):
                    img_path = os.path.join(dest_folder, 'profile.jpg')
                    if download_profile_image(profile_data['profile_image'], img_path):
                        row['downloaded_images'].append(img_path)

        # Download additional images from the page
        page_imgs = download_images_from_page(link, dest_folder, limit=3)
        row['downloaded_images'].extend(page_imgs)
        
        if row['downloaded_images']:
            print(f"  ✓ Downloaded {len(row['downloaded_images'])} image(s)")
            
            # Compare faces if reference image provided
            if ref_image_path and ref_embedding:
                for img_path in row['downloaded_images']:
                    try:
                        verified, distance = verify_faces(ref_image_path, img_path)
                        if verified:
                            row['face_match'] = True
                            row['face_distance'] = distance
                            print(f"  ✅ FACE MATCH! Distance: {distance:.4f}")
                            break
                        elif distance < 0.6:  # Close match
                            row['face_distance'] = distance
                            print(f"  ⚠️ Possible match. Distance: {distance:.4f}")
                    except Exception as e:
                        continue

        all_data.append(row)
        sleep(0.5)  # Rate limiting

    # Save results
    os.makedirs("outputs", exist_ok=True)
    csv_path = f"outputs/matches_{safe_filename(query)}_{ts}.csv"
    
    # Flatten profile_data for CSV
    csv_data = []
    for row in all_data:
        csv_row = {k: v for k, v in row.items() if k != 'profile_data'}
        csv_row['downloaded_images'] = '; '.join(row['downloaded_images'])
        csv_row.update({f'profile_{k}': v for k, v in row.get('profile_data', {}).items()})
        csv_data.append(csv_row)
    
    pd.DataFrame(csv_data).to_csv(csv_path, index=False)
    print(f"\n💾 Saved results to: {csv_path}")
    
    # Save detailed JSON
    json_path = f"outputs/matches_{safe_filename(query)}_{ts}.json"
    with open(json_path, 'w') as f:
        json.dump(all_data, f, indent=2)
    print(f"💾 Saved detailed results to: {json_path}")

    return all_data

# ==== GEMINI ANALYSIS ====
def analyze_results_with_gemini(results, query):
    """Summarize scraped results with Gemini."""
    if not results:
        print("⚠️ Nothing to analyze.")
        return
    
    # Create detailed summary
    summary_parts = []
    for r in results:
        part = f"**{r['title']}** ({r['domain']})\n"
        part += f"Link: {r['link']}\n"
        part += f"Snippet: {r['snippet']}\n"
        
        if r.get('face_match'):
            part += f"✅ FACE MATCH (distance: {r['face_distance']:.4f})\n"
        
        if r.get('profile_data'):
            part += f"Profile Data: {json.dumps(r['profile_data'], indent=2)}\n"
        
        part += f"Images: {len(r['downloaded_images'])}\n"
        summary_parts.append(part)
    
    text_summary = "\n---\n".join(summary_parts)
    
    prompt = f"""Analyze the following search results for '{query}'. 
    
Focus on:
1. Which profiles likely belong to the same person
2. Consistency in information across platforms
3. Any face matches found
4. Summary of the person's online presence

Results:
{text_summary}
"""

    try:
        resp = model.generate_content(prompt)
        print("\n🤖 Gemini Analysis:\n")
        print(resp.text)
    except Exception as e:
        print(f"Gemini error: {e}")

# ==== MAIN INTERFACE ====
if __name__ == "__main__":
    print("=== 🔍 Smart Profile Finder with Face Detection (DeepFace) ===")
    print("Supports: LinkedIn, Instagram, Facebook, Twitter/X")
    print("\nFeatures:")
    print("  • Face detection and verification using DeepFace")
    print("  • Profile data extraction from social media")
    print("  • Image downloading from discovered profiles")
    print("  • AI-powered analysis with Gemini")

    while True:
        print("\n" + "="*60)
        query = input("\nEnter person name/info (or 'exit' to quit): ").strip()
        if query.lower() == "exit":
            break

        img_path = input("Reference image path (optional, press Enter to skip): ").strip() or None
        
        if img_path and not os.path.exists(img_path):
            print(f"⚠️ Image file not found: {img_path}")
            img_path = None

        print("\n🚀 Starting search...")
        data = profile_matcher(query, img_path)
        
        if data:
            print(f"\n✅ Found {len(data)} results")
            
            # Show face matches
            face_matches = [r for r in data if r.get('face_match')]
            if face_matches:
                print(f"\n🎯 {len(face_matches)} profile(s) with face matches:")
                for match in face_matches:
                    print(f"  • {match['title']} - {match['link']}")
            
            # Analyze with Gemini
            analyze_results_with_gemini(data, query)
        else:
            print("\n❌ No results found")

    print("\n👋 Goodbye!")
