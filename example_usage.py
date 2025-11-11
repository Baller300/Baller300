#!/usr/bin/env python3
"""
Example usage of the profile_finder.py script
Demonstrates various use cases and features
"""

import os
from profile_finder import (
    profile_matcher,
    search_linkedin_profile,
    search_social_media_profiles,
    verify_faces,
    get_face_embedding,
    detect_faces_in_image,
    extract_linkedin_data,
    extract_instagram_data,
    extract_twitter_data
)

def example_1_basic_search():
    """Example 1: Basic profile search without face matching."""
    print("\n" + "="*60)
    print("Example 1: Basic Profile Search")
    print("="*60)
    
    query = "Elon Musk"
    print(f"Searching for: {query}")
    
    results = profile_matcher(query, ref_image_path=None, num_results=5)
    
    if results:
        print(f"\n✅ Found {len(results)} profiles")
        for r in results[:3]:
            print(f"  • {r['title']}")
            print(f"    {r['link']}")
    else:
        print("❌ No results found")

def example_2_face_matching():
    """Example 2: Profile search with face matching."""
    print("\n" + "="*60)
    print("Example 2: Profile Search with Face Matching")
    print("="*60)
    
    query = "Sundar Pichai"
    ref_image = "reference_photo.jpg"  # Replace with actual image path
    
    if not os.path.exists(ref_image):
        print(f"⚠️ Reference image not found: {ref_image}")
        print("Skipping this example. Please provide a valid image path.")
        return
    
    print(f"Searching for: {query}")
    print(f"Reference image: {ref_image}")
    
    results = profile_matcher(query, ref_image_path=ref_image, num_results=5)
    
    # Show face matches
    face_matches = [r for r in results if r.get('face_match')]
    if face_matches:
        print(f"\n🎯 Found {len(face_matches)} profile(s) with face matches:")
        for match in face_matches:
            print(f"  • {match['title']}")
            print(f"    Distance: {match['face_distance']:.4f}")
            print(f"    {match['link']}")

def example_3_linkedin_specific():
    """Example 3: LinkedIn-specific search."""
    print("\n" + "="*60)
    print("Example 3: LinkedIn-Specific Search")
    print("="*60)
    
    name = "Satya Nadella"
    company = "Microsoft"
    
    print(f"Searching LinkedIn for: {name} at {company}")
    
    results = search_linkedin_profile(name, company)
    
    if results:
        print(f"\n✅ Found {len(results)} LinkedIn profiles")
        for r in results[:3]:
            print(f"  • {r['title']}")
            print(f"    {r['link']}")
            
            # Extract detailed data
            profile_data = extract_linkedin_data(r['link'])
            if profile_data:
                print(f"    Name: {profile_data.get('name', 'N/A')}")
                print(f"    Headline: {profile_data.get('headline', 'N/A')}")

def example_4_multi_platform():
    """Example 4: Multi-platform social media search."""
    print("\n" + "="*60)
    print("Example 4: Multi-Platform Search")
    print("="*60)
    
    name = "Tim Cook"
    
    print(f"Searching all platforms for: {name}")
    
    results = search_social_media_profiles(name)
    
    if results:
        print(f"\n✅ Found {len(results)} profiles across platforms")
        
        # Group by platform
        by_platform = {}
        for r in results:
            domain = r.get('link', '').split('/')[2]
            if domain not in by_platform:
                by_platform[domain] = []
            by_platform[domain].append(r)
        
        for platform, profiles in by_platform.items():
            print(f"\n{platform}:")
            for p in profiles[:2]:
                print(f"  • {p['title']}")

def example_5_face_verification():
    """Example 5: Direct face verification between two images."""
    print("\n" + "="*60)
    print("Example 5: Face Verification")
    print("="*60)
    
    img1 = "person1.jpg"  # Replace with actual paths
    img2 = "person2.jpg"
    
    if not os.path.exists(img1) or not os.path.exists(img2):
        print(f"⚠️ Images not found")
        print("Skipping this example. Please provide valid image paths.")
        return
    
    print(f"Comparing faces:")
    print(f"  Image 1: {img1}")
    print(f"  Image 2: {img2}")
    
    verified, distance = verify_faces(img1, img2)
    
    print(f"\nResult:")
    print(f"  Verified: {verified}")
    print(f"  Distance: {distance:.4f}")
    
    if verified:
        print("  ✅ Same person!")
    else:
        print("  ❌ Different persons")

