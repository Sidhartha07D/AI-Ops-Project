# AI4I 2020 source data

Source: UCI Machine Learning Repository, AI4I 2020 Predictive Maintenance Dataset (ID 601). https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset

Citation: AI4I 2020 Predictive Maintenance Dataset [Dataset]. (2020). UCI Machine Learning Repository. https://doi.org/10.24432/C5HS5C

License: Creative Commons Attribution 4.0 International (CC BY 4.0).

Downloaded on 2026-11-07 from https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip. The ZIP SHA-256 is `f601f14294bcf190f9d720676b7f0aea46a26cde9ab8ebc7b4f8174d9d26b252`. The extracted `ai4i2020.csv` SHA-256 is `dc6630cd9b1f0f853922fad78a1b6436570d3f1ec863f1dd5c4340ac56bc8a8e`.

The dataset is synthetic. Its `Machine failure` target marks failure at the row's observation; it does not provide a future failure horizon. The input features for modeling are `Type`, `Air temperature [K]`, `Process temperature [K]`, `Rotational speed [rpm]`, `Torque [Nm]`, and `Tool wear [min]`. `UDI` and `Product ID` are identifiers. `TWF`, `HDF`, `PWF`, `OSF`, and `RNF` are failure mode indicators and must not be used as model inputs because they disclose the outcome.

The raw CSV is tracked with DVC. Run `python src/validate_data.py` from the repository root to inspect its schema and labels.

On this VM, DVC's default remote is a local directory at `/home/sidhartha/dvc-storage/smart-maintenance`; it is configured in the Git-ignored `.dvc/config.local`. `dvc push` and `dvc pull` have been verified. A Git clone on another machine will need its own DVC remote or a fresh download from the UCI URL above. The local DVC remote is a learning demonstration, not a shared backup service.
