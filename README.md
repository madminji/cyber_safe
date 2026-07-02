# CyberSafe Uzbekistan

Full-stack prototype for the CyberSafe Uzbekistan digital-safety platform.

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

Open the project folder in VS Code:

```text
C:\Users\madis\Documents\cyber
```

Backend terminal:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements\development.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py seed_courses
python manage.py seed_quiz
python manage.py seed_game
python manage.py seed_webgame
python manage.py runserver
```

If `Copy-Item` is not available because you are in Git Bash, use one of these:

```bash
cp .env.example .env
```

or create `.env` manually and copy the content from `.env.example`.

Default local `.env.example` values use SQLite and in-memory cache:

```env
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=locmem://
```

Frontend terminal:

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

If `Copy-Item` is not available in Git Bash:

```bash
cp .env.example .env.local
```

Open:

<http://localhost:3000/>

Backend API:

<http://127.0.0.1:8000/api/v1/health/>

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

To import the full 20-lesson CyberSafe course from a prepared Word document
and split it into three published levels:

```powershell
python manage.py import_course_docx _lessons_source.docx
```

The importer creates/updates:

- `cybersafe-basic` — 8 beginner lessons
- `cybersafe-advanced` — 8 intermediate lessons
- `cybersafe-expert` — 4 expert lessons

It also hides the old single `digital-safety-basics` course from the public
catalog, adds module titles, long lesson content, supplemental safety notes and
one mini-test question per lesson.

Admin course management:

```powershell
python manage.py createsuperuser
python manage.py runserver
```

Open:

<http://127.0.0.1:8000/admin/>

In the admin panel you can manage courses, lessons, lesson questions and answer
choices. On the course list page use `Импортировать DOCX` to upload a prepared
Word document and update the three course levels from the browser.

Unified lesson import:

The scalable lesson format is JSON. It is strict enough for backend validation
and still lets lesson authors write long Markdown-style text inside localized
fields. Example file:

```text
docs/lesson_import_example.json
```

The format supports:

- `course_slug` or `course_id`
- `lesson_slug`, `module.slug`, localized module title
- localized lesson title, summary and main content
- ordered blocks: `theory`, `definition`, `example`, `warning`, `note`, `code`,
  `checklist`, `task`, `quiz`, `materials`
- practical tasks
- one or more quiz questions with choices, correct answer and explanation
- additional materials and display order

Admin-only API endpoint:

```text
POST /api/v1/courses/admin/lessons/import/
```

JSON body example:

```json
{
  "payload": {
    "course_slug": "cybersafe-basic",
    "lesson_slug": "safe-clicking",
    "order": 1,
    "title": {"ru": "Безопасный клик", "uz": "Xavfsiz bosish"},
    "summary": {"ru": "Как проверять ссылки.", "uz": "Havolalarni tekshirish."},
    "content": {"ru": "Теория урока.", "uz": "Dars nazariyasi."},
    "quiz": [
      {
        "text": {"ru": "Что делать?", "uz": "Nima qilish kerak?"},
        "choices": [
          {"text": {"ru": "Открыть ссылку", "uz": "Havolani ochish"}, "is_correct": false},
          {"text": {"ru": "Проверить сервис вручную", "uz": "Qo‘lda tekshirish"}, "is_correct": true}
        ],
        "explanation": {"ru": "Так безопаснее.", "uz": "Bu xavfsizroq."}
      }
    ]
  }
}
```

Multipart upload is also supported with the file field named `file`.
Re-uploading the same `course_slug + lesson_slug` updates the lesson and
replaces its blocks, tasks and quiz questions without duplicates.

To convert existing database lessons into this JSON format:

```powershell
python manage.py export_lessons_json docs\lesson_imports
```

To load one JSON file or a whole directory back into the database:

```powershell
python manage.py import_lessons_json docs\lesson_imports
```

To split exported long lesson text into structured blocks and practical tasks
before importing:

```powershell
python manage.py enrich_lessons_json docs\lesson_imports
python manage.py import_lessons_json docs\lesson_imports
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

3D web game:

```powershell
python manage.py seed_webgame
```

1. `GET /api/v1/webgame/characters/`
2. `GET /api/v1/webgame/scenarios/`
3. `POST /api/v1/webgame/sessions/`
4. `POST /api/v1/webgame/sessions/{session_id}/actions/`
5. `POST /api/v1/webgame/sessions/{session_id}/complete/`
6. `GET /api/v1/webgame/leaderboard/`

Frontend pages:

- `/games` — 3D game module
- `/games/leaderboard` — game leaderboard

## Frontend development

```powershell
cd frontend
npm install
npm run dev
```

Important frontend pages:

- `/courses` — course catalog
- `/courses/{id}/lessons/{lessonId}` — lesson page with sidebar and optional video
- `/daily-quiz` — daily quiz
- `/analyzer` — SMS/URL/phone check
- `/numbers/report` — citizen scam-number report
- `/simulator` — AI-enhanced scam simulation
- `/moderation` — moderator panel

For moderator access:

```powershell
python manage.py set_user_role --phone +998XXXXXXXXX --role moderator
```
