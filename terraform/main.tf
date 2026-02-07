# ===================================
# AI AGENTIC FINTECH - TERRAFORM
# Main Infrastructure Configuration
# ===================================

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ===================================
# DATA SOURCES
# ===================================

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

# ===================================
# S3 BUCKETS
# ===================================

resource "aws_s3_bucket" "uploaded_files" {
  bucket = "${var.project_name}-uploaded-files-${var.environment}"
  
  tags = {
    Name        = "Uploaded Invoice Files"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_s3_bucket_versioning" "uploaded_files" {
  bucket = aws_s3_bucket.uploaded_files.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "uploaded_files" {
  bucket = aws_s3_bucket.uploaded_files.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket" "sanitized_data" {
  bucket = "${var.project_name}-sanitized-data-${var.environment}"
  
  tags = {
    Name        = "Sanitized Transaction Data"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_s3_bucket_versioning" "sanitized_data" {
  bucket = aws_s3_bucket.sanitized_data.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "sanitized_data" {
  bucket = aws_s3_bucket.sanitized_data.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket" "reports" {
  bucket = "${var.project_name}-reports-${var.environment}"
  
  tags = {
    Name        = "Final Reports"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_s3_bucket_versioning" "reports" {
  bucket = aws_s3_bucket.reports.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "reports" {
  bucket = aws_s3_bucket.reports.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "reports" {
  bucket = aws_s3_bucket.reports.id
  
  rule {
    id     = "delete-old-reports"
    status = "Enabled"
    
    expiration {
      days = 90
    }
  }
}

# ===================================
# DYNAMODB TABLES
# ===================================

resource "aws_dynamodb_table" "users" {
  name           = "${var.project_name}-users-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "email"
  
  attribute {
    name = "email"
    type = "S"
  }
  
  attribute {
    name = "user_id"
    type = "S"
  }
  
  global_secondary_index {
    name            = "UserIdIndex"
    hash_key        = "user_id"
    projection_type = "ALL"
  }
  
  point_in_time_recovery {
    enabled = var.enable_dynamodb_backup
  }
  
  tags = {
    Name        = "Users Table"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_dynamodb_table" "jobs" {
  name           = "${var.project_name}-jobs-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "job_id"
  range_key      = "user_email"
  
  attribute {
    name = "job_id"
    type = "S"
  }
  
  attribute {
    name = "user_email"
    type = "S"
  }
  
  attribute {
    name = "created_at"
    type = "S"
  }
  
  global_secondary_index {
    name            = "UserEmailIndex"
    hash_key        = "user_email"
    range_key       = "created_at"
    projection_type = "ALL"
  }
  
  point_in_time_recovery {
    enabled = var.enable_dynamodb_backup
  }
  
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"
  
  tags = {
    Name        = "Jobs Table"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_dynamodb_table" "audit_logs" {
  name           = "${var.project_name}-audit-logs-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "flow_id"
  range_key      = "timestamp"
  
  attribute {
    name = "flow_id"
    type = "S"
  }
  
  attribute {
    name = "timestamp"
    type = "S"
  }
  
  point_in_time_recovery {
    enabled = true
  }
  
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"
  
  tags = {
    Name        = "Audit Logs Table"
    Environment = var.environment
    Project     = var.project_name
  }
}

# ===================================
# KMS KEY
# ===================================

resource "aws_kms_key" "main" {
  description             = "KMS key for ${var.project_name}"
  deletion_window_in_days = 10
  enable_key_rotation     = true
  
  tags = {
    Name        = "${var.project_name}-key"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_kms_alias" "main" {
  name          = "alias/${var.project_name}-${var.environment}"
  target_key_id = aws_kms_key.main.key_id
}

# ===================================
# SECRETS MANAGER
# ===================================

resource "aws_secretsmanager_secret" "slack_webhook" {
  name        = "${var.project_name}/slack-webhook-${var.environment}"
  description = "Slack webhook URL for notifications"
  
  tags = {
    Name        = "Slack Webhook"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_secretsmanager_secret" "gemini_api_key" {
  name        = "${var.project_name}/gemini-api-key-${var.environment}"
  description = "Google Gemini API key"
  
  tags = {
    Name        = "Gemini API Key"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_secretsmanager_secret" "jwt_secret" {
  name        = "${var.project_name}/jwt-secret-${var.environment}"
  description = "JWT secret for authentication"
  
  tags = {
    Name        = "JWT Secret"
    Environment = var.environment
    Project     = var.project_name
  }
}

# ===================================
# IAM ROLES
# ===================================

# Lambda Execution Role
resource "aws_iam_role" "lambda_execution" {
  name = "${var.project_name}-lambda-role-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  
  tags = {
    Name        = "Lambda Execution Role"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_name}-lambda-policy-${var.environment}"
  role = aws_iam_role.lambda_execution.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          "${aws_s3_bucket.uploaded_files.arn}",
          "${aws_s3_bucket.uploaded_files.arn}/*",
          "${aws_s3_bucket.sanitized_data.arn}",
          "${aws_s3_bucket.sanitized_data.arn}/*",
          "${aws_s3_bucket.reports.arn}",
          "${aws_s3_bucket.reports.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          "${aws_dynamodb_table.users.arn}",
          "${aws_dynamodb_table.users.arn}/index/*",
          "${aws_dynamodb_table.jobs.arn}",
          "${aws_dynamodb_table.jobs.arn}/index/*",
          "${aws_dynamodb_table.audit_logs.arn}",
          "${aws_dynamodb_table.audit_logs.arn}/index/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:Encrypt",
          "kms:Sign",
          "kms:Verify"
        ]
        Resource = "${aws_kms_key.main.arn}"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "${aws_secretsmanager_secret.slack_webhook.arn}",
          "${aws_secretsmanager_secret.gemini_api_key.arn}",
          "${aws_secretsmanager_secret.jwt_secret.arn}"
        ]
      }
    ]
  })
}

# EC2 Instance Role
resource "aws_iam_role" "ec2_role" {
  name = "${var.project_name}-ec2-role-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
  
  tags = {
    Name        = "EC2 Instance Role"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_iam_role_policy" "ec2_policy" {
  name = "${var.project_name}-ec2-policy-${var.environment}"
  role = aws_iam_role.ec2_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          "${aws_s3_bucket.uploaded_files.arn}",
          "${aws_s3_bucket.uploaded_files.arn}/*",
          "${aws_s3_bucket.sanitized_data.arn}",
          "${aws_s3_bucket.sanitized_data.arn}/*",
          "${aws_s3_bucket.reports.arn}",
          "${aws_s3_bucket.reports.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          "${aws_dynamodb_table.users.arn}",
          "${aws_dynamodb_table.users.arn}/index/*",
          "${aws_dynamodb_table.jobs.arn}",
          "${aws_dynamodb_table.jobs.arn}/index/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "states:StartExecution",
          "states:DescribeExecution"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "${aws_secretsmanager_secret.slack_webhook.arn}",
          "${aws_secretsmanager_secret.gemini_api_key.arn}",
          "${aws_secretsmanager_secret.jwt_secret.arn}"
        ]
      }
    ]
  })
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${var.project_name}-ec2-profile-${var.environment}"
  role = aws_iam_role.ec2_role.name
}

# Step Functions Role
resource "aws_iam_role" "stepfunctions_role" {
  name = "${var.project_name}-stepfunctions-role-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "states.amazonaws.com"
        }
      }
    ]
  })
  
  tags = {
    Name        = "Step Functions Role"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_iam_role_policy" "stepfunctions_policy" {
  name = "${var.project_name}-stepfunctions-policy-${var.environment}"
  role = aws_iam_role.stepfunctions_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = "arn:aws:lambda:${var.aws_region}:${data.aws_caller_identity.current.account_id}:function:${var.project_name}-*"
      }
    ]
  })
}

