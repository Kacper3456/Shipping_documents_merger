"""
File for local testing purpose only
"""
from pathlib import Path
from pdf_utils import merge_pdfs

def merging_status(pod_files, einzerollkarte_files, bordero_files, output_path):
    """
    Verifies if merging process was sucessfull based on:
    - correct files input conditions,
    - correct merging output.

    Args:
        pod_files (list[Path]): POD list.
        einzerollkarte_files (list[Path]):Einzerollkarte files list.
        bordero_files (list[Path]):Bordero files list.
        output_path (Path | str): Output path.

    Returns:
        bool: True if merging was sucessful, False if it was not.
    """
    output_path = Path(output_path)

    if not pod_files:
        print("❌ Brak plików POD.")
        return False
    if not einzerollkarte_files:
        print("❌ Brak plików Einzerollkarte.")
        return False
    if not bordero_files:
        print("❌ Brak plików Bordero.")
        return False
    if not output_path.exists() or not any(output_path.iterdir()):
        print("❌ Brak plików wynikowych.")
        return False

    print("✅ Wszystkie pliki wejściowe i wyjściowe wyglądają poprawnie.")
    return True

# === KONFIGURACJA ===
BASE_PATH = Path("C:/Users/kacpe/PycharmProjects/DSV-PDF")
input_paths = {
    "einzerollkarte": f"{BASE_PATH}/Einzerollkarte",
    "pod": BASE_PATH / "PODs",
    "bordero": BASE_PATH / "Bordero",
}
output_path = BASE_PATH / "Output_PDFs"

# === WCZYTANIE PLIKÓW ===
def load_files(path: Path) -> list[Path]:
    return [f for f in path.iterdir() if f.is_file()]

Einzerollkarte = load_files(input_paths["einzerollkarte"])
pods_list = load_files(input_paths["pod"])
bordero_list = load_files(input_paths["bordero"])

# === LOGI WEJŚCIOWE ===
print(f"Einzerollkarte: {len(Einzerollkarte)} plik(ów)")
print(f"PODs: {len(pods_list)} plik(ów)")
print(f"Bordero: {len(bordero_list)} plik(ów)")

# === WALIDACJA WEJŚCIA ===
if not Einzerollkarte:
    print("⚠️ Brak plików Einzerollkarte – przerywam.")
    exit(1)

if len(pods_list) != 1:
    print("⚠️ Wymagany dokładnie jeden plik POD – przerywam.")
    exit(1)

# === URUCHOMIENIE MERGOWANIA ===
merge_pdfs(pods_list, Einzerollkarte, bordero_list, str(output_path), Bosch=True)

# === SPRAWDZENIE WYNIKU ===
status = merging_status(pods_list, Einzerollkarte, bordero_list, output_path)
print(f"✅ Merging complete: {status}")