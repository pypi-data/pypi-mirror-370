from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union

from pydantic import BaseModel, Field
from beanie import PydanticObjectId


class FileType(str, Enum):
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    FOLDER = "folder"
    OTHER = "other"


class BlobStorageBase(BaseModel):
    file_name: str = Field(..., description="Name of the file")
    file_type: FileType = Field(..., description="Type of the file")
    mime_type: str = Field(..., description="MIME type of the file")
    file_size: int = Field(..., description="Size of the file in bytes")
    storage_path: str = Field(..., description="Path to the file in storage")
    file_metadata: Dict[str, Any] = {}
    is_public: bool = Field(
        default=True, description="Whether the file is publicly accessible"
    )
    expires_at: Optional[datetime] = Field(None, description="When the file expires")
    verification_id: Optional[Union[str, PydanticObjectId, int]] = Field(None, description="ID of the file owner (can be str, ObjectId, or int)")
    container_name: Optional[str] = Field(None, description="Custom container name for the file")
    is_folder: bool = Field(default=False, description="Whether the file is a folder")

    @property
    def parent_path(self) -> str:
        """Get the parent path from storage_path."""
        if not self.storage_path or "/" not in self.storage_path:
            return ""
        return "/".join(self.storage_path.split("/")[:-1])


class BlobStorageCreate(BaseModel):
    file_name: str = Field(..., description="Name of the file")
    file_type: FileType = Field(..., description="Type of the file")
    mime_type: str = Field(..., description="MIME type of the file")
    file_size: int = Field(..., description="Size of the file in bytes")
    storage_path: str = Field(..., description="Path to the file in storage")
    file_metadata: Dict = Field(
        default={}, description="Additional metadata for the file"
    )
    is_public: bool = Field(
        default=True, description="Whether the file is publicly accessible"
    )
    expires_at: Optional[datetime] = Field(None, description="When the file expires")
    verification_id: Optional[Union[str, PydanticObjectId, int]] = Field(None, description="ID of the file owner (can be str, ObjectId, or int)")
    container_name: str = Field(..., description="Custom container name for the file")
    is_folder: bool = Field(default=False, description="Whether the file is a folder")
    parent_path: str = Field(default="", description="Parent path of the file")


class BlobStorageUpdate(BaseModel):
    file_metadata: Optional[Dict] = None
    is_public: Optional[bool] = None


class BlobStorage(BlobStorageBase):
    id: str = Field(..., description="The MongoDB document ID", validation_alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class BlobStorageResponse(BlobStorage):
    """Response model for blob storage with URL and additional metadata."""

    url: str
    last_modified: datetime
    etag: str
    content_length: int
    content_type: str

    class Config:
        from_attributes = True


class MultipleBlobStorageResponse(BaseModel):
    """Response model for multiple file uploads."""

    files: List[BlobStorage]
    total_files: int
    total_size: int
    success_count: int
    failed_count: int
    failed_files: List[Dict[str, str]] = Field(default_factory=list)

    class Config:
        from_attributes = True


class FileUploadRequest(BaseModel):
    expires_at: Optional[datetime] = Field(None, description="When the file expires")
    file_metadata: Optional[Dict] = Field(None, description="Additional metadata for the file")
    is_public: bool = Field(default=True, description="Whether the file is publicly accessible")
    container_name: Optional[str] = Field(None, description="Custom container name for the file")


class FileUploadResponse(BaseModel):
    file_id: str = Field(..., description="The id of the file", alias="id")
    file_name: str = Field(..., description="The name of the file")
    file_type: FileType = Field(..., description="The type of the file")
    mime_type: str = Field(..., description="The mime type of the file")

    class Config:
        populate_by_name = True


class RequestData(BaseModel):
    expires_at: Optional[datetime] = Field(None, description="When the file expires")
    file_metadata: Dict = Field(default={}, description="Additional metadata for the file")
    is_public: bool = Field(default=True, description="Whether the file is publicly accessible")
    container_name: Optional[str] = Field(None, description="Custom container name for the file")
    storage_path: Optional[str] = Field(None, description="Path to the file in storage")
    custom_filename: Optional[str] = Field(None, description="Custom filename to use instead of the original filename")
    timestamp_required: bool = Field(default=True, description="Whether to add timestamp prefix to filename")
    verification_folder: bool = Field(default=True, description="Whether to store files in verification-specific folder structure")
    is_replace: bool = Field(default=False, description="Whether to replace the file if it already exists")


class CreateFolderRequest(BaseModel):
    folder_name: str
    parent_path: str = ""
    is_public: bool = True
    container_name: Optional[str] = None
    metadata: Optional[dict] = None
    timestamp_required: bool = Field(default=True, description="Whether to add timestamp prefix to folder name")
    verification_folder: bool = Field(default=True, description="Whether to store folder in verification-specific folder structure")
