# main.py

import os
import boto3
from botocore.exceptions import ClientError
from langchain_community.document_loaders import S3DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec


def get_parameter(name, with_decryption=False):
    ssm = boto3.client('ssm')
    try:
        response = ssm.get_parameter(
            Name=name,
            WithDecryption=with_decryption
        )
        return response['Parameter']['Value']
    except ClientError as e:
        print(f"Error retrieving parameter {name}: {e}")
        return None

def main():
    # Set environment variables or use defaults for local testing
    s3_bucket_name = os.environ.get('S3_BUCKET_NAME', 'design-documents-bucket')
    pinecone_api_key_param = os.environ.get('PINECONE_API_KEY_PARAM', '/rag_data_ingestion/dev/pinecone_api_key')
    openai_api_key_param = os.environ.get('OPENAI_API_KEY_PARAM', '/rag_data_ingestion/dev/openai_api_key')
    pinecone_env_param = os.environ.get('PINECONE_ENV_PARAM', '/rag_data_ingestion/dev/pinecone_environment')

    # Get API keys and environment variables from Parameter Store
    PINECONE_API_KEY = get_parameter(pinecone_api_key_param, with_decryption=True)
    OPENAI_API_KEY = get_parameter(openai_api_key_param, with_decryption=True)
    PINECONE_ENVIRONMENT = get_parameter(pinecone_env_param)

    # Initialize OpenAI Embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    # Initialize Pinecone client
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index_name = "design-docs-index"

    # Check if index exists
    existing_indexes = pc.list_indexes().names()
    if index_name not in existing_indexes:
        # Create a new index
        pc.create_index(
            name=index_name,
            dimension=1536,
            metric='cosine',  # or 'euclidean', depending on your preference
            spec=ServerlessSpec(
                cloud='aws',
                region=PINECONE_ENVIRONMENT  # Ensure this matches your Pinecone environment
            )
        )
    index = pc.Index(index_name)

    # Load documents from S3
    loader = S3DirectoryLoader(bucket=s3_bucket_name)
    raw_documents = loader.load()
    print(f"Loaded {len(raw_documents)} documents from S3")

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=50)
    documents = text_splitter.split_documents(raw_documents)
    print(f"Split into {len(documents)} chunks")

    # Prepare data for upsert
    print(f"Total number of documents in S3: {len(documents)} documents")
    batch_size = 10  # Adjust batch size as needed
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        ids = []
        vectors = []
        metadata_list = []

        for idx, doc in enumerate(batch):
            # Generate embedding
            embedding = embeddings.embed_query(doc.page_content)

            # Create unique ID for each chunk
            doc_id = f"{doc.metadata.get('source', 'doc')}_{i}_{idx}"

            # Prepare data for upsert
            ids.append(doc_id)
            vectors.append(embedding)
            metadata_list.append(doc.metadata)

        # Upsert batch into Pinecone
        index.upsert(vectors=zip(ids, vectors, metadata_list))

    print("**** Loading to Pinecone vector store done ****")

if __name__ == "__main__":
    main()
