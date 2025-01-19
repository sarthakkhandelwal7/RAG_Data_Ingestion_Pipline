# variables.tf

variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "us-east-1"
}

variable "pinecone_api_key" {
  description = "Pinecone API Key"
  type        = string
}

variable "pinecone_environment" {
  description = "Pinecone Environment"
  type        = string
}

variable "openai_api_key" {
  description = "OpenAI API Key"
  type        = string
}

variable "s3_bucket_name" {
  description = "S3 Bucket Name for Documents"
  type        = string
}

variable "parameter_store_path" {
  description = "Base path for Parameter Store parameters"
  type        = string
  default     = "/rag_data_ingestion/dev/"
}

variable "lambda_image_uri" {
  description = "The ECR image URI for the Lambda function"
  type        = string
}

