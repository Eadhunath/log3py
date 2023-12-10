import importlib.resources as importlib_resources
import json
from logging import Formatter, LogRecord
from typing import Callable

from .resolvers import (
    DateTimeResolver,
    ExceptionResolver,
    LoggerResolver,
    MDCResolver,
    MessageResolver,
)

Resolver_resolve_Fn_Type = Callable[[LogRecord], dict | str | None]
DEFAULT_TEMPLATE: dict[str, Resolver_resolve_Fn_Type] = {
    "timestamp": DateTimeResolver().resolve,
    "message": MessageResolver().resolve,
}


def _load_from_json_file(file_path: str) -> dict[str, Resolver_resolve_Fn_Type]:
    """Load a json file from `file_path` and convert it to a template

    Args:
        file_path (str): file path to a json config file for the formatter

    Returns:
        dict[str, Callable[[LogRecord], dict|str|None]]: template for the Json formatter
    """
    config_json: dict = {}
    template = {}
    with open(file_path, "r", encoding="utf-8") as f:
        config_json = json.load(f)
    if not config_json:
        return {}

    for key in config_json.keys():
        value = config_json[key]
        if isinstance(value, str):
            template[key] = value
        if isinstance(value, dict):
            # find resolver
            template[key] = _get_matching_resolver_func(value)
    return template


def _get_matching_resolver_func(obj: dict) -> Resolver_resolve_Fn_Type:
    """Return a matching Callable reference of the appropriate Resolver.resolve()

    Args:
        obj (dict): the value for the key log key in the config file

    Raises:
        SyntaxError: if the config value does not have a "$resolver" key in it
        ModuleNotFoundError: if the "$resolver" is of an unknown type

    Returns:
        Resolver_resolve_Fn_Type: refence to the `resolve` function of a Resolver
    """
    if not obj.keys().__contains__("$resolver"):
        raise SyntaxError(f"Bad config {obj}")
    match obj["$resolver"]:
        case "timestamp":
            return DateTimeResolver(obj["format"]).resolve
        case "logger":
            return LoggerResolver(obj["field"]).resolve
        case "message":
            return MessageResolver().resolve
        case "mdc":
            return MDCResolver().resolve
        case "exception":
            return ExceptionResolver(obj["field"]).resolve
        case _:
            raise ModuleNotFoundError(f"Bad resolver {obj['$resolver']}")


class JsonFormatter(Formatter):
    """Formatting the output of the logger as a JSON"""

    def __init__(self, json_format_file_path=None, from_template=None):
        """Formatting the output of the logger as a JSON

        Args:
            json_format_file_path (str, optional): file path for a json template file. Defaults to None.
        """
        super().__init__()
        if json_format_file_path:
            try:
                self.template: dict[
                    str, Resolver_resolve_Fn_Type
                ] = _load_from_json_file(json_format_file_path)
            except Exception:
                RuntimeWarning("Could not configure Logger right")
                self.template: dict[
                    str, Resolver_resolve_Fn_Type
                ] = DEFAULT_TEMPLATE
        elif from_template == "pretty-good":
            format_file = (
                importlib_resources.files("log3py")
                / "resources"
                / "pretty_good_default_layout.json"
            )
            self.template = _load_from_json_file(format_file)
        else:
            self.template: dict[
                str, Resolver_resolve_Fn_Type
            ] = DEFAULT_TEMPLATE

    def format(self, record: LogRecord) -> str:
        """Use `self.template` to create a json string of `record`

        Template is expected to only have 2 types of values
            - str
                - In which case, simply use it
            - Callable (a Resolver.resolve function callable)
                - In which case, call the callable with the `record`

        Args:
            record (LogRecord): record to be formatted

        Returns:
            str: JSON string of the record to log, as per the template
        """

        log_data = {}
        for key, value in self.template.items():
            if isinstance(value, str):
                log_data[key] = value
            else:
                val = value(record)
                if val:
                    log_data[key] = val

        return json.dumps(log_data)
