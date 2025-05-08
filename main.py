from pathlib import Path
from pdf_utils import merge_pdfs,add_bordero,merging_status,check_bordero


folder_path=Path(f"C:\\Users\\kacpe\\PycharmProjects\\DSV-PDF\\Einzerollkarte")
Einzerollkarte=[]
POD_path=Path("C:\\Users\\kacpe\\PycharmProjects\\DSV-PDF\\PODs")
pods_list=[]
bordero_path=Path("C:\\Users\\kacpe\\PycharmProjects\\DSV-PDF\\Bordero")
bordero_list=[]
for file in folder_path.iterdir():
    if file.is_file():
        Einzerollkarte.append(file)
for file in POD_path.iterdir():
    if file.is_file():
        pods_list.append(file)
for file in bordero_path.iterdir():
    if file.is_file():
        bordero_list.append(file)
merge_pdfs(pods_list, Einzerollkarte, bordero_list, "C:\\Users\\kacpe\\PycharmProjects\\DSV-PDF\\Output_PDFs\\", Bosch=True)

print((merging_status(pods_list, Einzerollkarte, bordero_list, "C:\\Users\\kacpe\\PycharmProjects\\DSV-PDF\\Output_PDFs")) and check_bordero(bordero_list))
