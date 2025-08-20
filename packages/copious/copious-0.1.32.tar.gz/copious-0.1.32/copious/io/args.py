from typing import Sequence, Any
import argparse

class KeyValueAction(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Sequence[Any],
        option_string: str = None,
    ) -> None:
        setattr(namespace, self.dest, {})
        for value in values:
            parts = value.split("=")
            if len(parts) != 2:
                raise argparse.ArgumentError(self, f"Invalid key-value pair: {value}. A key and value must be separated by an '='.")
            key, value = parts
            getattr(namespace, self.dest)[key] = value


class TypeAction(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: str = None,
    ) -> None:
        _type_mapping = {"int": int, "float": float, "str": str}
        if values not in _type_mapping:
            parser.error(f"Invalid type: {values}. Choose from 'int', 'float', 'str'.")
        setattr(namespace, self.dest, _type_mapping[values])


def declare_vars_as_global(**kwargs) -> None:
    for k, v in kwargs.items():
        globals()[k] = v


def g(var_name: str) -> Any:
    return globals()[var_name]


__all__ = ["KeyValueAction", "TypeAction", "declare_vars_as_global", "g"]
