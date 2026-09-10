# VStore - Game Store API

A high-performance FastAPI-based backend for a modern game store. Features include a full-fledged admin panel, automated media processing, and a comprehensive store engine.

## Quick Start

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/vstore-ex/vstore.git
cd vstore

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

> **Important:** This project requires `ffmpeg` for video processing.
> - **Ubuntu/Debian:** `sudo apt install ffmpeg`
> - **macOS:** `brew install ffmpeg`
> - **Windows:** [Download from ffmpeg.org](https://ffmpeg.org/download.html)

### 2. Configuration
```bash
cp .env.local .env
# Open .env and update settings to match your environment
```

### 3. Database Setup
Initialize the database schema using Alembic:
```bash
./venv/bin/alembic upgrade head
```

### 4. Seeding Demo Data
To populate the store with games, categories, and demo users for testing:
```bash
./venv/bin/python scripts/seed_db.py
```

#### Demo Accounts
After seeding, you can use these credentials to test the API:
- **Admin:** `admin@vstore.com` / `adminpassword`
- **User:** `user@vstore.com` / `userpassword`

### 5. Run the Application
```bash
./venv/bin/uvicorn app.main:app --reload
```

---

## Development

### API Documentation
Once the app is running, you can access the interactive documentation:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Testing
Run the test suite to ensure everything is working correctly:
```bash
./venv/bin/python -m pytest
```

## Project Structure
- `app/` - Core application logic
  - `api/` - API endpoints and routes
  - `core/` - Security, config, and database setup
  - `models/` - SQLAlchemy database models
  - `services/` - Business logic layer
- `alembic/` - Database migration scripts
- `scripts/` - Utility scripts (seeding, maintenance)
- `tests/` - Pytest test suites