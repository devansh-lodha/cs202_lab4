import logging
import pandas as pd
from pydriller import Repository
from tqdm import tqdm

def mine_single_repository(repo_url, config):
    """
    Mines a single repository for both Myers and Histogram diffs.
    This function is designed to be run as a worker in a parallel pool.
    """
    repo_name = repo_url.split('/')[-1]
    logger = logging.getLogger(repo_name)
    logger.info("Starting safe, sequential mining process for this repository.")

    # Each worker process safely initializes its own Repository objects.
    # Since each worker handles a different repo_url, there are no conflicts.
    repo_myers = Repository(repo_url, clone_repo_to=config['clone_dir'], order='reverse')
    repo_hist = Repository(repo_url, clone_repo_to=config['clone_dir'], order='reverse', histogram_diff=True)

    logger.info("Building histogram diff lookup table...")
    hist_commits = {c.hash: c for c in tqdm(repo_hist.traverse_commits(), desc=f"Pre-caching Hist ({repo_name})")}

    logger.info("Processing commits and matching diffs...")
    all_data = []
    for commit_myers in tqdm(repo_myers.traverse_commits(), desc=f"Mining ({repo_name})"):
        if not commit_myers.parents:
            continue
        
        commit_hist = hist_commits.get(commit_myers.hash)
        if not commit_hist:
            continue

        hist_mod_lookup = {mod.new_path or mod.old_path: mod.diff for mod in commit_hist.modified_files}

        for mod_myers in commit_myers.modified_files:
            file_key = mod_myers.new_path or mod_myers.old_path
            all_data.append({
                'repo_name': repo_name,
                'commit_sha': commit_myers.hash,
                'parent_commit_sha': commit_myers.parents[0],
                'old_file_path': mod_myers.old_path,
                'new_file_path': mod_myers.new_path,
                'diff_myers': mod_myers.diff,
                'diff_hist': hist_mod_lookup.get(file_key)
            })

    logger.info(f"Safe mining complete. Found {len(all_data)} modified file entries for this repo.")
    return pd.DataFrame(all_data)