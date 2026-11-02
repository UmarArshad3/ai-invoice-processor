output "instance_id" {
  description = "ID of the proposed EC2 instance"
  value       = aws_instance.invoice_processor.id
}

output "instance_type" {
  description = "Proposed EC2 instance type"
  value       = aws_instance.invoice_processor.instance_type
}

output "security_group_id" {
  description = "ID of the proposed application security group"
  value       = aws_security_group.invoice_api.id
}

output "iam_role_arn" {
  description = "ARN of the EC2 application IAM role"
  value       = aws_iam_role.invoice_processor.arn
}
