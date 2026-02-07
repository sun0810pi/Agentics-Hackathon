# ===================================
# VARIABLES
# ===================================

variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "ap-southeast-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "apiflow-fintech"
}

variable "environment" {
  description = "Environment (dev/staging/prod)"
  type        = string
  default     = "dev"
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID for EC2 instance"
  type        = string
}

variable "ec2_ami" {
  description = "EC2 AMI ID (Ubuntu 22.04)"
  type        = string
}

variable "ec2_instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "ssh_key_name" {
  description = "SSH key pair name"
  type        = string
}

variable "allowed_ssh_cidr" {
  description = "CIDR blocks allowed to SSH"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "alert_email" {
  description = "Email for alerts"
  type        = string
  default     = ""
}

variable "enable_dynamodb_backup" {
  description = "Enable DynamoDB point-in-time recovery"
  type        = bool
  default     = true
}

variable "lambda_memory_size" {
  description = "Lambda memory size (MB)"
  type        = number
  default     = 512
}

variable "lambda_timeout" {
  description = "Lambda timeout (seconds)"
  type        = number
  default     = 300
}