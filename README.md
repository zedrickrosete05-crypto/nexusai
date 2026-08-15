NexusAI
========

Production-grade AI research & coding assistant — full-stack app combining a Python FastAPI backend (LLM integrations, vector DB, document ingestion) with a React/Next frontend for auth, chat, and document management.

Key features
------------
- Conversational assistant and code research tool backed by OpenAI + LangChain
- Vector store support (ChromaDB, sentence-transformers)
- Document ingestion: PDFs, Word, PowerPoint
- Async Postgres (asyncpg + SQLAlchemy), Redis for caching/sessions
- Frontend: Next.js (custom variant), React 19, Zustand state, TailwindCSS

Architecture
------------
- backend/: FastAPI application (app.main) using async SQLAlchemy, Alembic migrations, ChromaDB and LangChain.
- frontend/: Next.js app providing auth pages and a dashboard (src/app with auth, chat, documents routes).

Requirements
------------
- Python >= 3.12
- Node.js (recommended matching frontend package.json engines)
- Postgres, Redis
- OpenAI API key (or other LLM credentials)

Quickstart (development)
------------------------
1. Copy environment file and set secrets
   - Copy at repo root: .env.example -> .env and fill values (OPENAI_API_KEY, DATABASE_URL, REDIS_URL, SECRET_KEY, etc.)

2. Backend (recommended: Poetry)
   - cd backend
   - poetry install
   - poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

   Alternative using venv/pip:
   - python -m venv .venv
   - .\.venv\Scripts\activate
   - pip install -r requirements.txt  # if provided
   - python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

3. Frontend
   - cd frontend
   - npm install
   - npm run dev
   - Open http://localhost:3000

Testing & linting
-----------------
- Backend tests: cd backend && pytest
- Frontend lint: cd frontend && npm run lint

Developer notes
---------------
- The backend entrypoint is app.main: app = FastAPI(...) (see backend/app/main.py).
- There is a nonstandard Next.js variant in this repo. Before making frontend changes, read frontend/AGENTS.md and the Next.js docs shipped in node_modules/next/dist/docs/ — APIs and conventions may differ from common Next.js versions.
- Keep heavy ML/model dependencies inside the backend virtual environment to avoid polluting the frontend environment.

Contributing
------------
- Open issues and pull requests. Follow existing code style and tests. Add tests for new backend behavior (pytest) where applicable.

License
-------
- Add project license here (e.g., MIT) or update this section as appropriate.

Contact
-------
- Repo: zedrickrosete05-crypto/nexusai

Notes
-----
- If you change dependency manifests, run targeted installs or CI tasks to validate. See backend/pyproject.toml and frontend/package.json for primary dependencies and versions.
- For production deployment, ensure secure storage of keys and proper Postgres/Redis configuration, and run behind a production ASGI server (uvicorn/gunicorn + process manager).
