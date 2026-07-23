#  AI Code Copilot

An AI-powered code review platform that analyzes source code using Large Language Models and returns structured, production-ready feedback.

Built with **FastAPI**, **OpenRouter**, **Docker**, **GitHub Actions**, and **Pydantic**.

---

## Features

- AI-powered code review
- File upload support
- Structured JSON responses
- Prompt engineering
- Request validation
- Global exception handling
- Logging & middleware
- Dockerized deployment
- GitHub Actions CI
- Unit testing
- Code formatting with Black
- Static analysis using Ruff

---


## Tech Stack

| Category | Technology |
|-----------|------------|
| Backend | FastAPI |
| AI Model | OpenRouter |
| Validation | Pydantic |
| Testing | Pytest |
| Containerization | Docker |
| CI/CD | GitHub Actions |
| Formatting | Black |
| Linting | Ruff |

---


## Architecture

```text
                Client
                   │
                   ▼
             FastAPI Routes
                   │
                   ▼
           Review Service
                   │
                   ▼
          Prompt Generator
                   │
                   ▼
           OpenRouter Client
                   │
                   ▼
               LLM Model
                   │
                   ▼
       Structured JSON Review
```


## Project Structure

```text
app/
├── handlers/
├── llm/
├── middleware/
├── prompts/
├── routes/
├── schemas/
├── services/
├── utils/
├── config.py
└── main.py

tests/

Dockerfile
docker-compose.yml
requirements.txt
```

## Local Setup

Clone the repository

```bash
git clone <repo-url>
cd AI_Code_Copilot
```

Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create `.env`

```text
OPENAI_API_KEY=your_key_here
```

Run locally

```bash
uvicorn app.main:app --reload
```

## Docker

Build

```bash
docker compose build
```

Run

```bash
docker compose up
```

## Testing

Run tests

```bash
pytest
```

Run coverage

```bash
pytest --cov=app
```


## Continuous Integration

Every push automatically runs:

- Black
- Ruff
- Pytest
- Coverage


## Future Improvements

- GitHub Pull Request review
- Repository review
- Multi-file analysis
- Security review mode
- Performance review mode
- PostgreSQL persistence
- Authentication
- React frontend


## License

MIT License