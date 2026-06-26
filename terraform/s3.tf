# ─── S3 Bucket: MLflow Artifacts ────────────────────────────────────────────
resource "aws_s3_bucket" "mlflow" {
  bucket        = "${var.project_name}-mlflow-artifacts"
  force_destroy = false
  tags          = { Project = var.project_name, Purpose = "mlflow-artifacts" }
}

resource "aws_s3_bucket_versioning" "mlflow" {
  bucket = aws_s3_bucket.mlflow.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "mlflow" {
  bucket = aws_s3_bucket.mlflow.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# ─── S3 Bucket: DVC Dataset Storage ─────────────────────────────────────────
resource "aws_s3_bucket" "dvc" {
  bucket        = "${var.project_name}-dvc-storage"
  force_destroy = false
  tags          = { Project = var.project_name, Purpose = "dvc-data-versioning" }
}

resource "aws_s3_bucket_versioning" "dvc" {
  bucket = aws_s3_bucket.dvc.id
  versioning_configuration { status = "Enabled" }
}

# ─── DynamoDB: Terraform State Lock ─────────────────────────────────────────
resource "aws_dynamodb_table" "terraform_lock" {
  name         = "terraform-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = { Project = var.project_name, Purpose = "terraform-state-lock" }
}
