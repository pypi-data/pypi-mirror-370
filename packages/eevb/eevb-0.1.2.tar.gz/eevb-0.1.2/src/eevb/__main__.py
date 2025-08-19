import sys

if sys.platform != "win32":
    raise RuntimeError("This tool only supports Windows platforms.")

import argparse
import json
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom

try:
    from .models import EVBConfig
except ImportError:
    from models import EVBConfig  # type: ignore

EVB_EXECUTABLE = Path(__file__).parent / "data" / "enigmavbconsole.exe"
if not EVB_EXECUTABLE.exists():
    raise FileNotFoundError("Missing required executable: enigmavbconsole.exe")

TEMPLATE_CONFIG = {
    "input": "path/to/your/input/file.exe",
    "output": "path/to/your/output/file.exe",
    "files": {
        "delete_on_exit": False,
        "compress": False,
        "items": {
            "DefaultFolder": ["folder/to/include", "or/file/to/include"],
            "SystemFolder": [],
            "WindowsFolder": [],
            "MyDocumentsFolder": [],
            "ProgramFilesFolder": [],
            "ProgramFiles,CommonFolder": [],
            "AllUsers,DocumentsFolder": [],
            "MyPicturesFolder": [],
            "HistoryFolder": [],
            "CookiesFolder": [],
            "InternetCacheFolder": [],
            "ApplicationDataFolder": [],
            "TempFolder": [],
            "AllUsers,ApplicationDataFolder": [],
            "Local,ApplicationDataFolder": [],
            "SystemDrive": [],
            "UserProfileFolder": [],
        },
    },
}


def execute_evb(*args: str) -> None:
    subprocess.run([str(EVB_EXECUTABLE), *args], check=True)


def generate_evb_config_xml(evb_config: EVBConfig) -> str:
    root = ET.Element("__EasyEnigmaVirtualBox__")

    ET.SubElement(root, "InputFile").text = str(Path(evb_config.input_path).resolve())
    ET.SubElement(root, "OutputFile").text = str(Path(evb_config.output_path).resolve())

    files_section = ET.SubElement(root, "Files")
    ET.SubElement(files_section, "Enabled").text = "True"
    ET.SubElement(files_section, "DeleteExtractedOnExit").text = str(evb_config.files.delete_on_exit).title()
    ET.SubElement(files_section, "CompressFiles").text = str(evb_config.files.compress).title()

    embedded_files = ET.SubElement(files_section, "Files")
    _items = evb_config.files.items
    add_virtual_folder(embedded_files, "%DEFAULT FOLDER%", _items.default_folder)
    add_virtual_folder(embedded_files, "%SYSTEM FOLDER%", _items.system_folder)
    add_virtual_folder(embedded_files, "%WINDOWS FOLDER%", _items.windows_folder)
    add_virtual_folder(embedded_files, "%My Documents FOLDER%", _items.my_documents_folder)
    add_virtual_folder(embedded_files, "%Program Files FOLDER%", _items.program_files_folder)
    add_virtual_folder(embedded_files, "%Program Files,Common FOLDER%", _items.program_files_common_folder)
    add_virtual_folder(embedded_files, "%AllUsers,Documents FOLDER%", _items.all_users_documents_folder)
    add_virtual_folder(embedded_files, "%My Pictures FOLDER%", _items.my_pictures_folder)
    add_virtual_folder(embedded_files, "%History FOLDER%", _items.history_folder)
    add_virtual_folder(embedded_files, "%Cookies FOLDER%", _items.cookies_folder)
    add_virtual_folder(embedded_files, "%InternetCache FOLDER%", _items.internet_cache_folder)
    add_virtual_folder(embedded_files, "%ApplicationData FOLDER%", _items.application_data_folder)
    add_virtual_folder(embedded_files, "%Temp FOLDER%", _items.temp_folder)
    add_virtual_folder(embedded_files, "%AllUsers,ApplicationData FOLDER%", _items.all_users_application_data_folder)
    add_virtual_folder(embedded_files, "%Local,ApplicationData FOLDER%", _items.local_application_data_folder)
    add_virtual_folder(embedded_files, "%SYSTEM DRIVE%", _items.system_drive)
    add_virtual_folder(embedded_files, "%UserProfile FOLDER%", _items.user_profile_folder)

    xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    return minidom.parseString(xml_bytes).toprettyxml(indent="  ").replace("__EasyEnigmaVirtualBox__", "")


def add_virtual_folder(parent: ET.Element, folder: str, items: list[str]) -> None:
    if not items:
        return
    element = ET.SubElement(parent, "File")
    ET.SubElement(element, "Type").text = "3"
    ET.SubElement(element, "Name").text = folder
    files = ET.SubElement(element, "Files")
    add_file_entries(files, items, include_self_dir=False)


def add_file_entries(parent: ET.Element, items: list[str], include_self_dir: bool = True) -> None:
    for item in items:
        path = Path(item)
        if not path.exists():
            continue

        if path.is_dir():
            if include_self_dir:
                element = create_file_element(path)
                parent.append(element)
                add_file_entries(element, [str(p) for p in path.iterdir()])
            else:
                add_file_entries(parent, [str(p) for p in path.iterdir()])
        else:
            parent.append(create_file_element(path))


def create_file_element(path: Path) -> ET.Element:
    element = ET.Element("File")
    ET.SubElement(element, "Type").text = "3" if path.is_dir() else "2"
    ET.SubElement(element, "Name").text = path.name
    ET.SubElement(element, "File").text = str(path.resolve())
    return element


def init_config(path: Path) -> None:
    if path.exists():
        choice = input(f"{path} already exists. Overwrite? (y/N): ").strip().lower()
        if choice != "y":
            print("Initialization cancelled.")
            return
    path.write_text(json.dumps(TEMPLATE_CONFIG, indent=2), encoding="utf-8")
    print(f"Template configuration created at {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Easy Enigma VirtualBox builder")
    subparsers = parser.add_subparsers(dest="command")

    parser_init = subparsers.add_parser("init", help="Create a template eevb.json")
    parser_init.add_argument("--output", default="eevb.json", help="Path to configuration file (default: eevb.json)")

    parser_build = subparsers.add_parser("build", help="Build with configuration")
    parser_build.add_argument(
        "config", nargs="?", default="eevb.json", help="Path to configuration file (default: eevb.json)"
    )

    args, extras = parser.parse_known_args()

    if args.command is None and extras:
        first_arg = extras[0]
        if first_arg.lower().endswith(".json"):
            args.command = "build"
            args.config = first_arg

    if args.command is None:
        args.command = "build"
        args.config = "eevb.json"

    if args.command == "init":
        init_config(Path(args.output))
        return

    if args.command == "build":
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"[ERROR] Configuration file not found: {config_path}")
            return

        try:
            evb_config = EVBConfig.model_validate_json(config_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[ERROR] Failed to read configuration: {e}")
            return

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
        except Exception as e:
            print(f"[ERROR] Execution failed: {e}")
        finally:
            evb_temp_file.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
