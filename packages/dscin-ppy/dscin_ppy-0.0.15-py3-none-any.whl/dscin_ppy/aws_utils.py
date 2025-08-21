import re
import boto3


def build_s3_url(bucket, key):
    return f's3a://{bucket}/{key}'


def read_object_from_s3(bucket, key):
    s3_client = boto3.client("s3")
    try:
        # Get the file inside the S3 Bucket
        s3_response = s3_client.get_object(Bucket=bucket, Key=key)
        return s3_response["Body"].read()
    except s3_client.exceptions.NoSuchBucket as e:
        print("The S3 bucket does not exist.")
        print(e)
    except s3_client.exceptions.NoSuchKey as e:
        print("The S3 objects does not exist in the S3 bucket.")
        print(e)


def open_object_from_s3(bucket, key):
    s3_client = boto3.client("s3")
    try:
        # Get the file inside the S3 Bucket
        s3_response = s3_client.get_object(Bucket=bucket, Key=key)
        return s3_response["Body"]
    except s3_client.exceptions.NoSuchBucket as e:
        print("The S3 bucket does not exist.")
        print(e)
    except s3_client.exceptions.NoSuchKey as e:
        print("The S3 objects does not exist in the S3 bucket.")
        print(e)


def write_dataframe_to_s3(dataframe, s3_url, file_type):
    if file_type == "parquet":
        dataframe.to_parquet(s3_url, engine='pyarrow', index=False)
    elif file_type == "csv":
        dataframe.to_csv(s3_url, index=False)
    elif file_type == "xlsx":
        dataframe.to_excel(s3_url, index=False)
    else:
        raise Exception("Format not supported")

    # copy the file in the same location (to avoid permission problems)
    match = re.findall("s3a://([^/]+)/(.+)", s3_url)
    if len(match) > 0:
        s3_bucket, s3_key = match[0]
        copy_source = {"Bucket": s3_bucket, "Key": s3_key}
        copy_s3_object(copy_source, s3_bucket, s3_key)


def get_value_from_parameter_store(key, decrypt=False):
    ssm_client = boto3.client("ssm")
    value = ssm_client.get_parameter(Name=key, WithDecryption=decrypt)
    return value["Parameter"]["Value"]


def save_to_s3(df, s3_bucket, s3_key, file_format):
    s3_url = build_s3_url(s3_bucket, s3_key)
    write_dataframe_to_s3(df, s3_url, file_format)


def copy_s3_object(copy_source, target_bucket, target_key):
    s3_client = boto3.client("s3")
    s3_client.copy_object(
        ACL="bucket-owner-full-control",
        CopySource=copy_source,
        Bucket=target_bucket,
        Key=target_key
    )


def list_s3_objects(s3_bucket, s3_key_prefix):
    s3_client = boto3.client("s3")
    objects = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=s3_key_prefix)
    # Extract the keys of the objects
    objects_list = [
        obj['Key'] for obj in objects.get('Contents', []) if obj
    ]
    return objects_list

def upload_object_to_s3(obj, s3_bucket, s3_key):
    s3_client = boto3.client("s3")
    s3_client.upload_fileobj(obj, s3_bucket, s3_key)


def remove_object_from_s3(bucket, key):
    s3_client = boto3.client('s3')
    s3_client.delete_object(Bucket=bucket, Key=key)

def put_object_to_s3(obj, s3_bucket, s3_key):
    s3_resource = boto3.resource("s3")
    s3_resource.Object(s3_bucket, s3_key).put(Body=obj)