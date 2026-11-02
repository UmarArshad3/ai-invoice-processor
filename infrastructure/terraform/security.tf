data "aws_vpc" "default" {
  default = true
}

resource "aws_security_group" "invoice_api" {
  name        = "${var.project_name}-${var.environment}-sg"
  description = "Security group for the AI Invoice Processor"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH from trusted IP range"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  ingress {
    description = "FastAPI access from trusted IP range"
    from_port   = 8001
    to_port     = 8001
    protocol    = "tcp"
    cidr_blocks = [var.allowed_app_cidr]
  }

  egress {
    description = "Allow outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-sg"
    Environment = var.environment
    Project     = var.project_name
  }
}
