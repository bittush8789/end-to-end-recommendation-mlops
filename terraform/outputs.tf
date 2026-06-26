output "eks_cluster_name" {
  description = "Name of the EKS cluster"
  value       = aws_eks_cluster.main.name
}

output "eks_cluster_endpoint" {
  description = "API server endpoint for the EKS cluster"
  value       = aws_eks_cluster.main.endpoint
}

output "ecr_repository_url" {
  description = "ECR repository URL for Docker image pushes"
  value       = aws_ecr_repository.app.repository_url
}

output "mlflow_s3_bucket" {
  description = "S3 bucket name for MLflow artifact storage"
  value       = aws_s3_bucket.mlflow.bucket
}

output "dvc_s3_bucket" {
  description = "S3 bucket name for DVC dataset versioning"
  value       = aws_s3_bucket.dvc.bucket
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "app_irsa_role_arn" {
  description = "IAM Role ARN for the Kubernetes service account"
  value       = aws_iam_role.app_irsa.arn
}
