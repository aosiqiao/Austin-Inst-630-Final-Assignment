import pdfplumber
import json
import os

PDF_FOLDER = "/Users/aosiqiao/Desktop/PDF Folder"
OUTPUT_FILE = "/Users/aosiqiao/Desktop/research_data.json"  

data = []

for pdf_file in os.listdir(PDF_FOLDER):
    if pdf_file.endswith(".pdf"):  
        file_path = os.path.join(PDF_FOLDER, pdf_file)
        print(f"Processing {file_path}...")
        
        with pdfplumber.open(file_path) as pdf:
            content = ""
            for page in pdf.pages:
                content += page.extract_text() + "\n"  
            
            data.append({
                "file_name": pdf_file,
                "content": content.strip()  
            })

with open(OUTPUT_FILE, "w", encoding="utf-8") as json_file:
    json.dump(data, json_file, indent=4)

print(f"Data saved to {OUTPUT_FILE}")
