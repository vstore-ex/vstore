# VStore - Game Store API

FastAPI-based backend for a game store with admin panel, media processing, and statistics.

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/vstore-ex/vstore.git
   cd vstore
   ```

2. **Setup Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

   **Note:** This project requires `ffmpeg` installed on your system for video processing.
   - Ubuntu/Debian: `sudo apt install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Windows: Download from ffmpeg.org


3. **Configuration**
   ```bash
   cp .env.local .env
   # Edit .env with your credentials
   ```

4. **Database Setup**
   ```bash
   # Run migrations
   alembic upgrade head
   ```

5. **Run the App**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation
- Swagger UI: `http://localhost:8000/docs`
- Redoc: `http://localhost:8000/redoc`

## Testing
```bash
python -m pytest
```