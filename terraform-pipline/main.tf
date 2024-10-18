# main.tf

provider "aws" {
  region = var.aws_region  

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
