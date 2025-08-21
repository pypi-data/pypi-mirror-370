# simplex/core/config/auth.py

from simplex.core.config.environment import ENVIRONMENT

# Authentication configurations for different environments
AUTH_CONFIG_DEV = {
    "domain": "auth-dev.onstrusoft.com",
    "client_id": "X4qsjclYoVWsWHdsx8ostSCgTyiYbf3o",
    "audience": "https://simplex-gateway-dev.private.strusoft.com/",
    "scope": ""
}

AUTH_CONFIG_TEST = {
    "domain": "auth-test.onstrusoft.com",
    "client_id": "xAfEqnFALVzuAIKR5e2JFAyakBhc0gs9",
    "audience": "https://simplex-gateway-test.private.strusoft.com/",
    "scope": ""
}

AUTH_CONFIG_STAGE = {
    "domain": "auth-stage.onstrusoft.com",
    "client_id": "Tgq0jZq7Jo0l7lsVJwqoM2t9BdYEyJRG",
    "audience": "https://simplex-gateway-stage.onstrusoft.com",
    "scope": ""
}

AUTH_CONFIG_PROD = {
    "domain": "auth.onstrusoft.com",
    "client_id": "SyUc2sj4bkjHwkmxdYuPqFLejxVAtAif",
    "audience": "https://simplex-gateway.onstrusoft.com",
    "scope": ""
}

def get_auth_config() -> dict:
    """
    Returns the appropriate authentication configuration based on the environment.
    
    Returns:
        dict: Authentication configuration for the specified environment
    """

    environment = ENVIRONMENT
    
    if environment.name == "DEV":
        return AUTH_CONFIG_DEV
    elif environment.name == "STAGE":
        return AUTH_CONFIG_STAGE
    elif environment.name == "PROD":
        return AUTH_CONFIG_PROD
    elif environment.name == "TEST":
        return AUTH_CONFIG_TEST
    else:
        # Default to PROD if environment is not recognized
        return AUTH_CONFIG_PROD