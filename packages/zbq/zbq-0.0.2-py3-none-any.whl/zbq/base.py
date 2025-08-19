
from contextlib import contextmanager
from google.auth import default as get_google_credentials
from google.auth.exceptions import DefaultCredentialsError
import configparser
import os
import logging
from loguru import logger

# Custom exceptions
class ZbqError(Exception):
    """Base exception for zbq package"""

    pass


class ZbqAuthenticationError(ZbqError):
    """Authentication related errors"""

    pass


class ZbqConfigurationError(ZbqError):
    """Configuration related errors"""

    pass


class ZbqOperationError(ZbqError):
    """Operation related errors"""

    pass

class BaseClientManager:
    def __init__(self, project_id: str = "", log_level: str = "INFO"):
        # Suppress Google Cloud library logging early
        self._suppress_gcp_logging()
        
        self._project_id = project_id.strip() or self._get_default_project()
        self.logger = logger
        self._setup_logging(log_level)
        self._client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
        return False

    def _create_client(self):
        raise NotImplementedError("Subclasses must implement _create_client()")

    def _suppress_gcp_logging(self):
        """Suppress verbose logging from Google Cloud libraries"""
        # Set environment variables to suppress gRPC and absl logging
        os.environ.setdefault('GRPC_VERBOSITY', 'ERROR')
        os.environ.setdefault('GRPC_TRACE', '')
        os.environ.setdefault('ABSL_LOGGING_VERBOSITY', '1')  # WARNING level
        
        # Suppress specific Google Cloud loggers
        gcp_loggers = [
            'google.auth',
            'google.cloud',
            'google.api_core',
            'grpc',
            'absl'
        ]
        
        for logger_name in gcp_loggers:
            gcp_logger = logging.getLogger(logger_name)
            gcp_logger.setLevel(logging.WARNING)
            gcp_logger.propagate = False
            
        # Try to initialize absl logging early if available
        try:
            import absl.logging
            absl.logging.set_verbosity(absl.logging.WARNING)
            absl.logging.set_stderrthreshold(absl.logging.WARNING)
        except ImportError:
            pass  # absl not available, skip

    def _setup_logging(self, level: str = "INFO"):
        """Set up loguru logging for zbq operations"""
        logger.remove()  # Remove default handler
        logger.add(
            lambda msg: print(msg, end=""),
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>zbq</cyan> | <level>{message}</level>",
            level=level.upper()
        )


    @contextmanager
    def _fresh_client(self):
        """Context manager that provides a fresh client for each operation.

        This eliminates shared client state issues by creating a new client
        for each operation and ensuring proper cleanup.
        """
        temp_client = None
        try:
            if not self._check_adc():
                raise ZbqAuthenticationError(
                    "No Google Cloud credentials found. Run:\n"
                    "  gcloud auth application-default login\n"
                    "Or set the GOOGLE_APPLICATION_CREDENTIALS environment variable."
                )
            if not self.project_id:
                raise ZbqConfigurationError(
                    "No GCP project found. Set one via:\n"
                    "  gcloud config set project YOUR_PROJECT_ID\n"
                    "Or set manually: zclient.project_id = 'your-project'"
                )

            temp_client = self._create_client()
            yield temp_client

        finally:
            if temp_client:
                try:
                    temp_client.close()
                except Exception:
                    pass  # Ignore cleanup errors

    def _get_default_project(self):
        config_path = os.path.expanduser(
            "~/.config/gcloud/configurations/config_default"
        )
        if os.name == "nt":  # Windows
            config_path = os.path.expandvars(
                r"%APPDATA%\gcloud\configurations\config_default"
            )

        parser = configparser.ConfigParser()
        try:
            parser.read(config_path)
            project = parser.get("core", "project", fallback="")
            return project.strip()
        except Exception:
            return os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip()

        # Fallback to environment
        return os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip()

    @property
    def client(self):
        if self._client is None:
            self._init_client()
        return self._client

    def _check_adc(self) -> bool:
        try:
            creds, proj = get_google_credentials()
            return True
        except DefaultCredentialsError:
            return False

    @property
    def project_id(self):
        return self._project_id

    @project_id.setter
    def project_id(self, id: str):
        if not isinstance(id, str):
            raise ValueError("Project ID must be a string")
        if id != self._project_id:
            self._project_id = id

