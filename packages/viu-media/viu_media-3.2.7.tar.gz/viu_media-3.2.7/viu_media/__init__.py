import sys

if sys.version_info < (3, 10):
    raise ImportError(
        "You are using an unsupported version of Python. Only Python versions 3.10 and above are supported by Viu"
    )  # noqa: F541


def Cli():
    from .cli import run_cli

    run_cli()
