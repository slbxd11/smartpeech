# SmartSpeech OCR Web Application

A web application that uses Google's Gemini AI to perform OCR (Optical Character Recognition) on uploaded images and PDFs.

## Features

- Upload images (JPG, PNG, GIF, BMP) and PDFs
- AI-powered text extraction using Google Gemini API
- Modern, responsive web interface
- Docker support for easy deployment

## Prerequisites

- Python 3.11+
- Google Gemini API key

## Installation

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your Google API key:
```bash
export GOOGLE_API_KEY="your-actual-api-key-here"
```

3. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t smartpeech-ocr .
```

2. Run the container:
```bash
docker run -p 5000:5000 -e GOOGLE_API_KEY="your-actual-api-key-here" smartpeech-ocr
```

## Usage

1. Open your web browser and navigate to `http://localhost:5000`
2. Upload an image or PDF file using the drag-and-drop interface or file picker
3. Click "Extract Text" to process the file
4. View the extracted text in the results area

## API Endpoints

- `GET /` - Main web interface
- `POST /upload` - Upload and process files

## Dependencies

- `fasthtml` - Fast web framework
- `google-genai` - Google Gemini AI client
- `Pillow` - Image processing
- `PyMuPDF` - PDF processing

## Notes

- The application uses port 5000 as specified
- Make sure to replace the placeholder API key with your actual Google Gemini API key
- The Docker image is based on Debian and includes all necessary system dependencies
# smartpeech
