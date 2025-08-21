import boto3
import pandas as pd
from io import StringIO
from typing import Dict, Any, Optional
from botocore.response import StreamingBody


class S3Helper:
    def __init__(self, client: Any, s3_bucket: str) -> None:
        self.client = client
        self.__bucket = s3_bucket

    @staticmethod
    def create_by_cfg(cfg: Dict[str, Any], **kwargs) -> 'S3Helper':
        s3_client = boto3.client(
            's3',
            region_name=cfg.get('aws_region'),
            aws_access_key_id=cfg['aws_access_key_id'],
            aws_secret_access_key=cfg['aws_secret_access_key'],
            endpoint_url=cfg.get('endpoint_url'),
            **kwargs
        )
        return S3Helper(s3_client, cfg['s3_bucket'])

    def get_object(self, key: str, bucket: Optional[str] = None) -> Optional[StreamingBody]:
        if bucket is None:
            bucket = self.__bucket
        response = self.client.get_object(Bucket=bucket, Key=key)
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        if status == 200:
            return response.get("Body")
        else:
            print(f"S3Helper: get by key=\"{key}\" failed")
            return None

    def get_df(self, key: str, bucket: Optional[str] = None) -> pd.DataFrame:
        obj = self.get_object(key, bucket=bucket)
        if obj is None:
            return pd.DataFrame()
        return pd.read_csv(obj)

    def save_object(self, body: Any, key: str, bucket: Optional[str] = None) -> None:
        if bucket is None:
            bucket = self.__bucket
        response = self.client.put_object(Bucket=bucket, Body=body, Key=key)
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        if status >= 400:
            print(f"S3Helper: save by key=\"{key}\" failed")

    def save_df(self, df: pd.DataFrame, key: str, bucket: Optional[str] = None) -> None:
        csv_buf = StringIO()
        df.to_csv(csv_buf, header=True, index=False)
        csv_buf.seek(0)
        self.save_object(csv_buf.getvalue(), key, bucket=bucket)

    def delete_object(self, key: str, bucket: Optional[str] = None) -> None:
        if bucket is None:
            bucket = self.__bucket
        response = self.client.delete_object(Bucket=bucket, Key=key)
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        if status >= 400:
            print(f"S3Helper: delete by key=\"{key}\" failed")
