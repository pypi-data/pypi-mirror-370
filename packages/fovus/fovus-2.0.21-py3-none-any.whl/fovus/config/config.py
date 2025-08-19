# Prod
from fovus.constants.cli_constants import (
    API_DOMAIN_NAME,
    AUTH_WS_API_URL,
    AWS_REGION,
    CLIENT_ID,
    DOMAIN_NAME,
    SSO_USER_POOL_ID,
    USER_POOL_ID,
    WORKSPACE_SSO_CLIENT_ID,
)


class Config:
    __conf = {
        CLIENT_ID: "353su1970rpnfcigu09j9078c0",
        API_DOMAIN_NAME: "https://api.fovus.co",
        USER_POOL_ID: "us-east-1_fVH5TjPp5",
        DOMAIN_NAME: "fovus.co",
        AUTH_WS_API_URL: "wss://websocket.fovus.co/cli-auth/",
        SSO_USER_POOL_ID: "us-east-1_CnRexWenj",
        WORKSPACE_SSO_CLIENT_ID: "r5tvmbh26n5o883pstbo9gapi",
        AWS_REGION: "us-east-1",
    }

    __gov_conf = {
        CLIENT_ID: "3q8r7k9mls49qb5mu3io9c5j83",
        API_DOMAIN_NAME: "https://api.fovus-gov.co",
        USER_POOL_ID: "us-gov-west-1_xnYxMZTbb",
        DOMAIN_NAME: "fovus-gov.co",
        AUTH_WS_API_URL: "wss://websocket.fovus-gov.co/cli-auth/",
        SSO_USER_POOL_ID: "us-gov-west-1_Y7Rc46zXy",
        WORKSPACE_SSO_CLIENT_ID: "5nmvcqpjbsflo9pot5fulhfef0",
        AWS_REGION: "us-gov-west-1",
    }

    _is_gov = False

    @staticmethod
    def set_is_gov(is_gov):
        Config._is_gov = is_gov

    @staticmethod
    def is_gov() -> bool:
        return Config._is_gov

    @staticmethod
    def get(key):
        if Config._is_gov:
            return Config.__gov_conf[key]

        return Config.__conf[key]
