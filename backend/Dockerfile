# =====================================================
# AgentFlow Backend - Lambda Container Image
# Base: AWS Lambda Python 3.11
# =====================================================

FROM public.ecr.aws/lambda/python:3.11

# Install system dependencies
RUN yum install -y gcc postgresql-devel && yum clean all

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy and install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Lambda handler entry point
CMD ["lambda_handler.handler"]
