"""
main.py
-------
GridGuard AI — primary entry point.

Usage
-----
  python main.py              # run pipeline with cached model
  python main.py --retrain    # force model retraining

After completion, results are saved to:
  src/results/predictions.csv

To launch the dashboard:
  streamlit run src/dashboard/app.py
"""

import sys
from pathlib import Path

# Add src/ to path so imports resolve correctly from project root
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pipeline import run_pipeline

if __name__ == "__main__":
    force_retrain = "--retrain" in sys.argv
    results = run_pipeline(force_retrain=force_retrain)
    print(f"\nDone. {len(results)} equipment records processed.")
    print("Launch dashboard with:  streamlit run src/dashboard/app.py")
