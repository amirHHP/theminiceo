import os
import sys
import mimetypes
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

def load_env(env_path="scripts/.env"):
    config = {}
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    config[k.strip()] = v.strip()
    return config

def get_s3_client():
    env = load_env()
    access_key = env.get("ARVAN_ACCESS_KEY")
    secret_key = env.get("ARVAN_SECRET_KEY")
    endpoint = env.get("ARVAN_ENDPOINT", "https://s3.ir-thr-at1.arvanstorage.ir")
    
    if not access_key or not secret_key:
        raise ValueError("Missing ARVAN_ACCESS_KEY or ARVAN_SECRET_KEY in scripts/.env")
        
    s3 = boto3.client(
        's3',
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version='s3v4')
    )
    return s3, env.get("ARVAN_BUCKET", "tmc-pdfs")

def test_connection():
    s3, bucket = get_s3_client()
    print(f"Testing connection to bucket: {bucket}...")
    try:
        response = s3.list_objects_v2(Bucket=bucket, MaxKeys=5)
        print("✅ Connection successful!")
        contents = response.get('Contents', [])
        print(f"Existing objects in bucket: {len(contents)}")
        for obj in contents:
            print(f" - {obj['Key']} ({obj['Size']} bytes)")
        return True
    except ClientError as e:
        print(f"❌ Error connecting to bucket: {e}")
        return False

def upload_single_file(filename, pdf_dir="content/pdfs"):
    s3, bucket = get_s3_client()
    filepath = os.path.join(pdf_dir, filename)
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return False
        
    content_type, _ = mimetypes.guess_type(filepath)
    if not content_type:
        content_type = "application/pdf"
        
    print(f"Uploading {filename} to s3://{bucket}/ (size: {os.path.getsize(filepath)/(1024*1024):.2f} MB)...")
    try:
        s3.upload_file(
            filepath,
            bucket,
            filename,
            ExtraArgs={
                'ACL': 'public-read',
                'ContentType': content_type
            }
        )
        print(f"✅ Uploaded successfully: {filename}")
        return True
    except ClientError as e:
        print(f"❌ Upload failed: {e}")
        return False

def sync_all(pdf_dir="content/pdfs"):
    s3, bucket = get_s3_client()
    files = sorted([f for f in os.listdir(pdf_dir) if not f.startswith('.') and " (1)" not in f])
    
    # Get existing objects in bucket to avoid re-uploading
    existing_keys = set()
    print("Fetching existing objects list from bucket...")
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket):
        for obj in page.get('Contents', []):
            existing_keys.add(obj['Key'])
            
    print(f"Found {len(existing_keys)} existing files in bucket.")
    to_upload = [f for f in files if f not in existing_keys]
    print(f"Need to upload: {len(to_upload)} files out of {len(files)} total.")
    
    uploaded_count = 0
    for idx, f in enumerate(to_upload, 1):
        filepath = os.path.join(pdf_dir, f)
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        print(f"[{idx}/{len(to_upload)}] Uploading {f} ({size_mb:.1f} MB)...")
        content_type, _ = mimetypes.guess_type(filepath)
        if not content_type:
            content_type = "application/pdf"
        try:
            s3.upload_file(
                filepath,
                bucket,
                f,
                ExtraArgs={
                    'ACL': 'public-read',
                    'ContentType': content_type
                }
            )
            uploaded_count += 1
        except Exception as e:
            print(f"❌ Error uploading {f}: {e}")
            
    print(f"\n🎉 Sync finished! Uploaded {uploaded_count} files.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_connection()
    elif len(sys.argv) > 1 and sys.argv[1] == "--single":
        filename = sys.argv[2] if len(sys.argv) > 2 else "The-Lean-Startup.pdf"
        upload_single_file(filename)
    elif len(sys.argv) > 1 and sys.argv[1] == "--sync":
        sync_all()
    else:
        print("Usage:")
        print("  python3 upload_to_arvan.py --test")
        print("  python3 upload_to_arvan.py --single <filename>")
        print("  python3 upload_to_arvan.py --sync")
