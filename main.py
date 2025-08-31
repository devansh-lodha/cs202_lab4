import time
import logging
import pandas as pd
from multiprocessing import Pool, cpu_count
from functools import partial
import os
import warnings

from src.config_loader import load_config_and_prepare_dirs
from src.data_miner import mine_single_repository
from src.analyzer import analyze_data_in_parallel
from src.plotter import Plotter

# Suppress the numpy FutureWarning from pandas internals in multiprocessing
warnings.simplefilter(action='ignore', category=FutureWarning)
# Suppress the UserWarning about leaked semaphores on macOS, which is a known, non-fatal issue.
warnings.filterwarnings("ignore", message="resource_tracker: There appear to be 1 leaked semaphore objects to clean up at shutdown")

def main():
    """Main orchestrator for the diff analysis experiment with checkpointing."""
    logger = logging.getLogger(__name__)
    start_time = time.time()
    
    config = load_config_and_prepare_dirs()
    repo_urls = config['repositories']
    raw_csv_path = os.path.join(config['results_dir'], "raw_diff_dataset.csv")
    analyzed_csv_path = os.path.join(config['results_dir'], "analyzed_diff_dataset.csv")

    # --- Stage 1: Parallel Mining (with checkpointing) ---
    if os.path.exists(raw_csv_path):
        logger.info(f"Found existing raw dataset at '{raw_csv_path}'. Skipping mining stage.")
        raw_df = pd.read_csv(raw_csv_path)
    else:
        available_cores = cpu_count()
        num_procs_config = config['parallel_processes'] or available_cores
        num_procs_mining = min(num_procs_config, len(repo_urls))
        logger.info(f"Starting parallel mining of {len(repo_urls)} repositories across {num_procs_mining} cores.")
        
        worker_func = partial(mine_single_repository, config=config)
        with Pool(processes=num_procs_mining) as pool:
            list_of_dataframes = pool.map(worker_func, repo_urls)
        
        raw_df = pd.concat(list_of_dataframes, ignore_index=True)
        raw_df.to_csv(raw_csv_path, index=False)
        logger.info(f"All mining complete. Saved {len(raw_df)} total records to '{raw_csv_path}'.")

    # --- Stage 2: Parallel Analysis (with checkpointing) ---
    if os.path.exists(analyzed_csv_path):
        logger.info(f"Found existing analyzed dataset at '{analyzed_csv_path}'. Skipping analysis stage.")
        analyzed_df = pd.read_csv(analyzed_csv_path)
    else:
        logger.info("Starting parallel data analysis pipeline...")
        analyzed_df = analyze_data_in_parallel(raw_df, config)
        analyzed_df.to_csv(analyzed_csv_path, index=False)
        logger.info(f"Data analysis complete. Saved to '{analyzed_csv_path}'.")

    # --- Stage 3: Visualization (always runs, as it's fast) ---
    logger.info("Generating all visualizations...")
    plotter = Plotter(analyzed_df, config['results_dir'])
    plotter.generate_all_plots()
    logger.info("Visualizations saved successfully.")

    logger.info(f"Experiment finished in {time.time() - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()