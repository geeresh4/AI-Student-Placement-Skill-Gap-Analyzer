# API guide

FastAPI exposes interactive documentation at `http://localhost:8000/docs`. Authenticated endpoints use `Authorization: Bearer <access_token>`.

Core routes: `POST /api/auth/login`, `GET /api/auth/me`; `GET/PUT /api/student/profile`, `POST /api/student/predict`, `GET /api/student/history`, `GET /api/student/jobs/{id}/gaps`, `PUT /api/student/recommendations`; officer routes include `GET /api/officer/stats`, `GET /api/officer/students`, `GET/POST /api/officer/jobs`, `PUT /api/officer/jobs/{id}`, `GET /api/officer/jobs/{id}/matches`, training plans, CSV preview/confirm and CSV exports. `GET /api/health` provides a minimal health check.

Student endpoints resolve a profile from the authenticated account. Officer functions require the officer role. Imported files are bounded to 10 MB and require field mapping and a second explicit confirmation.
