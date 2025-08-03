import os
import subprocess

if os.name == "nt":
    PY_VENV = ".venv\\Scripts\\python"
else:
    PY_VENV = ".venv/bin/python"

if __name__ == "__main__":
    subprocess.run([PY_VENV, str(os.path.join('src','pipeline','get_raw_data.py'))], check=True)
    subprocess.run([PY_VENV, str(os.path.join('src','pipeline','process_raw_data.py'))], check=True)
    subprocess.run([PY_VENV, str(os.path.join('src','pipeline','conduct_sentiment_analysis.py'))], check=True)
    subprocess.run([PY_VENV, str(os.path.join('src','pipeline','compile_final_data.py'))], check=True)