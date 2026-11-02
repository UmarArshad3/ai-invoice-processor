variable "aws_region" {
  description = "AWS deployment region"
  type        = string
  default     = "eu-north-1"
}

variable "project_name" {
  description = "Name of the application"
  type        = string
  default     = "ai-invoice-processor"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "portfolio"
}

variable "instance_type" {
  description = "EC2 instance type for future deployment"
  type        = string
  default     = "t4g.micro"
}

variable "allowed_ssh_cidr" {
  description = "Trusted IPv4 CIDR allowed to access SSH"
  type        = string

  validation {
    condition     = can(cidrnetmask(var.allowed_ssh_cidr))
    error_message = "Provide a valid IPv4 CIDR block."
  }
}

variable "allowed_app_cidr" {
  description = "Trusted IPv4 CIDR allowed to access the API"
  type        = string

  validation {
    condition     = can(cidrnetmask(var.allowed_app_cidr))
    error_message = "Provide a valid IPv4 CIDR block."
  }
}

variable "bedrock_inference_profile_arn" {
  description = "Amazon Bedrock inference profile ARN"
  type        = string
}
