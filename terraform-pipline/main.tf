# Provider configuration for AWS
provider "aws" {
  region = var.aws_region  # Ensure your region is set using variables
}

# Data source to get AWS account ID
data "aws_caller_identity" "current" {}

# S3 Bucket
resource "aws_s3_bucket" "documents_bucket" {
  bucket = var.s3_bucket_name
}

# AWS Systems Manager Parameter Store Parameters

# Pinecone API Key
resource "aws_ssm_parameter" "pinecone_api_key" {
  name        = "${var.parameter_store_path}pinecone_api_key"
  description = "Pinecone API Key"
  type        = "SecureString"
  value       = var.pinecone_api_key
  overwrite   = true
}

# OpenAI API Key
resource "aws_ssm_parameter" "openai_api_key" {
  name        = "${var.parameter_store_path}openai_api_key"
  description = "OpenAI API Key"
  type        = "SecureString"
  value       = var.openai_api_key
  overwrite   = true
}

# Pinecone Environment
resource "aws_ssm_parameter" "pinecone_environment" {
  name        = "${var.parameter_store_path}pinecone_environment"
  description = "Pinecone Environment"
  type        = "String"
  value       = var.pinecone_environment
  overwrite   = true
}

# Add IAM Role for Lambda to access S3
resource "aws_iam_role" "lambda_role" {
  name = "lambda_s3_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "lambda_ssm_policy" {
  name   = "lambda_ssm_policy"
  role   = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect   = "Allow",
      Action   = "ssm:GetParameter",
      Resource = [
        "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter${var.parameter_store_path}*"
      ]
    }]
  })
}

# Attach policies to Lambda role for S3 access and CloudWatch logs
resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "lambda_logs_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Define the Lambda function using a Docker image from ECR
resource "aws_lambda_function" "ingest_documents" {
  function_name = "ingest_documents_function"
  role          = aws_iam_role.lambda_role.arn
  package_type  = "Image"  # Indicating we're using a Docker image
  image_uri     = var.lambda_image_uri
  timeout       = 90
  memory_size   = 512

  environment {
    variables = {
      S3_BUCKET_NAME          = aws_s3_bucket.documents_bucket.bucket
      PINECONE_API_KEY_PARAM  = "/rag_data_ingestion/dev/pinecone_api_key"
      OPENAI_API_KEY_PARAM    = "/rag_data_ingestion/dev/openai_api_key"
      PINECONE_ENV_PARAM      = "/rag_data_ingestion/dev/pinecone_environment"
    }
  }

  depends_on = [aws_iam_role_policy_attachment.lambda_policy_attachment]
}

# S3 Event Notification to trigger Lambda when a new document is uploaded
resource "aws_s3_bucket_notification" "s3_lambda_trigger" {
  bucket = aws_s3_bucket.documents_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.ingest_documents.arn
    events              = ["s3:ObjectCreated:*"]  # Trigger on object creation
  }

  depends_on = [aws_lambda_permission.allow_s3_invoke]
}

# Allow S3 to invoke the Lambda function
resource "aws_lambda_permission" "allow_s3_invoke" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingest_documents.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.documents_bucket.arn
}
