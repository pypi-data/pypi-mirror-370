from importlib import metadata

from .curl import Curl

__title__ = "cffi_curl"
__description__ = metadata.metadata("cffi_curl")["Summary"]
__version__ = metadata.version("cffi_curl")
__curl_version__ = Curl().version().decode()
