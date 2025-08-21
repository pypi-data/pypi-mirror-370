from datetime import datetime
import importlib.metadata

__copyright__ = f"Copyright (C) {datetime.now().year} :em engineering methods AG. All rights reserved."
__author__ = "Daniel Klein"

try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0-dev"
    
__project__ = "aas-http-client"
__package__ = "aas-http-client"

from aas_http_client.core.version_check import check_for_update
from aas_http_client.client import create_client_by_config, create_client_by_url, AasHttpClient
from aas_http_client.utilities import model_builder
from aas_http_client.wrapper.sdk_wrapper import create_wrapper_by_config, create_wrapper_by_url, SdkWrapper

check_for_update()

__all__ = ["create_client_by_config", "create_client_by_url", "AasHttpClient", "model_builder", "create_wrapper_by_config", "create_wrapper_by_url", "SdkWrapper"]