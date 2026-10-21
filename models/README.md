# Model artifacts

The trained model artifact is produced locally by `scripts/train_model.py` and is intentionally not required in the source archive; `setup.ps1` reliably trains it after dependencies and demo CSV are generated. Persisted artifact contains the fitted preprocessing/calibration pipeline, selected model, version, features, label, source and holdout evaluation. Do not interpret synthetic-demo metrics as real placement validation.
