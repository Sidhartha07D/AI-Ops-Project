# AI assistance disclosure

AI assistance has been used for project planning and Phase 1 setup. With the student's authorization, an AI assistant created the initial project files and Python environment in the Ubuntu VM over SSH, verified the setup, and prepared the Git commit. The student will review the results and update this record as further AI assistance is used in code, debugging, evaluation, and documentation.

For Phase 2, the assistant downloaded the official UCI dataset, copied it into the VM, wrote and ran a CSV validation script, installed DVC, configured a local DVC remote, and verified a restore. The student should review the dataset choice, validation output, and DVC evidence.

For Phase 3, the assistant wrote the Spark and Ray preparation scripts, configured the DVC pipeline, ran both jobs in the VM, and compared their outputs. The student should review the feature definitions, run evidence screenshots, and update this disclosure if the implementation changes.

The assistant also timed one Spark and one Ray preparation run, calculated throughput, and documented the measurement limits. These are observed values, not predicted performance.

For Phase 4, the assistant added the exploratory analysis, plots, and fixed train/validation/test split logic, including checks for exact duplicate inputs and target/failure-mode disagreements. The assistant also implemented four model candidates, ran the tracked MLproject entry points, selected a threshold on validation data, evaluated the locked test once, saved a loadable probability model in MLflow, and recorded the observed metrics and VM-browser screenshots. The student should review the model card, MLflow runs, and limitations before submission.


For Phase 5, the assistant implemented and tested a local MLflow model endpoint, FastAPI wrapper, separate browser UI, pipeline status/validation console, and feedback review queue. The assistant ran an integration smoke check and inspected the browser pages in the VM. The student should review the API contract, UI behavior, screenshots, and any later changes before submission.

For Phase 6, the assistant exported the selected MLflow model to a DVC-tracked artifact, created three Docker Compose services, adjusted the API for its container address, added four focused API tests and a CI workflow definition, and ran container integration checks in the VM. The student should review the Docker layout, observed test report, and CI behavior after the project is pushed to GitHub.
