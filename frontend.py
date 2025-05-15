import streamlit as st
from streamlit import session_state
import streamlit.components.v1 as components
from pdf_utils import merge_pdfs,zip_files,convert_to_pdf
import tempfile
import os
from pathlib import Path
import base64

# Sprawdź, jaki motyw jest ustawiony
current_theme = st.get_option("theme.base")

# Ustaw tło i style w zależności od motywu
if current_theme == "dark":
    bg_color = "rgba(0, 0, 0, 0.6)"
    text_color = "white"
else:
    bg_color = "rgba(255, 255, 255, 0.6)"
    text_color = "black"

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



if "uploaded_files" not in st.session_state:
    st.session_state["uploaded_files"]=[]

with st.expander("Options"):
    Bosch = st.checkbox("Bosch shipment")
    to_zip = st.checkbox("Convert to zip")

with st.form("merge_form",clear_on_submit=False):
    st.subheader("POD merger for german transports")
    uploaded_einzerollkarte=st.file_uploader("Einzerollkarte", type="pdf",
                                             accept_multiple_files=True
    )
    uploaded_POD = st.file_uploader("POD", type=["pdf","jpeg","jpg","png"], accept_multiple_files=False)
    if Bosch:
        uploaded_Bordero = st.file_uploader("Bordero", type="pdf",
                                            accept_multiple_files=False)
    merging_button=st.form_submit_button("Merge")
if merging_button:
    if uploaded_einzerollkarte and uploaded_POD:
        #storing file paths as lists
        einzerollkarte_paths=[]
        pod_paths=[]
        bordero_paths = []


        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_output:
            #creating temporary pdf file
            for file in uploaded_einzerollkarte:
                #creating separate file for every einzerollkarte
                temp=tempfile.NamedTemporaryFile(delete=False,suffix=".pdf")
                temp.write(file.read())
                temp.close()
                einzerollkarte_paths.append(temp.name)
            # creating separate file for POD file

            # creating separate file for Bordero file
            if uploaded_POD:
                pod_format = Path(uploaded_POD.name).suffix.lower()
                if pod_format in [".jpg", ".jpeg", ".png"]:
                    # If the POD is an image, convert to PDF
                    converted_pod_path = convert_to_pdf(uploaded_POD)
                    pod_paths = [converted_pod_path]  # Replacing pod_paths with one PDF file
                else:
                    # If the POD is already a PDF, save it directly
                        temp_pod = tempfile.NamedTemporaryFile(delete=False,suffix=".pdf")
                        temp_pod.write(uploaded_POD.read())
                        temp_pod.close()
                        pod_paths.append(temp_pod.name)
            temp_output_prefix = tempfile.gettempdir() + os.sep
        if Bosch:
            if uploaded_Bordero:
                temp_bordero = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                temp_bordero.write(uploaded_Bordero.read())
                temp_bordero.close()
                bordero_paths.append(temp_bordero.name)
                merged_files=merge_pdfs(pod_paths,einzerollkarte_paths,bordero_paths,
                                        temp_output_prefix,True)
                if merged_files:
                    st.session_state["uploaded_files"] = merged_files
            else:
                st.warning("Bordero is missing")
                st.stop()
        else:
            merged_files = merge_pdfs(pod_paths, einzerollkarte_paths, bordero_paths,
                                      temp_output_prefix, False)
            if merged_files:
                st.session_state["uploaded_files"]=merged_files
        if to_zip:
            zip_data = zip_files(st.session_state["uploaded_files"])

            st.download_button(
                label="📦 Download ZIP",
                data=zip_data,
                file_name="merged_pdfs.zip",
                mime="application/zip"
            )
        else:
            for i,path in enumerate(st.session_state["uploaded_files"]):
                    with open(path, "rb") as f:
                        filename = os.path.basename(path)
                        if filename.endswith("merged.pdf"):
                            filename=f"merged{i}.pdf"
                        st.download_button(f"Download {filename}", f.read(), file_name=filename,
                                           mime="application/pdf",key=f"download_{i}",on_click="ignore")
                        st.toast("Merged succesfully")
    else:
        st.warning("Einzerollkarte or POD is missing")

