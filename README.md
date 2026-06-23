# CyberSafe Uzbekistan

Backend foundation for the CyberSafe Uzbekistan digital-safety platform.

## Included in the first increment

- Django REST API with OpenAPI/Swagger documentation
- PostgreSQL and Redis development services
- Privacy-preserving phone storage (encrypted value + HMAC lookup index)
- OTP registration/login flow
- JWT access and refresh tokens
- Role-ready custom user model
- Automated API tests
- Bilingual quiz sessions with server-side scoring
- PDF certificates with QR verification
- Privacy-preserving scam-number reports and moderation

## Quick start with Docker

1. Copy `.env.example` to `.env`.
2. Generate `PHONE_ENCRYPTION_KEY` using the command shown in `.env.example`.
3. Replace all placeholder secrets.
4. Run:

```powershell
docker compose up --build
```

API health: <http://localhost:8000/api/v1/health/>

Swagger UI: <http://localhost:8000/api/docs/>

Frontend: <http://localhost:3000/>

## Local development without Docker

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements\development.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py runserver
```

For local development, change `DATABASE_URL` to
`sqlite:///db.sqlite3` and `REDIS_URL` to `locmem://`.

## Authentication flow

1. `POST /api/v1/auth/request-otp/`
2. `POST /api/v1/auth/verify-otp/`
3. Use the returned access token as `Authorization: Bearer <token>`.
4. Refresh it through `POST /api/v1/auth/token/refresh/`.

When `OTP_ECHO_IN_RESPONSE=True`, the request endpoint returns a
`development_otp` field. This exists only for local development.

## Seed the initial quiz

```powershell
python manage.py seed_quiz
```

Quiz flow:

1. `POST /api/v1/quiz/sessions/`
2. `POST /api/v1/quiz/sessions/{session_id}/submit/`
3. `GET /api/v1/certificates/{certificate_id}/`
4. `GET /api/v1/certificates/{certificate_id}/pdf/`

Scammer database flow:

1. `GET /api/v1/scammer-db/check/?phone=+998XXXXXXXXX`
2. `POST /api/v1/scammer-db/reports/`
3. `GET /api/v1/scammer-db/reports/my/`
4. Moderator: `GET /api/v1/scammer-db/moderation/reports/?status=pending`
5. Moderator: `PATCH /api/v1/scammer-db/moderation/reports/{report_id}/`
6. Moderator verification:
   `PATCH /api/v1/scammer-db/moderation/numbers/{number_id}/verification/`

Assign moderator access to an existing registered user:

```powershell
python manage.py set_user_role --phone +998XXXXXXXXX --role moderator
```

The moderator interface is available at:

<http://localhost:3000/moderation>

`not_found` means that no approved reports exist. It never means that a
number has been proven safe.

Analyzer:

1. `POST /api/v1/analyzer/url/` with `{ "url": "..." }`
2. `POST /api/v1/analyzer/sms/` with `{ "text": "..." }`

The analyzer never opens submitted URLs and stores only a keyed SHA-256 hash,
the verdict and triggered signals.

Courses:

```powershell
python manage.py seed_courses
```

1. `GET /api/v1/courses/`
2. `GET /api/v1/courses/{course_id}/`
3. `GET /api/v1/courses/lessons/{lesson_id}/`
4. `POST /api/v1/courses/lessons/{lesson_id}/answer/`

Fraud simulator:

```powershell
python manage.py seed_game
```

1. `GET /api/v1/game/scenarios/`
2. `POST /api/v1/game/sessions/`
3. `POST /api/v1/game/sessions/{session_id}/answer/`
4. `GET /api/v1/game/sessions/{session_id}/result/`

Optional OpenRouter enhancement:

```env
OPENROUTER_API_KEY=your-key
OPENROUTER_MODEL=openrouter/free
OPENROUTER_TIMEOUT_SECONDS=12
```

AI rewrites the next scammer message and creates a final coaching summary.
Scoring and scenario progression remain local and deterministic.

## Frontend development

```powershell
cd frontend
npm install
npm run dev
```
