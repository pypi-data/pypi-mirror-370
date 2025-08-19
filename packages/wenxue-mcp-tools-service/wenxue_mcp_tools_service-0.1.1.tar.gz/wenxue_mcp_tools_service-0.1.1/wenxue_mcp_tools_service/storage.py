import uuid
from . import config
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

import logging

def upload_to_cloud(image_data: bytes, format: str) -> str:
    """上传图片到云存储"""
    if not config.UPLOAD_ENABLED:
        raise RuntimeError("云存储功能未启用")

    filename = f"{uuid.uuid4()}.{format}"
    q_cloud_config = CosConfig(
        Region=config.QCLOUD_REGION,
        SecretId=config.QCLOUD_SECRET_ID,
        SecretKey=config.QCLOUD_SECRET_KEY,
        Token=config.QCLOUD_TOKEN,
        Scheme=config.QCLOUD_SCHEME)
    client = CosS3Client(q_cloud_config)

    bucketName = config.QCLOUD_BUCKET_NAME
    appId = config.QCLOUD_APP_ID


    try:
        response = client.put_object(
            Bucket=bucketName + '-' + appId,
            Key='pdf2img/' + filename,
            Body=image_data)
        logging.info(response)


        url = client.get_object_url(
            Bucket=bucketName + '-' + appId,
            Key='pdf2img/' + filename
        )
        # print(url)
        return url
    except Exception as e:
        raise ConnectionError(f"文件上传失败: {e}")


