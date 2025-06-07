import fitz
from pathlib import Path
import re
import zipfile
import os
import io
from PIL import Image
import tempfile

def merge_pdfs(POD_pdfs, einzerollkarte_pdfs,bordero_pdfs, output_pdf,Bosch=False):
    """Merging Einzerollkarte with POD and optionally bordero"""
    output_files = []

    for pdf in einzerollkarte_pdfs:
        merged_pdf = fitz.open()
        current_pdf=fitz.open(pdf)
        merged_pdf.insert_pdf(current_pdf)
        if len(POD_pdfs)!=1:
            print("Too many/little PODs elements,"
                  " please attach only single POD you want to merge")
            break
        else:
            for pod in POD_pdfs:
                current_pod=fitz.open(pod)
                merged_pdf.insert_pdf(current_pod)
                if Bosch:
                    if len(bordero_pdfs) != 1:
                        print("Too many/little PODs elements,"
                    " please attach only single POD you want to merge")
                        break
                    for bordero in bordero_pdfs:
                        add_bordero(merged_pdf,bordero_pdfs)
                        merged_pdf.save(output_pdf +str(rename_file(pdf))  + ".pdf")
                        output_files.append(output_pdf + str(rename_file(pdf)) + ".pdf")
                        continue
                elif len(bordero_pdfs) != 0:
                    print("Bordero is necessary only for bosch."
                          "Please delete file or mark shipment as such before merging")
                    break
                else:
                    merged_pdf.save(output_pdf+str(rename_file(pdf))+".pdf")
                    output_files.append(output_pdf+str(rename_file(pdf))+".pdf")
    return output_files
def convert_to_pdf(file):
    image=Image.open(file)
    rgb_image=image.convert("RGB")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        pdf_path = temp_pdf.name
        rgb_image.save(pdf_path, "PDF")

    return pdf_path

def zip_files(file_paths):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for path in file_paths:
            filename = os.path.basename(path)
            with open(path, "rb") as f:
                zipf.writestr(filename, f.read())
    buffer.seek(0)
    return buffer

def add_bordero(merged_pdf,bordero_pdfs):
    """adding bordero to merged file in case Bosch condition is fullfilled"""
    for bordero in bordero_pdfs:
        current_bordero = fitz.open(bordero)
        merged_pdf.insert_pdf(current_bordero)

def rename_file(file):
    """Renames file to number on einzerollkarte"""
    doc=fitz.open(file)
    page_text=doc.load_page(0)
    text=page_text.get_text()
    match=re.search(r'\b\d{16}\b',text)
    if match:
        file_name=match.group()
    else:
        file_name="merged"
    return file_name

def save_uploaded_file_to_temp_pdf(uploaded_file):
    uploaded_file.seek(0)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.read())
        return temp_file.name