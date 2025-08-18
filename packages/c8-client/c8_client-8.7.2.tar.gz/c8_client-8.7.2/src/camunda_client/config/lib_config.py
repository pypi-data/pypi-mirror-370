import logging
import threading
from typing import get_origin, get_args, Type

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

from camunda_client.config.models import ApiConfig, AuthConfig
from camunda_client.utils import JsonBaseModel

log = logging.getLogger(__name__)


class C8Config(JsonBaseModel):
    api: ApiConfig = Field(..., description="Camunda 8 API specific config")
    auth: AuthConfig = Field(..., alias="auth", description="Camunda API Authentication related configuration.")


class ConfigManager:
    _instance = None
    _lock = threading.Lock()
    _config: C8Config | None = None

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def init_config(self, config_dict: dict[str, any] = None, config: C8Config = None):
        load_dotenv()
        if self._config is not None:
            raise RuntimeError("Library configuration has already been initialized.")
        if config is not None:
            self._config = config
            log.info("Library configuration initialized successfully.")
            return
        try:
            # Pydantic automatically handles nested model validation and default merging
            self._config = C8Config(**config_dict)
            log.info("Library configuration initialized successfully.")
        except ValidationError as e:
            log.critical(f"Error initializing library configuration: {e}")
            raise

    def get_config(self) -> C8Config:
        if self._config is None:
            raise RuntimeError("Library configuration has not been initialized. Call initialize_config() first.")
        return self._config


def initialize_config(config_dict: dict[str, any] = None, config: C8Config = None):
    """
    Initializes the camunda_8_client configuration.

    This function should be called once at the start of the application.

    :param config: C8Config as alternative to config_dict
    :param config_dict: dictionary that contains the config properties
    :raises ValidationError: If the provided config_dict does not match the LibraryConfig schema.
    :raises RuntimeError: If the configuration is attempted to be initialized more than once.
    """
    ConfigManager().init_config(config_dict=config_dict, config=config)


def get_config() -> C8Config:
    """
    Retrieves the initialized camunda_8_client library configuration.
    :raises RuntimeError: If the configuration has not been initialized yet.
    :returns: C8Config: The initialized configuration object.
    """
    return ConfigManager().get_config()


def config_help_base(model: Type[BaseModel], indent: int = 0):
    """
    Prints a formatted help message for a Pydantic configuration model,
    including field names, types, descriptions, and default values.
    Handles nested Pydantic models recursively.
    """
    prefix = "  " * indent
    print(f"{prefix}--- {model.__name__} Configuration ---")
    if model.__doc__:
        print(f"{prefix}{model.__doc__.strip()}")
    print(f"{prefix}{'-' * (len(model.__name__) + 18)}")

    for field_name, field_info in model.model_fields.items():
        field_type = field_info.annotation
        description = field_info.description if field_info.description else "No description provided."

        # Determine if it's a required field
        required_str = "Required" if field_info.is_required else "Optional"

        # Get default value
        default_value_str = ""
        if not field_info.is_required:
            if field_info.default_factory:
                default_value_str = f" (Default: {field_info.default_factory()})"
            elif field_info.default is not None:
                default_value_str = f" (Default: {repr(field_info.default)})"
            else:
                default_value_str = " (No explicit default)"

        # Handle nested Pydantic models
        is_nested_model = False
        if isinstance(field_type, type) and issubclass(field_type, BaseModel):
            is_nested_model = True
        else:
            # Handle Optional[NestedModel] or List[NestedModel]
            origin = get_origin(field_type)
            args = get_args(field_type)
            if origin and args:
                for arg in args:
                    if isinstance(arg, type) and issubclass(arg, BaseModel):
                        is_nested_model = True
                        field_type = arg  # Use the inner model for recursion
                        break

        if is_nested_model:
            print(f"\n{prefix}  - {field_name}: {required_str}")
            config_help_base(field_type, indent + 1)
        else:
            print(f"{prefix}  - {field_name}: {field_type.__name__} ({required_str}){default_value_str}")
            print(f"{prefix}    Description: {description}")


def config_help():
    config_help_base(C8Config)
