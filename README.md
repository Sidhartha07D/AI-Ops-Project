# Smart Maintenance Monitor

DA3408 course project using the UCI AI4I 2020 Predictive Maintenance dataset.

This project will build an observation-level machine failure classifier and demonstrate a reproducible AIOps workflow: data versioning, distributed data processing, experiment tracking, model serving, a user interface, container orchestration, and monitoring.

The project is developed incrementally in an Ubuntu ARM64 VM. Model metrics will be reported honestly; the main learning goal is to demonstrate the tools and workflow.

## Data preparation

Activate the `smart-maintenance` environment and run `dvc repro` to prepare the raw CSV with Spark and Ray. The two jobs are deliberately limited to two local workers and run sequentially on the VM. Run `python src/compare_features.py` to check that their 10,000-row outputs match. See `data/README.md` for source and license details and `docs/feature_schema.md` for the model input columns.

## Exploration and fixed splits

Run `python src/explore_data.py` to regenerate the data audit and figures. The DVC pipeline now compares the Spark/Ray outputs and creates a seeded 60/20/20 stratified ID manifest with a locked test set. `dvc repro` recreates these inputs before training. The split report is in `reports/split_summary.json` after `dvc pull` or reproduction.
