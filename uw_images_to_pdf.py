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
import glob


def is_valid_url(url):
    """Check if a URL is valid"""
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def download_image(url):
    """Download an image from a URL and return it as PIL Image with original filename"""
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()

        # Check if content is actually an image
        content_type = response.headers.get("content-type", "")
        if "image" not in content_type:
            print(f"URL does not point to an image (Content-Type: {content_type})")
            return None, None

        # Extract original filename from URL
        img_filename = os.path.basename(urlparse(url).path)
        if not img_filename:
            img_filename = "image.jpg"

        return Image.open(BytesIO(response.content)), img_filename

    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")
        return None, None
    except Exception as e:
        print(f"Error processing image: {e}")
        return None, None


def save_as_png(images_with_names, output_dir):
    """Save images as individual PNG files with sequence prefix and original names"""
    try:
        os.makedirs(output_dir, exist_ok=True)

        for i, (img, original_name) in enumerate(images_with_names, 1):
            # Split filename and extension
            name_part, ext = os.path.splitext(original_name)
            if not ext or ext.lower() not in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
                ext = ".png"  # Default to .png if no valid extension

            # Create new filename with sequence prefix
            new_filename = f"{i:03d}_{name_part}{ext}"
            filepath = os.path.join(output_dir, new_filename)

            # Convert to PNG if needed
            if ext.lower() != ".png":
                img = img.convert("RGB")

            img.save(filepath, "PNG")
            print(f"Saved: {filepath}")

        print(f"\nSuccessfully saved {len(images_with_names)} images to {output_dir}")
        return True
    except Exception as e:
        print(f"Failed to save PNG files: {e}")
        return False


def create_pdf(
    images_with_names,
    output_path,
    image_width=63 * mm,
    image_height=88 * mm,
    margin=0 * mm,
    back_card_path="card_back/objective-back.png",
    alternate_back_card_path="card_back/power-back.png",
    back_card_limit=12,
    background_color=(1, 1, 1),  # Default to white (RGB)
    draw_cut_lines=False,        # Added parameter
):
    """
    Create a PDF with images at specific sizes and interleave even pages with card backs
    """
    try:
        pdf_canvas = canvas.Canvas(output_path, pagesize=A4)
        page_width, page_height = A4

        # Calculate how many images fit horizontally and vertically
        available_width = page_width - 2 * margin
        available_height = page_height - 2 * margin

        images_per_row = max(1, math.floor(available_width / (image_width + margin)))
        images_per_col = max(1, math.floor(available_height / (image_height + margin)))
        actual_per_page = images_per_row * images_per_col

        print(
            f"Arranging {actual_per_page} images per page ({images_per_row}×{images_per_col})"
        )

        current_page_images = []
        total_pages = math.ceil(len(images_with_names) / actual_per_page)

        # Load card back images
        back_card = ImageReader(back_card_path)
        alternate_back_card = ImageReader(alternate_back_card_path)

        back_counter = 0
        for page_num in range(1, total_pages + 1):
            # Add front card images
            start_index = (page_num - 1) * actual_per_page
            end_index = start_index + actual_per_page
            current_page_images = [
                img for img, _ in images_with_names[start_index:end_index]
            ]
            draw_images_on_page(
                pdf_canvas,
                current_page_images,
                images_per_row,
                images_per_col,
                page_width,
                page_height,
                image_width,
                image_height,
                margin,
                background_color,
                direction="ltr",  # Default to left-to-right
                draw_cut_lines=draw_cut_lines,  # Pass parameter
            )
            pdf_canvas.showPage()

            # Add back card on even pages
            back_images = []
            for i in range(len(current_page_images)):
                if back_counter < back_card_limit:
                    back_images.append(back_card)
                else:
                    back_images.append(alternate_back_card)
                back_counter += 1

            draw_images_on_page(
                pdf_canvas,
                back_images,
                images_per_row,
                images_per_col,
                page_width,
                page_height,
                image_width,
                image_height,
                margin,
                background_color,
                direction="rtl",  # Right-to-left for back cards
                draw_cut_lines=draw_cut_lines,  # Pass parameter
            )
            pdf_canvas.showPage()

        pdf_canvas.save()
        print(f"Successfully created PDF: {output_path}")
        return True

    except Exception as e:
        print(f"Failed to create PDF: {e}")
        return False


