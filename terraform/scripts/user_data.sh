#!/bin/bash
# ===================================
# EC2 USER DATA SCRIPT
# Automatically configure web server
# ===================================

set -e

LOG_FILE="/var/log/user-data.log"
exec > >(tee -a $LOG_FILE) 2>&1

echo "========================================="
echo "Starting EC2 Bootstrap"
echo "Time: $(date)"
echo "========================================="

# ===================================
# SYSTEM UPDATE
# ===================================
echo "📦 Updating system packages..."
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

# ===================================
# INSTALL DEPENDENCIES
# ===================================
echo "📦 Installing dependencies..."
apt-get install -y \
    python3.10 \
    python3-pip \
    python3-venv \
    git \
    nginx \
    supervisor \
    curl \
    wget \
    unzip \
    awscli

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# ===================================
# CREATE APPLICATION USER
# ===================================
echo "👤 Creating application user..."
useradd -m -s /bin/bash appuser || true
mkdir -p /opt/fintech-app
chown -R appuser:appuser /opt/fintech-app

# ===================================
# SETUP PYTHON ENVIRONMENT
# ===================================
echo "🐍 Setting up Python environment..."
cd /opt/fintech-app
sudo -u appuser python3 -m venv venv
sudo -u appuser /opt/fintech-app/venv/bin/pip install --upgrade pip

# Install FastAPI dependencies
sudo -u appuser /opt/fintech-app/venv/bin/pip install \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    pydantic==2.5.0 \
    python-multipart==0.0.6 \
    python-jose[cryptography]==3.3.0 \
    passlib[bcrypt]==1.7.4 \
    boto3==1.34.0

# ===================================
# CONFIGURE NGINX
# ===================================
echo "🌐 Configuring Nginx..."
cat > /etc/nginx/sites-available/fintech-app << 'EOF'
server {
    listen 80;
    server_name _;

    # Frontend
    location / {
        root /opt/fintech-app/frontend/build;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API Docs
    location /docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}
EOF

ln -sf /etc/nginx/sites-available/fintech-app /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
systemctl enable nginx

# ===================================
# CONFIGURE SUPERVISOR
# ===================================
echo "⚙️  Configuring Supervisor..."
cat > /etc/supervisor/conf.d/fastapi.conf << 'EOF'
[program:fastapi]
command=/opt/fintech-app/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
directory=/opt/fintech-app/backend
user=appuser
autostart=true
autorestart=true
stderr_logfile=/var/log/fastapi.err.log
stdout_logfile=/var/log/fastapi.out.log
environment=HOME="/home/appuser",USER="appuser"
EOF

systemctl restart supervisor
systemctl enable supervisor

# ===================================
# CREATE ENV FILE
# ===================================
echo "📝 Creating environment file..."
cat > /opt/fintech-app/.env << 'EOF'
# AWS Configuration
AWS_REGION=ap-southeast-1
PROJECT_NAME=apiflow-fintech
ENVIRONMENT=dev

# These will be auto-populated by Terraform
DYNAMODB_USERS_TABLE=apiflow-fintech-users-dev
DYNAMODB_JOBS_TABLE=apiflow-fintech-jobs-dev
S3_BUCKET_UPLOADS=apiflow-fintech-uploaded-files-dev
EOF

chown appuser:appuser /opt/fintech-app/.env

# ===================================
# CREATE DEPLOYMENT SCRIPT
# ===================================
cat > /opt/fintech-app/deploy.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Deploying application..."

# Activate virtual environment
source /opt/fintech-app/venv/bin/activate

# Install/update Python dependencies
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi

# Restart services
sudo supervisorctl restart fastapi
sudo systemctl restart nginx

echo "✅ Deployment complete!"
EOF

chmod +x /opt/fintech-app/deploy.sh
chown appuser:appuser /opt/fintech-app/deploy.sh

# ===================================
# CREATE PLACEHOLDER APP
# ===================================
mkdir -p /opt/fintech-app/backend
cat > /opt/fintech-app/backend/main.py << 'EOF'
from fastapi import FastAPI

app = FastAPI(title="AI Agentic Fintech API")

@app.get("/")
async def root():
    return {
        "message": "AI Agentic Fintech API",
        "status": "operational",
        "note": "Upload your backend code to /opt/fintech-app/backend/"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
EOF

chown -R appuser:appuser /opt/fintech-app/backend

# ===================================
# INSTALL CLOUDWATCH AGENT
# ===================================
echo "📊 Installing CloudWatch Agent..."
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i amazon-cloudwatch-agent.deb
rm amazon-cloudwatch-agent.deb

# ===================================
# CONFIGURE FIREWALL
# ===================================
echo "🔥 Configuring firewall..."
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

# ===================================
# CREATE MOTD
# ===================================
cat > /etc/motd << 'EOF'

╔═══════════════════════════════════════════════════╗
║   AI AGENTIC FINTECH - WEB SERVER                ║
╚═══════════════════════════════════════════════════╝

📂 App Directory: /opt/fintech-app
📝 Logs: /var/log/fastapi.*.log
🔧 Deploy: /opt/fintech-app/deploy.sh

Quick Commands:
  - sudo supervisorctl status       # Check FastAPI status
  - sudo supervisorctl restart fastapi  # Restart FastAPI
  - sudo systemctl status nginx     # Check Nginx status
  - tail -f /var/log/fastapi.out.log   # View logs

EOF

echo "========================================="
echo "✅ Bootstrap Complete!"
echo "Time: $(date)"
echo "========================================="