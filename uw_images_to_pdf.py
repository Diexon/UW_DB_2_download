import os
import sys
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def is_valid_url(url):
    """Check if a URL is valid"""
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def download_image(url, save_path):
    """Download an image from a URL and save it locally"""
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        # Check if content is actually an image
        content_type = response.headers.get('content-type', '')
        if 'image' not in content_type:
            print(f"URL does not point to an image (Content-Type: {content_type})")
            return False
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        
        print(f"Successfully downloaded: {save_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")
        return False

def find_and_download_images(target_url, save_dir='downloaded_images', class_name='mb-4 cardviewcard'):
    """
    Navigate through a webpage's HTML to find and download images within specific class
    """
    try:
        # Create save directory if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)
        
        # Fetch the page with a timeout
        print(f"Fetching page: {target_url}")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(target_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all containers with the specified class
        containers = soup.find_all(class_=class_name)
        
        if not containers:
            print(f"No containers found with class: '{class_name}'")
            return False
        
        print(f"Found {len(containers)} containers with class '{class_name}'")
        
        # Find all images within these containers
        downloaded_count = 0
        for i, container in enumerate(containers, 1):
            img_tags = container.find_all('img')
            
            if not img_tags:
                print(f"No images found in container {i}")
                continue
            
            for img in img_tags:
                img_url = img.get('src') or img.get('data-src')
                if not img_url:
                    continue
                
                # Make URL absolute
                img_url = urljoin(target_url, img_url)
                
                if not is_valid_url(img_url):
                    print(f"Invalid image URL: {img_url}")
                    continue
                
                # Generate filename
                img_filename = os.path.basename(urlparse(img_url).path)
                if not img_filename:
                    img_filename = f"image_{downloaded_count + 1}.jpg"
                
                save_path = os.path.join(save_dir, img_filename)
                
                # Avoid overwriting existing files
                counter = 1
                while os.path.exists(save_path):
                    name, ext = os.path.splitext(img_filename)
                    save_path = os.path.join(save_dir, f"{name}_{counter}{ext}")
                    counter += 1
                
                print(f"Downloading image {downloaded_count + 1}: {img_url}")
                if download_image(img_url, save_path):
                    downloaded_count += 1
        
        print(f"\nDownload complete. {downloaded_count} images saved to {save_dir}")
        return downloaded_count > 0
        
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description='Download images from specific HTML containers')
    parser.add_argument('url', help='URL of the webpage to scan')
    parser.add_argument('--output', '-o', default='downloaded_images',
                      help='Output directory for downloaded images')
    parser.add_argument('--class', '-c', dest='class_name', default='mb-4 cardviewcard',
                      help='HTML class name to search for image containers')
    
    args = parser.parse_args()
    
    if not is_valid_url(args.url):
        print(f"Error: Invalid URL provided - {args.url}", file=sys.stderr)
        sys.exit(1)
    
    success = find_and_download_images(
        target_url=args.url,
        save_dir=args.output,
        class_name=args.class_name
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()