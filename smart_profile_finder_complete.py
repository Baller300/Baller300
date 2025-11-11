#!/usr/bin/env python3
"""
Smart Profile Finder with Face Detection - Complete Script
===========================================================

A comprehensive tool that searches for social media profiles across multiple platforms
(LinkedIn, Instagram, Facebook, Twitter) and uses DeepFace AI for face detection and 
verification to match profiles with reference images.

Features:
- Multi-platform profile search (LinkedIn, Instagram, Facebook, Twitter/X)
- AI-powered face detection using DeepFace with RetinaFace
- Face verification and matching with reference images
- Profile data extraction (name, bio, headline, location, images)
- Automatic image downloading from discovered profiles
- AI analysis using Google Gemini
- Detailed CSV and JSON reports with match confidence scores
- Reverse image search capability
- Rate limiting and error handling

Requirements:
- Python 3.8+
- SERPAPI_KEY environment variable (get from https://serpapi.com/)
- GEMINI_API_KEY environment variable (get from https://makersuite.google.com/)

Usage:
    python smart_profile_finder_complete.py

Author: Uday Kashyap
Version: 2.0
Last Updated: November 2025
"""

import os
import re
import json
import requests
import pandas as pd
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
import sys
from typing import List, Dict, Optional, Tuple, Any

# ============================================================================
# CONFIGURATION
# ============================================================================

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Validate API keys
if not SERPAPI_KEY or not GEMINI_API_KEY:
    print("❌ ERROR: Missing required API keys!")
    print("\nPlease set the following environment variables:")
    print("  export SERPAPI_KEY='your_serpapi_key_here'")
    print("  export GEMINI_API_KEY='your_gemini_api_key_here'")
    print("\nGet your keys from:")
    print("  - SerpAPI: https://serpapi.com/")
    print("  - Gemini: https://makersuite.google.com/app/apikey")
    sys.exit(1)

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-exp")

# Configuration constants
FACE_MATCH_THRESHOLD = 0.6  # Lower = stricter matching
FACE_DETECTION_MODEL = 'retinaface'  # Options: opencv, ssd, dlib, mtcnn, retinaface, mediapipe
FACE_RECOGNITION_MODEL = 'Facenet512'  # Options: VGG-Face, Facenet, Facenet512, OpenFace, DeepFace, DeepID, ArcFace, Dlib
REQUEST_DELAY = 0.5  # Seconds between requests (rate limiting)
MAX_IMAGES_PER_PAGE = 3  # Maximum images to download per profile page
DEFAULT_NUM_RESULTS = 10  # Default number of search results

# User agent for web requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def safe_filename(s: str) -> str:
    """
    Convert string to safe filename by removing invalid characters.
    
    Args:
        s: Input string
        
    Returns:
        Safe filename string
    """
    return re.sub(r'[\\/*?:"<>|]', "_", s)


def print_banner():
    """Print application banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║     🔍 Smart Profile Finder with Face Detection (DeepFace)          ║
║                                                                      ║
║  Features:                                                           ║
║    • Multi-platform search (LinkedIn, Instagram, Facebook, Twitter) ║
║    • AI face detection and verification using DeepFace              ║
║    • Profile data extraction and image downloading                  ║
║    • AI-powered analysis with Google Gemini                         ║
║    • Detailed CSV and JSON reports                                  ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_section(title: str):
    """Print formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def print_progress(current: int, total: int, message: str):
    """Print progress indicator."""
    print(f"[{current}/{total}] {message}")


# ============================================================================
# IMAGE PROCESSING FUNCTIONS
# ============================================================================

def get_phash_from_url(url: str) -> Optional[imagehash.ImageHash]:
    """
    Compute perceptual hash from image URL.
    
    Args:
        url: Image URL
        
    Returns:
        ImageHash object or None if failed
    """
    try:
        img_data = requests.get(url, timeout=10, headers={"User-Agent": USER_AGENT}).content
        img = Image.open(BytesIO(img_data)).convert("RGB")
        return imagehash.phash(img)
    except Exception as e:
        print(f"  [!] pHash error: {e}")
        return None


def compare_phashes(p1: Optional[imagehash.ImageHash], 
                   p2: Optional[imagehash.ImageHash]) -> float:
    """
    Calculate similarity ratio between two perceptual hashes.
    
    Args:
        p1: First perceptual hash
        p2: Second perceptual hash
        
    Returns:
        Similarity ratio (0.0 to 1.0)
    """
    if not p1 or not p2:
        return 0.0
    dist = p1 - p2
    return 1.0 - dist / (len(p1.hash) ** 2)


