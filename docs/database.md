# Database

SQLAlchemy models are in `backend/app/models.py`; SQLite defaults to `backend/placement.db`. The schema persists users, student profiles and skills JSON, jobs and requirements JSON, predictions, recommendation progress, training plans and import audit metadata. Credentials are in the users table and never returned by profile endpoints. The included Alembic revision initializes the schema; run from project root with `alembic -c backend/alembic.ini upgrade head`. PostgreSQL can be configured through `DATABASE_URL` with the included psycopg driver.
