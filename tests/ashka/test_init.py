from os import environ
from subprocess import run
from sys import executable


def test_before_dishka():
    result = run(
        [executable, "-c", "import ashka; ashka.activate()"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.stdout == result.stderr == ""


def test_after_dishka():
    result = run(
        [executable, "-c", "import dishka; import ashka; ashka.activate()"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert "Make sure" in result.stderr


def test_after_dishka_with_no_warning():
    child_environment = environ.copy()
    child_environment["ASHKA_DISABLE_IMPORT_WARNING"] = "1"
    result = run(
        [executable, "-c", "import dishka; import ashka; ashka.activate()"],
        capture_output=True,
        text=True,
        env=child_environment,
        check=False,
    )

    assert result.stdout == result.stderr == ""


def test_no_lifecycle():
    code = """
from importlib import util

real_find_spec = util.find_spec


def find_spec(name, *args, **kwargs):
    if name == "ashka_lifecycle":
        return None
    return real_find_spec(name, *args, **kwargs)


util.find_spec = find_spec

import ashka

assert not hasattr(ashka, "__all__")
"""
    result = run(
        [executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
