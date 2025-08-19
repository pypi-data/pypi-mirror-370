from pathlib import Path


class Global:
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

    BASE_PATH = Path(".")

    @classmethod
    def resolve_path(cls, path: Path) -> Path:
        if path.is_absolute():
            return path.resolve()
        return (cls.BASE_PATH / path).resolve()
