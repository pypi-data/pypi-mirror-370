import os
import logging
from pathlib import Path
from dataclasses import field, dataclass
from functools import cached_property
from typing import TypedDict, Literal, Optional

import istari_digital_core

from istari_digital_client.env import env_bool, env_int, env_str, env_cache_root

BearerAuthSetting = TypedDict(
    "BearerAuthSetting",
    {
        "type": Literal["bearer"],
        "in": Literal["header"],
        "key": Literal["Authorization"],
        "value": str,
    },
)

AuthSettings = TypedDict(
    "AuthSettings",
    {
        "RequestAuthenticator": BearerAuthSetting,
    },
    total=False,
)


@dataclass
class Configuration:
    """
    Client configuration for the Istari Digital SDK.

    This class provides runtime configuration options for the SDK, including registry
    connection settings, retry policies, filesystem cache behavior, logging options,
    and multipart upload settings. Values are loaded from environment variables and
    can be overridden at runtime.

    Most configuration values are optional. Defaults are applied via helper functions
    that read from environment variables with appropriate fallbacks.
    """

    registry_url: Optional[str] = field(
        default_factory=env_str("ISTARI_REGISTRY_URL", default=None)
    )
    registry_auth_token: Optional[str] = field(
        default_factory=env_str("ISTARI_REGISTRY_AUTH_TOKEN")
    )
    http_request_timeout_secs: Optional[int] = field(
        default_factory=env_int("ISTARI_CLIENT_HTTP_REQUEST_TIMEOUT_SECS"),
    )
    # === Retry config fields ===
    retry_enabled: Optional[bool] = field(
        default_factory=env_bool("ISTARI_CLIENT_RETRY_ENABLED", default=True)
    )
    retry_max_attempts: Optional[int] = field(
        default_factory=env_int("ISTARI_CLIENT_RETRY_MAX_ATTEMPTS")
    )
    retry_min_interval_millis: Optional[int] = field(
        default_factory=env_int("ISTARI_CLIENT_RETRY_MIN_INTERVAL_MILLIS")
    )
    retry_max_interval_millis: Optional[int] = field(
        default_factory=env_int("ISTARI_CLIENT_RETRY_MAX_INTERVAL_MILLIS")
    )
    # === Filesystem cache config fields ===
    filesystem_cache_enabled: Optional[bool] = field(
        default_factory=env_bool("ISTARI_CLIENT_FILESYSTEM_CACHE_ENABLED", default=True)
    )
    filesystem_cache_root: Path = field(
        default_factory=env_cache_root("ISTARI_CLIENT_FILESYSTEM_CACHE_ROOT")
    )
    filesystem_cache_clean_on_exit: Optional[bool] = field(
        default_factory=env_bool(
            "ISTARI_CLIENT_FILESYSTEM_CACHE_CLEAN_BEFORE_EXIT", default=True
        )
    )
    retry_jitter_enabled: Optional[bool] = field(
        default_factory=env_bool("ISTARI_CLIENT_RETRY_JITTER_ENABLED", default=True)
    )
    # === Multipart upload config fields ===
    multipart_chunksize: Optional[int] = field(
        default_factory=env_int("ISTARI_CLIENT_MULTIPART_CHUNKSIZE")
    )
    multipart_threshold: Optional[int] = field(
        default_factory=env_int("ISTARI_CLIENT_MULTIPART_THRESHOLD")
    )

    # === Logging config fields ===
    log_level: Optional[str] = field(
        default_factory=env_str("ISTARI_CLIENT_LOG_LEVEL", default="INFO")
    )
    log_to_file: Optional[bool] = field(
        default_factory=env_bool("ISTARI_CLIENT_LOG_TO_FILE", default=False)
    )
    log_file_path: Optional[str] = field(
        default_factory=env_str("ISTARI_CLIENT_LOG_FILE_PATH", default=None)
    )

    # === Date and time formats ===
    datetime_format: str = field(init=False, default="%Y-%m-%dT%H:%M:%S.%f%z")
    date_format: str = field(init=False, default="%Y-%m-%d")

    def __post_init__(self) -> None:
        os.environ["ISTARI_REGISTRY_URL"] = self.registry_url or ""
        os.environ["ISTARI_REGISTRY_AUTH_TOKEN"] = self.registry_auth_token or ""

        self._configure_logging()

    def _configure_logging(self) -> None:
        """Configures logging based on the configuration settings."""
        log_level_str = (self.log_level or "INFO").upper()
        log_level = getattr(logging, log_level_str, logging.INFO)

        if not isinstance(log_level, int):
            raise ValueError(f"Invalid log level: {self.log_level}")

        logger = logging.getLogger("istari-digital-client")
        logger.setLevel(log_level)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        handlers: list[logging.Handler] = []

        if self.log_to_file:
            if not self.log_file_path:
                raise ConfigurationError(
                    "ISTARI_CLIENT_LOG_FILE_PATH must be set when ISTARI_CLIENT_LOG_TO_FILE=true"
                )

            log_dir = Path(self.log_file_path).parent
            if not log_dir.exists():
                raise ConfigurationError(
                    f"Directory does not exist for log file: {log_dir}"
                )

            file_handler = logging.FileHandler(self.log_file_path)
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        handlers.append(stream_handler)

        for handler in handlers:
            logger.addHandler(handler)

        logger.propagate = False

        logger.info("Logging configured with level: %s", self.log_level)

    def auth_settings(self) -> AuthSettings:
        """Gets Auth Settings dict for api client.

        :return: The Auth Settings information dict.
        """
        auth: AuthSettings = {}
        if self.registry_auth_token is not None:
            auth["RequestAuthenticator"] = {
                "type": "bearer",
                "in": "header",
                "key": "Authorization",
                "value": "Bearer " + self.registry_auth_token,
            }
        return auth

    @classmethod
    def from_native_configuration(
        cls: type["Configuration"], native: istari_digital_core.Configuration
    ) -> "Configuration":
        """
        Create a `Configuration` instance from a native core configuration.

        This utility method bridges from an `istari_digital_core.Configuration` object to the
        SDK's configuration format.

        :param native: Core configuration object from the istari_digital_core package.
        :type native: istari_digital_core.Configuration
        """

        return Configuration(
            registry_url=native.registry_url,
            registry_auth_token=native.registry_auth_token,
            retry_enabled=native.retry_enabled,  # type: ignore[attr-defined]
            retry_max_attempts=native.retry_max_attempts,  # type: ignore[attr-defined]
            retry_min_interval_millis=native.retry_min_interval_millis,  # type: ignore[attr-defined]
            retry_max_interval_millis=native.retry_max_interval_millis,  # type: ignore[attr-defined]
            retry_jitter_enabled=native.retry_jitter_enabled,
            multipart_chunksize=native.multipart_chunksize,
            multipart_threshold=native.multipart_threshold,
        )

    @cached_property
    def native_configuration(self) -> istari_digital_core.Configuration:
        """
        Convert this SDK configuration to an `istari_digital_core.Configuration` object.

        Useful when interoperating with lower-level APIs that expect a core-native config format.
        """

        return istari_digital_core.Configuration(
            registry_url=self.registry_url,
            registry_auth_token=self.registry_auth_token,
            retry_enabled=self.retry_enabled,  # type: ignore[attr-defined]
            retry_max_attempts=self.retry_max_attempts,  # type: ignore[attr-defined]
            retry_min_interval_millis=self.retry_min_interval_millis,  # type: ignore[attr-defined]
            retry_max_interval_millis=self.retry_max_interval_millis,  # type: ignore[attr-defined]
            retry_jitter_enabled=self.retry_jitter_enabled,
            multipart_chunksize=self.multipart_chunksize,
            multipart_threshold=self.multipart_threshold,
        )


class ConfigurationError(ValueError):
    pass