def download_image(url: str, dest_path: str) -> Optional[str]:
    """
    Download image from URL to destination path.
    
    Args:
        url: Image URL
        dest_path: Destination file path
        
    Returns:
        Destination path if successful, None otherwise
    """
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        with open(dest_path, 'wb') as f:
            f.write(response.content)
        
        return dest_path
    except Exception as e:
        print(f"  [!] Image download error: {e}")
        return None


def download_images_from_page(url: str, dest_folder: str, 
                              limit: int = MAX_IMAGES_PER_PAGE) -> List[str]:
    """
    Download images from a webpage.
    
    Args:
        url: Page URL
        dest_folder: Destination folder for images
        limit: Maximum number of images to download
        
    Returns:
        List of downloaded image paths
    """
    try:
        headers = {"User-Agent": USER_AGENT}
        html = requests.get(url, timeout=10, headers=headers).text
    except Exception as e:
        print(f"  [!] Failed to load {url}: {e}")
        return []

    soup = BeautifulSoup(html, "html.parser")
    imgs = [img.get("src") for img in soup.find_all("img") if img.get("src")]
    saved = []

    for img_url in imgs[:limit]:
        try:
            # Handle relative URLs
            if img_url.startswith("//"):
                img_url = "https:" + img_url
            elif img_url.startswith("/"):
                parsed = urlparse(url)
                img_url = f"{parsed.scheme}://{parsed.netloc}{img_url}"
            elif not img_url.startswith("http"):
                continue

            # Download image
            img_data = requests.get(img_url, timeout=10, headers=headers).content
            
            # Generate filename
            fname = os.path.join(
                dest_folder, 
                safe_filename(os.path.basename(img_url.split("?")[0])) or f"img_{len(saved)+1}.jpg"
            )
            
            # Ensure proper extension
            if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                fname += ".jpg"
            
            # Save image
            with open(fname, "wb") as f:
                f.write(img_data)
            
            saved.append(fname)
            
        except Exception as e:
            continue

    return saved


# ============================================================================
# DEEPFACE FACE DETECTION & RECOGNITION FUNCTIONS
# ============================================================================

def detect_faces_in_image(image_path: str) -> List[Dict[str, Any]]:
    """
    Detect faces in an image using DeepFace.
    
    Args:
        image_path: Path to image file
        
    Returns:
        List of detected face dictionaries
    """
    try:
        faces = DeepFace.extract_faces(
            img_path=image_path,
            detector_backend=FACE_DETECTION_MODEL,
            enforce_detection=False
        )
        return faces
    except Exception as e:
        print(f"  [!] Face detection error: {e}")
        return []


def get_face_embedding(image_path: str, 
                       model_name: str = FACE_RECOGNITION_MODEL) -> Optional[List[float]]:
    """
    Extract face embedding from image using DeepFace.
    
    Args:
        image_path: Path to image file
        model_name: Face recognition model to use
        
    Returns:
        Face embedding vector or None if failed
    """
    try:
        embedding = DeepFace.represent(
            img_path=image_path,
            model_name=model_name,
            detector_backend=FACE_DETECTION_MODEL,
            enforce_detection=False
        )
        return embedding[0]['embedding'] if embedding else None
    except Exception as e:
        print(f"  [!] Embedding error: {e}")
        return None


def verify_faces(img1_path: str, img2_path: str, 
                model_name: str = FACE_RECOGNITION_MODEL) -> Tuple[bool, float]:
    """
    Verify if two images contain the same person using DeepFace.
    
    Args:
        img1_path: Path to first image
        img2_path: Path to second image
        model_name: Face recognition model to use
        
    Returns:
        Tuple of (verified: bool, distance: float)
    """
    try:
        result = DeepFace.verify(
            img1_path=img1_path,
            img2_path=img2_path,
            model_name=model_name,
            detector_backend=FACE_DETECTION_MODEL,
            enforce_detection=False
        )
        return result['verified'], result['distance']
    except Exception as e:
        print(f"  [!] Verification error: {e}")
        return False, 1.0


