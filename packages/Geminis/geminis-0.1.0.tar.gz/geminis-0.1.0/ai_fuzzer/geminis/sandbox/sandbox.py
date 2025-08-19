import subprocess
from pathlib import Path
import tempfile
import os
from textwrap import dedent
import venv

def sandbox_venv(code: str, save_path = os.getcwd(), debug=False) -> subprocess.CompletedProcess:
    """
    Always creates a Python 3.11 virtual environment, runs the supplied Python `code` inside it,
    and returns the `CompletedProcess` result (stdout/stderr captured).

    Notes
    -----
    - Assumes Python 3.11 is available at /usr/bin/python3.11.
    - This is not a secure sandbox; it isolates site-packages only.
    """
    print("DEBUG: starting python3.11 venv to run code")
    import shutil
    python_exe = shutil.which("python3.11")
    if not python_exe:
        raise RuntimeError("Python 3.11 not found. Please install it at /usr/bin/python3.11")
    workdir = tempfile.TemporaryDirectory()
    env_dir = Path(workdir.name) / "venv"
    subprocess.run([python_exe, "-m", "venv", str(env_dir)], check=True)
    env_python = env_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    script_path = env_dir / "sandbox_exec.py"
    script_path.write_text(dedent(code).lstrip())
    proc = subprocess.run(
        [str(env_python), str(script_path)],
        check=False,
        cwd=save_path
    )
    workdir.cleanup()
    print("DEBUG: closing python3.11 venv to run code")
    return proc

def save_to_file(text=None, path=None, debug=False):
    with open(os.path.join(path, 'gemini_created_code.py'), 'w') as f:
        f.write(text)
        if debug:
            print(f"DEBUG: Text length: {len(text) if text else 0}")
            
def run_file(filename=None):
    try:
        result = subprocess.run(
            [sys.executable, filename],                
        )
        print("Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error:", e.stderr)

