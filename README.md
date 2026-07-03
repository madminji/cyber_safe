# CyberSafe Uzbekistan

CyberSafe Uzbekistan is a full-stack educational web platform for digital safety,
fraud awareness, scam reporting, moderation, certificates, quizzes, courses and
user ranking.

The project has two main parts:

- Backend: Django + Django REST Framework
- Frontend: Next.js + React

Main features:

- OTP login
- Courses and lessons
- JSON lesson import
- Quiz and daily quiz
- PDF certificates with QR verification
- SMS / URL / phone analyzer
- Citizen scam reports
- Moderator panel
- Suspicious number registry
- User management for admins
- User leaderboard
- Scam dialogue simulator

---

## 1. Requirements

Install these tools first:

- Python 3.11 or 3.12
- Node.js LTS
- npm
- Git
- VS Code

Check installation:

```bash
python --version
node --version
npm --version
git --version
```

---

## 2. Clone or open the project

Clone with Git:

```bash
git clone git@github.com:madminji/cyber_safe.git
cd cyber
```

Or open the already downloaded project folder in VS Code.

Backend commands must be executed from the project root, where `manage.py` is
located.

---

## 3. Backend virtual environment

From the project root:

```bash
python -m venv .venv
```

Activate in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Activate in Git Bash:

```bash
source .venv/Scripts/activate
```

If PowerShell blocks script execution:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## 4. Backend dependencies

From the project root:

```bash
pip install -r requirements/development.txt
```

On Windows this also works:

```powershell
pip install -r requirements\development.txt
```

---

## 5. Backend `.env`

Create a file named `.env` in the project root.

You can copy the example:

PowerShell:

```powershell
Copy-Item .env.example .env
```

Git Bash:

```bash
cp .env.example .env
```

If copy commands do not work, create `.env` manually in VS Code.

Minimal local `.env`:

```env
DJANGO_SETTINGS_MODULE=config.settings.development
SECRET_KEY=dev-secret-key-change-me
DEBUG=True

DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=locmem://

PHONE_LOOKUP_SECRET=dev-phone-lookup-secret-change-me
PHONE_ENCRYPTION_KEY=PASTE_GENERATED_FERNET_KEY_HERE

PUBLIC_SITE_URL=http://127.0.0.1:3000

OTP_ECHO_IN_RESPONSE=True

OPENROUTER_API_KEY=
OPENROUTER_MODEL=deepseek/deepseek-chat-v3-0324:free
OPENROUTER_TIMEOUT_SECONDS=12
```

Generate `PHONE_ENCRYPTION_KEY`:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Paste the generated value into `.env`:

```env
PHONE_ENCRYPTION_KEY=generated_key_here
```

Without `PHONE_ENCRYPTION_KEY`, phone encryption and scam reports can fail.

---

## 6. Backend migrations

From the project root:

```bash
python manage.py migrate
```

---

## 7. Seed initial data

After migrations, the database is empty. Seed commands add demo/start data.

Recommended minimum:

```bash
python manage.py seed_quiz
python manage.py seed_realistic_simulations
python manage.py sync_course_metadata
```

What these commands do:

- `seed_quiz` adds quiz and daily quiz questions.
- `seed_realistic_simulations` adds realistic scam dialogue simulations.
- `sync_course_metadata` updates course titles and descriptions.

Optional old simulator data:

```bash
python manage.py seed_game
```

Optional 3D web game data:

```bash
python manage.py seed_webgame
```

The 3D game is currently postponed, so `seed_webgame` can be skipped.

---

## 8. Run backend

From the project root:

```bash
python manage.py runserver
```

Backend:

```text
http://127.0.0.1:8000/
```

Health check:

```text
http://127.0.0.1:8000/api/v1/health/
```

Swagger/OpenAPI:

```text
http://127.0.0.1:8000/api/docs/
```

Keep this terminal open.

---

## 9. Frontend dependencies

Open a second VS Code terminal.

Go to the frontend folder:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

---

## 10. Frontend `.env.local`

Create this file:

```text
frontend/.env.local
```

