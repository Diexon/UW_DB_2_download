import os
import sys
import argparse
import requests
import math
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, mm
from reportlab.lib.utils import ImageReader


def is_valid_url(url):
    """Check if a URL is valid"""
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def download_image(url):
    """Download an image from a URL and return it as PIL Image"""
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()

        # Check if content is actually an image
        content_type = response.headers.get("content-type", "")
        if "image" not in content_type:
            print(f"URL does not point to an image (Content-Type: {content_type})")
            return None

        return Image.open(BytesIO(response.content))

    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")
        return None
    except Exception as e:
        print(f"Error processing image: {e}")
        return None


def create_pdf(
    images,
    output_path,
    page_size=A4,
    image_width=63 * mm,
    image_height=88 * mm,
    margin=0 * mm,
):
    """
    Create a PDF with images at specific sizes (default 63×88 mm)
    """
    try:
        c = canvas.Canvas(output_path, pagesize=page_size)
        page_width, page_height = page_size

        # Calculate how many images fit horizontally and vertically
        available_width = page_width - 2 * margin
        available_height = page_height - 2 * margin

        images_per_row = max(1, math.floor(available_width / (image_width + margin)))
        images_per_col = max(1, math.floor(available_height / (image_height + margin)))

        # Recalculate images per page based on actual fit
        actual_per_page = images_per_row * images_per_col
        print(
            f"Arranging {actual_per_page} images per page ({images_per_row}×{images_per_col})"
        )

        current_page_images = []

        for i, img in enumerate(images):
            current_page_images.append(img)

            # When we have enough images for a page, draw them
            if len(current_page_images) >= actual_per_page:
                draw_images_on_page(
                    c,
                    current_page_images,
                    images_per_row,
                    images_per_col,
                    page_width,
                    page_height,
                    image_width,
                    image_height,
                    margin,
                )
                c.showPage()
                current_page_images = []

        # Draw remaining images
        if current_page_images:
            draw_images_on_page(
                c,
                current_page_images,
                images_per_row,
                images_per_col,
                page_width,
                page_height,
                image_width,
                image_height,
                margin,
            )
            c.showPage()

        c.save()
        print(f"Successfully created PDF: {output_path}")
        return True

    except Exception as e:
        print(f"Failed to create PDF: {e}")
        return False


def draw_images_on_page(
    c,
    images,
    images_per_row,
    images_per_col,
    page_width,
    page_height,
    image_width,
    image_height,
    margin,
):
    """Draw images on a PDF page with specific dimensions"""
    for i, img in enumerate(images):
        row = i // images_per_row
        col = i % images_per_row

        # Calculate position (centered in available space)
        total_row_width = images_per_row * image_width + (images_per_row - 1) * margin
        start_x = (page_width - total_row_width) / 2 + col * (image_width + margin)

        total_col_height = images_per_col * image_height + (images_per_col - 1) * margin
        start_y = page_height - (
            (page_height - total_col_height) / 2
            + (row + 1) * image_height
            + row * margin
        )

        # Open image with PIL and create ImageReader
        img_reader = ImageReader(img)

        # Draw image with exact dimensions
        c.drawImage(
            img_reader,
            start_x,
            start_y,
            width=image_width,
            height=image_height,
            preserveAspectRatio=True,
            anchor="c",
        )


def find_and_process_images(
    target_url,
    output_pdf,
    class_name="mb-4 cardviewcard",
    image_width=63,
    image_height=88,
):
    """
    Navigate through a webpage's HTML to find images within specific class
    and save them to a PDF with specific image sizes
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
        images = []
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
                image = download_image(img_url)
                if image:
                    images.append(image)
                    downloaded_count += 1

        if not images:
            print("No images were downloaded")
            return False

        print(
            f"\nCreating PDF with {downloaded_count} images (size: {image_width}×{image_height} mm)..."
        )
        return create_pdf(
            images,
            output_pdf,
            image_width=image_width * mm,
            image_height=image_height * mm,
        )

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Download images from HTML containers and save as PDF with specific image sizes"
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
    parser.add_argument(
        "--width", type=float, default=63, help="Image width in mm (default: 63)"
    )
    parser.add_argument(
        "--height", type=float, default=88, help="Image height in mm (default: 88)"
    )

    args = parser.parse_args()

    if not is_valid_url(args.url):
        print(f"Error: Invalid URL provided - {args.url}", file=sys.stderr)
        sys.exit(1)

    if args.width <= 0 or args.height <= 0:
        print("Error: Image dimensions must be positive values", file=sys.stderr)
        sys.exit(1)

    success = find_and_process_images(
        target_url=args.url,
        output_pdf=args.output,
        class_name=args.class_name,
        image_width=args.width,
        image_height=args.height,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
