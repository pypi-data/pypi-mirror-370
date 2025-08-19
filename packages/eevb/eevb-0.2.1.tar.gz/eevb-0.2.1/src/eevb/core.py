import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom

try:
    from .globals import Global
    from .models import EVBConfig
except ImportError:
    from globals import Global  # type: ignore
    from models import EVBConfig  # type: ignore


def execute_evb(*args: str) -> None:
    try:
        subprocess.run([str(Global.EVB_EXECUTABLE), *args], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Execution failed with error code {e.returncode}")


def generate_evb_config_xml(evb_config: EVBConfig) -> str:
    root = ET.Element("__EasyEnigmaVirtualBox__")

    ET.SubElement(root, "InputFile").text = str(Global.resolve_path(Path(evb_config.input_path)))
    ET.SubElement(root, "OutputFile").text = str(Global.resolve_path(Path(evb_config.output_path)))

    files_section = ET.SubElement(root, "Files")
    ET.SubElement(files_section, "Enabled").text = "True"
    ET.SubElement(files_section, "DeleteExtractedOnExit").text = str(evb_config.files.delete_on_exit).title()
    ET.SubElement(files_section, "CompressFiles").text = str(evb_config.files.compress).title()

    embedded_files = ET.SubElement(files_section, "Files")
    _items = evb_config.files.items
    # region Add virtual folders
    _add_virtual_folder(embedded_files, "%DEFAULT FOLDER%", _items.default_folder)
    _add_virtual_folder(embedded_files, "%SYSTEM FOLDER%", _items.system_folder)
    _add_virtual_folder(embedded_files, "%WINDOWS FOLDER%", _items.windows_folder)
    _add_virtual_folder(embedded_files, "%My Documents FOLDER%", _items.my_documents_folder)
    _add_virtual_folder(embedded_files, "%Program Files FOLDER%", _items.program_files_folder)
    _add_virtual_folder(embedded_files, "%Program Files,Common FOLDER%", _items.program_files_common_folder)
    _add_virtual_folder(embedded_files, "%AllUsers,Documents FOLDER%", _items.all_users_documents_folder)
    _add_virtual_folder(embedded_files, "%My Pictures FOLDER%", _items.my_pictures_folder)
    _add_virtual_folder(embedded_files, "%History FOLDER%", _items.history_folder)
    _add_virtual_folder(embedded_files, "%Cookies FOLDER%", _items.cookies_folder)
    _add_virtual_folder(embedded_files, "%InternetCache FOLDER%", _items.internet_cache_folder)
    _add_virtual_folder(embedded_files, "%ApplicationData FOLDER%", _items.application_data_folder)
    _add_virtual_folder(embedded_files, "%Temp FOLDER%", _items.temp_folder)
    _add_virtual_folder(embedded_files, "%AllUsers,ApplicationData FOLDER%", _items.all_users_application_data_folder)
    _add_virtual_folder(embedded_files, "%Local,ApplicationData FOLDER%", _items.local_application_data_folder)
    _add_virtual_folder(embedded_files, "%SYSTEM DRIVE%", _items.system_drive)
    _add_virtual_folder(embedded_files, "%UserProfile FOLDER%", _items.user_profile_folder)
    # endregion

    xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    return minidom.parseString(xml_bytes).toprettyxml(indent="  ").replace("__EasyEnigmaVirtualBox__", "")


def _add_virtual_folder(parent: ET.Element, folder: str, items: list[str]) -> None:
    if not items:
        return
    element = ET.SubElement(parent, "File")
    ET.SubElement(element, "Type").text = "3"
    ET.SubElement(element, "Name").text = folder
    files = ET.SubElement(element, "Files")
    _add_file_entries(files, items, with_dir=False)


def _add_file_entries(parent: ET.Element, items: list[str], with_dir: bool = True) -> None:
    for item in items:
        add_dir = item.endswith("*") or with_dir
        item = item.rstrip("*").strip()
        path = Global.resolve_path(Path(item))

        if not path.exists():
            continue

        if path.is_file():
            parent.append(_create_file_element(path))
            continue

        if path.is_dir():
            if add_dir:
                element = _create_file_element(path)
                parent.append(element)
                _add_file_entries(element, [str(p) for p in path.iterdir()])
            else:
                _add_file_entries(parent, [str(p) for p in path.iterdir()])


def _create_file_element(path: Path) -> ET.Element:
    element = ET.Element("File")
    ET.SubElement(element, "Type").text = "3" if path.is_dir() else "2"
    ET.SubElement(element, "Name").text = path.name
    ET.SubElement(element, "File").text = str(path.resolve())
    return element
