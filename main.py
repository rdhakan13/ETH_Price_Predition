import os
import subprocess

if os.name == "nt":
    PY_VENV = ".venv/Scripts/python"
else:
    PY_VENV = ".venv/bin/python"

if __name__ == "__main__":
    subprocess.run([PY_VENV, "src/pipeline/get_raw_data.py"], check=True)
    subprocess.run([PY_VENV, "src/pipeline/process_raw_data.py"], check=True)
    subprocess.run([PY_VENV, "src/pipeline/conduct_sentiment_analysis.py"], check=True)
    subprocess.run([PY_VENV, "src/pipeline/compile_final_data.py"], check=True)
    subprocess.run([PY_VENV, "src/pipeline/run_model.py"], check=True)
    subprocess.run([PY_VENV, "src/pipeline/get_results.py"], check=True)