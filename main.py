
# Imports the Google Cloud client library
from google.cloud import vision
import argparse
from PIL import Image
import fitz  # PyMuPDF
from PyPDF2 import PdfReader, PdfWriter
import nltk
from nltk.corpus import wordnet
import pandas as pd
from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key='ADD_YOUR_OPEN_API_KEY_HERE'
)

nltk.download('wordnet')

def summarize_text(text):
    try:
        summaries = []

        response = client.chat.completions.create(
            model="gpt-4o",  # You can use "gpt-4" or "gpt-3.5-turbo"
            messages=[{"role": "user","content":f"Please summarize the following text:\n\n{text}\n\nSummary:"}],
            max_tokens=300,  # You can adjust this based on the length of the summary you need
            temperature=0.2,  # Controls creativity, lower = more factual
        )
        # Extracting the summarized text
        summaries.append(response.choices[0].message.content)
        final_summary = "\n".join(summaries)

        return final_summary
    except Exception as e:
        return f"Error: {str(e)}"

def detect_text(pixmap):
    """Detects full text in the file."""
    img = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
    temp_img_path = 'temp_image.png'
    img.save(temp_img_path)
    client = vision.ImageAnnotatorClient()

    with open(temp_img_path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    if texts:
        full_text = texts[0].description
        return full_text
    else:
        return ""



def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())  # Add synonym to set
    return synonyms
    
def filter_pdf(input_path, output_path, report_path):
    """Main PDF filtering function"""
    try:
        keywords = [
            "Consignment security declaration",
            "Air cargo manifest",
            "Air freight manifest",
            "Dangerous goods acceptance",
            "Consignment Security Certificate",
            "Notification to captain",
            "Wrong AWB",
            "Mail Lodgement Statement",
            "void",
            "missing"
        ]
        removal_log = []  # To log the removed pages

        reader = PdfReader(input_path)
        writer = PdfWriter()
        doc = fitz.open(input_path)

        keywords_with_synonyms = list(keywords)
        for keyword in keywords:
            synonyms = get_synonyms(keyword)
            keywords_with_synonyms.extend(synonyms)
        total = len(reader.pages)
        removed = 0
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = doc[page_num].get_text()
            reason = None
            
            if not text.strip():
                pix = doc[page_num].get_pixmap()
                text = detect_text(pix)
                print(f'Successfully scanned {page_num+1} out of {len(reader.pages)}')
            
            summary = summarize_text(text)
            found_keyword = contains_keywords(text, keywords)
            if found_keyword:  # If a keyword is found, log it
                reason = f"Contains keyword: {found_keyword}"
                removed+=1

            if reason:  # Log the removed page and reason
                removal_log.append({'Page Number': page_num + 1,'Summary':summary , 'Page Removed?':'Yes','Reason': reason})
            else:
                removal_log.append({'Page Number': page_num + 1,'Summary':summary ,'Page Removed?':'No','Reason': "Page not removed."})
                writer.add_page(page)

                # Write the output PDF
                with open(output_path, 'wb') as f:
                    writer.write(f)

        # Write Excel report
        report_df = pd.DataFrame(removal_log)
        report_df.to_excel(report_path, index=False)
        workbook = load_workbook(report_path)
        worksheet = workbook.active

        # Assuming the second column is 'B'
        for row in worksheet['B']:
            row.alignment = Alignment(wrapText=True)

        workbook.save(report_path)
        return True,total,removed
    except Exception as e:
        print(f"Error: {str(e)}")
        return False,total,removed
def contains_keywords(text, keywords):
    """Check if text contains any keywords with possible intervening characters"""
    import re
    
    text = text.lower()
    keywords = [k.lower() for k in keywords]

    for keyword in keywords:
        # Split keyword into words
        words = re.split(r'\s+', keyword.strip())
        # Build pattern allowing optional non-word characters between words
        pattern = r'\b' + r'\W*'.join(map(re.escape, words)) + r'\b'
        
        if re.search(pattern, text):
            return keyword  # Return the found keyword
    
    return None  # Return None if no keyword is found

import tkinter as tk
from tkinter import filedialog

try:
    # Create a root Tkinter window and hide it
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Open a file dialog to select a PDF file
    input_file_path = filedialog.askopenfilename(
        title='Select a PDF File',
        filetypes=[('PDF Files', '*.pdf')]
    )

    # Check if a file was selected
    if input_file_path:
        output_file_path = 'formatted_' + input_file_path.split('/')[-1]
        report_file_path = 'report_' + input_file_path.split('/')[-1].replace('.pdf', '.xlsx')
        start_time = time.time()
        success,total_pages,filtered_pages = filter_pdf(input_file_path, output_file_path, report_file_path)
        end_time = time.time()
        time_taken = end_time - start_time
        mins, secs = divmod(time_taken, 60)
        if success:
            print("\n=== Filtering Summary ===")
            print(f"Time taken: {int(mins)} min {secs:.2f} sec")
            print(f"Initial number of pages: {total_pages}")
            print(f"Number of pages filtered out: {filtered_pages}")
            print(f"Final number of pages: {total_pages - filtered_pages}")
            print(f'The output file is generated at {output_file_path}.')
            print(f'The report file is generated at {report_file_path}.')
        else:
            print('File not processed completely')
    else:
        print("No file selected.")
except Exception as e:
    print(e)
