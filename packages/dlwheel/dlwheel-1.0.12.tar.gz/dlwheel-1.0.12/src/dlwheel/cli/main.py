import argparse
import importlib
import pkgutil
import inspect
from dlwheel.cli import commands


def main():
    parser = argparse.ArgumentParser(prog="dlwheel")
    subparsers = parser.add_subparsers(dest="command")

    for _, module_name, _ in pkgutil.iter_modules(commands.__path__):
        module = importlib.import_module(f"dlwheel.cli.commands.{module_name}")
        if hasattr(module, "add_subparser") and inspect.isfunction(
            module.add_subparser
        ):
            module.add_subparser(subparsers)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
