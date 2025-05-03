# Warband Image Processing Scripts

This repository contains two Python scripts for processing images related to warbands. These scripts allow you to download images, organize them, and generate PDFs with specific layouts.

## Scripts Overview

### 1. `process_warbands.py`

This script processes warband files to download images and generate PDFs. It supports downloading images from URLs listed in text files or loading images from a local folder.

#### Usage

```bash
python process_warbands.py --source [links|folder] --warbands-folder <path> --output-folder <path>
```

#### Arguments

- `--source`: Specify whether to get images from links in the files (`links`) or from the output folder (`folder`). Default is `folder`.
- `--warbands-folder`: Path to the folder containing warband text files. Default is `warbands`.
- `--output-folder`: Path to the folder where images and PDFs will be saved. Default is `output_pdfs`.

#### Examples

1. Download images from URLs in text files and generate PDFs:
   ```bash
   python process_warbands.py --source links --warbands-folder ./warbands --output-folder ./output_pdfs
   ```

2. Load images from a folder and generate PDFs:
   ```bash
   python process_warbands.py --source folder --warbands-folder ./warbands --output-folder ./output_pdfs
   ```

---

### 2. `uw_images_to_pdf.py`

This script downloads images from a webpage containing Rivals Decks or loads them from a local folder, then saves them as PNG files or generates a PDF with specific layouts.

#### Usage

```bash
python uw_images_to_pdf.py <url> --output <path> [options]
```

#### Arguments

- `<url>`: URL of the webpage to scan for images.
- `--output`, `-o`: Output path (directory for PNGs or filename for PDF). Default is `downloaded_images`.
- `--class`, `-c`: HTML class name to search for image containers. Default is `mb-4 cardviewcard`.
- `--format`, `-f`: Output format (`png` or `pdf`). Default is `png`.
- `--width`: Image width in mm (PDF only). Default is `63`.
- `--height`: Image height in mm (PDF only). Default is `88`.
- `--margin`: Cards margin in mm (PDF only). Default is `0`.
- `--folder`, `-l`: Path to a local folder containing images (skips downloading).
- `--background-color`, `-b`: Background color for the PDF in `R,G,B` format (values between 0 and 1). Default is `1,1,1` (white).

#### Examples

1. Download images from a webpage and save as PNG files:
   ```bash
   python uw_images_to_pdf.py https://example.com --output ./images --format png
   ```

2. Generate a PDF with specific image dimensions:
   ```bash
   python uw_images_to_pdf.py https://example.com --output ./output.pdf --format pdf --width 70 --height 100 --margin 5
   ```

3. Load images from a local folder and generate a PDF:
   ```bash
   python uw_images_to_pdf.py --folder ./images --output ./output.pdf --format pdf --width 63 --height 88
   ```

---

## Requirements

- Python 3.6 or higher
- Required Python libraries:
  - `requests`
  - `Pillow`
  - `reportlab`
  - `beautifulsoup4`

Install the required libraries using pip:
```bash
pip install requests pillow reportlab beautifulsoup4
```

---

## Notes

- Ensure that the input files and folders are correctly structured as expected by the scripts.
- For `uw_images_to_pdf.py`, ensure the webpage contains images within the specified HTML class.