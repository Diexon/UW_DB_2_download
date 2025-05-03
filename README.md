# Warband Image Processing Scripts

This repository contains three Python scripts for processing images related to warbands. These scripts allow you to download images, organize them, and generate PDFs with specific layouts.

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

### 3. `batch_generate_pdfs.py`

This script automates the generation of PDFs for multiple sets of images. It processes multiple folders or files in batch mode, making it easier to handle large datasets.

#### Usage

```bash
python batch_generate_pdfs.py --input-folder <path> --output-folder <path> [options]
```

#### Arguments

- `--input-folder`: Path to the folder containing subfolders or files with images to process.
- `--output-folder`: Path to the folder where the generated PDFs will be saved.
- Additional options can be added as needed for customization.

#### Examples

1. Generate PDFs for all image sets in a folder:
   ```bash
   python batch_generate_pdfs.py --input-folder ./image_sets --output-folder ./output_pdfs
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

---

# Scripts para Procesamiento de Imágenes de Warbands

Este repositorio contiene tres scripts en Python para procesar imágenes relacionadas con warbands. Estos scripts permiten descargar imágenes, organizarlas y generar archivos PDF con diseños específicos.

## Descripción de los Scripts

### 1. `process_warbands.py`

Este script procesa archivos de warbands para descargar imágenes y generar archivos PDF. Admite la descarga de imágenes desde URLs listadas en archivos de texto o la carga de imágenes desde una carpeta local.

#### Uso

```bash
python process_warbands.py --source [links|folder] --warbands-folder <ruta> --output-folder <ruta>
```

#### Argumentos

- `--source`: Especifica si obtener imágenes desde enlaces en los archivos (`links`) o desde la carpeta de salida (`folder`). Por defecto es `folder`.
- `--warbands-folder`: Ruta a la carpeta que contiene los archivos de texto de warbands. Por defecto es `warbands`.
- `--output-folder`: Ruta a la carpeta donde se guardarán las imágenes y los archivos PDF. Por defecto es `output_pdfs`.

#### Ejemplos

1. Descargar imágenes desde URLs en archivos de texto y generar archivos PDF:
   ```bash
   python process_warbands.py --source links --warbands-folder ./warbands --output-folder ./output_pdfs
   ```

2. Cargar imágenes desde una carpeta y generar archivos PDF:
   ```bash
   python process_warbands.py --source folder --warbands-folder ./warbands --output-folder ./output_pdfs
   ```

---

### 2. `uw_images_to_pdf.py`

Este script descarga imágenes desde una página web que contiene Rivals Decks o las carga desde una carpeta local, luego las guarda como archivos PNG o genera un archivo PDF con diseños específicos.

#### Uso

```bash
python uw_images_to_pdf.py <url> --output <ruta> [opciones]
```

#### Argumentos

- `<url>`: URL de la página web para buscar imágenes.
- `--output`, `-o`: Ruta de salida (carpeta para PNGs o nombre del archivo para PDF). Por defecto es `downloaded_images`.
- `--class`, `-c`: Nombre de la clase HTML para buscar contenedores de imágenes. Por defecto es `mb-4 cardviewcard`.
- `--format`, `-f`: Formato de salida (`png` o `pdf`). Por defecto es `png`.
- `--width`: Ancho de las imágenes en mm (solo para PDF). Por defecto es `63`.
- `--height`: Altura de las imágenes en mm (solo para PDF). Por defecto es `88`.
- `--margin`: Margen de las tarjetas en mm (solo para PDF). Por defecto es `0`.
- `--folder`, `-l`: Ruta a una carpeta local que contiene imágenes (omite la descarga).
- `--background-color`, `-b`: Color de fondo para el PDF en formato `R,G,B` (valores entre 0 y 1). Por defecto es `1,1,1` (blanco).

#### Ejemplos

1. Descargar imágenes desde una página web y guardarlas como archivos PNG:
   ```bash
   python uw_images_to_pdf.py https://example.com --output ./images --format png
   ```

2. Generar un archivo PDF con dimensiones específicas para las imágenes:
   ```bash
   python uw_images_to_pdf.py https://example.com --output ./output.pdf --format pdf --width 70 --height 100 --margin 5
   ```

3. Cargar imágenes desde una carpeta local y generar un archivo PDF:
   ```bash
   python uw_images_to_pdf.py --folder ./images --output ./output.pdf --format pdf --width 63 --height 88
   ```

---

### 3. `batch_generate_pdfs.py`

Este script automatiza la generación de archivos PDF para múltiples conjuntos de imágenes. Procesa varias carpetas o archivos en modo batch, facilitando el manejo de grandes volúmenes de datos.

#### Uso

```bash
python batch_generate_pdfs.py --input-folder <ruta> --output-folder <ruta> [opciones]
```

#### Argumentos

- `--input-folder`: Ruta a la carpeta que contiene subcarpetas o archivos con imágenes para procesar.
- `--output-folder`: Ruta a la carpeta donde se guardarán los archivos PDF generados.
- Opciones adicionales pueden ser añadidas según sea necesario para personalización.

#### Ejemplos

1. Generar archivos PDF para todos los conjuntos de imágenes en una carpeta:
   ```bash
   python batch_generate_pdfs.py --input-folder ./image_sets --output-folder ./output_pdfs
   ```

---

## Requisitos

- Python 3.6 o superior
- Librerías de Python requeridas:
  - `requests`
  - `Pillow`
  - `reportlab`
  - `beautifulsoup4`

Instala las librerías requeridas usando pip:
```bash
pip install requests pillow reportlab beautifulsoup4
```

---

## Notas

- Asegúrate de que los archivos y carpetas de entrada estén estructurados correctamente como lo esperan los scripts.
- Para `uw_images_to_pdf.py`, asegúrate de que la página web contenga imágenes dentro de la clase HTML especificada.