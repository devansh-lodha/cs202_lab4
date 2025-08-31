import pandas as pd

def _normalize_diff(diff_text):
    """Normalizes a diff string for robust comparison."""
    if not isinstance(diff_text, str): return ""
    lines = [line.strip() for line in diff_text.strip().split('\n')]
    return "\n".join(filter(None, lines))

def find_discrepancy(row):
    """Applies normalized comparison to determine if diffs are different."""
    norm_myers = _normalize_diff(row['diff_myers'])
    norm_hist = _normalize_diff(row['diff_hist'])
    return 'No' if norm_myers == norm_hist else 'Yes'

def apply_heuristic(row):
    """
    Applies a context-aware heuristic and returns results as a dictionary.
    """
    if row['Discrepancy'] == 'No':
        return {'preferred_algorithm': 'N/A'}
    
    diff_myers, diff_hist = row['diff_myers'], row['diff_hist']
    if pd.isna(diff_myers) or pd.isna(diff_hist):
        return {'preferred_algorithm': 'Inconclusive'}

    # Calculate metrics
    hunks_myers = diff_myers.count('@@ ')
    hunks_hist = diff_hist.count('@@ ')
    lines_myers = len(diff_myers)
    lines_hist = len(diff_hist)

    # Decision logic
    preferred = 'Tie'
    is_code = row['file_type'] in ['Source Code', 'Test Code']
    if is_code:
        if hunks_hist < hunks_myers: preferred = 'Histogram'
        elif hunks_myers < hunks_hist: preferred = 'Myers'
        elif lines_hist < lines_myers: preferred = 'Histogram'
        elif lines_myers < lines_hist: preferred = 'Myers'
    else:
        if lines_hist < lines_myers: preferred = 'Histogram'
        elif lines_myers < lines_hist: preferred = 'Myers'
        elif hunks_hist < hunks_myers: preferred = 'Histogram'
        elif hunks_myers < hunks_hist: preferred = 'Myers'
        
    return {
        'preferred_algorithm': preferred,
        'hunks_myers': hunks_myers,
        'hunks_hist': hunks_hist,
        'lines_myers': lines_myers,
        'lines_hist': lines_hist
    }