def draw_pdf_cut_lines(
    pdf_canvas,
    images_per_row,
    images_per_col,
    page_width,
    page_height,
    image_width,
    image_height,
    margin
):
    """Draw cut lines for guiding vertical and horizontal cuts of the images."""
    pdf_canvas.setStrokeColorRGB(0, 0, 0)
    pdf_canvas.setLineWidth(1)
    # Calculate grid start positions
    total_row_width = images_per_row * image_width + (images_per_row - 1) * margin
    grid_start_x = (page_width - total_row_width) / 2
    total_col_height = images_per_col * image_height + (images_per_col - 1) * margin
    grid_start_y = page_height - (page_height - total_col_height) / 2 - total_col_height

    CUT_LINE_LENGTH = 5 * mm  # Length of cut lines

    # Draw vertical cut lines between columns
    for c in range(images_per_row):
        x = grid_start_x + c * (image_width + margin) - (margin if c == images_per_row else 0)
        for offset in [0, image_width]:
            pdf_canvas.line(
                x + offset,
                grid_start_y - CUT_LINE_LENGTH,
                x + offset,
                grid_start_y
            )
            pdf_canvas.line(
                x + offset,
                grid_start_y + total_col_height,
                x + offset,
                grid_start_y + total_col_height + CUT_LINE_LENGTH
            )

    # Draw horizontal cut lines between rows
    for r in range(images_per_col + 1):
        y = grid_start_y + r * (image_height + margin) - (margin if r == images_per_col else 0)
        for offset in [0, image_height]:
            pdf_canvas.line(
                grid_start_x - CUT_LINE_LENGTH,
                y + offset,
                grid_start_x,
                y + offset
            )        
            pdf_canvas.line(
                grid_start_x + total_row_width,
                y + offset,
                grid_start_x + total_row_width + CUT_LINE_LENGTH,
                y + offset
            )


def draw_images_on_page(
    pdf_canvas,
    images,
    images_per_row,
    images_per_col,
    page_width,
    page_height,
    image_width,
    image_height,
    margin,
    background_color,
    direction,  # New option: "ltr" (left-to-right, default) or "rtl" (right-to-left)
    draw_cut_lines=False,
):
    """Draw images on a PDF page with a configurable background color and direction."""
    # Set the background color
    pdf_canvas.setFillColorRGB(*background_color)  # Unpack RGB tuple
    pdf_canvas.rect(0, 0, page_width, page_height, fill=True, stroke=False)

    # Draw the images
    for i, img in enumerate(images):
        row = i // images_per_row
        col = i % images_per_row

        # Adjust column for direction
        if direction == "rtl":
            col = images_per_row - 1 - col

        total_row_width = images_per_row * image_width + (images_per_row - 1) * margin
        start_x = (page_width - total_row_width) / 2 + col * (image_width + margin)

        total_col_height = images_per_col * image_height + (images_per_col - 1) * margin
        start_y = page_height - (
            (page_height - total_col_height) / 2
            + (row + 1) * image_height
            + row * margin
        )

        img_reader = ImageReader(img)
        pdf_canvas.drawImage(
            img_reader,
            start_x,
            start_y,
            width=image_width,
            height=image_height,
            preserveAspectRatio=True,
            anchor="c",
        )

    if draw_cut_lines:
        draw_pdf_cut_lines(
            pdf_canvas,
            images_per_row,
            images_per_col,
            page_width,
            page_height,
            image_width,
            image_height,
            margin
        )


def process_images(images_with_names, output_path, output_format="png", **kwargs):
    """Process images according to the specified output format"""
    if output_format.lower() == "pdf":
        return create_pdf(
            images_with_names,
            output_path,
            image_width=kwargs.get("image_width", 63 * mm),
            image_height=kwargs.get("image_height", 88 * mm),
            margin=kwargs.get("margin", 0 * mm),
            background_color=kwargs.get("background_color", (1, 1, 1)),
            draw_cut_lines=kwargs.get("draw_cut_lines", False),  # Pass parameter
        )
    else:
        return save_as_png(images_with_names, output_path)


