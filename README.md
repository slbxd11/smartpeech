# OCR Web Application

A web application built with FastHTML and Google GenAI for optical character recognition (OCR) from uploaded images and PDF files.

## Features

- Upload images (PNG, JPG, JPEG, GIF) or PDF files
- Extract text using Google GenAI's Gemini model
- Clean, responsive web interface
- Docker support with Debian base image

## Prerequisites

- Python 3.11+
- Docker (optional)

## Installation

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Docker

1. Build the Docker image:
```bash
docker build -t ocr-app .
```

2. Run the container:
```bash
docker run -p 5000:5000 ocr-app
```

## Usage

1. Open your browser and navigate to `http://localhost:5000`
2. Click "Choose file" and select an image or PDF file
3. Click "Extract Text" to process the file
4. View the extracted text on the results page

## API Key

The application uses the provided Google GenAI API key. Make sure you have proper permissions for the Gemini API.

## File Support

- **Images**: PNG, JPG, JPEG, GIF
- **PDFs**: Multi-page PDF support with individual page processing

## Dependencies

- `fasthtml`: Web framework
- `google-generativeai`: Google GenAI integration
- `Pillow`: Image processing
- `PyMuPDF`: PDF processing
