import os
import ast
from typing import List
from pathlib import Path
from ai_fuzzer.geminis.logger.logs import log

def is_virtualenv_dir(path, debug=False):
    """
    Returns True if the given directory looks like a Python virtual environment.
    """
    pyvenv_cfg = os.path.join(path, "pyvenv.cfg")
    bin_python = os.path.join(path, "bin", "python")
    scripts_python = os.path.join(path, "Scripts", "python.exe")
    if os.path.isfile(pyvenv_cfg):
        if os.path.isfile(bin_python) or os.path.isfile(scripts_python):
            log(f"Found virtualenv at {path}, which we will ignore", debug)
            return True
    return False

def get_python_file_paths(directory_path, debug=False):
    """
    Recursively get .py files, skipping virtual environments.
    """
    log(f"Walking directory {directory_path} (type: {type(directory_path)})", debug)
    python_files: List[str] = []
    for root, dirs, files in os.walk(directory_path):
        dirs[:] = [d for d in dirs if not is_virtualenv_dir(os.path.join(root, d), debug)]
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                python_files.append(full_path)
                log(f"Found Python file: {full_path} (type: {type(full_path)})", debug)
    return python_files

def extract_functions(path: str | Path, debug=False) -> List[str]:
    """
    Parses a Python file and extracts all functions as source code strings.
    """
    if not isinstance(path, (str, Path)) or not Path(path).is_file():
        log(f"Invalid path or not a file: {path} (type: {type(path)})", debug)
        return []

    source_code = Path(path).read_text(encoding="utf-8")
    tree = ast.parse(source_code, filename=str(path))

    log(f"Parsed AST for file: {path} (length of source: {len(source_code)})", debug)

    functions = [
        ast.get_source_segment(source_code, node)
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]

    result = [func for func in functions if func is not None]

    log(f"Extracted {len(result)} function(s) from {path}", debug)

    return result

def extract_classes(path: str | Path, debug=False) -> List[str]:
    """
    Parses a Python file and extracts all classes as source code strings.
    """
    if not isinstance(path, (str, Path)) or not Path(path).is_file():
        log(f"Invalid path or not a file: {path} (type: {type(path)})", debug)
        return []

    source_code = Path(path).read_text(encoding="utf-8")
    tree = ast.parse(source_code, filename=str(path))

    log(f"Parsed AST for file: {path} (length of source: {len(source_code)})", debug)

    classes = [
        ast.get_source_segment(source_code, node)
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
    ]

    result = [cls for cls in classes if cls is not None]

    log(f"Extracted {len(result)} class(es) from {path}", debug)

    return result
