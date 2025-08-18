"""
Implementation of `zut.files` for S3-compatible buckets.
"""
from __future__ import annotations

import os
import re
from typing import NamedTuple
from urllib.parse import urlparse

import boto3
import botocore.client
import botocore.exceptions
import botocore.awsrequest

from zut import DelayedStr, get_logger
from zut.files import BaseAdapter, BaseOpenTempContext

# Fix botocore expecting a reason phrase in "100 Continue" responses, which makes tests with adobe/s3mock fail
# See: https://github.com/boto/botocore/issues/3455
def _is_100_continue_status(self: botocore.awsrequest.AWSConnection, maybe_status_line: bytes):
    parts = maybe_status_line.split(None, 2)
    # Check for HTTP/<version> 100 Continue\r\n
    return (
        len(parts) >= 2
        and parts[0].startswith(b'HTTP/')
        and parts[1] == b'100'
    )
botocore.awsrequest.AWSConnection._is_100_continue_status = _is_100_continue_status


_logger = get_logger(__name__)
_credentials: dict[str|None, tuple[str,DelayedStr|str]] = {}
_clients: dict[str, botocore.client.BaseClient] = {}

def configure_s3(endpoint: str|None, access_key_id: str, secret_access_key: DelayedStr|str):
    if endpoint is not None:
        endpoint = get_normalized_s3_endpoint(endpoint)[0]
    _credentials[endpoint] = access_key_id, secret_access_key


def get_normalized_s3_endpoint(endpoint: str) -> tuple[str, str]:
    if not '://' in endpoint:
        endpoint = f'https://{endpoint}'
    parts = urlparse(endpoint)
    
    netloc = parts.netloc
    if parts.scheme == 'https':
        if netloc.endswith(':443'):
            netloc = netloc[:-4]
    elif parts.scheme == 'http':
        if netloc.endswith(':80'):
            netloc = netloc[:-3]

    # Search bucket name in netloc
    pos = netloc.rfind('.s3.')
    if pos > 0:
        bucket = netloc[0:pos]
        return f'{parts.scheme}://{netloc[pos+1:]}', bucket
    else:
        return f'{parts.scheme}://{netloc}', ''
    

S3NormalizedPath = NamedTuple('S3NormalizedPath', [('endpoint', str), ('bucket', str), ('key', str)])


def normalize_s3_path(url: str|os.PathLike) -> S3NormalizedPath:
    if not isinstance(url, str):
        url = str(url)
    if url.startswith('s3:'):
        url = url[3:]

    endpoint, bucket = get_normalized_s3_endpoint(url)
    
    # Search bucket and object key in path
    path = urlparse(url).path
    if bucket:
        key = path.lstrip('/')
    else:
        m = re.match(r'/([^/]+)/(.+)', path)
        if m:
            bucket = m[1]
            key = m[2]
        else:
            bucket = path.strip('/')
            key = ''

    return S3NormalizedPath(endpoint, bucket, key)


def get_s3_client(endpoint: str) -> botocore.client.BaseClient:
    client = _clients.get(endpoint)
    if not client:
        kwargs = {
            'endpoint_url': endpoint,
            'use_ssl': False if endpoint.startswith('http://') else True,
        }

        credentials = _credentials.get(endpoint)
        if credentials:
            access_key_id, secret_access_key = credentials
            kwargs['aws_access_key_id'] = access_key_id
            kwargs['aws_secret_access_key'] = DelayedStr.ensure_value_notblank(secret_access_key)
            _logger.debug("Create s3 client for endpoint %s using access key %s", endpoint, access_key_id)
        else:
            if not endpoint.startswith(('http://127.0.0.1:', 'http://localhost:', 'http://s3:')):
                raise ValueError(f"Credentials not configured for S3 endpoint {endpoint}")
            kwargs['aws_access_key_id'] = ''
            kwargs['aws_secret_access_key'] = ''
            kwargs['config'] = botocore.client.Config(signature_version=botocore.UNSIGNED)
            _logger.debug("Create s3 client for endpoint %s without an access key", endpoint)

        client = boto3.client('s3', **kwargs)
        _clients[endpoint] = client
    return client


def s3_object_exists(path: str|os.PathLike|S3NormalizedPath) -> bool:
    if not isinstance(path, tuple):
        path = normalize_s3_path(path)
    s3 = get_s3_client(path.endpoint)
    try:
        s3.head_object(Bucket=path.bucket, Key=path.key)
        return True
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            raise


def s3_path_exists(path: str|os.PathLike|S3NormalizedPath) -> bool:
    if not isinstance(path, tuple):
        path = normalize_s3_path(path)
    s3 = get_s3_client(path.endpoint)
    resp = s3.list_objects(Bucket=path.bucket, Prefix=path.key, MaxKeys=1)
    return True if resp.get('Contents') else False


class S3OpenContext(BaseOpenTempContext[S3NormalizedPath]):
    def before_open_temp(self):
        self.s3 = get_s3_client(self.path.endpoint)        
        if self.is_reading:
            try:
                self.s3.download_file(self.path.bucket, self.path.key, self.temp_path)            
            except Exception as err:
                if isinstance(err, botocore.exceptions.ClientError) and err.response['Error']['Code'] == '404':
                    raise FileNotFoundError(f"Key '{self.path.key}' not found in bucket '{self.path.bucket}'") from None
                else:
                    raise err from None

    def after_close_temp(self):
        if self.is_writing:
            try:
                if os.stat(self.temp_path).st_size < 1024**3:
                    with open(self.temp_path, 'rb') as fp:
                        body = fp.read()
                    self.s3.put_object(Bucket=self.path.bucket, Key=self.path.key, Body=body)
                else:
                    self.s3.upload_file(bucket=self.path.bucket, key=self.path.key, filename=self.temp_path)
            except Exception as err:
                raise err from None


class S3Adapter(BaseAdapter[S3NormalizedPath]):
    open_context_cls = S3OpenContext

    @classmethod
    def normalize_path(cls, path: str|os.PathLike|S3NormalizedPath) -> S3NormalizedPath:
        if not isinstance(path, tuple):
            path = normalize_s3_path(path)
        return path
    
    @classmethod
    def exists(cls, path: str|os.PathLike|S3NormalizedPath) -> bool:
        return s3_path_exists(path)

    @classmethod
    def makedirs(cls, path: str|os.PathLike|S3NormalizedPath, *, exist_ok: bool = False):
        pass # nothing to do

    @classmethod
    def _remove(cls, path: str|os.PathLike|S3NormalizedPath, *, tree_ok: bool = False):
        if not isinstance(path, tuple):
            path = normalize_s3_path(path)
        s3 = get_s3_client(path.endpoint)

        if tree_ok:
            resp = s3.list_objects(Bucket=path.bucket, Prefix=path.key)
            objects_to_delete = resp.get('Contents')
            if not objects_to_delete:
                raise FileNotFoundError(f"No S3 object found with prefix '{path.key}' in bucket '{path.bucket}'")
            
            delete_keys = {
                'Objects': [{'Key' : k} for k in [obj['Key'] for obj in objects_to_delete]]
            }
            s3.delete_objects(Bucket=path.bucket, Delete=delete_keys)
        else:
            resp = s3.delete_object(Bucket=path.bucket, Key=path.key)
            if not resp['DeleteMarker']:
                raise FileNotFoundError(f"No S3 object found with key '{path.key}' in bucket '{path.bucket}'")
