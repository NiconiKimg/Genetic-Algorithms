from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from benchmarks import run_e1e2, run_e3
from logger import Logger

if __name__ == '__main__':
    logger = Logger()
    logger.clear()
    # quick sweep for e1e2: n = 4,6,8,10; k=3
    n_values = [4,5,6,8,10]
    run_e1e2(logger, n_values=n_values, k=10, shuffle=False, start_seed=0)
    print('Quick benchmark finished. CSV at', logger.csv_location())