def find_similar_faces(reference_image: str, image_folder: str, 
                      threshold: float = FACE_MATCH_THRESHOLD) -> List[Dict[str, Any]]:
    """
    Find images with similar faces in a folder.
    
    Args:
        reference_image: Path to reference image
        image_folder: Folder containing images to compare
        threshold: Distance threshold for matching
        
    Returns:
        List of matching images with distances
    """
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


# ============================================================================
# SEARCH FUNCTIONS (SERPAPI)
# ============================================================================

def fetch_profiles(query: str, num: int = DEFAULT_NUM_RESULTS) -> List[Dict[str, Any]]:
    """
    Fetch Google search results using SerpAPI.
    
    Args:
        query: Search query
        num: Number of results to fetch
        
    Returns:
        List of search result dictionaries
    """
    params = {
        "engine": "google",
        "q": query,
        "num": num,
        "api_key": SERPAPI_KEY
    }
    
    try:
        resp = requests.get("https://serpapi.com/search.json", params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("organic_results", [])
    except Exception as e:
        print(f"  [!] SerpAPI error: {e}")
        return []


def search_linkedin_profile(name: str, company: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search for LinkedIn profiles.
    
    Args:
        name: Person's name
        company: Optional company name
        
    Returns:
        List of LinkedIn profile search results
    """
    query = f'site:linkedin.com/in/ "{name}"'
    if company:
        query += f' "{company}"'
    
    return fetch_profiles(query, num=5)


def search_social_media_profiles(name: str, 
                                 platform: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search for social media profiles across platforms.
    
    Args:
        name: Person's name
        platform: Optional specific platform (instagram, facebook, twitter, linkedin)
        
    Returns:
        List of social media profile search results
    """
    platforms = ['instagram', 'facebook', 'twitter', 'linkedin'] if not platform else [platform]
    all_results = []
    
    for plat in platforms:
        query = f'site:{plat}.com "{name}"'
        results = fetch_profiles(query, num=3)
        all_results.extend(results)
        sleep(REQUEST_DELAY)
    
    return all_results


def reverse_image_search(image_path: str) -> List[Dict[str, Any]]:
    """
    Perform reverse image search using SerpAPI.
    
    Note: This is a placeholder. Full implementation requires uploading
    the image to a public URL or using SerpAPI's Google Lens API.
    
    Args:
        image_path: Path to image file
        
    Returns:
        List of reverse image search results
    """
    print("  [i] Reverse image search requires image URL. Feature not fully implemented.")
    return []


# ============================================================================
# PROFILE DATA EXTRACTION FUNCTIONS
# ============================================================================

def extract_linkedin_data(url: str) -> Optional[Dict[str, Any]]:
    """
    Extract data from LinkedIn profile (public view).
    
    Args:
        url: LinkedIn profile URL
        
    Returns:
        Dictionary with profile data or None if failed
    """
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {
            'url': url,
            'name': None,
            'headline': None,
            'location': None,
            'profile_image': None
        }
        
        # Extract name
        name_tag = soup.find('h1', {'class': lambda x: x and 'name' in x.lower()})
        if name_tag:
            data['name'] = name_tag.get_text(strip=True)
        
        # Extract headline
        headline_tag = soup.find('div', {'class': lambda x: x and 'headline' in x.lower()})
        if headline_tag:
            data['headline'] = headline_tag.get_text(strip=True)
        
        # Extract profile image
        img_tag = soup.find('img', {'class': lambda x: x and 'profile' in x.lower()})
        if img_tag and img_tag.get('src'):
            data['profile_image'] = img_tag['src']
        
        return data
    except Exception as e:
        print(f"  [!] LinkedIn extraction error: {e}")
        return None


def extract_instagram_data(username: str) -> Optional[Dict[str, Any]]:
    """
    Extract data from Instagram profile (public view).
    
    Args:
        username: Instagram username
        
    Returns:
        Dictionary with profile data or None if failed
    """
    try:
        url = f'https://www.instagram.com/{username}/'
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {
            'url': url,
            'username': username,
            'name': None,
            'bio': None,
            'profile_image': None
        }
        
        # Extract from meta tags
        meta_description = soup.find('meta', {'property': 'og:description'})
        if meta_description:
            data['bio'] = meta_description.get('content', '')
        
        meta_image = soup.find('meta', {'property': 'og:image'})
        if meta_image:
            data['profile_image'] = meta_image.get('content')
        
        return data
    except Exception as e:
        print(f"  [!] Instagram extraction error: {e}")
        return None


def extract_twitter_data(username: str) -> Optional[Dict[str, Any]]:
    """
    Extract data from Twitter/X profile (public view).
    
    Args:
        username: Twitter username
        
    Returns:
        Dictionary with profile data or None if failed
    """
    try:
        url = f'https://twitter.com/{username}'
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {
            'url': url,
            'username': username,
            'name': None,
            'bio': None,
            'profile_image': None
        }
        
        # Extract from meta tags
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


def extract_facebook_data(url: str) -> Optional[Dict[str, Any]]:
    """
    Extract data from Facebook profile (public view).
    
    Args:
        url: Facebook profile URL
        
    Returns:
        Dictionary with profile data or None if failed
    """
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {
            'url': url,
            'name': None,
            'bio': None,
            'profile_image': None
        }
        
        # Extract from meta tags
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
        print(f"  [!] Facebook extraction error: {e}")
        return None


# ============================================================================
# CORE PROFILE MATCHING FUNCTION
# ============================================================================

def profile_matcher(query: str, 
                   ref_image_path: Optional[str] = None,
                   num_results: int = DEFAULT_NUM_RESULTS) -> List[Dict[str, Any]]:
    """
    Main profile matching function with face detection and verification.
    
    This function:
    1. Searches for profiles across multiple platforms
    2. Downloads profile images and page images
    3. Extracts profile data (name, bio, headline, etc.)
    4. Performs face matching if reference image provided
    5. Generates detailed reports (CSV and JSON)
    
    Args:
        query: Search query (person name, username, etc.)
        ref_image_path: Optional path to reference image for face matching
        num_results: Number of search results to process
        
    Returns:
        List of profile dictionaries with match results
    """
    print_section(f"🔍 Searching for: {query}")
    
    # Search LinkedIn profiles
    print("\n📊 Searching LinkedIn profiles...")
    linkedin_results = search_linkedin_profile(query)
    print(f"  ✓ Found {len(linkedin_results)} LinkedIn results")
    
    # Search other social media platforms
    print("\n📱 Searching social media profiles...")
    social_results = search_social_media_profiles(query)
    print(f"  ✓ Found {len(social_results)} social media results")
    
    # Combine all results
    results = linkedin_results + social_results
    
    if not results:
        print("\n⚠️ No results found.")
        return []
    
    print(f"\n✅ Total results found: {len(results)}")
    
    # Process reference image if provided
    ref_embedding = None
    ref_faces = []
    
    if ref_image_path and os.path.exists(ref_image_path):
        print(f"\n📸 Processing reference image: {ref_image_path}")
        ref_faces = detect_faces_in_image(ref_image_path)
        ref_embedding = get_face_embedding(ref_image_path)
        
        if ref_faces:
            print(f"  ✓ Detected {len(ref_faces)} face(s) in reference image")
        else:
            print("  ⚠️ No faces detected in reference image")
    
    # Setup directories
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_img_dir = os.path.join("downloads", safe_filename(query))
    os.makedirs(base_img_dir, exist_ok=True)
    
    all_data = []
    
    # Process each search result
    print(f"\n{'='*70}")
    print("Processing search results...")
    print(f"{'='*70}")
    
    for i, result in enumerate(results):
        link = result.get("link")
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        domain = urlparse(link).netloc.replace("www.", "")
        
        print_progress(i + 1, len(results), f"Processing: {domain}")
        
        # Create domain-specific folder
        dest_folder = os.path.join(base_img_dir, domain)
        os.makedirs(dest_folder, exist_ok=True)
        
        # Initialize result row
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
                if profile_data.get('profile_image'):
                    img_path = os.path.join(dest_folder, 'profile.jpg')
                    if download_image(profile_data['profile_image'], img_path):
                        row['downloaded_images'].append(img_path)
        
        elif 'instagram.com' in domain:
            username = link.split('instagram.com/')[-1].strip('/')
            profile_data = extract_instagram_data(username)
            if profile_data:
                row['profile_data'] = profile_data
                if profile_data.get('profile_image'):
                    img_path = os.path.join(dest_folder, 'profile.jpg')
                    if download_image(profile_data['profile_image'], img_path):
                        row['downloaded_images'].append(img_path)
        
        elif 'twitter.com' in domain or 'x.com' in domain:
            username = link.split('/')[-1].strip('/')
            profile_data = extract_twitter_data(username)
            if profile_data:
                row['profile_data'] = profile_data
                if profile_data.get('profile_image'):
                    img_path = os.path.join(dest_folder, 'profile.jpg')
                    if download_image(profile_data['profile_image'], img_path):
                        row['downloaded_images'].append(img_path)
        
        elif 'facebook.com' in domain:
            profile_data = extract_facebook_data(link)
            if profile_data:
                row['profile_data'] = profile_data
                if profile_data.get('profile_image'):
                    img_path = os.path.join(dest_folder, 'profile.jpg')
                    if download_image(profile_data['profile_image'], img_path):
                        row['downloaded_images'].append(img_path)
        
        # Download additional images from the page
        page_imgs = download_images_from_page(link, dest_folder, limit=MAX_IMAGES_PER_PAGE)
        row['downloaded_images'].extend(page_imgs)
        
        if row['downloaded_images']:
            print(f"  ✓ Downloaded {len(row['downloaded_images'])} image(s)")
            
            # Perform face matching if reference image provided
            if ref_image_path and ref_embedding:
                for img_path in row['downloaded_images']:
                    try:
                        verified, distance = verify_faces(ref_image_path, img_path)
                        
                        if verified:
                            row['face_match'] = True
                            row['face_distance'] = distance
                            print(f"  ✅ FACE MATCH! Distance: {distance:.4f}")
                            break
                        elif distance < FACE_MATCH_THRESHOLD:
                            row['face_distance'] = distance
                            print(f"  ⚠️ Possible match. Distance: {distance:.4f}")
                    except Exception as e:
                        continue
        
        all_data.append(row)
        sleep(REQUEST_DELAY)  # Rate limiting
    
    # Save results
    print(f"\n{'='*70}")
    print("Saving results...")
    print(f"{'='*70}")
    
    os.makedirs("outputs", exist_ok=True)
    
    # Save CSV report
    csv_path = f"outputs/matches_{safe_filename(query)}_{timestamp}.csv"
    csv_data = []
    
    for row in all_data:
        csv_row = {k: v for k, v in row.items() if k != 'profile_data'}
        csv_row['downloaded_images'] = '; '.join(row['downloaded_images'])
        csv_row.update({f'profile_{k}': v for k, v in row.get('profile_data', {}).items()})
        csv_data.append(csv_row)
    
    pd.DataFrame(csv_data).to_csv(csv_path, index=False)
    print(f"💾 CSV report saved: {csv_path}")
    
    # Save JSON report
    json_path = f"outputs/matches_{safe_filename(query)}_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    print(f"💾 JSON report saved: {json_path}")
    
    return all_data


# ============================================================================
# AI ANALYSIS FUNCTION (GEMINI)
# ============================================================================

def analyze_results_with_gemini(results: List[Dict[str, Any]], query: str):
    """
    Analyze search results using Google Gemini AI.
    
    Args:
        results: List of profile search results
        query: Original search query
    """
    if not results:
        print("\n⚠️ No results to analyze.")
        return
    
    print_section("🤖 AI Analysis (Google Gemini)")
    
    # Create detailed summary for Gemini
    summary_parts = []
    
    for r in results:
        part = f"**{r['title']}** ({r['domain']})\n"
        part += f"Link: {r['link']}\n"
        part += f"Snippet: {r['snippet']}\n"
        
        if r.get('face_match'):
            part += f"✅ FACE MATCH (distance: {r['face_distance']:.4f})\n"
        elif r.get('face_distance'):
            part += f"⚠️ Possible match (distance: {r['face_distance']:.4f})\n"
        
        if r.get('profile_data'):
            part += f"Profile Data: {json.dumps(r['profile_data'], indent=2)}\n"
        
        part += f"Images Downloaded: {len(r['downloaded_images'])}\n"
        summary_parts.append(part)
    
    text_summary = "\n---\n".join(summary_parts)
    
    # Create prompt for Gemini
    prompt = f"""Analyze the following search results for '{query}'.

Focus on:
1. Which profiles likely belong to the same person
2. Consistency in information across platforms
3. Any face matches found and their reliability
4. Summary of the person's online presence
5. Recommendations for further investigation

Search Results:
{text_summary}

Please provide a comprehensive analysis with clear sections and actionable insights.
"""
    
    try:
        print("\n⏳ Analyzing with Gemini AI...")
        response = model.generate_content(prompt)
        print("\n" + "="*70)
        print(response.text)
        print("="*70)
    except Exception as e:
        print(f"\n❌ Gemini analysis error: {e}")


# ============================================================================
# INTERACTIVE MENU FUNCTIONS
# ============================================================================

def display_menu():
    """Display main menu options."""
    menu = """
╔══════════════════════════════════════════════════════════════════════╗
║                           MAIN MENU                                  ║
╠══════════════════════════════════════════════════════════════════════╣
║  1. Search profiles (with optional face matching)                    ║
║  2. Search LinkedIn profiles only                                    ║
║  3. Search specific social media platform                            ║
║  4. Verify faces between two images                                  ║
║  5. Detect faces in an image                                         ║
║  6. Find similar faces in folder                                     ║
║  7. View configuration                                               ║
║  8. Exit                                                             ║
╚══════════════════════════════════════════════════════════════════════╝
    """
    print(menu)


def option_1_search_profiles():
    """Option 1: Search profiles with optional face matching."""
    print_section("Search Profiles")
    
    query = input("\nEnter person name/info: ").strip()
    if not query:
        print("❌ Query cannot be empty")
        return
    
    ref_image = input("Reference image path (optional, press Enter to skip): ").strip() or None
    
    if ref_image and not os.path.exists(ref_image):
        print(f"⚠️ Image file not found: {ref_image}")
        ref_image = None
    
    num_results = input(f"Number of results (default {DEFAULT_NUM_RESULTS}): ").strip()
    num_results = int(num_results) if num_results.isdigit() else DEFAULT_NUM_RESULTS
    
    print("\n🚀 Starting search...")
    results = profile_matcher(query, ref_image, num_results)
    
    if results:
        print(f"\n✅ Search completed! Found {len(results)} results")
        
        # Show face matches
        face_matches = [r for r in results if r.get('face_match')]
        if face_matches:
            print(f"\n🎯 {len(face_matches)} profile(s) with face matches:")
            for match in face_matches:
                print(f"  • {match['title']}")
                print(f"    Distance: {match['face_distance']:.4f}")
                print(f"    {match['link']}")
        
        # Ask for AI analysis
        analyze = input("\n🤖 Analyze results with Gemini AI? (y/n): ").strip().lower()
        if analyze == 'y':
            analyze_results_with_gemini(results, query)
    else:
        print("\n❌ No results found")


def option_2_linkedin_search():
    """Option 2: Search LinkedIn profiles only."""
    print_section("LinkedIn Profile Search")
    
    name = input("\nEnter person name: ").strip()
    if not name:
        print("❌ Name cannot be empty")
        return
    
    company = input("Company name (optional, press Enter to skip): ").strip() or None
    
    print("\n🚀 Searching LinkedIn...")
    results = search_linkedin_profile(name, company)
    
    if results:
        print(f"\n✅ Found {len(results)} LinkedIn profiles:")
        for i, r in enumerate(results, 1):
            print(f"\n{i}. {r['title']}")
            print(f"   {r['link']}")
            print(f"   {r.get('snippet', '')[:100]}...")
    else:
        print("\n❌ No LinkedIn profiles found")


def option_3_platform_search():
    """Option 3: Search specific social media platform."""
    print_section("Platform-Specific Search")
    
    print("\nAvailable platforms:")
    print("  1. Instagram")
    print("  2. Facebook")
    print("  3. Twitter/X")
    print("  4. LinkedIn")
    print("  5. All platforms")
    
    choice = input("\nSelect platform (1-5): ").strip()
    
    platform_map = {
        '1': 'instagram',
        '2': 'facebook',
        '3': 'twitter',
        '4': 'linkedin',
        '5': None
    }
    
    platform = platform_map.get(choice)
    if choice not in platform_map:
        print("❌ Invalid choice")
        return
    
    name = input("\nEnter person name: ").strip()
    if not name:
        print("❌ Name cannot be empty")
        return
    
    print(f"\n🚀 Searching {platform or 'all platforms'}...")
    results = search_social_media_profiles(name, platform)
    
    if results:
        print(f"\n✅ Found {len(results)} profiles:")
        for i, r in enumerate(results, 1):
            print(f"\n{i}. {r['title']}")
            print(f"   {r['link']}")
            print(f"   {r.get('snippet', '')[:100]}...")
    else:
        print("\n❌ No profiles found")


def option_4_verify_faces():
    """Option 4: Verify faces between two images."""
    print_section("Face Verification")
    
    img1 = input("\nFirst image path: ").strip()
    img2 = input("Second image path: ").strip()
    
    if not os.path.exists(img1):
        print(f"❌ Image not found: {img1}")
        return
    
    if not os.path.exists(img2):
        print(f"❌ Image not found: {img2}")
        return
    
    print("\n🔍 Comparing faces...")
    verified, distance = verify_faces(img1, img2)
    
    print(f"\n{'='*70}")
    print("Results:")
    print(f"  Verified: {verified}")
    print(f"  Distance: {distance:.4f}")
    print(f"  Threshold: {FACE_MATCH_THRESHOLD}")
    
    if verified:
        print("\n  ✅ Same person!")
    else:
        print("\n  ❌ Different persons")
    print(f"{'='*70}")


def option_5_detect_faces():
    """Option 5: Detect faces in an image."""
    print_section("Face Detection")
    
    image_path = input("\nImage path: ").strip()
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    print("\n🔍 Detecting faces...")
    faces = detect_faces_in_image(image_path)
    
    if faces:
        print(f"\n✅ Detected {len(faces)} face(s):")
        for i, face in enumerate(faces, 1):
            print(f"\nFace {i}:")
            print(f"  Confidence: {face.get('confidence', 'N/A')}")
            print(f"  Region: {face.get('facial_area', 'N/A')}")
    else:
        print("\n❌ No faces detected")


def option_6_find_similar():
    """Option 6: Find similar faces in folder."""
    print_section("Find Similar Faces")
    
    ref_image = input("\nReference image path: ").strip()
    folder = input("Folder to search: ").strip()
    
    if not os.path.exists(ref_image):
        print(f"❌ Reference image not found: {ref_image}")
        return
    
    if not os.path.isdir(folder):
        print(f"❌ Folder not found: {folder}")
        return
    
    threshold = input(f"Match threshold (default {FACE_MATCH_THRESHOLD}): ").strip()
    threshold = float(threshold) if threshold else FACE_MATCH_THRESHOLD
    
    print("\n🔍 Searching for similar faces...")
    similar = find_similar_faces(ref_image, folder, threshold)
    
    if similar:
        print(f"\n✅ Found {len(similar)} similar face(s):")
        for i, match in enumerate(similar, 1):
            print(f"\n{i}. {os.path.basename(match['path'])}")
            print(f"   Distance: {match['distance']:.4f}")
            print(f"   Verified: {match['verified']}")
    else:
        print("\n❌ No similar faces found")


def option_7_view_config():
    """Option 7: View configuration."""
    print_section("Current Configuration")
    
    config = f"""
Face Detection Model:     {FACE_DETECTION_MODEL}
Face Recognition Model:   {FACE_RECOGNITION_MODEL}
Face Match Threshold:     {FACE_MATCH_THRESHOLD}
Request Delay:            {REQUEST_DELAY}s
Max Images Per Page:      {MAX_IMAGES_PER_PAGE}
Default Num Results:      {DEFAULT_NUM_RESULTS}

API Keys:
  SerpAPI:                {'✓ Set' if SERPAPI_KEY else '✗ Not set'}
  Gemini:                 {'✓ Set' if GEMINI_API_KEY else '✗ Not set'}

Directories:
  Downloads:              ./downloads/
  Outputs:                ./outputs/
    """
    print(config)


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main application entry point."""
    print_banner()
    
    # Check API keys
    if not SERPAPI_KEY or not GEMINI_API_KEY:
        print("\n❌ ERROR: Missing API keys!")
        print("Please set SERPAPI_KEY and GEMINI_API_KEY environment variables.")
        return
    
    print("\n✅ API keys configured")
    print("✅ DeepFace initialized")
    print("✅ Ready to search!")
    
    # Main menu loop
    while True:
        display_menu()
        
        choice = input("Select option (1-8): ").strip()
        
        if choice == '1':
            option_1_search_profiles()
        elif choice == '2':
            option_2_linkedin_search()
        elif choice == '3':
            option_3_platform_search()
        elif choice == '4':
            option_4_verify_faces()
        elif choice == '5':
            option_5_detect_faces()
        elif choice == '6':
            option_6_find_similar()
        elif choice == '7':
            option_7_view_config()
        elif choice == '8':
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid option. Please try again.")
        
        input("\nPress Enter to continue...")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