# ===================================
# SECURITY GROUP
# ===================================

resource "aws_security_group" "web_server" {
  name        = "${var.project_name}-web-sg-${var.environment}"
  description = "Security group for web server"
  vpc_id      = var.vpc_id
  
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ssh_cidr
  }
  
  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name        = "${var.project_name}-web-sg"
    Environment = var.environment
    Project     = var.project_name
  }
}

# ===================================
# EC2 INSTANCE
# ===================================

resource "aws_instance" "web_server" {
  ami                    = var.ec2_ami
  instance_type          = var.ec2_instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [aws_security_group.web_server.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name
  key_name               = var.ssh_key_name
  
  user_data = file("${path.module}/scripts/user_data.sh")
  
  root_block_device {
    volume_size           = 30
    volume_type           = "gp3"
    encrypted             = true
    delete_on_termination = true
  }
  
  tags = {
    Name        = "${var.project_name}-web-server"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_eip" "web_server" {
  domain   = "vpc"
  instance = aws_instance.web_server.id
  
  tags = {
    Name        = "${var.project_name}-eip"
    Environment = var.environment
    Project     = var.project_name
  }
}

# ===================================
# CLOUDWATCH LOG GROUPS
# ===================================

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.project_name}"
  retention_in_days = 30
  
  tags = {
    Name        = "Lambda Logs"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_cloudwatch_log_group" "stepfunctions_logs" {
  name              = "/aws/states/${var.project_name}"
  retention_in_days = 30
  
  tags = {
    Name        = "Step Functions Logs"
    Environment = var.environment
    Project     = var.project_name
  }
}

# ===================================
# SNS TOPIC
# ===================================

resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-alerts-${var.environment}"
  
  tags = {
    Name        = "Alert Notifications"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_sns_topic_subscription" "email_alerts" {
  count     = var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# ===================================
# API GATEWAY (Optional)
# ===================================

resource "aws_apigatewayv2_api" "http_api" {
  name          = "${var.project_name}-api-${var.environment}"
  protocol_type = "HTTP"
  
  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["*"]
    max_age       = 300
  }
  
  tags = {
    Name        = "HTTP API Gateway"
    Environment = var.environment
    Project     = var.project_name
  }
}