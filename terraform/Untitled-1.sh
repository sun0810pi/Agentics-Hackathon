# ===================================
# TERRAFORM VARIABLES
# Copy to terraform.tfvars and edit
# ===================================

aws_region  = "ap-southeast-1"
project_name = "apiflow-fintech"
environment  = "dev"

# VPC Configuration
# Get VPC ID: aws ec2 describe-vpcs --query 'Vpcs[?IsDefault==`true`].VpcId' --output text
vpc_id = "vpc-xxxxxxxxx"

# Get Subnet ID: aws ec2 describe-subnets --query 'Subnets[0].SubnetId' --output text
subnet_id = "subnet-xxxxxxxxx"

# EC2 Configuration
# Get Ubuntu 22.04 AMI: aws ec2 describe-images --owners 099720109477 --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' --output text
ec2_ami = "ami-xxxxxxxxx"

ec2_instance_type = "t3.medium"

# SSH Key
# Create key: aws ec2 create-key-pair --key-name fintech-web-key --query 'KeyMaterial' --output text > ~/.ssh/fintech-web-key.pem
ssh_key_name = "fintech-web-key"

# Security
allowed_ssh_cidr = ["0.0.0.0/0"]  # Change to your IP for better security

# Alerts
alert_email = "your-email@example.com"

# Optional Settings
enable_dynamodb_backup = true
lambda_memory_size     = 512
lambda_timeout         = 300