def find_and_process_images(
    target_url,
    output_path,
    class_name="mb-4 cardviewcard",
    output_format="png",
    **kwargs,
):
    """
    Navigate through a webpage's HTML to find images and process them
    """
    try:
        print(f"Fetching page: {target_url}")
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(target_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        containers = soup.find_all(class_=class_name)

        if not containers:
            print(f"No containers found with class: '{class_name}'")
            return False

        print(f"Found {len(containers)} containers with class '{class_name}'")

        images_with_names = []
        for i, container in enumerate(containers, 1):
            img_tags = container.find_all("img")

            if not img_tags:
                print(f"No images found in container {i}")
                continue

            for img in img_tags:
                img_url = img.get("src") or img.get("data-src")
                if not img_url:
                    continue

                img_url = urljoin(target_url, img_url)

                if not is_valid_url(img_url):
                    print(f"Invalid image URL: {img_url}")
                    continue

                print(f"Downloading image {len(images_with_names) + 1}: {img_url}")
                image, original_name = download_image(img_url)
                if image:
                    images_with_names.append((image, original_name))

        if not images_with_names:
            print("No images were downloaded")
            return False

        print(
            f"\nProcessing {len(images_with_names)} images as {output_format.upper()}..."
        )
        return process_images(images_with_names, output_path, output_format, **kwargs)

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        return False


def load_images_from_folder(folder_path):
    """Load images from a local folder"""
    try:
        image_files = glob.glob(os.path.join(folder_path, "*"))
        images_with_names = []

        for image_file in image_files:
            try:
                img = Image.open(image_file)
                images_with_names.append((img, os.path.basename(image_file)))
            except Exception as e:
                print(f"Failed to load image {image_file}: {e}")

        if not images_with_names:
            print(f"No valid images found in folder: {folder_path}")
            return None

        print(f"Loaded {len(images_with_names)} images from folder: {folder_path}")
        return images_with_names
    except Exception as e:
        print(f"Error loading images from folder: {e}")
        return None


def parse_background_color(color_str):
    """Parse a background color string in the format 'R,G,B' into an RGB tuple."""
    try:
        r, g, b = map(float, color_str.split(","))
        return r, g, b
    except Exception:
        raise argparse.ArgumentTypeError(
            "Background color must be in the format 'R,G,B' with values between 0 and 1."
        )


def main():
    parser = argparse.ArgumentParser(
        description="Download images and save as PNG (default) or PDF"
    )
    parser.add_argument("url", help="URL of the webpage to scan")
    parser.add_argument(
        "--output",
        "-o",
        default="downloaded_images",
        help="Output path (directory for PNGs or filename for PDF)",
    )
    parser.add_argument(
        "--class",
        "-c",
        dest="class_name",
        default="mb-4 cardviewcard",
        help="HTML class name to search for image containers",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["png", "pdf"],
        default="png",
        help="Output format (png or pdf)",
    )
    parser.add_argument(
        "--width",
        type=float,
        default=63,
        help="Image width in mm (PDF only, default: 63)",
    )
    parser.add_argument(
        "--height",
        type=float,
        default=88,
        help="Image height in mm (PDF only, default: 88)",
    )
    parser.add_argument(
        "--margin",
        type=float,
        default=0,
        help="Cards margin in mm (PDF only, default: 0)",
    )
    parser.add_argument(
        "--folder",
        "-l",
        help="Path to a local folder containing images (skips downloading)",
    )
    parser.add_argument(
        "--background-color",
        "-b",
        type=parse_background_color,
        default="1,1,1",  # Default to white
        help="Background color for the PDF in 'R,G,B' format (values between 0 and 1). Default is white.",
    )
    parser.add_argument(
        "--draw-cut-lines",
        type=lambda x: (str(x).lower() == "true"),
        default=True,
        help="Draw black cut lines at the edges of images in the PDF (PDF only). Use 'True' or 'False'. Default is False.",
    )

    args = parser.parse_args()

    if args.folder:
        images_with_names = load_images_from_folder(args.folder)
        if not images_with_names:
            sys.exit(1)
        success = process_images(
            images_with_names,
            args.output,
            output_format=args.format,
            image_width=args.width * mm,
            image_height=args.height * mm,
            margin=args.margin * mm,
            background_color=args.background_color,
            draw_cut_lines=args.draw_cut_lines,  # Pass parameter
        )
    else:
        if not is_valid_url(args.url):
            print(f"Error: Invalid URL provided - {args.url}", file=sys.stderr)
            sys.exit(1)

        if args.format == "pdf" and (args.width <= 0 or args.height <= 0):
            print("Error: Image dimensions must be positive values", file=sys.stderr)
            sys.exit(1)

        success = find_and_process_images(
            target_url=args.url,
            output_path=args.output,
            class_name=args.class_name,
            output_format=args.format,
            image_width=args.width * mm,
            image_height=args.height * mm,
            margin=args.margin * mm,
            background_color=args.background_color,
            draw_cut_lines=args.draw_cut_lines,  # Pass parameter
        )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
