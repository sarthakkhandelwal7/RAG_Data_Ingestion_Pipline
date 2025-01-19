import os
import boto3
from botocore.exceptions import ClientError
from langchain_community.document_loaders import UnstructuredHTMLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
import nltk

nltk_data_dir = '/tmp/nltk_data'
if not os.path.exists(nltk_data_dir):
    os.makedirs(nltk_data_dir)
    
nltk.data.path.append(nltk_data_dir)

s3_client = boto3.client('s3')

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

def lambda_handler(event, context):
    # Extract the bucket name and object key from the S3 event
    print("Records below\n", event['Records'])
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']

        # Download the document from S3 to the local /tmp directory
        download_path = f"/tmp/{object_key.split('/')[-1]}"
        s3_client.download_file(bucket_name, object_key, download_path)
        
        loader = UnstructuredHTMLLoader(download_path)
        raw_documents = loader.load()

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=50)
        documents = text_splitter.split_documents(raw_documents)

        pinecone_api_key = get_parameter(os.environ['PINECONE_API_KEY_PARAM'], with_decryption=True)
        openai_api_key = get_parameter(os.environ['OPENAI_API_KEY_PARAM'], with_decryption=True)
        pinecone_environment = get_parameter(os.environ['PINECONE_ENV_PARAM'])

        embedding = OpenAIEmbeddings(openai_api_key=openai_api_key, model="text-embedding-3-small")

        pc = Pinecone(api_key=pinecone_api_key)

        index_name = "design-docs-index"
        if index_name not in pc.list_indexes().names():
            pc.create_index(
                name=index_name,
                dimension=1536,
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region=pinecone_environment
                )
            )

        texts = []
        metadatas = []
        print(f"Going to add {len(documents)} to Pinecone")
        for doc in documents:
            
            new_url = doc.metadata["source"]
            new_url = new_url.replace("langchain-docs", "https:/")
            doc.metadata.update({"source": new_url})

            texts.append(doc.page_content)
            metadatas.append(doc.metadata)

        # PineconeVectorStore.from_texts(texts, embeddings, metadatas=metadatas, async_req=False, index_name="design-docs-index")
        vector_Store = PineconeVectorStore(index=pc.Index(index_name), embedding=embedding)
        vector_Store.add_texts(texts, metadatas=metadatas, async_req=False)
        print("**** Loading to Pinecone vector store done ****")