# React Frontend - AI Agentic Fintech

## Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your backend URL
```

### 3. Run Development Server
```bash
npm start
```

### 4. Build for Production
```bash
npm run build
# Output will be in build/
```

## Features

- ✅ User registration & login
- ✅ JWT authentication
- ✅ Dashboard with metrics
- ✅ File upload with drag & drop
- ✅ Job status tracking
- ✅ Responsive design

## Pages

- `/login` - User login
- `/register` - User registration
- `/dashboard` - Main dashboard
- `/upload` - File upload

## Deployment

### Deploy to EC2

1. Build the app:
```bash
npm run build
```

2. Copy to EC2:
```bash
scp -r build/* ubuntu@EC2_IP:/opt/fintech-app/frontend/build/
```

3. Nginx will serve the static files