# FastAPI Backend - AI Agentic Fintech

## Setup

### 1. Install Dependencies
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your AWS credentials
```

### 3. Run Server
```bash
uvicorn main:app --reload
```

### 4. Access API
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- POST `/api/auth/register` - Register new user
- POST `/api/auth/login` - Login user

### Jobs
- POST `/api/jobs/upload` - Upload file & start processing
- GET `/api/jobs/list` - List user's jobs
- GET `/api/jobs/{job_id}` - Get job details

### Dashboard
- GET `/api/dashboard/metrics` - Get metrics
- GET `/api/dashboard/recent-jobs` - Get recent jobs

### Health
- GET `/health` - Basic health check
- GET `/health/detailed` - Detailed health check