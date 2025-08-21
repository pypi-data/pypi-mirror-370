import base64
from enum import Enum
from typing import Optional
from urllib.parse import urlparse

from flask import current_app

DEFAULT_PROD_CDN_URLS = [
    'https://d1cka1o15bmsqv.cloudfront.net',
    'https://dashhudson-static.s3.amazonaws.com',
    'https://cdn.dashhudson.com',
    'https://cdn.dashsocial.com',
]
DEFAULT_DEV_CDN_URLS = [
    'https://d9jugqqmw8t1m.cloudfront.net',
    'https://dev-dashhudson-static.s3.amazonaws.com',
    'https://cdn.dhdev.co',
]
DEFAULT_OLD_DEV_CDN_URLS = [
    'https://dxw5fz2k5hbid.cloudfront.net',
    'https://dashhudson-dev.s3.amazonaws.com',
    'https://cdn.dhdev.io',
]
DEFAULT_PROD_IMAGE_API_URL = 'https://images.dashsocial.com'
DEFAULT_OLD_PROD_IMAGE_API_URL = 'https://images.dashhudson.com'
DEFAULT_DEV_IMAGE_API_URL = 'https://images.dhdev.co'
DEFAULT_OLD_DEV_IMAGE_API_URL = 'https://images.dhdev.io'


class ImageApi:
    class FitType(Enum):
        INSIDE = 'inside'
        COVER = 'cover'

    @classmethod
    def build_url(
        cls,
        url_orig: str,
        w: Optional[int] = None,
        h: Optional[int] = None,
        fit: Optional[FitType] = None,
        download: bool = False,
        extension: str = 'jpg',
    ) -> str:
        """
        Returns a formatted URL to the Image API service
        :param url_orig: String, full URL to Dash Hudson image
            e.g. https://dashhudson-dev.s3.amazonaws.com/images/items/1532976128.41429521549.jpeg
        :param w: Int, requested width
        :param h: Int, requested height
        :param fit: FitType, how the image should be fit into the dimensions
            INSIDE: fit the image inside the bounds, maintaining aspect ratio
            COVER: fit the image to the size of the box, using a center crop if necessary
        :param download: Bool, flag that's sent to the image API to receive a download header,
            default False
        :param extension: String, image file extension, default 'jpg'
        """
        if not url_orig:
            return url_orig

        # Prevents accidental re-encoding of URLs
        (
            dev_api_url,
            prod_api_url,
            old_dev_api_url,
            old_prod_api_url,
        ) = ImageApi._get_image_api_urls()
        if (
            url_orig.startswith(prod_api_url)
            or url_orig.startswith(old_prod_api_url)
            or url_orig.startswith(dev_api_url)
            or url_orig.startswith(old_dev_api_url)
        ):
            url_orig = cls._decode_original_url(url_orig)

        host = cls._get_image_api_host_for_url(url_orig)

        url = url_orig.encode('utf-8')
        url_bytes = base64.urlsafe_b64encode(url)
        encoded_path = str(url_bytes, 'utf-8')

        params = []
        if w is not None:
            params.append(f'w={w}')
        if h is not None:
            params.append(f'h={h}')
        if fit is not None:
            params.append(f'fit={fit.value}')
        if download:
            params.append('download=true')

        param_string = f'?{"&".join(params)}' if len(params) > 0 else ''

        return f'{host}/{encoded_path}.{extension}{param_string}'

    @classmethod
    def _decode_original_url(cls, url_orig):
        image_path = urlparse(url_orig).path[1:]
        image_path_without_extension = image_path.split('.')[0]
        return base64.b64decode(image_path_without_extension).decode('utf-8')

    @classmethod
    def _get_image_api_host_for_url(cls, url_orig):
        dev_api_url, prod_api_url, old_dev_api_url, _ = ImageApi._get_image_api_urls()
        prod_cdn_urls = (
            current_app.config.get('DH_POTLUCK_PROD_IMAGE_CDN_URLS') or DEFAULT_PROD_CDN_URLS
        )
        for prod_cdn_url in prod_cdn_urls:
            if url_orig.startswith(prod_cdn_url):
                return prod_api_url
        old_dev_cdn_urls = (
            current_app.config.get('DH_POTLUCK_OLD_DEV_IMAGE_CDN_URLS') or DEFAULT_OLD_DEV_CDN_URLS
        )
        for old_dev_cdn_url in old_dev_cdn_urls:
            if url_orig.startswith(old_dev_cdn_url):
                return old_dev_api_url
        dev_cdn_urls = (
            current_app.config.get('DH_POTLUCK_DEV_IMAGE_CDN_URLS') or DEFAULT_DEV_CDN_URLS
        )
        for dev_cdn_url in dev_cdn_urls:
            if url_orig.startswith(dev_cdn_url):
                return dev_api_url
        raise UnsupportedOriginalImageUrlException()

    @staticmethod
    def _get_image_api_urls():
        dev_url = (
            current_app.config.get('DH_POTLUCK_DEV_IMAGE_API_URL') or DEFAULT_DEV_IMAGE_API_URL
        )
        prod_url = (
            current_app.config.get('DH_POTLUCK_PROD_IMAGE_API_URL') or DEFAULT_PROD_IMAGE_API_URL
        )
        old_dev_url = (
            current_app.config.get('DH_POTLUCK_OLD_DEV_IMAGE_API_URL')
            or DEFAULT_OLD_DEV_IMAGE_API_URL
        )
        old_prod_url = (
            current_app.config.get('DH_POTLUCK_OLD_PROD_IMAGE_API_URL')
            or DEFAULT_OLD_PROD_IMAGE_API_URL
        )
        return dev_url, prod_url, old_dev_url, old_prod_url


class UnsupportedOriginalImageUrlException(Exception):
    pass
