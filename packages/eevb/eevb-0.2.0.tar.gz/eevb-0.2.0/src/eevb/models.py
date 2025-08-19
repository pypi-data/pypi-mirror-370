from typing import List

from pydantic import BaseModel, Field


class EmbeddedItems(BaseModel):
    default_folder: List[str] = Field(default_factory=list, alias="DefaultFolder")
    system_folder: List[str] = Field(default_factory=list, alias="SystemFolder")
    windows_folder: List[str] = Field(default_factory=list, alias="WindowsFolder")
    my_documents_folder: List[str] = Field(default_factory=list, alias="MyDocumentsFolder")
    program_files_folder: List[str] = Field(default_factory=list, alias="ProgramFilesFolder")
    program_files_common_folder: List[str] = Field(default_factory=list, alias="ProgramFiles,CommonFolder")
    all_users_documents_folder: List[str] = Field(default_factory=list, alias="AllUsers,DocumentsFolder")
    my_pictures_folder: List[str] = Field(default_factory=list, alias="MyPicturesFolder")
    history_folder: List[str] = Field(default_factory=list, alias="HistoryFolder")
    cookies_folder: List[str] = Field(default_factory=list, alias="CookiesFolder")
    internet_cache_folder: List[str] = Field(default_factory=list, alias="InternetCacheFolder")
    application_data_folder: List[str] = Field(default_factory=list, alias="ApplicationDataFolder")
    temp_folder: List[str] = Field(default_factory=list, alias="TempFolder")
    all_users_application_data_folder: List[str] = Field(default_factory=list, alias="AllUsers,ApplicationDataFolder")
    local_application_data_folder: List[str] = Field(default_factory=list, alias="Local,ApplicationDataFolder")
    system_drive: List[str] = Field(default_factory=list, alias="SystemDrive")
    user_profile_folder: List[str] = Field(default_factory=list, alias="UserProfileFolder")

    class Config:
        populate_by_name = True
        validate_by_name = True


class FileOptions(BaseModel):
    delete_on_exit: bool = Field(default=False, description="Delete extracted files on exit")
    compress: bool = Field(default=False, description="Compress embedded files")
    items: EmbeddedItems


class EVBConfig(BaseModel):
    input_path: str = Field(alias="input")
    output_path: str = Field(alias="output")
    files: FileOptions

    class Config:
        populate_by_name = True
        validate_by_name = True
