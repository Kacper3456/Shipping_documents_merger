import fitz
import re
import zipfile
import os
import io
from PIL import Image
import tempfile


def merge_pdfs(
        pod_pdfs,
        einzerollkarte_pdfs,
        bordero_pdfs,
        output_pdf,
        bosch=False):
    """Merging Einzerollkarte with POD and optionally bordero"""
    output_files = []
    assert len(einzerollkarte_pdfs) > 0, "Einzerollkarte file is required."
    for pdf in einzerollkarte_pdfs:
        assert len(pod_pdfs) == 1, "Expected exactly one POD file."
        merged_pdf = fitz.open()
        current_pdf = fitz.open(pdf)
        merged_pdf.insert_pdf(current_pdf)

        for pod in pod_pdfs:
            current_pod = fitz.open(pod)
            merged_pdf.insert_pdf(current_pod)
            if bosch:
                assert len(
                    bordero_pdfs) == 1, "Expected exactly one bordero  file."
                add_bordero(merged_pdf, bordero_pdfs)
                merged_pdf.save(output_pdf + str(rename_file(pdf)) + ".pdf")
                output_files.append(
                    output_pdf + str(rename_file(pdf)) + ".pdf")

            else:
                merged_pdf.save(output_pdf + str(rename_file(pdf)) + ".pdf")
                output_files.append(
                    output_pdf + str(rename_file(pdf)) + ".pdf")
    return output_files


def convert_to_pdf(file):
    image = Image.open(file)
    rgb_image = image.convert("RGB")
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


def add_bordero(merged_pdf, bordero_pdfs):
    """adding bordero to merged file in case Bosch condition is fullfilled"""
    for bordero in bordero_pdfs:
        current_bordero = fitz.open(bordero)
        merged_pdf.insert_pdf(current_bordero)


def rename_file(file):
    """Renames file to number on einzerollkarte"""
    doc = fitz.open(file)
    page_text = doc.load_page(0)
    text = page_text.get_text()
    match = re.search(r'\b\d{16}\b', text)
    if match:
        file_name = match.group()
    else:
        file_name = "merged"
    return file_name


def save_uploaded_file_to_temp_pdf(uploaded_file):
    uploaded_file.seek(0)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.read())
        return temp_file.name