def example_6_face_detection():
    """Example 6: Detect faces in an image."""
    print("\n" + "="*60)
    print("Example 6: Face Detection")
    print("="*60)
    
    image_path = "group_photo.jpg"  # Replace with actual path
    
    if not os.path.exists(image_path):
        print(f"⚠️ Image not found: {image_path}")
        print("Skipping this example. Please provide a valid image path.")
        return
    
    print(f"Detecting faces in: {image_path}")
    
    faces = detect_faces_in_image(image_path)
    
    if faces:
        print(f"\n✅ Detected {len(faces)} face(s)")
        for i, face in enumerate(faces):
            print(f"\nFace {i+1}:")
            print(f"  Confidence: {face.get('confidence', 'N/A')}")
            print(f"  Region: {face.get('facial_area', 'N/A')}")
    else:
        print("❌ No faces detected")

def example_7_instagram_extraction():
    """Example 7: Extract Instagram profile data."""
    print("\n" + "="*60)
    print("Example 7: Instagram Profile Extraction")
    print("="*60)
    
    username = "instagram"  # Instagram's official account
    
    print(f"Extracting data for Instagram user: @{username}")
    
    data = extract_instagram_data(username)
    
    if data:
        print(f"\n✅ Profile data:")
        print(f"  Username: {data.get('username', 'N/A')}")
        print(f"  Name: {data.get('name', 'N/A')}")
        print(f"  Bio: {data.get('bio', 'N/A')[:100]}...")
        print(f"  Profile Image: {data.get('profile_image', 'N/A')[:50]}...")
    else:
        print("❌ Failed to extract data")

def example_8_twitter_extraction():
    """Example 8: Extract Twitter profile data."""
    print("\n" + "="*60)
    print("Example 8: Twitter Profile Extraction")
    print("="*60)
    
    username = "elonmusk"
    
    print(f"Extracting data for Twitter user: @{username}")
    
    data = extract_twitter_data(username)
    
    if data:
        print(f"\n✅ Profile data:")
        print(f"  Username: {data.get('username', 'N/A')}")
        print(f"  Name: {data.get('name', 'N/A')}")
        print(f"  Bio: {data.get('bio', 'N/A')[:100]}...")
        print(f"  Profile Image: {data.get('profile_image', 'N/A')[:50]}...")
    else:
        print("❌ Failed to extract data")

def main():
    """Run all examples."""
    print("="*60)
    print("Profile Finder - Example Usage")
    print("="*60)
    print("\nThis script demonstrates various features of profile_finder.py")
    print("\n⚠️ Note: Some examples require actual image files to work.")
    print("Replace placeholder paths with real images to test face matching.")
    
    # Check environment variables
    if not os.getenv("SERPAPI_KEY") or not os.getenv("GEMINI_API_KEY"):
        print("\n❌ Error: Missing API keys!")
        print("Set SERPAPI_KEY and GEMINI_API_KEY environment variables.")
        return
    
    examples = [
        ("Basic Search", example_1_basic_search),
        ("Face Matching", example_2_face_matching),
        ("LinkedIn Search", example_3_linkedin_specific),
        ("Multi-Platform", example_4_multi_platform),
        ("Face Verification", example_5_face_verification),
        ("Face Detection", example_6_face_detection),
        ("Instagram Extraction", example_7_instagram_extraction),
        ("Twitter Extraction", example_8_twitter_extraction),
    ]
    
    print("\n\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print("  0. Run all examples")
    
    choice = input("\nSelect example (0-8, or 'q' to quit): ").strip()
    
    if choice.lower() == 'q':
        return
    
    try:
        choice = int(choice)
        if choice == 0:
            for name, func in examples:
                try:
                    func()
                except Exception as e:
                    print(f"\n❌ Error in {name}: {e}")
        elif 1 <= choice <= len(examples):
            examples[choice-1][1]()
        else:
            print("Invalid choice")
    except ValueError:
        print("Invalid input")

if __name__ == "__main__":
    main()