Content:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api/v1
```

Important: `.env.local` must be inside the `frontend` folder, not in the project
root.

---

## 11. Run frontend

From the `frontend` folder:

```bash
npm run dev
```

Open:

```text
http://localhost:3000
```

---

## 12. Daily run commands

Terminal 1, backend:

```bash
cd cyber
.\.venv\Scripts\Activate.ps1
python manage.py runserver
```

Terminal 2, frontend:

```bash
cd cyber/frontend
npm run dev
```

Open:

```text
http://localhost:3000
```

---

## 13. Login

Open:

```text
http://localhost:3000/login
```

Use a phone number in this format:

```text
+998901234567
```

In local development, OTP is returned in the API response because:

```env
OTP_ECHO_IN_RESPONSE=True
```

---

## 14. Make a user admin or moderator

The user must log in at least once before role assignment.

Make admin:

```bash
python manage.py set_user_role --phone +998901234567 --role admin
```

Make moderator:

```bash
python manage.py set_user_role --phone +998901234567 --role moderator
```

After changing the role, log out from the website and log in again.

Moderator/admin panel:

```text
http://localhost:3000/moderation
```

Available there:

- citizen reports
- number registry
- lesson import
- lesson deletion
- user management
- user blocking/unblocking

---

## 15. Courses and JSON lesson import

Courses support:

- levels
- modules
- lessons
- theory blocks
- definitions
- examples
- warnings
- practical tasks
- quizzes
- materials
- video links

Lessons can be imported as JSON from the moderation panel:

```text
http://localhost:3000/moderation
```

Open the `Lessons` tab.

Example JSON:

```text
docs/lesson_import_example.json
```

Backend endpoint:

```text
POST /api/v1/courses/admin/lessons/import/
```

Re-uploading the same `course_slug + lesson_slug` updates the lesson without
duplicates.

---

## 16. Certificates

Certificates are created after a successful quiz.

Certificate page:

```text
http://localhost:3000/certificates
```

Public QR verification:

```text
http://localhost:3000/certificates/verify/<certificate_id>
```

Rules:

- Public QR verification only confirms authenticity.
- PDF download is available only to the certificate owner or admin.

---

## 17. Scam reports

Report form:

```text
http://localhost:3000/numbers/report
```

Users can report:

- phone number
- URL
- account
- card/account number
- other suspicious target

Only approved phone reports affect the public number database.

Moderators see the full phone number in moderation, but public users see only a
masked number.

---

## 18. Analyzer

Analyzer page:

```text
http://localhost:3000/analyzer
```

Features:

- URL check
- SMS/text check
- phone number check

API:

```text
POST /api/v1/analyzer/url/
POST /api/v1/analyzer/sms/
GET  /api/v1/scammer-db/check/?phone=+998XXXXXXXXX
```

---

## 19. Leaderboard

Profile shows:

- points
- rank
- certificates
- course progress
- reports

Leaderboard page:

```text
http://localhost:3000/leaderboard
```

API:

```text
GET /api/v1/auth/leaderboard/
```

The leaderboard does not expose full phone numbers.

---

## 20. OpenRouter / AI

If you have an OpenRouter key, add it to backend `.env`:

```env
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=deepseek/deepseek-chat-v3-0324:free
OPENROUTER_TIMEOUT_SECONDS=12
```

AI is used in the simulator for more natural scammer messages and final
feedback.

If the key is empty, the project still runs.

---

## 21. Before pushing to GitHub

Check:

```bash
git status
```

Do not commit:

- `.env`
- `frontend/.env.local`
- `.venv`
- `db.sqlite3`
- secret API keys
- real personal data

Frontend build:

```bash
cd frontend
npm run build
```

Backend checks:

```bash
python manage.py check
pytest
```

---

## 22. Common errors

### `npm error Missing script: "dev"`

You are probably not inside the `frontend` folder.

Correct:

```bash
cd frontend
npm run dev
```

### `Copy-Item` not found

You are using Git Bash, not PowerShell.

Use:

```bash
cp .env.example .env
```

Or create the file manually in VS Code.

### `cp: command not found`

Create `.env` or `.env.local` manually in VS Code.

### Redis connection error

Check backend `.env`:

```env
REDIS_URL=locmem://
```

### Login returns 500

Check:

- backend is running
- frontend `.env.local` is inside `frontend`
- `NEXT_PUBLIC_API_URL` is correct
- migrations were applied
- `PHONE_ENCRYPTION_KEY` is filled

### Users tab is not visible in moderation

The account must have the `admin` role:

```bash
python manage.py set_user_role --phone +998901234567 --role admin
```

Then log out and log in again.

---

## 23. Useful local links

Frontend:

```text
http://localhost:3000
```

Backend health:

```text
http://127.0.0.1:8000/api/v1/health/
```

Swagger:

```text
http://127.0.0.1:8000/api/docs/
```

Moderation:

```text
http://localhost:3000/moderation
```

Leaderboard:

```text
http://localhost:3000/leaderboard
```

