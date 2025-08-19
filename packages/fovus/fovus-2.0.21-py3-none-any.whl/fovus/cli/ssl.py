import os
import ssl

import certifi

ca_file = os.environ.get("FOVUS_CA_BUNDLE", default=certifi.where())

ssl_context = ssl.create_default_context(cafile=ca_file)


def configure_ssl_env():
    os.environ["AWS_CA_BUNDLE"] = ca_file
    os.environ["REQUESTS_CA_BUNDLE"] = ca_file
    os.environ["CURL_CA_BUNDLE"] = ca_file
    os.environ["CA_BUNDLE"] = ca_file
