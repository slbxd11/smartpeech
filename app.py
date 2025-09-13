from fasthtml.common import *
from google.genai import GenerativeModel
import os
import base64
from PIL import Image
import io
import fitz  # PyMuPDF for PDF processing

# Configure Gemini API
os.environ["GOOGLE_API_KEY"] = "AIzaSyB-xxx-k"

# Initialize Gemini model
model = GenerativeModel("gemini-1.5-flash")

# Create upload directory
os.makedirs("uploads", exist_ok=True)

def process_image(image_data):
    """Process image and extract text using Gemini OCR"""
    try:
        # Convert image to base64 for Gemini API
        if isinstance(image_data, bytes):
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        else:
            image_base64 = image_data
        
        # Create the prompt for OCR
        prompt = "Extract all text from this image. Return only the text content, no additional formatting or explanations."
        
        # Call Gemini API for OCR
        response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_base64}])
        
        return response.text
    except Exception as e:
        return f"Error processing image: {str(e)}"

def process_pdf(pdf_data):
    """Process PDF and extract text using Gemini OCR for each page"""
    try:
        # Open PDF with PyMuPDF
        pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
        extracted_text = ""
        
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            # Convert PDF page to image
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")
            
            # Convert to base64
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            
            # Process with Gemini OCR
            page_text = process_image(img_base64)
            extracted_text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
        
        pdf_document.close()
        return extracted_text
    except Exception as e:
        return f"Error processing PDF: {str(e)}"

# FastHTML routes
@app.route("/")
def index():
    return Html("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SmartSpeech OCR</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            h1 {
                text-align: center;
                color: #333;
                margin-bottom: 30px;
                font-size: 2.5em;
            }
            .upload-area {
                border: 3px dashed #667eea;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                margin: 20px 0;
                background: #f8f9ff;
                transition: all 0.3s ease;
            }
            .upload-area:hover {
                border-color: #764ba2;
                background: #f0f2ff;
            }
            .upload-area.dragover {
                border-color: #764ba2;
                background: #e8ebff;
            }
            input[type="file"] {
                margin: 20px 0;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                width: 100%;
                box-sizing: border-box;
            }
            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                font-weight: bold;
                transition: transform 0.2s ease;
                width: 100%;
                margin: 10px 0;
            }
            button:hover {
                transform: translateY(-2px);
            }
            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            .result {
                margin-top: 30px;
                padding: 20px;
                background: #f8f9ff;
                border-radius: 10px;
                border-left: 4px solid #667eea;
                white-space: pre-wrap;
                max-height: 400px;
                overflow-y: auto;
            }
            .loading {
                text-align: center;
                color: #667eea;
                font-style: italic;
            }
            .file-info {
                margin: 10px 0;
                padding: 10px;
                background: #e8f4fd;
                border-radius: 5px;
                color: #333;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 SmartSpeech OCR</h1>
            <p style="text-align: center; color: #666; margin-bottom: 30px;">
                Upload images or PDFs to extract text using AI-powered OCR
            </p>
            
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-area" id="uploadArea">
                    <p>📁 Drag and drop files here or click to browse</p>
                    <input type="file" id="fileInput" name="file" accept=".jpg,.jpeg,.png,.gif,.bmp,.pdf" required>
                    <p style="color: #666; font-size: 14px;">
                        Supported formats: JPG, PNG, GIF, BMP, PDF
                    </p>
                </div>
                <button type="submit" id="submitBtn">🚀 Extract Text</button>
            </form>
            
            <div id="fileInfo" class="file-info" style="display: none;"></div>
            <div id="result" class="result" style="display: none;"></div>
        </div>

        <script>
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            const form = document.getElementById('uploadForm');
            const submitBtn = document.getElementById('submitBtn');
            const resultDiv = document.getElementById('result');
            const fileInfoDiv = document.getElementById('fileInfo');

            // Drag and drop functionality
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });

            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    fileInput.files = files;
                    showFileInfo(files[0]);
                }
            });

            uploadArea.addEventListener('click', () => {
                fileInput.click();
            });

            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    showFileInfo(e.target.files[0]);
                }
            });

            function showFileInfo(file) {
                fileInfoDiv.innerHTML = `
                    <strong>Selected file:</strong> ${file.name}<br>
                    <strong>Size:</strong> ${(file.size / 1024 / 1024).toFixed(2)} MB<br>
                    <strong>Type:</strong> ${file.type}
                `;
                fileInfoDiv.style.display = 'block';
            }

            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData(form);
                submitBtn.disabled = true;
                submitBtn.textContent = '⏳ Processing...';
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '<div class="loading">🔄 Extracting text from your file...</div>';

                try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });

                    const data = await response.json();
                    
                    if (data.success) {
                        resultDiv.innerHTML = `<strong>Extracted Text:</strong><br><br>${data.text}`;
                    } else {
                        resultDiv.innerHTML = `<strong>Error:</strong> ${data.error}`;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<strong>Error:</strong> ${error.message}`;
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.textContent = '🚀 Extract Text';
                }
            });
        </script>
    </body>
    </html>
    """)

@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        # Get uploaded file
        file = request.files.get('file')
        if not file:
            return Json({"success": False, "error": "No file uploaded"})
        
        # Read file data
        file_data = file.read()
        file_extension = file.filename.lower().split('.')[-1]
        
        # Process based on file type
        if file_extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            # Process image
            extracted_text = process_image(file_data)
        elif file_extension == 'pdf':
            # Process PDF
            extracted_text = process_pdf(file_data)
        else:
            return Json({"success": False, "error": "Unsupported file format"})
        
        return Json({
            "success": True,
            "text": extracted_text,
            "filename": file.filename
        })
        
    except Exception as e:
        return Json({"success": False, "error": str(e)})

if __name__ == "__main__":
    serve(host="0.0.0.0", port=5000)
