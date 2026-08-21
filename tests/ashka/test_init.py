from os import environ
from subprocess import run
from sys import executable


def test_before_dishka():
    result = run(
        [executable, "-c", "import ashka"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.stdout == result.stderr == ""


def test_after_dishka():
    result = run(
        [executable, "-c", "import dishka; import ashka"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert "Make sure" in result.stderr


def test_after_dishka_with_no_warning():
    child_environment = environ.copy()
    child_environment["ASHKA_DISABLE_IMPORT_WARNING"] = "1"
    result = run(
        [executable, "-c", "import dishka; import ashka"],
        capture_output=True,
        text=True,
        env=child_environment,
        check=False,
    )

    assert result.stdout == result.stderr == ""
