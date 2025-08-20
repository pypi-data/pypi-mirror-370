from typing import Optional

from pydantic import ValidationError
from rb_commons.orm.enum import MediaSource


class MediaUtils:
    BILLZ_S3_ENDPOINT_URL = "https://cdn-grocery.billz.ai/billz"
    BITTO_S3_ENDPOINT_URL = "https://api.bito.uz/upload-api/public/uploads"
    EURO_PHARM_S3_ENDPOINT_URL = "https://api.europharm.uz/images/click_webp"

    @classmethod
    def url_builder(cls, key: str, source: Optional[MediaSource] = MediaSource.ROBO):
        source = MediaSource.ROBO if source is None else source

        try:
            from rb_commons.configs.config import configs
            DIGITALOCEAN_S3_ENDPOINT_URL = configs.DIGITALOCEAN_S3_ENDPOINT_URL
            DIGITALOCEAN_STORAGE_BUCKET_NAME = configs.DIGITALOCEAN_STORAGE_BUCKET_NAME
        except ValidationError as e:
            from rb_commons.configs.v2.config import configs
            DIGITALOCEAN_S3_ENDPOINT_URL = configs.DIGITALOCEAN_S3_ENDPOINT_URL
            DIGITALOCEAN_STORAGE_BUCKET_NAME = configs.DIGITALOCEAN_STORAGE_BUCKET_NAME

        media_url = f"{DIGITALOCEAN_S3_ENDPOINT_URL}/{DIGITALOCEAN_STORAGE_BUCKET_NAME}/{key}"

        if source == MediaSource.BILLZ:
            media_url = f"{cls.BILLZ_S3_ENDPOINT_URL}/{key}"
        elif source == MediaSource.BITO:
            media_url = f"{cls.BITTO_S3_ENDPOINT_URL}/{key}"
        elif source == MediaSource.EUROPHARM:
            media_url = f"{cls.EURO_PHARM_S3_ENDPOINT_URL}/{key}"

        return media_url