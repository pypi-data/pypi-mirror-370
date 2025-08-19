# Snipster

A code snippet management application built with FastAPI backend and Reflex frontend.

## Development Setup

### Prerequisites

- Python 3.8+
- [uv](https://docs.astral.sh/uv/) package manager

### Quick Start (Recommended)

For the fastest setup, use the provided Makefile commands:

```bash
# Install dependencies and start backend server
make dev

# In another terminal, start the frontend
make ui
```

This will automatically:
- Install all dependencies
- Initialize the database
- Start the FastAPI backend at http://localhost:8000
- Start the Reflex frontend at http://localhost:3000

### Manual Setup

If you prefer to run commands manually, follow the steps below.

### Backend (FastAPI)

The FastAPI backend provides the REST API for managing code snippets.

1. **Navigate to the project root:**

   ```bash
   cd snipster
   ```

2. **Install dependencies:**

   ```bash
   uv sync
   ```

3. **Initialize the database (REQUIRED):**

   ```bash
   uv run alembic upgrade head
   ```

   **Important**: This step is required before starting the server. It creates the database tables and schema.

4. **Start the FastAPI development server:**

   ```bash
   uv run fastapi dev src/snipster/api.py
   ```

   The API will be available at `http://localhost:8000`

5. **Optional: Run tests:**

   ```bash
   uv run pytest
   ```

### Frontend (Reflex)

The Reflex frontend provides a modern web interface for managing snippets.

1. **Navigate to the frontend directory:**

   ```bash
   cd ui
   ```

2. **Install dependencies:**

   ```bash
   uv sync
   ```

3. **Start the Reflex development server:**

   ```bash
   uv run reflex run
   ```

   The frontend will be available at `http://localhost:3000`

4. **Optional: Build for production:**

   ```bash
   uv run reflex export
   ```

## Database Management

### Alembic Migrations

Alembic handles database schema migrations for the project.

1. **Create a new migration:**

   ```bash
   uv run alembic revision --autogenerate -m "Description of changes"
   ```

2. **Apply pending migrations:**

   ```bash
   uv run alembic upgrade head
   ```

3. **Rollback to previous migration:**

   ```bash
   uv run alembic downgrade -1
   ``****`

4. **View migration history:**

   ```bash
   uv run alembic history
   ```

5. **Check current migration status:**

   ```bash
   uv run alembic current
   ```

**Note**: Always review auto-generated migrations before applying them to production.

## Project Structure

### Backend (`src/snipster/`)

- **`api.py`**: FastAPI application with REST endpoints
- **`models.py`**: Pydantic models for request/response validation
- **`repo.py`**: Data access layer for snippets
- **`db.py`**: Database connection and session management
- **`cli.py`**: Command-line interface for snippet management

### Frontend (`ui/`)

- **`ui/ui.py`**: Main Reflex application with UI components
- **`rxconfig.py`**: Reflex configuration (ports, app name)
- **`pyproject.toml`**: Frontend dependencies and configuration

### Database

- **`alembic/`**: Database schema migrations
- **`snipster.sqlite`**: SQLite database file

### Development Tools

- **`pyproject.toml`**: Project configuration and dependencies
- **`Makefile`**: Common development commands
- **`.pre-commit-config.yaml`**: Code quality hooks
- **`tests/`**: Comprehensive test suite

## API Endpoints

- `GET /health` - Health check

  ```
  GET /health
  Response: {"status": "ok"}
  ```

- `POST /create` - Create new snippet

  ```json
  POST /create
  {
    "title": "Hello World",
    "code": "print('Hello World')",
    "language": "python",
    "tags": ["example", "hello"]
  }
  ```

- `GET /snippets` - List all snippets

  ```
  GET /snippets
  Response: [
    {
      "id": 1,
      "title": "Hello World",
      "code": "print('Hello World')",
      "language": "python",
      "tags": ["example", "hello"]
    }
  ]
  ```

- `GET /snippets/{id}` - Get snippet by ID

  ```
  GET /snippets/1
  Response: {
    "id": 1,
    "title": "Hello World",
    "code": "print('Hello World')",
    "language": "python",
    "tags": ["example", "hello"]
  }
  ```

- `DELETE /snippets/{id}` - Delete snippet

  ```
  DELETE /snippets/1
  Response: {"message": "Snippet deleted"}
  ```

- `POST /snippets/{id}/toggle-favorite` - Toggle favorite status

  ```
  POST /snippets/1/toggle-favorite
  Response: {"id": 1, "is_favorite": true}
  ```

- `POST /snippets/{id}/add-tags` - Add tags to snippet

  ```json
  POST /snippets/1/add-tags
  {
    "tags": ["new", "tags"]
  }
  Response: {
    "id": 1,
    "tags": ["example", "hello", "new", "tags"]
  }
  ```

- `GET /search` - Search snippets by query string

  ```
  GET /search?q=hello
  Response: [
    {
      "id": 1,
      "title": "Hello World",
      "code": "print('Hello World')",
      "language": "python",
      "tags": ["example", "hello"]
    }
  ]
  ```

## Development Workflow

1. Start the FastAPI backend first
2. Start the Reflex frontend
3. Make changes to either backend or frontend
4. Both servers support hot reloading for development
