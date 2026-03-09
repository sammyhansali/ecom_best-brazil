import os
from pathlib import PurePosixPath

import duckdb
import kagglehub
from dotenv import load_dotenv

load_dotenv()

# Download latest version
tmp_path = PurePosixPath(
    kagglehub.dataset_download("olistbr/brazilian-ecommerce").replace("\\", "/")
)
bucket_path = "s3://ecom-best-brazil/raw"

conn = duckdb.connect()
conn.execute("install httpfs")
conn.execute("load httpfs")
conn.execute("set s3_region=?", [os.getenv("AWS_REGION", "us-east-1")])
conn.execute("set s3_access_key_id=?", [os.getenv("AWS_ACCESS_KEY_ID")])
conn.execute("set s3_secret_access_key=?", [os.getenv("AWS_SECRET_ACCESS_KEY")])

for file in os.listdir(tmp_path):
    # conn.execute(f"SELECT * FROM '{tmp_path}/{file}'")
    stem = file.split(".")[0]
    conn.execute(f"""
        copy (
            SELECT *
            FROM read_csv_auto('{tmp_path}/{file}')
        )
        to '{bucket_path}/{stem}.parquet'
        (format parquet)
        ;
    """)

results = conn.fetchall()
