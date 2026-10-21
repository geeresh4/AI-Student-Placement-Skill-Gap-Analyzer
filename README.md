# AI-Powered Student Placement Prediction & Skill Gap Analyzer

Local academic decision-support demo: React/TypeScript, FastAPI, SQLite, SQLAlchemy and scikit-learn. Synthetic demo records and estimates are explicitly not real-world evidence.

## Quick start (Windows PowerShell, Python 3.11+ and Node 20+)

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup.ps1
.\run-dev.ps1
```

Visit http://localhost:5173; API docs http://localhost:8000/docs. Demo accounts: `student@demo.local` / `StudentDemo!2026`; `officer@demo.local` / `OfficerDemo!2026`. Change these and SECRET_KEY before deployment. Demo auth is not production security.

Setup generates 20,000 reproducible synthetic rows, trains and persists the demo model, seeds SQLite and installs frontend dependencies. Student workflows include profile edits, persisted model estimates, job-specific skill gaps and recommendation progress. Officer workflows include analytics, student search, jobs/matching, training plans, CSV exports and import preview.

## Data, training and import

No real data is bundled. Synthetic target generation and limitations: `docs/ml_methodology.md`. Sources and current access/terms policy: `docs/dataset_sources.md`. Retrain:

```powershell
.\.venv\Scripts\Activate.ps1
python data/synthetic/generate_demo_data.py --output data/synthetic/students.csv
python scripts/prepare_data.py --input data/synthetic/students.csv
python scripts/train_model.py --input data/synthetic/students.csv
python scripts/evaluate_model.py
```

Officer CSV Import validates and previews then requires explicit confirmation. Review provenance, license, label and mappings before importing. Inspect from CLI with `python scripts/validate_dataset.py data.csv`.

## Power BI

Use officer Reports CSV downloads. In Power BI Desktop, use Get Data → Text/CSV. Schema, measures and dictionary are in `powerbi/`. No PBIX or cloud integration is claimed.

## Tests and runtime

```powershell
.\.venv\Scripts\Activate.ps1
pytest
cd frontend; npm test; npm run build
```

Python 3.11+ and Node 20+; local ports 8000 and 5173. `.env.example` documents configuration. SQLite persists at `backend/placement.db`; PostgreSQL URL can be configured. Run `alembic upgrade head` or the seed script for schema.


## Add student accounts

Sign in as a placement officer, open **Students**, and choose **Add student**. Enter a unique student ID and email, name, program, graduation year, CGPA, an initial password of at least 12 characters, and optional comma-separated skills. The API stores only a password hash; share the initial password with the student privately. The student can sign in with that email and password and complete the rest of their profile.

For bulk profile-only imports, use **Reports & imports** and the CSV preview/confirmation workflow. CSV imports do not create student login accounts.
