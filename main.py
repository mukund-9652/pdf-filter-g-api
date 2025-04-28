
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

        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = doc[page_num].get_text()
            reason = None
            
            if not text.strip():
                pix = doc[page_num].get_pixmap()
                text = detect_text(pix)
            
            summary = summarize_text(text)
            found_keyword = contains_keywords(text, keywords)
            if found_keyword:  # If a keyword is found, log it
                reason = f"Contains keyword: {found_keyword}"

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
        
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
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

input = 'LY316_FF.pdf'
output = 'formatted_'+input
filter_pdf(input,output, 'report_log.xlsx')
