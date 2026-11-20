# IP Calculator (MVP)

FastAPI backend (Python `ipaddress`) + Next.js frontend (App Router, TypeScript) + SQLite history.

## Run (Docker, Ubuntu 22.04)
    docker compose up -d --build
- App:     http://SERVER_IP:3000
- Swagger: http://SERVER_IP:8000/docs

## Tests
    docker compose run --rm backend pytest -q

## Dev without Docker
    cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
    uvicorn app.main:app --reload            # :8000
    cd frontend && npm install && npm run dev  # :3000 (proxies /api to :8000)

## Input formats
`172.16.2.12/24`, `172.16.0.0 255.128.0.0` (IPv6: `2001:db8::1/64`)
