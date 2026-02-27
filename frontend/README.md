AI-Powered Invoice Fraud Detection System - Streamlit Frontend

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.30+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running Locally](#running-locally)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Development](#development)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## 🌟 Overview

AgentFlow Frontend is a production-ready Streamlit application that provides a beautiful, responsive UI for the AgentFlow invoice fraud detection system. It features:

- **17-Agent AI System** for comprehensive fraud detection
- **Real-time Processing** with WebSocket updates
- **Dark & Light Themes** with cyberpunk aesthetics
- **Role-Based Access Control** (Admin, Analyst, Viewer)
- **Demo Mode** for testing without backend
- **AWS Integration** (Cognito, S3, RDS, X-Ray)

---

## ✨ Features

### 🎨 UI/UX
- **Dual Themes:** Dark (cyberpunk neon) & Light (glassmorphism)
- **Responsive Design:** Works on desktop, tablet, mobile
- **Interactive Charts:** Plotly visualizations
- **Real-time Updates:** Live fraud detection alerts
- **Smooth Animations:** CSS transitions and effects

### 🔐 Security
- **AWS Cognito Authentication:** Secure user management
- **JWT Token Management:** Automatic refresh
- **Input Validation:** SQL injection, XSS prevention
- **Rate Limiting:** Client-side protection
- **Audit Logging:** All actions tracked

### 📊 Pages (9 Total)
1. **📊 Overview** - Dashboard with key metrics
2. **📄 Upload** - Invoice upload and processing
3. **🚨 Fraud** - Active fraud scenarios
4. **🧠 ML Insights** - Model performance analytics
5. **🛡️ Security** - Security monitoring + attack demo
6. **📈 Observability** - X-Ray traces & CloudWatch
7. **💼 Merchant** - Merchant insights and trends
8. **🔗 Integrations** - External service connections
9. **⚙️ Settings** - User preferences

### 🤖 17-Agent System
- **Tier 1 (0-7):** Core detection (OCR, PII, AI Analyst, etc.)
- **Tier 2 (8-10):** ML intelligence
- **Tier 3 (11-13):** Merchant success
- **Tier 4 (14-16):** Security & fraud rings

---

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────────┐
│                  Streamlit Cloud                    │
│                (Frontend Hosting)                   │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ HTTPS/TLS
                  │
┌─────────────────▼───────────────────────────────────┐
│              AWS API Gateway                        │
│           (Backend Entry Point)                     │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ REST API
                  │
┌─────────────────▼───────────────────────────────────┐
│          AWS Lambda (FastAPI)                       │
│        17-Agent Processing Pipeline                 │
└──┬──────────────┬──────────────┬────────────────────┘
   │              │              │
   │              │              │
   ▼              ▼              ▼
┌──────┐    ┌─────────┐    ┌─────────┐
│  S3  │    │   RDS   │    │ Cognito │
│Files │    │PostgreSQL    │  Auth   │
└──────┘    └─────────┘    └─────────┘
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.11+** (3.11.0 or higher)
- **pip** (latest version)
- **Git** (for cloning)

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/agentflow.git
cd agentflow/frontend
```

### Step 2: Create Virtual Environment
```bash
# Using venv
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**Core Dependencies:**
- streamlit==1.30.0
- pandas==2.1.4
- plotly==5.18.0
- requests==2.31.0
- boto3==1.34.20
- pydantic==2.5.3

---

## ⚙️ Configuration

### 1. Environment Variables

Create `.env` file:
```bash
# Backend Configuration
BACKEND_URL=https://api.agentflow.ai
BACKEND_TIMEOUT=30

# Demo Mode
DEMO_MODE=false

# AWS Configuration (if using real Cognito)
AWS_REGION=ap-southeast-1
COGNITO_USER_POOL_ID=ap-southeast-1_xxxxxxxxx
COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxx
```

### 2. Streamlit Secrets

Create `.streamlit/secrets.toml`:
```toml
# .streamlit/secrets.toml

[general]
app_name = "AgentFlow Finance Guard"
app_version = "3.1.0"

[backend]
url = "https://api.agentflow.ai"
timeout = 30

[aws]
region = "ap-southeast-1"
cognito_user_pool_id = "ap-southeast-1_xxxxxxxxx"
cognito_client_id = "xxxxxxxxxxxxxxxxxxxxx"

[demo]
enabled = true

# Demo users (only for demo mode)
[[demo.users]]
email = "admin@agentflow.ai"
password = "Admin@2026!"
name = "Admin User"
role = "admin"

[[demo.users]]
email = "analyst@agentflow.ai"
password = "Analyst@2026!"
name = "Analyst User"
role = "analyst"

[[demo.users]]
email = "viewer@agentflow.ai"
password = "Viewer@2026!"
name = "Viewer User"
role = "viewer"
```

### 3. Streamlit Config

`.streamlit/config.toml` is already configured with:
- Dark theme as default
- Wide layout
- Hidden menu items
- Performance optimizations

---

## 🏃 Running Locally

### Option 1: Standard Run
```bash
streamlit run app.py
```

### Option 2: Custom Port
```bash
streamlit run app.py --server.port 8501
```

### Option 3: Demo Mode (No Backend)
```bash
# Set in .env
DEMO_MODE=true

# Or inline
DEMO_MODE=true streamlit run app.py
```

### Option 4: Development Mode
```bash
# Auto-reload on changes
streamlit run app.py --server.runOnSave true
```

**Access the app:**
- Local: http://localhost:8501
- Network: http://YOUR_IP:8501

---

## 🌐 Deployment

### Streamlit Cloud (Recommended)

**1. Push to GitHub:**
```bash
git add .
git commit -m "Deploy AgentFlow Frontend"
git push origin main
```

**2. Deploy on Streamlit Cloud:**

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select repository: `yourusername/agentflow`
4. Main file: `frontend/app.py`
5. Python version: 3.11
6. Add secrets from `.streamlit/secrets.toml`
7. Click "Deploy"

**3. Custom Domain (Optional):**

- Go to app settings
- Add custom domain
- Update DNS records

### Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Build & Run:**
```bash
docker build -t agentflow-frontend .
docker run -p 8501:8501 agentflow-frontend
```

### AWS EC2 Deployment
```bash
# SSH to EC2
ssh -i key.pem ec2-user@your-ec2-ip

# Install dependencies
sudo yum update -y
sudo yum install python3.11 -y

# Clone and setup
git clone https://github.com/yourusername/agentflow.git
cd agentflow/frontend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with PM2
npm install -g pm2
pm2 start "streamlit run app.py" --name agentflow

# Setup nginx reverse proxy (optional)
sudo yum install nginx -y
# Configure nginx to proxy :8501
```

---

## 📁 Project Structure
```
frontend/
├── app.py                    # Main entry point
├── config.py                 # Configuration management
├── requirements.txt          # Dependencies
├── README.md                # This file
├── .gitignore               # Git ignore rules
│
├── .streamlit/
│   ├── config.toml          # Streamlit configuration
│   └── secrets.toml.example # Secrets template
│
├── auth/
│   ├── cognito_client.py    # AWS Cognito client
│   └── login.py             # Login/signup UI
│
├── components/
│   ├── charts.py            # Plotly visualizations
│   ├── metrics.py           # Metric cards
│   ├── widgets.py           # UI widgets
│   ├── attack_demo.py       # Attack simulation
│   └── xray_viewer.py       # X-Ray trace viewer
│
├── pages/                   # Streamlit pages (auto-detected)
│   ├── 1_📊_Overview.py
│   ├── 2_📄_Upload.py
│   ├── 3_🚨_Fraud.py
│   ├── 4_🧠_ML_Insights.py
│   ├── 5_🛡️_Security.py
│   ├── 6_📈_Observability.py
│   ├── 7_💼_Merchant.py
│   ├── 8_🔗_Integrations.py
│   └── 9_⚙️_Settings.py
│
├── themes/
│   ├── dark.py              # Dark cyberpunk theme
│   └── light.py             # Light glassmorphism theme
│
├── services/
│   ├── api_client.py        # Backend API client
│   ├── data_provider.py     # Data switcher (demo/real)
│   ├── demo_data.py         # Demo data generator
│   └── rate_limiter.py      # Rate limiter
│
└── utils/
    ├── constants.py         # Application constants
    ├── helpers.py           # Helper functions
    └── validators.py        # Input validators
```

---

## 👨‍💻 Development

### Adding a New Page

1. Create file in `pages/` folder:
```python
   # pages/10_🎯_MyPage.py
   import streamlit as st
   
   st.markdown("# My New Page")
   st.write("Content here...")
```

2. Streamlit auto-detects it!

### Adding a New Component

1. Create component function:
```python
   # components/my_widget.py
   def my_custom_widget(data):
       st.markdown("...")
```

2. Export in `components/__init__.py`:
```python
   from .my_widget import my_custom_widget
   __all__ = [..., 'my_custom_widget']
```

3. Use in pages:
```python
   from components import my_custom_widget
   my_custom_widget(data)
```

### Code Style
```bash
# Format code
black frontend/

# Lint
flake8 frontend/

# Type check
mypy frontend/
```

---

## 🧪 Testing

### Manual Testing Checklist

**Authentication:**
- [ ] Login with demo credentials
- [ ] Login with real Cognito (if enabled)
- [ ] Logout works correctly
- [ ] Session persists on refresh

**Pages:**
- [ ] All 9 pages load without errors
- [ ] Navigation works smoothly
- [ ] Charts render correctly
- [ ] Data tables display properly

**Themes:**
- [ ] Dark theme applies correctly
- [ ] Light theme applies correctly
- [ ] Theme switch persists

**Upload:**
- [ ] File upload works
- [ ] Processing displays progress
- [ ] Results show correctly
- [ ] Error handling works

**Demo Mode:**
- [ ] Works without backend
- [ ] Demo data generates correctly
- [ ] All features accessible

### Automated Testing (Future)
```bash
# Install test dependencies
pip install pytest pytest-streamlit

# Run tests
pytest tests/
```

---

## 🐛 Troubleshooting

### Issue: Import Errors

**Problem:** `ModuleNotFoundError: No module named 'streamlit'`

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Pages Not Showing

**Problem:** Sidebar navigation is empty

**Solution:**
- Ensure files in `pages/` follow format: `N_emoji_Name.py`
- Check file permissions
- Restart Streamlit

### Issue: Backend Connection Fails

**Problem:** Cannot connect to backend

**Solution:**
1. Check `BACKEND_URL` in config
2. Verify backend is running
3. Check network/firewall
4. Enable demo mode as fallback:
```bash
   DEMO_MODE=true streamlit run app.py
```

### Issue: Cognito Authentication Fails

**Problem:** Login not working

**Solution:**
1. Verify AWS credentials
2. Check Cognito pool ID and client ID
3. Ensure user pool is in correct region
4. Use demo mode for testing:
```python
   # In config.py
   DEMO_MODE = True
```

### Issue: Theme Not Applying

**Problem:** Custom theme not loading

**Solution:**
1. Clear Streamlit cache: `Ctrl+Shift+R`
2. Check `.streamlit/config.toml` exists
3. Restart Streamlit server

### Issue: Slow Performance

**Problem:** App is slow/laggy

**Solution:**
1. Enable caching:
```python
   @st.cache_data
   def expensive_function():
       ...
```

2. Reduce data size
3. Optimize queries
4. Use pagination

---

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Plotly Documentation](https://plotly.com/python/)
- [AWS Cognito Guide](https://docs.aws.amazon.com/cognito/)
- [FastAPI Backend Repo](https://github.com/yourusername/agentflow-backend)

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📝 License

MIT License - see LICENSE file for details

---

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

---

## 🙏 Acknowledgments

- Claude (Anthropic) for AI assistance
- Streamlit team for the amazing framework
- AWS for cloud infrastructure
- Open source community

---

## 📞 Support

- **Email:** support@agentflow.ai
- **Issues:** [GitHub Issues](https://github.com/yourusername/agentflow/issues)
- **Docs:** [Documentation](https://docs.agentflow.ai)

---

**Built with ❤️ using Streamlit and Claude**