# CS202 Lab 4: An Empirical Study of Git Diff Algorithms

This repository contains the source code and results for an empirical study on the differences between the `Myers` and `Histogram` Git diff algorithms.

## Overview

The purpose of this project was to analyze the frequency, nature, and impact of discrepancies between Git's default `Myers` diff and the more advanced `Histogram` algorithm. We developed a robust, parallel data pipeline in Python to mine three large-scale open-source repositories: `pandas`, `fastapi`, and `scikit-learn`.

The findings show that a tangible **4.18%** of all file modifications produce different diffs, and these discrepancies are concentrated in source code files. Our analysis, based on a context-aware heuristic, confirms that the **`Histogram` algorithm produces superior, more cohesive diffs for code changes.**

## Data Management and Reproducibility

The full execution of the pipeline on the selected repositories generates over 4 GB of data, which exceeds GitHub's file size limits.

In accordance with best practices for academic and professional projects, this repository prioritizes **reproducibility**. The full, multi-gigabyte datasets have been excluded from version control. Instead, we provide:

1.  **The complete source code** required to generate the data from scratch.
2.  **A representative sample** of the final datasets (`*_SAMPLE.csv`) in the `/results` directory for immediate inspection of the data schema and output.

## How to Run the Full Experiment

1.  Clone the repository.
2.  Create a Python virtual environment and install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Execute the main script. This will take approximately 20-30 minutes on a modern multi-core machine.
    ```bash
    python main.py
    ```
    The script is **fully resumable**. It will generate the large `raw_diff_dataset.csv` and `analyzed_diff_dataset.csv` files. If you run it a second time, it will detect these files and skip directly to the final plotting stage.

## Project Structure

-   `/main.py`: The main orchestrator for the experiment.
-   `/config.yaml`: Configuration file for selecting repositories.
-   `/src/`: Contains the core source code.
-   `/results/`: Contains the final output.
    -   `*_SAMPLE.csv`: Small samples of the datasets.
    -   `*.png`: The final plots used in the report.