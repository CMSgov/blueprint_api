import logging
import os
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Environment:
    def __init__(self):
        default_cors_headers = [
            "accept",
            "accept-encoding",
            "access-control-allow-origin",
            "authorization",
            "content-type",
            "dnt",
            "origin",
            "user-agent",
            "x-csrftoken",
            "x-requested-with",
        ]
        defaul_secret_key = (
            "django-insecure-_o$0y5g@1*uyrw0!3(0%wdv-ds5wp26yp*bko+q#y4b&y!50%6"
        )
        hosts = ["localhost", "127.0.0.1"]
        env_hosts = os.environ.get("ALLOWED_HOSTS")
        if env_hosts:
            hosts.append(env_hosts)
            # In case of containerized deployment to ECS/Fargate get the ip address of target group and add it to allowed hosts.
            # metadata_uri = os.environ.get('ECS_CONTAINER_METADATA_URI')
            # if metadata_uri:
            #     container_metadata = requests.get(metadata_uri).json()
            #     hosts.append(container_metadata['Networks'][0]['IPv4Addresses'][0])
        self.allowed_hosts      = hosts
        self.log_level          = os.environ.get("LOG_LEVEL", logging.INFO)
        self.oidc_config        = os.environ.get("OIDC_CONFIG")
        self.metrics_env        = os.environ.get("METRICS_ENV_NAME")
        self.db_username        = os.environ.get("POSTGRES_USER")
        self.db_password        = os.environ.get("POSTGRES_PASSWORD")
        self.db_name            = os.environ.get("POSTGRES_DB_NAME")
        self.db_host            = os.environ.get("POSTGRES_DB_HOST")
        self.db_port            = os.environ.get("POSTGRES_DB_PORT", "5432")
        self.cors_allow_origins = os.environ.get("CORS_ALLOW_ALL_ORIGINS", True)
        self.cors_allow_headers = os.environ.get(
            "CORS_ALLOW_HEADERS", default_cors_headers
        )
        self.debug = os.environ.get("API_DEBUG", True)
        self.secret_key = os.environ.get("SECRET_KEY", defaul_secret_key)

        # Log basic environment variables except db related for security reasons.
        logger.info("============== Environment Variables ================")
        logger.info(f"Allowed Hosts         : {self.allowed_hosts}")
        logger.info(f"Log Level             : {self.log_level}")
        logger.info(f"OIDC Config           : {self.oidc_config}")
        logger.info(f"Metrics Env           : {self.metrics_env}")
        logger.info(f"Cors allow origin     : {self.cors_allow_origins}")
        logger.info(f"Cors allow headers    : {self.cors_allow_headers}")
        logger.info(f"Debug                 : {self.debug}")
        logger.info("============== End Environment Variables ================")

    def get_allowed_hosts(self):
        return self.allowed_hosts

    def get_log_level(self):
        return self.log_level

    def get_oidc_config(self):
        return self.oidc_config

    def get_metrics_env(self):
        return self.metrics_env

    def get_db_username(self):
        return self.db_username

    def get_db_password(self):
        return self.db_password

    def get_db_name(self):
        return self.db_name

    def get_db_host(self):
        return self.db_host

    def get_db_port(self):
        return self.db_port

    def get_cors_allow_origins(self):
        return self.cors_allow_origins

    def get_cors_allow_headers(self):
        return self.cors_allow_headers

    def get_debug(self):
        return self.debug

    def get_secret_key(self):
        return self.secret_key
