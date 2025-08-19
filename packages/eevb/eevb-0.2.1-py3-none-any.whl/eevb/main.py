import argparse
import json
import sys
import tempfile
from pathlib import Path

try:

    from .core import execute_evb, generate_evb_config_xml
    from .globals import Global
    from .models import EmbeddedItems, EVBConfig, FileOptions
except ImportError:
    from core import execute_evb, generate_evb_config_xml  # type: ignore
    from globals import Global  # type: ignore
    from models import EmbeddedItems, EVBConfig, FileOptions  # type: ignore


def init_config(path: Path) -> None:
    if path.exists():
        choice = input(f"{path} already exists. Overwrite? (y/N): ").strip().lower()
        if choice != "y":
            print("Initialization cancelled.")
            return
    path.write_text(json.dumps(Global.TEMPLATE_CONFIG, indent=2), encoding="utf-8")
    print(f"Template configuration created at {path}")


def build_from_config(evb_config: EVBConfig):
    try:
        evb_xml = generate_evb_config_xml(evb_config)
    except Exception as e:
        print(f"[ERROR] Failed to build XML: {e}")
        return
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".evb", encoding="utf-8") as temp_file:
        temp_file.write(evb_xml)
        evb_temp_file = Path(temp_file.name)
    try:
        execute_evb(str(evb_temp_file))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"[ERROR] Execution failed: {e}")
    finally:
        evb_temp_file.unlink(missing_ok=True)


def main() -> None:

    # If the first argument is a JSON file, automatically insert the build command
    argv = sys.argv[1:]
    if argv and argv[0].lower().endswith(".json"):
        argv = ["build"] + argv

    parser = argparse.ArgumentParser(description="Easy Enigma VirtualBox builder")
    subparsers = parser.add_subparsers(dest="command")

    parser_init = subparsers.add_parser("init", help="Create a template eevb.json")
    parser_init.add_argument("--output", default="eevb.json", help="Path to configuration file (default: eevb.json)")

    parser_quick = subparsers.add_parser("quick", help="Quick build without config file")
    parser_quick.add_argument("-i", "--input", required=True, help="Input exe file")
    parser_quick.add_argument("-o", "--output", required=True, help="Output exe file")
    parser_quick.add_argument("-c", "--compress", action="store_true", help="Compress files")
    parser_quick.add_argument("-d", "--delete_on_exit", action="store_true", help="Delete extracted files on exit")
    parser_quick.add_argument("items", nargs="*", help="Files or folders to include (DefaultFolder)")

    parser_build = subparsers.add_parser("build", help="Build with configuration")
    parser_build.add_argument(
        "config", nargs="?", default="eevb.json", help="Path to configuration file (default: eevb.json)"
    )

    args = parser.parse_args(argv)

    if args.command is None:
        args.command = "build"
        args.config = "eevb.json"

    if args.command == "init":
        init_config(Path(args.output))
        return

    if args.command == "quick":
        _items = EmbeddedItems(DefaultFolder=args.items)
        _files = FileOptions(delete_on_exit=args.delete_on_exit, compress=args.compress, items=_items)
        _config = EVBConfig(input=args.input, output=args.output, files=_files)
        build_from_config(_config)
        return

    if args.command == "build":
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"[ERROR] Configuration file not found: {config_path}")
            return

        Global.BASE_PATH = config_path.parent

        try:
            evb_config = EVBConfig.model_validate_json(config_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[ERROR] Failed to read configuration: {e}")
            return

        build_from_config(evb_config)
