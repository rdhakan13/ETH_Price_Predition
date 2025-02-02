from pathlib import Path

def get_working_directory() -> str:
    current_path = Path(__file__).resolve()
    while current_path != current_path.parent:
        if (current_path / '.git').exists():
            break
        current_path = current_path.parent
    return current_path
