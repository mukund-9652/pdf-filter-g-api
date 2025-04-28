# PDF Filter and Summary Tool

This Python project processes PDF files to **detect, summarize, and filter pages** based on the presence of specific keywords or related synonyms.  
It uses a simple **GUI file picker** (via Tkinter) to let users easily select the input PDF.  
The output includes a cleaned PDF and a detailed Excel report summarizing the actions taken on each page.

## 📦 Features

- Select PDF files via a file picker window (Tkinter GUI)
- Extract and OCR text from PDFs (even from scanned images)
- Summarize page content using OpenAI's GPT models
- Detect and filter pages based on configurable keywords
- Generate detailed Excel reports of actions taken
- Show time taken, number of pages processed, pages filtered out
- Automatically expand keyword matching with synonyms (via WordNet)

## Installation

### Prerequisites
- Python >= 3.8
- Google Cloud Vision API credentials
- Environment variable for OpenAI API key

### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/mukund-9652/pdf-filter-g-api.git
   cd pdf-filter-g-api
   ```
2. **Set up a Python virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate
   ```
3. **Install the dependencies:**
   Make sure you have a **requirements.txt** file containing:
   ```bash
   google-cloud-vision
   fitz
   PyMuPDF
   PyPDF2
   nltk
   pandas
   openai
   pillow
   tk
   openpyxl
   ```
   Activate the virtual environment and Run the pip installation to install from requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```
## ⚙️ Configuration

### Google Cloud Vision API Setup

1. **Create a Google Cloud Project**:
   - Visit: [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project (or select an existing one).

2. **Enable the Vision API**:
   - Navigate to **APIs & Services → Library**.
   - Search for **"Vision API"** and **Enable** it.

3. **Create Service Account Credentials**:
   - Go to **APIs & Services → Credentials → Create Credentials → Service Account**.
   - Follow the prompts to create a service account.
   - Assign the role **"Project > Editor"** or **"Vision AI User"**.

4. **Download the JSON Key File**:
   - After creating the service account, click on it → **Keys** → **Add Key** → **Create new key** → Choose **JSON**.
   - Save the `.json` file securely.

5. **Set the environment variable**:  
   Before running your code, set the environment variable to point to your downloaded credentials.

   On **Linux/Mac**:

   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/your-key.json"
   ```
### OpenAI API Key Setup

1. Create/Open an OpenAI Account

- Go to [OpenAI Platform](https://platform.openai.com/).

2. Generate an API Key

- After signing in, navigate to **User Settings → API Keys**.
- Click **Create New Secret Key**.
- Copy and securely store your API key.

3. Configure API Key in Your Project

- In your `main.py`, replace the placeholder value:

```python
client = OpenAI(
    api_key='your-openai-api-key-here'
)
```

⚠️ **Important:**
For production, avoid hardcoding API keys. Use environment variables or secure vaults instead.

## 🛠 How to Run
Simply activate your virtual environment and run:

  ```bash
    python main.py
  ```
  - A file picker window will open.
  - Select the PDF file you want to process.
  - The script will generate:
    - A filtered PDF (formatted_<original_filename>.pdf)
    - An Excel report (report_<original_filename>.xlsx)
   
## 🧪 Example Flow
1. Run:
   ```bash
   python main.py
   ```
2. A window will pop up asking you to select a .pdf file.
3. After processing:
  - Output PDF will be saved as:
    - formatted_<your_filename>.pdf
  - Report Excel file will be saved as:
    - report_<your_filename>.xlsx
  - Example output if you select invoice.pdf:
    - formatted_invoice.pdf
    - report_invoice.xlsx
