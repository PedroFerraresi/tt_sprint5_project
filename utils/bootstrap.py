# utils/bootstrap.py
# ------------------------------------------------------------
# Centraliza o ajuste do sys.path para evitar repetição.

from pathlib import Path
import sys

def add_root(project_root_path):
    """
    Adiciona 'project_root_path' ao sys.path, se ainda não estiver.
    Use no main.py (normalmente suficiente para todo o app).
    """
    root = Path(project_root_path).resolve()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return root

def add_root_relative_to(this_file_path, up=1):
    """
    Útil quando você executa um script isolado (ex.: pages/*.py pelo VS Code).
    Sobe 'up' níveis a partir do arquivo atual e adiciona ao sys.path.
    Ex.: add_root_relative_to(__file__, up=1)  # de pages/ para a raiz
    """
    p = Path(this_file_path).resolve()
    for _ in range(max(0, int(up))):
        p = p.parent
    return add_root(p)
