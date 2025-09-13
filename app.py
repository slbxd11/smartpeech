from fasthtml.common import *
from fasthtml import *
import google.generativeai as genai
import os
import tempfile
from PIL import Image
import fitz  # PyMuPDF for PDF processing
import io
import base64

# Configure Google GenAI
genai.configure(api_key="AIzaSyB-ssyREcxmGX8KnV9JbxfEZLh6xhXC7-k")

# Create FastHTML app
app = FastHTML()

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_images_from_pdf(pdf_path):
    """Extract images from PDF file"""
    images = []
    doc = fitz.open(pdf_path)
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # Convert page to image
        mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        images.append(img_data)
    
    doc.close()
    return images

def process_image_with_ocr(image_data):
    """Process image with Google GenAI OCR"""
    try:
        # Convert image data to PIL Image
        if isinstance(image_data, bytes):
            image = Image.open(io.BytesIO(image_data))
        else:
            image = image_data
        
        # Convert to base64 for GenAI
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Use GenAI for OCR
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([
            "Extract all text from this image using OCR. Return only the extracted text, no additional formatting or explanations.",
            {
                "mime_type": "image/png",
                "data": img_base64
            }
        ])
        
        return response.text
    except Exception as e:
        return f"Error processing image: {str(e)}"

@app.route("/")
def index():
    return Html(
        Head(
            Title("OCR Web Application"),
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Style("""
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #333;
                    text-align: center;
                    margin-bottom: 30px;
                }
                .upload-area {
                    border: 2px dashed #ccc;
                    border-radius: 10px;
                    padding: 40px;
                    text-align: center;
                    margin: 20px 0;
                    background-color: #fafafa;
                }
                .upload-area:hover {
                    border-color: #007bff;
                    background-color: #f0f8ff;
                }
                input[type="file"] {
                    margin: 10px 0;
                }
                button {
                    background-color: #007bff;
                    color: white;
                    padding: 12px 24px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                }
                button:hover {
                    background-color: #0056b3;
                }
                .result {
                    margin-top: 20px;
                    padding: 20px;
                    background-color: #f8f9fa;
                    border-radius: 5px;
                    border-left: 4px solid #007bff;
                }
                .error {
                    border-left-color: #dc3545;
                    background-color: #f8d7da;
                }
            """)
        ),
        Body(
            Div(
                H1("OCR Web Application"),
                P("Upload an image or PDF file to extract text using Google GenAI"),
                Form(
                    Div(
                        Label("Choose file:", For="file"),
                        Input(type="file", id="file", name="file", accept=".png,.jpg,.jpeg,.gif,.pdf", required=True),
                        Br(),
                        Button("Extract Text", type="submit")
                    ),
                    method="post",
                    enctype="multipart/form-data",
                    class_="upload-area"
                ),
                class_="container"
            )
        )
    )

@app.route("/", methods=["POST"])
def upload_file():
    try:
        # Get uploaded file
        file = request.files.get('file')
        
        if not file or file.filename == '':
            return Html(
                Head(Title("Error")),
                Body(
                    Div(
                        H1("Error"),
                        P("No file selected"),
                        A("Back to upload", href="/")
                    )
                )
            )
        
        if not allowed_file(file.filename):
            return Html(
                Head(Title("Error")),
                Body(
                    Div(
                        H1("Error"),
                        P("File type not allowed. Please upload PNG, JPG, JPEG, GIF, or PDF files."),
                        A("Back to upload", href="/")
                    )
                )
            )
        
        # Read file data
        file_data = file.read()
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        
        extracted_text = ""
        
        if file_ext == 'pdf':
            # Process PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(file_data)
                tmp_file.flush()
                
                # Extract images from PDF
                images = extract_images_from_pdf(tmp_file.name)
                
                if not images:
                    return Html(
                        Head(Title("Error")),
                        Body(
                            Div(
                                H1("Error"),
                                P("No images found in PDF"),
                                A("Back to upload", href="/")
                            )
                        )
                    )
                
                # Process each page
                for i, img_data in enumerate(images):
                    page_text = process_image_with_ocr(img_data)
                    extracted_text += f"Page {i+1}:\n{page_text}\n\n"
                
                os.unlink(tmp_file.name)
        else:
            # Process image
            extracted_text = process_image_with_ocr(file_data)
        
        # Display results
        return Html(
            Head(
                Title("OCR Results"),
                Meta(charset="utf-8"),
                Meta(name="viewport", content="width=device-width, initial-scale=1"),
                Style("""
                    body {
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }
                    .container {
                        background: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }
                    h1 {
                        color: #333;
                        text-align: center;
                        margin-bottom: 30px;
                    }
                    .result {
                        margin-top: 20px;
                        padding: 20px;
                        background-color: #f8f9fa;
                        border-radius: 5px;
                        border-left: 4px solid #007bff;
                        white-space: pre-wrap;
                        font-family: monospace;
                    }
                    .back-link {
                        text-align: center;
                        margin-top: 20px;
                    }
                    a {
                        color: #007bff;
                        text-decoration: none;
                        padding: 10px 20px;
                        background-color: #e9ecef;
                        border-radius: 5px;
                    }
                    a:hover {
                        background-color: #dee2e6;
                    }
                """)
            ),
            Body(
                Div(
                    H1("OCR Results"),
                    Div(
                        H3("Extracted Text:"),
                        Div(extracted_text, class_="result")
                    ),
                    Div(
                        A("Upload Another File", href="/"),
                        class_="back-link"
                    ),
                    class_="container"
                )
            )
        )
        
    except Exception as e:
        return Html(
            Head(Title("Error")),
            Body(
                Div(
                    H1("Error"),
                    P(f"An error occurred: {str(e)}"),
                    A("Back to upload", href="/")
                )
            )
        )

if __name__ == "__main__":
    # Run on port 5000 as specified in FastHTML documentation
    serve(port=5000)
