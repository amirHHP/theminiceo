import os
import sys
import json
import subprocess
import mimetypes
from concurrent.futures import ThreadPoolExecutor, as_completed

PDF_DIR = "content/pdfs"
STATE_FILE = "data/r2_uploaded.json"
BUCKET_NAME = "theminiceo-books"

def get_clean_env():
    env = os.environ.copy()
    for k in ['http_proxy', 'https_proxy', 'all_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
        env.pop(k, None)
    return env

def load_uploaded_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_uploaded_state(uploaded_set):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(sorted(list(uploaded_set)), f, indent=2)

def upload_file(filename):
    filepath = os.path.join(PDF_DIR, filename)
    if not os.path.exists(filepath):
        return filename, False, "File not found"
        
    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    content_type, _ = mimetypes.guess_type(filepath)
    if not content_type:
        content_type = "application/pdf"
        
    cmd = [
        "npx", "wrangler", "r2", "object", "put",
        f"{BUCKET_NAME}/{filename}",
        "--file", filepath,
        "--content-type", content_type,
        "--remote"
    ]
    
    # Dynamic timeout: at least 600s, plus 80s per MB for large files
    file_timeout = max(600, int(size_mb * 80))
    
    try:
        res = subprocess.run(
            cmd,
            env=get_clean_env(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=file_timeout
        )
        if res.returncode == 0:
            return filename, True, f"{size_mb:.1f} MB"
        else:
            return filename, False, res.stderr.strip() or res.stdout.strip()
    except subprocess.TimeoutExpired:
        return filename, False, f"Timeout ({file_timeout}s)"
    except Exception as e:
        return filename, False, str(e)

def main():
    with open("data/books_metadata.json", "r") as f:
        books = json.load(f)
        
    uploaded = load_uploaded_state()
    # Also add the one we uploaded already as a test
    uploaded.add("The_Lean_Startup_How_Todays_Entrepreneurs_Use_Continuous_Innovation.pdf")
    save_uploaded_state(uploaded)
    
    to_upload = [b["filename"] for b in books if b["filename"] not in uploaded]
    # Sort files by size ascending so smaller files finish quickly
    to_upload.sort(key=lambda fn: os.path.getsize(os.path.join(PDF_DIR, fn)) if os.path.exists(os.path.join(PDF_DIR, fn)) else 0)
    total_to_upload = len(to_upload)
    
    print(f"📊 Total books: {len(books)}")
    print(f"✅ Already uploaded: {len(uploaded)}")
    print(f"⏳ Remaining to upload: {total_to_upload}")
    
    if total_to_upload == 0:
        print("🎉 All books are already uploaded to Cloudflare R2!")
        return

    # Check for limit argument (e.g. python3 upload_to_r2.py --batch 10)
    batch_limit = None
    if "--batch" in sys.argv:
        idx = sys.argv.index("--batch")
        if idx + 1 < len(sys.argv):
            batch_limit = int(sys.argv[idx + 1])
            to_upload = to_upload[:batch_limit]
            print(f"Running in batch mode: processing {len(to_upload)} files...")

    # Upload with 1 worker to devote full bandwidth to each large file
    max_workers = 1
    success_count = 0
    fail_count = 0
    
    print(f"\n🚀 Starting upload to Cloudflare R2 (bucket: {BUCKET_NAME}) with {max_workers} parallel workers...\n")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(upload_file, fn): fn for fn in to_upload}
        for i, future in enumerate(as_completed(futures), 1):
            fn, ok, msg = future.result()
            if ok:
                uploaded.add(fn)
                save_uploaded_state(uploaded)
                success_count += 1
                print(f"[{i}/{len(to_upload)}] ✅ Uploaded: {fn} ({msg})")
            else:
                fail_count += 1
                print(f"[{i}/{len(to_upload)}] ❌ Failed: {fn} -> {msg}")
                
    print(f"\n🏁 Finished batch! Successfully uploaded: {success_count}, Failed: {fail_count}")
    print(f"Total uploaded so far: {len(uploaded)} / {len(books)}")

if __name__ == "__main__":
    main()
