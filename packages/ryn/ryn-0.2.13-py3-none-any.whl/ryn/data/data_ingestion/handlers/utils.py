import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def summarize_dataset(path: Path) -> str:
    summary_parts = []
    try:
        if path.is_file():
            if path.suffix == ".csv":
                df = pd.read_csv(path, nrows=5)
                return f"CSV file: {path.name} with columns: {list(df.columns)}"
            else:
                return f"File: {path.name}"
        csv_files = list(path.rglob("*.csv"))
        for csv in csv_files[:3]:
            try:
                df = pd.read_csv(csv, nrows=5)
                summary_parts.append(f"- CSV: {csv.relative_to(path)} (Cols: {list(df.columns)})")
            except Exception as e:
                summary_parts.append(f"- Could not read CSV '{csv.name}': {e}")
    except Exception as e:
        logger.warning(f"Could not generate summary for {path}: {e}")
        return f"Could not generate summary: {e}"
    return "\n".join(summary_parts) if summary_parts else "No summary available."


def save_request_info_to_temp(temp_path: Path, request_info: dict):
    try:
        with open(temp_path / "_request_info.json", 'w') as f:
            request_info["timestamp"] = datetime.now().isoformat()
            json.dump(request_info, f, indent=4)
    except (IOError, TypeError) as e:
        logger.warning(f"Could not save request info to temp directory {temp_path}: {e}")