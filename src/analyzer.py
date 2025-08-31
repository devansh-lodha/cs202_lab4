import pandas as pd
from src.utils.diff_utils import find_discrepancy, apply_heuristic
from src.utils.file_utils import classify_file_type
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import numpy as np
import logging

def _apply_analysis_to_chunk(df_chunk):
    """
    Worker function to apply the full analysis pipeline to a DataFrame chunk.
    This function is pure and operates only on data, making it perfectly safe for parallelization.
    """
    # Apply discrepancy and file type classification first
    df_chunk['Discrepancy'] = df_chunk.apply(find_discrepancy, axis=1)
    df_chunk['file_type'] = df_chunk['new_file_path'].fillna(df_chunk['old_file_path']).apply(classify_file_type)
    
    # Apply the heuristic, which returns a dictionary of new columns
    heuristic_results = df_chunk.apply(apply_heuristic, axis=1).apply(pd.Series)
    
    # Join the new columns back to the chunk
    return df_chunk.join(heuristic_results)

def analyze_data_in_parallel(df, config):
    """
    Runs the full analysis pipeline in parallel on the consolidated DataFrame.
    """
    logger = logging.getLogger(__name__)
    num_procs = config['parallel_processes'] or cpu_count()
    logger.info(f"Analyzing {len(df)} records in parallel across {num_procs} cores.")
    
    # Split the DataFrame into chunks for the worker pool.
    # Splitting into more chunks than processes helps with load balancing.
    chunks = np.array_split(df, num_procs * 4)
    
    analyzed_chunks = []
    with Pool(processes=num_procs) as pool:
        with tqdm(total=len(chunks), desc="Analyzing data") as pbar:
            for result_chunk in pool.imap_unordered(_apply_analysis_to_chunk, chunks):
                analyzed_chunks.append(result_chunk)
                pbar.update()

    # Consolidate the processed chunks back into a single DataFrame
    analyzed_df = pd.concat(analyzed_chunks)
    return analyzed_df