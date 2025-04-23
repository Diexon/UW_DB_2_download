import os
import sys
import argparse
import requests
import img2pdf
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from PIL import Image
from io import BytesIO


def is_valid_url(url):
    """Check if a URL is valid"""
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def download_image(url):
    """Download an image from a URL and return it as bytes"""
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()

        # Check if content is actually an image
        content_type = response.headers.get("content-type", "")
        if "image" not in content_type:
            print(f"URL does not point to an image (Content-Type: {content_type})")
            return None

        return response.content

    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")
        return None


def create_pdf(images_data, output_path):
    """Create a PDF from a list of image data"""
    try:
        # Convert images to PDF
        with open(output_path, "wb") as f:
            f.write(img2pdf.convert(images_data))

        print(f"Successfully created PDF: {output_path}")
        return True
    except Exception as e:
        print(f"Failed to create PDF: {e}")
        return False


def find_and_process_images(target_url, output_pdf, class_name="mb-4 cardviewcard"):
    """
    Navigate through a webpage's HTML to find images within specific class
    and save them to a PDF
    """
    try:
        # Fetch the page with a timeout
        print(f"Fetching page: {target_url}")
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(target_url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all containers with the specified class
        containers = soup.find_all(class_=class_name)

        if not containers:
            print(f"No containers found with class: '{class_name}'")
            return False

        print(f"Found {len(containers)} containers with class '{class_name}'")

        # Find all images within these containers
        images_data = []
        downloaded_count = 0

        for i, container in enumerate(containers, 1):
            img_tags = container.find_all("img")

            if not img_tags:
                print(f"No images found in container {i}")
                continue

            for img in img_tags:
                img_url = img.get("src") or img.get("data-src")
                if not img_url:
                    continue

                # Make URL absolute
                img_url = urljoin(target_url, img_url)

                if not is_valid_url(img_url):
                    print(f"Invalid image URL: {img_url}")
                    continue

                print(f"Downloading image {downloaded_count + 1}: {img_url}")
                image_data = download_image(img_url)
                if image_data:
                    images_data.append(image_data)
                    downloaded_count += 1

        if not images_data:
            print("No images were downloaded")
            return False

        print(f"\nCreating PDF with {downloaded_count} images...")
        return create_pdf(images_data, output_pdf)

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Download images from specific HTML containers and save as PDF"
    )
    parser.add_argument("url", help="URL of the webpage to scan")
    parser.add_argument(
        "--output",
        "-o",
        default="output.pdf",
        help="Output PDF filename (default: output.pdf)",
    )
    parser.add_argument(
        "--class",
        "-c",
        dest="class_name",
        default="mb-4 cardviewcard",
        help="HTML class name to search for image containers",
    )

    args = parser.parse_args()

    if not is_valid_url(args.url):
        print(f"Error: Invalid URL provided - {args.url}", file=sys.stderr)
        sys.exit(1)

    success = find_and_process_images(
        target_url=args.url, output_pdf=args.output, class_name=args.class_name
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
