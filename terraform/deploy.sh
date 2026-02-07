#!/bin/bash
# ===================================
# TERRAFORM DEPLOYMENT SCRIPT
# ===================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════╗
║   TERRAFORM DEPLOYMENT                            ║
║   AI Agentic Fintech Infrastructure               ║
╚═══════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

# ===================================
# PRE-FLIGHT CHECKS
# ===================================
echo -e "${YELLOW}🔍 Running pre-flight checks...${NC}\n"

if ! command -v terraform &> /dev/null; then
    echo -e "${RED}❌ Terraform not found${NC}"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found${NC}"
    exit 1
fi

if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All checks passed${NC}\n"

# ===================================
# AUTO-DETECT AWS RESOURCES
# ===================================
echo -e "${BLUE}🔍 Auto-detecting AWS resources...${NC}\n"

# Get default VPC
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query 'Vpcs[0].VpcId' --output text 2>/dev/null || echo "")

if [ -z "$VPC_ID" ] || [ "$VPC_ID" == "None" ]; then
    echo -e "${YELLOW}⚠️  No default VPC found. Creating one...${NC}"
    VPC_ID=$(aws ec2 create-default-vpc --query 'Vpc.VpcId' --output text)
    echo -e "${GREEN}✅ Created default VPC: ${VPC_ID}${NC}"
fi

# Get first available subnet
SUBNET_ID=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=${VPC_ID}" --query 'Subnets[0].SubnetId' --output text)

# Get latest Ubuntu 22.04 AMI
EC2_AMI=$(aws ec2 describe-images \
    --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
    --output text)

# Check/Create SSH key
SSH_KEY_NAME="fintech-web-key"
if ! aws ec2 describe-key-pairs --key-names "$SSH_KEY_NAME" &> /dev/null; then
    echo -e "${YELLOW}🔑 Creating SSH key pair...${NC}"
    mkdir -p ~/.ssh
    aws ec2 create-key-pair --key-name "$SSH_KEY_NAME" --query 'KeyMaterial' --output text > ~/.ssh/${SSH_KEY_NAME}.pem
    chmod 400 ~/.ssh/${SSH_KEY_NAME}.pem
    echo -e "${GREEN}✅ SSH key created: ~/.ssh/${SSH_KEY_NAME}.pem${NC}"
fi

echo -e "${GREEN}✅ VPC ID: ${VPC_ID}${NC}"
echo -e "${GREEN}✅ Subnet ID: ${SUBNET_ID}${NC}"
echo -e "${GREEN}✅ AMI ID: ${EC2_AMI}${NC}"
echo -e "${GREEN}✅ SSH Key: ${SSH_KEY_NAME}${NC}\n"

# ===================================
# CREATE TERRAFORM VARIABLES
# ===================================
cat > terraform.tfvars << EOF
aws_region        = "ap-southeast-1"
project_name      = "apiflow-fintech"
environment       = "dev"
vpc_id            = "${VPC_ID}"
subnet_id         = "${SUBNET_ID}"
ec2_ami           = "${EC2_AMI}"
ec2_instance_type = "t3.medium"
ssh_key_name      = "${SSH_KEY_NAME}"
allowed_ssh_cidr  = ["0.0.0.0/0"]
alert_email       = ""
EOF

echo -e "${GREEN}✅ Created terraform.tfvars${NC}\n"

# ===================================
# INTERACTIVE MENU
# ===================================
while true; do
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Select an action:${NC}"
    echo -e "  1) Initialize Terraform"
    echo -e "  2) Plan deployment"
    echo -e "  3) Apply (deploy infrastructure)"
    echo -e "  4) Destroy (remove all resources)"
    echo -e "  5) Show outputs"
    echo -e "  6) Exit"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    read -p "Enter choice [1-6]: " choice

    case $choice in
        1)
            echo -e "\n${BLUE}🔧 Initializing Terraform...${NC}"
            terraform init
            echo -e "${GREEN}✅ Initialization complete${NC}\n"
            ;;
        2)
            echo -e "\n${BLUE}📋 Planning deployment...${NC}"
            terraform plan
            echo -e "${GREEN}✅ Plan complete${NC}\n"
            ;;
        3)
            echo -e "\n${BLUE}🚀 Applying infrastructure...${NC}"
            terraform apply -auto-approve
            
            # Save outputs
            terraform output -json > outputs.json
            echo -e "${GREEN}✅ Deployment complete!${NC}\n"
            
            terraform output deployment_summary
            ;;
        4)
            echo -e "\n${RED}⚠️  WARNING: This will destroy ALL resources!${NC}"
            read -p "Are you sure? (yes/no): " confirm
            if [ "$confirm" == "yes" ]; then
                terraform destroy
                echo -e "${GREEN}✅ Destruction complete${NC}\n"
            else
                echo -e "${YELLOW}Cancelled${NC}\n"
            fi
            ;;
        5)
            echo -e "\n${BLUE}📊 Terraform Outputs:${NC}"
            terraform output
            echo ""
            ;;
        6)
            echo -e "\n${GREEN}Goodbye!${NC}\n"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}\n"
            ;;
    esac
done
```

## File: `terraform/.gitignore`
```
# Terraform
.terraform/
*.tfstate
*.tfstate.*
*.tfvars
!terraform.tfvars.example
.terraform.lock.hcl
override.tf
override.tf.json
*_override.tf
*_override.tf.json

# Crash logs
crash.log
crash.*.log

# Outputs
outputs.json

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Keys
*.pem
*.key