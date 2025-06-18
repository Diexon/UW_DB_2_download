import os
import glob
import requests
import argparse
from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, mm
from reportlab.lib.utils import ImageReader
from uw_images_to_pdf import draw_pdf_cut_lines


def read_urls_from_folder(folder_path):
    """Read all URLs from text files in the given folder."""
    urls = []
    try:
        for file_path in glob.glob(os.path.join(folder_path, "*.txt")):
            with open(file_path, "r") as file:
                urls.extend(line.strip() for line in file if line.strip())
        print(f"Found {len(urls)} URLs in folder: {folder_path}")
    except Exception as e:
        print(f"Error reading URLs from folder: {e}")
    return urls


def download_images(urls, output_folder):
    """Download images from the given URLs and save them as PNG files."""
    os.makedirs(output_folder, exist_ok=True)
    images_with_names = []

    for i, url in enumerate(urls, 1):
        try:
            print(f"Downloading image {i}/{len(urls)}: {url}")
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()

            # Check if content is an image
            content_type = response.headers.get("content-type", "")
            if "image" not in content_type:
                print(f"URL does not point to an image: {url}")
                continue

            # Extract filename and save the image
            img_filename = os.path.basename(url.split("?")[0]) or f"image_{i}.png"
            img_path = os.path.join(output_folder, img_filename)

            image = Image.open(BytesIO(response.content))
            image.save(img_path, "PNG")
            images_with_names.append((image, img_filename))
        except Exception as e:
            print(f"Error downloading image from {url}: {e}")

    print(f"Downloaded {len(images_with_names)} images to {output_folder}")
    return images_with_names


def draw_images_on_page_specific(
    pdf_canvas,
    images_with_names,
    image_width,
    image_height,
    margin,
    direction,
    draw_cut_lines=True,
):
    """Draw images on a PDF, creating new pages as needed."""
    page_width, page_height = A4

    # Calculate how many images fit horizontally and vertically
    available_width = page_width - 2 * margin
    available_height = page_height - 2 * margin

    images_per_row = max(1, int(available_width // (image_width + margin)))
    images_per_col = max(1, int(available_height // (image_height + margin)))
    images_per_page = images_per_row * images_per_col

    for page_start in range(0, len(images_with_names), images_per_page):
        page_images = images_with_names[page_start : page_start + images_per_page]

        for i, (img, _) in enumerate(page_images):
            row = i // images_per_row
            col = i % images_per_row

            # Adjust column for direction
            if direction == "rtl":
                col = images_per_row - 1 - col

            total_row_width = (
                images_per_row * image_width + (images_per_row - 1) * margin
            )
            start_x = (page_width - total_row_width) / 2 + col * (image_width + margin)

            total_col_height = (
                images_per_col * image_height + (images_per_col - 1) * margin
            )
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

        # Add a new page if there are more images to process
        if page_start + images_per_page < len(images_with_names):
            pdf_canvas.showPage()

        if draw_cut_lines:
            draw_pdf_cut_lines(
                pdf_canvas,
                images_per_row,
                images_per_col,
                page_width,
                page_height,
                image_width,
                image_height,
                margin,
            )


def process_images_and_generate_pdf(images_with_names, output_pdf, draw_cut_lines=True):
    """Process images and generate a PDF based on the specified constraints."""
    try:
        if not images_with_names:
            print("No valid images to process.")
            return

        # Separate images based on constraints
        dedicated_images = []
        inspired_images = []
        other_images = []

        for img, name in images_with_names:
            lower_name = name.lower()
            if any(
                keyword in lower_name
                for keyword in ["0", "order", "destruction", "death", "chaos"]
            ):
                dedicated_images.append((img, name))
            elif "inspired" in lower_name:
                inspired_images.append((img, name))
            else:
                other_images.append((img, name))

        # Create the PDF
        pdf_canvas = canvas.Canvas(output_pdf, pagesize=A4)

        # Add other images to a page
        if other_images:
            draw_images_on_page_specific(
                pdf_canvas,
                other_images,
                image_width=63 * mm,
                image_height=88 * mm,
                margin=3 * mm,
                direction="ltr",  # Default direction is left-to-right
                draw_cut_lines=draw_cut_lines,
            )
            pdf_canvas.showPage()
        # Add inspired images to a page
        if inspired_images:
            draw_images_on_page_specific(
                pdf_canvas,
                inspired_images,
                image_width=63 * mm,
                image_height=88 * mm,
                margin=3 * mm,
                direction="rtl",  # Inspired images are drawn right-to-left
                draw_cut_lines=draw_cut_lines,
            )
            pdf_canvas.showPage()
        # Add dedicated images to their own page
        if dedicated_images:
            draw_images_on_page_specific(
                pdf_canvas,
                dedicated_images,
                image_width=148 * mm,
                image_height=105 * mm,
                margin=3 * mm,
                direction="ltr",  # Default direction is left-to-right
                draw_cut_lines=draw_cut_lines,
            )
            pdf_canvas.showPage()

        pdf_canvas.save()
        print(f"PDF successfully created: {output_pdf}")

    except Exception as e:
        print(f"Error processing images and generating PDF: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Process warband files to download images and generate PDFs."
    )
    parser.add_argument(
        "--source",
        choices=["links", "folder"],
        default="folder",
        help="Specify whether to get images from links in the files or from the output folder. Default is 'links'.",
    )
    parser.add_argument(
        "--warbands-folder",
        default="warbands",
        help="Path to the folder containing warband files. Default is 'warbands'.",
    )
    parser.add_argument(
        "--output-folder",
        default="output_pdfs",
        help="Path to the folder where images and PDFs will be saved. Default is 'output_pdfs'.",
    )
    parser.add_argument(
        "--draw-cut-lines",
        type=lambda x: (str(x).lower() == "true"),
        default=True,
        help="Draw black cut lines at the edges of images in the PDF. Use 'True' or 'False'. Default is True.",
    )
    args = parser.parse_args()

    warbands_folder = args.warbands_folder
    output_folder = args.output_folder

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Process each file in the warbands folder
    for file_path in glob.glob(os.path.join(warbands_folder, "*.txt")):
        try:
            # Extract the base name of the file (without extension) for output naming
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            print(f"Processing file: {file_path}")

            # Define output paths
            output_images_folder = os.path.join(output_folder, f"{base_name}_images")
            output_pdf_path = os.path.join(output_folder, f"{base_name}.pdf")

            if args.source == "links":
                # Read URLs from the file
                with open(file_path, "r") as file:
                    urls = [line.strip() for line in file if line.strip()]

                if not urls:
                    print(f"No URLs found in file: {file_path}")
                    continue

                # Download images as PNG
                images_with_names = download_images(urls, output_images_folder)
            else:
                # Load images from the output folder
                images_with_names = []
                for image_file in glob.glob(
                    os.path.join(output_images_folder, "*.png")
                ):
                    try:
                        img = Image.open(image_file)
                        images_with_names.append((img, os.path.basename(image_file)))
                    except Exception as e:
                        print(f"Failed to load image {image_file}: {e}")

                if not images_with_names:
                    print(f"No valid images found in folder: {output_images_folder}")
                    continue

            # Convert images to PDF
            process_images_and_generate_pdf(
                images_with_names, output_pdf_path, draw_cut_lines=args.draw_cut_lines
            )

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")


if __name__ == "__main__":
    main()
