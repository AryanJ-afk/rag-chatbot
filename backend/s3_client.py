from dotenv import load_dotenv
import boto3
import os

load_dotenv()
s3 = boto3.client('s3')

def upload_file_to_s3(file_bytes, filename, user_id):
    
    bucket_name = os.getenv("S3_BUCKET_NAME")
    s3_key = f"{user_id}/{filename}"
    
    s3.put_object(Bucket=bucket_name,
                  Key=s3_key,
                  Body=file_bytes,
                  ContentType='application/pdf')
    
    return {"s3_key": s3_key, "path": f"{bucket_name}/{s3_key}"}

def download_file_from_s3(s3_key) -> bytes:
    
    bucket_name = os.getenv("S3_BUCKET_NAME")
    response = s3.get_object(Bucket=bucket_name, Key=s3_key)
    
    pdf_bytes = response['Body'].read()
    
    return pdf_bytes