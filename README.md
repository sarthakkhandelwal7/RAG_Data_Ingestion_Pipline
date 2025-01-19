# RAG Data Ingestion Pipeline

An automated pipeline for ingesting HTML documents into a vector database (Pinecone) for RAG (Retrieval-Augmented Generation) applications. The pipeline uses AWS Lambda for serverless processing and is deployed using Terraform.

## Architecture Overview

The pipeline consists of the following components:

- **S3 Bucket**: Stores the input HTML documents
- **AWS Lambda**: Processes documents and generates embeddings using OpenAI
- **Pinecone**: Vector database for storing document embeddings
- **AWS Parameter Store**: Securely stores configuration and API keys
- **Docker**: Containerizes the Lambda function with all dependencies

## Prerequisites

- AWS Account
- Terraform installed
- Docker installed
- Pinecone account and API key
- OpenAI account and API key
- AWS CLI configured with appropriate credentials

## Project Structure

```
├── lambda_function/
│   ├── Dockerfile         # Docker configuration for Lambda function
│   ├── Pipfile           # Python dependencies
│   └── lambda_function.py # Main Lambda function code
└── terraform-pipeline/
    ├── main.tf           # Main Terraform configuration
    ├── variables.tf      # Terraform variables definition
    └── tfvars-example.md # Example variable values
```

## Setup and Deployment

### 1. Configure Environment Variables

Create a `terraform.tfvars` file in the `terraform-pipeline` directory using the example in `tfvars-example.md`:

```hcl
aws_region = "us-east-1"
pinecone_api_key = "your-pinecone-api-key"
pinecone_environment = "your-pinecone-environment"
openai_api_key = "your-openai-api-key"
s3_bucket_name = "your-bucket-name"
parameter_store_path = "/rag_data_ingestion/dev/"
lambda_image_uri = "account.dkr.ecr.region.amazonaws.com/repository:tag"
```

### 2. Build and Push Docker Image

```bash
cd lambda_function
docker build -t rag-ingestion-lambda .
# Tag and push to ECR (follow AWS ECR push commands)
```

### 3. Deploy Infrastructure

```bash
cd terraform-pipeline
terraform init
terraform plan
terraform apply
```

## How It Works

1. HTML documents are uploaded to the configured S3 bucket
2. S3 event triggers the Lambda function
3. Lambda function:
   - Downloads the document from S3
   - Loads and processes the HTML using UnstructuredHTMLLoader
   - Splits the content into chunks
   - Generates embeddings using OpenAI
   - Stores the embeddings in Pinecone

## Features

- Serverless architecture with AWS Lambda
- Secure storage of API keys in AWS Parameter Store
- Infrastructure as Code using Terraform
- Containerized Lambda function with all dependencies
- Automatic triggering on S3 uploads
- Document chunking for optimal processing
- Integration with OpenAI embeddings
- Serverless Pinecone vector database

## Environment Variables

The Lambda function expects the following environment variables:

- `S3_BUCKET_NAME`: Name of the S3 bucket
- `PINECONE_API_KEY_PARAM`: Parameter Store path for Pinecone API key
- `OPENAI_API_KEY_PARAM`: Parameter Store path for OpenAI API key
- `PINECONE_ENV_PARAM`: Parameter Store path for Pinecone environment

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Notes

- The Lambda function uses OpenAI's `text-embedding-3-small` model
- Document chunks are set to 600 characters with 50 character overlap
- Lambda timeout is set to 90 seconds
- Lambda memory is set to 512MB
- Pinecone index is created with cosine similarity metric
