from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = SRC_DIR / "data" / "raw"
PROCESSED_DATA_DIR = SRC_DIR / "data" / "processed"
MODEL_DIR = SRC_DIR / "models"
RESULTS_DIR = SRC_DIR / "results"
