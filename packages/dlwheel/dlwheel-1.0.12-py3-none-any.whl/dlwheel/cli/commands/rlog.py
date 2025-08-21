from pathlib import Path
import os
from dlwheel.utils import get_timestamp_name


def rename_log(target_path, new_name=None):
    target = Path(target_path)
    if not target.exists() or not target.is_dir():
        print(f"{target} does not exist.")
        return
    if new_name is None:
        new_name = get_timestamp_name()
    new_dir = target.parent / new_name
    os.rename(target, new_dir)
    print(f"Renamed '{target}' to '{new_dir}'")


def rlog_cli(args):
    rename_log(args.target_path, args.new_name)


def add_subparser(subparsers):
    rlog_parser = subparsers.add_parser("rlog")
    rlog_parser.add_argument("target_path", nargs="?", default="log/_tmp")
    rlog_parser.add_argument("new_name", nargs="?", default=None)
    rlog_parser.set_defaults(func=rlog_cli)
