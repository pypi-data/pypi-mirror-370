import argparse
import sys
import pytest

from copious.io.args import KeyValueAction, TypeAction


def test_key_value_action():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyvalue", nargs="+", action=KeyValueAction)
    args = parser.parse_args(["--keyvalue", "key1=val1", "key2=val2"])

    assert args.keyvalue == {"key1": "val1", "key2": "val2"}, "The KeyValueAction did not parse the arguments correctly"


def test_key_value_action_with_invalid_input():
    if sys.version_info.major == 3 and sys.version_info.minor > 8:
        parser = argparse.ArgumentParser(exit_on_error=False)
        parser.add_argument("--keyvalue", nargs="+", action=KeyValueAction)

        with pytest.raises(argparse.ArgumentError):
            args = parser.parse_args(["--keyvalue", "key1val1"])


def test_type_action_int():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", action=TypeAction)
    args = parser.parse_args(["--type", "int"])
    assert args.type == int


def test_type_action_float():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", action=TypeAction)
    args = parser.parse_args(["--type", "float"])
    assert args.type == float


def test_type_action_str():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", action=TypeAction)
    args = parser.parse_args(["--type", "str"])
    assert args.type == str


def test_type_action_invalid():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", action=TypeAction)
    with pytest.raises(SystemExit):  # argparse calls sys.exit() on error
        parser.parse_args(["--type", "invalid"])


def test_type_action_no_value():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", action=TypeAction)
    with pytest.raises(SystemExit):  # argparse calls sys.exit() on error
        parser.parse_args(["--type"])
