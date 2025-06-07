import streamlit as st
from pdf_utils import merge_pdfs, zip_files, convert_to_pdf, save_uploaded_file_to_temp_pdf
import tempfile
import os
from pathlib import Path
import base64

#setting up custom theme
bg_color = "rgba(255, 255, 255, 0.6)"
text_color = "Chocolate"


def get_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()



bg_img = get_base64("background.jpg")

custom_css = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/jpg;base64,{bg_img}");
    background-size: cover;
    background-position: center;
}}

.block-container {{
    background-color: {bg_color};
    color: {text_color};
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}}
[data-testid="stHeader"] {{
    background-color: rgba(0, 0, 0, 0);
    color: inherit;
}}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

def remove_files():
    st.session_state.pop("einzerollkarte", None)
    st.session_state.pop("POD", None)

if "reset_counter" not in st.session_state:
    st.session_state.reset_counter = 0

# Deletes all uploaded files
if st.button("🗑️Remove all"):
    st.session_state.reset_counter += 1
    st.session_state.Bosch_shipment = False
    st.rerun()

# create keys necessary to refresh file uploader
uploader_key1 = f"einzerollkarte_{st.session_state.reset_counter}"
uploader_key2 = f"POD_{st.session_state.reset_counter}"
uploader_key3 = f"Bordero_{st.session_state.reset_counter}"


if "uploaded_files" not in st.session_state:
    st.session_state["uploaded_files"] = []

with st.expander("Options"):
#checkboxes to enable adding bordero and converting output files to zip
    Bosch = st.checkbox("Bosch shipment", key="Bosch_shipment")
    to_zip = st.checkbox("Convert to zip", key="zip")

with st.form("merge_form", clear_on_submit=False):
#add form for uploading temporary files and triggering merging
    st.subheader("German Transport Document Merger")
    uploaded_einzerollkarte = st.file_uploader("Einzerollkarte", type="pdf",
                                               accept_multiple_files=True,
                                               key=uploader_key1
                                               )
    uploaded_POD = st.file_uploader(
        "POD",
        type=[
            "pdf",
            "jpeg",
            "jpg",
            "png"],
        accept_multiple_files=False,
        key=uploader_key2)
    if Bosch:
        uploaded_Bordero = st.file_uploader("Bordero", type="pdf",
                                            accept_multiple_files=False,
                                            key=uploader_key3)
    merging_button = st.form_submit_button("Merge")
if merging_button:
    if uploaded_einzerollkarte and uploaded_POD:
        # storing file paths as lists
        einzerollkarte_paths = []
        pod_paths = []
        bordero_paths = []



        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_output:
            # save einzerollkarte to temp file
            for file in uploaded_einzerollkarte:
                einzerollkarte_paths.append(save_uploaded_file_to_temp_pdf(file))

            if uploaded_POD:
                #check file format and convert to pdf
                pod_format = Path(uploaded_POD.name).suffix.lower()
                if pod_format in [".jpg", ".jpeg", ".png"]:
                    converted_pod_path = convert_to_pdf(uploaded_POD)
                    pod_paths = [converted_pod_path]
                else:
                    pod_paths.append(save_uploaded_file_to_temp_pdf(uploaded_POD))

            temp_output_prefix = tempfile.gettempdir() + os.sep

        if Bosch and uploaded_Bordero:
            #add bordero to merged file
            bordero_paths.append(save_uploaded_file_to_temp_pdf(uploaded_Bordero))
            merged_files = merge_pdfs(
                pod_paths,
                einzerollkarte_paths,
                bordero_paths,
                temp_output_prefix,
                True
            )
            if merged_files:
                st.session_state["uploaded_files"] = merged_files
            else:
                st.warning("Bordero is missing")
                st.stop()
        else:
            merged_files = merge_pdfs(
                pod_paths,
                einzerollkarte_paths,
                bordero_paths,
                temp_output_prefix,
                False)
            if merged_files:
                st.session_state["uploaded_files"] = merged_files
                st.session_state["show_zip"] = to_zip
        if to_zip:
            #generate download button for zip file
            zip_data = zip_files(st.session_state["uploaded_files"])

            st.download_button(
                label="📦 Download ZIP",
                data=zip_data,
                file_name="merged_pdfs.zip",
                mime="application/zip"
            )

        else:
            #generate separate button for each merged file
            for i, path in enumerate(st.session_state["uploaded_files"]):
                with open(path, "rb") as f:
                    filename = os.path.basename(path)
                    if filename.endswith("merged.pdf"):
                        filename = f"merged{i}.pdf"
                    st.download_button(
                        f"Download {filename}",
                        f.read(),
                        file_name=filename,
                        mime="application/pdf",
                        key=f"download_{i}",
                        on_click="ignore")
        st.toast("Merged succesfully")


    else:
        st.warning("Einzerollkarte or POD is missing")
