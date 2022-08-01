import environ,os, boto3
from pathlib import Path
import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

env = environ.Env(
    DEBUG=(bool, True)
)

def upload(user,image):
    s3 = boto3.client('s3',
        aws_access_key_id=env('AWSAccessKeyId'),
        aws_secret_access_key=env('AWSSecretKey'),
        region_name='ap-northeast-2',
    )

    Bucket = "pracs3"

    key = f'{user}/profile.jpg'

    s3.put_object(
        ACL="public-read",
        Bucket=Bucket,
        Body=image,
        Key=key,
        ContentType=image.content_type
        )

    url = f'https://{Bucket}.s3.ap-northeast-2.amazonaws.com/{key}'

    return url