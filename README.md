# PDF Image Extractor

A command-line utility to extract all distinct images from PDF files for content reuse purposes. The utility supports batch processing of multiple PDFs and maintains the directory structure in the output.

## Overview

PDF Image Extractor is designed to:
- Process single PDF files or entire directories (including subdirectories)
- Extract all distinct images from each PDF
- Identify and extract multiple distinct images from a single page raster
- Maintain original image quality by default
- Support optional image compression or scaling
- Filter images by size 
- Save extracted images in a parallel directory structure

## Target Platforms
- macOS
- Linux

## Installation

### Prerequisites
- Python 3.8 or later
- [Poppler](https://poppler.freedesktop.org/) (required by pdf2image)

### Installation Instructions
```bash
# Clone the repository
git clone https://github.com/yourusername/pdfimages.git
cd pdfimages

# Set up a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

## Usage

```
pdfimages [options] <input_path> [<output_path>]
```

### Required Arguments
- `<input_path>`: Path to a PDF file or directory containing PDFs
- `<output_path>`: (Optional) Path to the output directory. If not specified, creates a directory named "extracted_images" in the current location

### Options
- `-c, --config <file>`: Use specified configuration file
- `-m, --min-size <size>`: Filter out images smaller than specified size (e.g., 10KB, 100x100)
- `-M, --max-size <size>`: Filter out images larger than specified size
- `-q, --quality <percent>`: Compress images to specified quality percentage
- `-s, --scale <factor>`: Scale images by the specified factor
- `-v, --verbose`: Enable verbose output
- `-d, --debug`: Enable debug logging
- `-h, --help`: Display help information

## License

[MIT License](LICENSE)