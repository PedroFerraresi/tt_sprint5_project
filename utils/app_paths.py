# utilitários de caminho/diretórios (sem type annotations)
from pathlib import Path

def get_paths(project_root):
    """Retorna dicionário com caminhos importantes usados pelo app."""
    data_dir = project_root / "data"
    paths = {
        "DATA_DIR": data_dir,
        "DATA_RAW_DIR": data_dir / "raw",
        "DATA_PROCESSED_DIR": data_dir / "processed",
        "RAW_PATH": data_dir / "raw" / "dataset_ruido.csv",      # ajuste se necessário
        "PROCESSED_PATH": data_dir / "processed" / "processed.csv",
    }
    return paths

def ensure_dirs(paths):
    """Garante que as pastas data/raw e data/processed existam."""
    paths["DATA_RAW_DIR"].mkdir(parents=True, exist_ok=True)
    paths["DATA_PROCESSED_DIR"].mkdir(parents=True, exist_ok=True)
