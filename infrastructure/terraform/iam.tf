resource "aws_iam_role" "invoice_processor" {
  name = "${var.project_name}-${var.environment}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-role"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_iam_role_policy" "bedrock_access" {
  name = "${var.project_name}-bedrock-access"
  role = aws_iam_role.invoice_processor.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = [
          var.bedrock_inference_profile_arn,
          "arn:aws:bedrock:*::foundation-model/amazon.nova-micro-v1:0"
        ]
      }
    ]
  })
}

resource "aws_iam_instance_profile" "invoice_processor" {
  name = "${var.project_name}-${var.environment}-profile"
  role = aws_iam_role.invoice_processor.name
}
