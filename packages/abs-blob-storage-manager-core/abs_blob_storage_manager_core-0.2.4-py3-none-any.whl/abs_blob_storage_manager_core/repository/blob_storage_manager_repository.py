import os
from datetime import datetime, timedelta, UTC
from typing import Any, Dict, List, Optional, Union
import uuid
import asyncio
import time

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import (
    BlobSasPermissions,
    BlobServiceClient,
    ContainerClient,
    generate_blob_sas,
)
from fastapi import UploadFile
from abs_exception_core.exceptions import ValidationError
from beanie import PydanticObjectId

from abs_nosql_repository_core.repository import BaseRepository
from abs_blob_storage_manager_core.schema.blob_storage_schema import (
    BlobStorage,
    BlobStorageCreate,
    BlobStorageResponse,
    FileType,
    RequestData,
    CreateFolderRequest,
)
from abs_blob_storage_manager_core.schema.blob_storage_model import BlobStorageDocument
from abs_nosql_repository_core.schema.base_schema import FilterSchema, ListFilter, LogicalOperator, FieldOperatorCondition, Operator, SortSchema, SortDirection
from abs_exception_core.exceptions import NotFoundError, ValidationError, InternalServerError, PermissionDeniedError
from abs_utils.logger import setup_logger

logger = setup_logger(__name__)

class BlobStorageRepository(BaseRepository):
    def __init__(
        self,
        connection_string: str,
        public_container: str,
        private_container: str
    ):
        super().__init__(BlobStorageDocument)
        self._connection_string = connection_string
        self._public_container = public_container
        self._private_container = private_container

        if not connection_string:
            raise ValidationError(
                detail="Azure Storage connection string is not properly configured"
            )
        
        if not public_container or not private_container:
            raise ValidationError(
                detail="Public and private containers are not properly configured"
            )

        self._blob_service_client = BlobServiceClient.from_connection_string(
            self._connection_string
        )

        try:
            if self._public_container:
                self._blob_service_client.create_container(
                    self._public_container, public_access="container"
                )

        except ResourceExistsError:
            container_client = self._blob_service_client.get_container_client(
                self._public_container
            )
            container_client.set_container_access_policy(
                public_access="container",
                signed_identifiers={},
            )

        try:
            if self._private_container:
                self._blob_service_client.create_container(
                    self._private_container, public_access=None
                )
        except ResourceExistsError:
            container_client = self._blob_service_client.get_container_client(
                self._private_container
            )
            container_client.set_container_access_policy(
                public_access=None,
                signed_identifiers={},
            )

        self._allowed_extensions = {
            FileType.DOCUMENT: {".pdf", ".doc", ".docx", ".txt", ".rtf"},
            FileType.IMAGE: {".jpg", ".jpeg", ".png", ".gif", ".webp"},
            FileType.VIDEO: {".mp4", ".avi", ".mov", ".wmv"},
            FileType.AUDIO: {".mp3", ".wav", ".ogg", ".m4a"},
            FileType.ARCHIVE: {".zip", ".rar", ".7z", ".tar", ".gz"},
        }

    def _get_default_container_name(self, is_public: bool) -> str:
        """
        Get the default container name based on visibility.

        Args:
            is_public: Whether the container should be public

        Returns:
            str: The default container name
        """
        return self._public_container if is_public else self._private_container

    def _create_or_configure_container(
        self, 
        container_client: ContainerClient, 
        container_name: str, 
        is_public: bool
    ) -> ContainerClient:
        """
        Create container if it doesn't exist or configure its access policy.

        Args:
            container_client: The container client
            container_name: Name of the container
            is_public: Whether the container should be public

        Returns:
            ContainerClient: The configured container client
        """
        public_access = "container" if is_public else None
        
        if not container_client.exists():
            container_client = self._blob_service_client.create_container(
                container_name, public_access=public_access
            )
        else:
            container_client.set_container_access_policy(
                public_access=public_access,
                signed_identifiers={},
            )
        return container_client

    def _get_container_client(
        self, container_name: str, is_public: bool = True
    ) -> ContainerClient:
        """Get the appropriate container client for the specified container."""
        try:
            container_client = self._blob_service_client.get_container_client(container_name)
            return self._create_or_configure_container(container_client, container_name, is_public)

        except Exception as e:
            raise InternalServerError(detail=str(e))

    def _get_file_type(self, filename: str) -> FileType:
        """
        Determine file type based on extension.

        Args:
            filename: Name of the file

        Returns:
            FileType: The determined file type (document, image, video, etc.)
        """
        ext = os.path.splitext(filename)[1].lower()
        for file_type, extensions in self._allowed_extensions.items():
            if ext in extensions:
                return file_type
        return FileType.OTHER

    def _get_mime_type(self, filename: str) -> str:
        """
        Get MIME type based on file extension.

        Args:
            filename: Name of the file

        Returns:
            str: The MIME type for the file
        """
        ext = os.path.splitext(filename)[1].lower()
        mime_types = {
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".txt": "text/plain",
            ".rtf": "application/rtf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".mp4": "video/mp4",
            ".avi": "video/x-msvideo",
            ".mov": "video/quicktime",
            ".wmv": "video/x-ms-wmv",
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".ogg": "audio/ogg",
            ".m4a": "audio/mp4",
            ".zip": "application/zip",
            ".rar": "application/x-rar-compressed",
            ".7z": "application/x-7z-compressed",
            ".tar": "application/x-tar",
            ".gz": "application/gzip",
        }
        return mime_types.get(ext, "application/octet-stream")

    def _resolve_final_filename(self, original_filename: str, custom_filename: Optional[str] = None) -> str:
        """
        Resolve the final filename to use, ensuring proper extension handling.
        
        Args:
            original_filename: Original filename from uploaded file
            custom_filename: Optional custom filename provided by user
            
        Returns:
            str: Final filename with proper extension
        """
        if not custom_filename:
            return original_filename
        
        # If custom filename has no extension, use the original file's extension
        if not os.path.splitext(custom_filename)[1]:
            original_ext = os.path.splitext(original_filename)[1]
            if original_ext:
                return f"{custom_filename}{original_ext}"
        
        return custom_filename

    def _generate_timestamped_filename(self, filename: str) -> str:
        """
        Generate a timestamped filename for blob storage.
        
        Args:
            filename: The filename to add timestamp to
            
        Returns:
            str: Timestamped filename
        """
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        return f"{timestamp}_{filename}"

    def _get_blob_path(self, filename: str, custom_filename: Optional[str] = None, timestamp_required: bool = True) -> str:
        """
        Generate a unique blob path for the file.

        Args:
            filename: Original filename
            custom_filename: Optional custom filename to use instead of the original
            timestamp_required: Whether to add timestamp prefix to filename

        Returns:
            str: A unique path for the blob (with timestamp if required)
        """
        final_filename = self._resolve_final_filename(filename, custom_filename)
        if timestamp_required:
            return self._generate_timestamped_filename(final_filename)
        else:
            return final_filename

    async def _check_duplicate_storage_path(
        self,
        storage_path: str,
        is_public: bool,
        container_name: str,
    ) -> bool:
        """
        Check if a file with the same storage path already exists.

        Args:
            storage_path: The storage path to check
            is_public: Whether the file is public
            container_name: Name of the container

        Returns:
            bool: True if duplicate exists, False otherwise
        """
        find_query = FilterSchema(
            operator=LogicalOperator.AND,
            conditions=[
                FieldOperatorCondition(
                    field="storage_path",
                    operator=Operator.LIKE,
                    value=storage_path
                ),
                FieldOperatorCondition(
                    field="is_public",
                    operator=Operator.EQ,
                    value=is_public
                ),
                FieldOperatorCondition(
                    field="container_name",
                    operator=Operator.EQ,
                    value=container_name
                )
            ]
        )
        
        db_records = await self.get_all(find=ListFilter(filters=find_query))
        founds = db_records.get("founds", [])
        return len(founds) > 0


    def _generate_sas_url(
        self,
        blob_client,
        is_public: bool,
        token_expiry: timedelta = timedelta(hours=1, minutes=0, seconds=0)
    ) -> str:
        """
        Generate a SAS URL for private files or return direct URL for public files.

        Args:
            blob_client: The Azure blob client
            is_public: Whether the file is public

        Returns:
            str: The URL to access the file (direct for public, SAS for private)
        """
        if is_public:
            return blob_client.url

        sas_token = generate_blob_sas(
            account_name=blob_client.account_name,
            container_name=blob_client.container_name,
            blob_name=blob_client.blob_name,
            account_key=self._blob_service_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(UTC) + token_expiry,
        )
        return f"{blob_client.url}?{sas_token}"

    def _get_verification_folder_path(self, verification_id: Optional[str]) -> str:
        """
        Get the verification account's folder path.

        Args:
            verification_id: ID of the verification account

        Returns:
            str: The verification account's folder path
        """
        return f"{verification_id}" if verification_id else ""

    def _get_folder_path(self, verification_id: Optional[str], folder_path: str = "", use_verification_folder: bool = True) -> str:
        """
        Get the full folder path, optionally including verification folder.

        Args:
            verification_id: ID of the verification account (None for anonymous access)
            folder_path: Optional subfolder path
            use_verification_folder: Whether to include verification folder in path

        Returns:
            str: The complete folder path
        """
        if use_verification_folder and verification_id:
            verification_folder = self._get_verification_folder_path(verification_id)
            if folder_path:
                return f"{verification_folder}/{folder_path.strip('/')}"
            return verification_folder
        else:
            return folder_path.strip('/') if folder_path else ""

    def _ensure_verification_folder_exists(self, container_client: ContainerClient, verification_id: Optional[Union[str, PydanticObjectId, int]], is_public: bool, container_name: str) -> None:
        """Ensure verification folder exists in the container."""
        if not verification_id:
            return
        
        verification_folder_path = self._get_verification_folder_path(str(verification_id))
        verification_folder_client = container_client.get_blob_client(f"{verification_folder_path}/.folder")
        
        if not verification_folder_client.exists():
            verification_folder_client.upload_blob(b"", overwrite=True)
            verification_folder_client.set_blob_metadata({
                "file_name": self._sanitize_metadata_value(str(verification_id)),
                "file_type": "folder",
                "mime_type": "application/x-directory",
                "file_size": "0",
                "verification_id": str(verification_id),
                "is_public": str(is_public),
                "container_name": container_name,
                "is_folder": "true",
            })


    async def _ensure_folder_path_exists(
        self,
        container_client: ContainerClient,
        verification_id: Optional[Union[str, PydanticObjectId, int]],
        storage_path: str,
        is_public: bool,
        container_name: str,
        use_verification_folder: bool = True,
    ) -> None:
        """Ensure all folders in the path exist in both storage and database."""
        path_parts = storage_path.strip('/').split('/')
        current_path = ""

        for part in path_parts:
            current_path = f"{current_path}/{part}" if current_path else part
            if use_verification_folder and verification_id:
                full_folder_path = self._get_folder_path(str(verification_id), current_path, use_verification_folder=True)
            else:
                full_folder_path = current_path
            folder_marker_path = f"{full_folder_path}/.folder"
            folder_client = container_client.get_blob_client(folder_marker_path)

            if not folder_client.exists():
                folder_client.upload_blob(b"", overwrite=True)
                folder_client.set_blob_metadata({
                    "file_name": self._sanitize_metadata_value(part),
                    "file_type": "folder",
                    "mime_type": "application/x-directory",
                    "file_size": "0",
                    "verification_id": str(verification_id) if verification_id else "",
                    "is_public": str(is_public),
                    "container_name": container_name,
                    "is_folder": "true",
                })

            # Create database records for all folders, including anonymous ones
            # Skip only verification root folders to avoid redundant records
            should_create_record = (
                not use_verification_folder or  # Always create when not using verification folders
                (verification_id and full_folder_path != str(verification_id)) or  # Create when verification folder is not root
                (not verification_id and use_verification_folder)  # Create when anonymous but verification_folder=True
            )
            
            if should_create_record:
                # Use consistent path format with trailing slash for folder records
                folder_storage_path = f"{full_folder_path}/"
                find_query = FilterSchema(
                    operator=LogicalOperator.AND,
                    conditions=[
                        FieldOperatorCondition(
                            field="storage_path",
                            operator=Operator.EQ,
                            value=folder_storage_path
                        ),
                        FieldOperatorCondition(
                            field="verification_id",
                            operator=Operator.EQ,
                            value=str(verification_id) if verification_id else ""
                        ),
                        FieldOperatorCondition(
                            field="is_public",
                            operator=Operator.EQ,
                            value=str(is_public)
                        )
                    ]
                )
                db_records = await self.get_all(find=ListFilter(filters=find_query))
                
                if not db_records["founds"]:
                    await self._create_blob_storage_record(
                        file_name=part,
                        file_type=FileType.FOLDER,
                        mime_type="application/x-directory",
                        file_size=0,
                        storage_path=folder_storage_path,
                        verification_id=verification_id,
                        is_public=is_public,
                        container_name=container_name,
                        metadata=None,
                        is_folder=True,
                    )

    async def get_by_id(self, id: str, verification_id: Optional[Union[str, PydanticObjectId, int]] = None, is_safe: bool = False) -> Optional[BlobStorage]:
        """
        Get a file by ID, ensuring user has access.

        Args:
            id: UUID of the file
            verification_id: ID of the requesting user (None for anonymous access)

        Returns:
            Optional[BlobStorage]: The file record if found and accessible

        Raises:
            PermissionDeniedError: If access is denied
        """
        file = await self.get_by_attr("id", id)

        if file:
            file_verification_id = file.get("verification_id")
            is_public = file.get("is_public", False)
            
            # If verification_id is None (anonymous access)
            if verification_id is None and file_verification_id:
                # Allow access only to public files when is_safe=True
                if not is_public or not is_safe:
                    raise PermissionDeniedError()
            # If verification_id is provided, check ownership
            elif file_verification_id is not None and str(file_verification_id) != str(verification_id):
                # User is not the owner, check if file is public and we're in safe mode
                if not is_public or not is_safe:
                    raise PermissionDeniedError()
                    
        return file

    async def _create_blob_storage_record(
        self,
        file_name: str,
        file_type: FileType,
        mime_type: str,
        file_size: int,
        storage_path: str,
        verification_id: Optional[Union[str, PydanticObjectId, int]],
        is_public: bool,
        container_name: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict] = None,
        is_folder: bool = False,
    ) -> BlobStorage:
        """
        Create a BlobStorage record in the database.

        Args:
            file_name: Name of the file or folder
            file_type: Type of the file (document, image, etc.)
            mime_type: MIME type of the file
            file_size: Size of the file in bytes
            storage_path: Full path in storage
            verification_id: ID of the owner
            is_public: Whether the file is public
            container_name: Optional custom container name
            expires_at: Optional expiration date
            metadata: Optional additional metadata
            is_folder: Whether this is a folder

        Returns:
            BlobStorage: The created database record
        """
        if container_name is None:
            container_name = self._public_container if is_public else self._private_container

        blob_data = BlobStorageCreate(
            file_name=file_name,
            file_type=file_type,
            mime_type=mime_type,
            file_size=file_size,
            storage_path=storage_path,
            expires_at=expires_at,
            verification_id=verification_id,
            is_public=is_public,
            container_name=container_name,
            file_metadata=metadata or {},
            is_folder=is_folder,
        )
        return await self.create(blob_data)

    def _sanitize_metadata_value(self, value: str) -> str:
        """
        Sanitize a metadata value to ensure it's Latin-1 encodable.
        
        Args:
            value: The metadata value to sanitize
            
        Returns:
            str: A Latin-1 safe version of the value
        """
        if not value:
            return value
            
        try:
            # Try to encode as Latin-1 - if it works, return as-is
            value.encode('latin-1')
            return value
        except UnicodeEncodeError:
            # Replace problematic characters with safe alternatives
            sanitized = (
                value.replace('\u2014', '-')  # em dash to hyphen
                .replace('\u2013', '-')       # en dash to hyphen  
                .replace('\u2019', "'")       # right single quotation mark to apostrophe
                .replace('\u2018', "'")       # left single quotation mark to apostrophe
                .replace('\u201C', '"')       # left double quotation mark to quote
                .replace('\u201D', '"')       # right double quotation mark to quote
                .replace('\u2026', '...')     # horizontal ellipsis to three dots
                .replace('\u00A0', ' ')       # non-breaking space to regular space
            )
            
            # As a final fallback, encode to latin-1 with 'replace' error handling
            # This will replace any remaining problematic characters with '?'
            try:
                return sanitized.encode('latin-1', errors='replace').decode('latin-1')
            except Exception:
                # Ultimate fallback - return a safe default
                return "sanitized_filename"

    def _set_blob_metadata(
        self,
        blob_client: Any,
        file_name: str,
        file_type: str,
        mime_type: str,
        file_size: int,
        verification_id: Optional[Union[str, PydanticObjectId, int]],
        is_public: bool,
        container_name: str,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict] = None,
        is_folder: bool = False,
    ) -> None:
        """
        Set metadata for a blob in Azure Storage.

        Args:
            blob_client: The Azure blob client
            file_name: Name of the file
            file_type: Type of the file
            mime_type: MIME type of the file
            file_size: Size of the file in bytes
            verification_id: ID of the owner
            is_public: Whether the file is public
            container_name: Name of the container
            expires_at: Optional expiration date
            metadata: Optional additional metadata
            is_folder: Whether this is a folder
        """
        # Sanitize the file_name to ensure Latin-1 compatibility
        sanitized_file_name = self._sanitize_metadata_value(file_name)
        
        blob_metadata = {
            "file_name": sanitized_file_name,
            "file_type": file_type,
            "mime_type": mime_type,
            "file_size": str(file_size),
            "verification_id": str(verification_id) if verification_id else "",
            "is_public": str(is_public),
            "container_name": container_name or "",
            "expires_at": expires_at.isoformat() if expires_at else None,
            "is_folder": str(is_folder).lower(),
        }
        
        # Sanitize additional metadata if provided
        if metadata:
            for key, value in metadata.items():
                if isinstance(value, str):
                    blob_metadata[key] = self._sanitize_metadata_value(value)
                else:
                    blob_metadata[key] = str(value)
        
        blob_client.set_blob_metadata(blob_metadata)

    async def _ensure_folder_exists(
        self,
        container_client: ContainerClient,
        folder_path: str,
        verification_id: Union[str, PydanticObjectId, int],
        is_public: bool,
        container_name: str,
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        Ensure a folder exists in both storage and database.

        Args:
            container_client: The Azure container client
            folder_path: Path of the folder
            verification_id: ID of the owner
            is_public: Whether the folder is public
            container_name: Name of the container
            metadata: Optional additional metadata

        Note:
            Creates the folder in both Azure Storage and the database if it doesn't exist
        """
        folder_marker_path = f"{folder_path}/.folder"
        folder_client = container_client.get_blob_client(folder_marker_path)

        if not folder_client.exists():
            folder_client.upload_blob(b"", overwrite=True)
            self._set_blob_metadata(
                blob_client=folder_client,
                file_name=os.path.basename(folder_path),
                file_type="folder",
                mime_type="application/x-directory",
                file_size=0,
                verification_id=verification_id,
                is_public=is_public,
                container_name=container_name,
                metadata=metadata,
                is_folder=True,
            )

            find_query = FilterSchema(
                operator=LogicalOperator.AND,
                conditions=[
                    FieldOperatorCondition(
                        field="storage_path",
                        operator=Operator.EQ,
                        value=folder_path
                    ),
                    FieldOperatorCondition(
                        field="verification_id",
                        operator=Operator.EQ,
                        value=str(verification_id)
                    ),
                    FieldOperatorCondition(
                        field="is_public",
                        operator=Operator.EQ,
                        value=str(is_public)
                    )
                ]
            )
            db_records = await self.get_all(find=ListFilter(filters=find_query))
            
            if not db_records["founds"] and folder_path != str(verification_id):
                await self._create_blob_storage_record(
                    file_name=os.path.basename(folder_path),
                    file_type=FileType.FOLDER,
                    mime_type="application/x-directory",
                    file_size=0,
                    storage_path=f"{folder_path}/",
                    verification_id=verification_id,
                    is_public=is_public,
                    container_name=container_name,
                    metadata=metadata,
                    is_folder=True,
                )

    async def _delete_blob_and_record(
        self,
        blob_path: str,
        container_client: ContainerClient,
    ) -> None:
        """
        Delete a blob and its database record.

        Args:
            blob_path: Path of the blob in storage
            container_client: The Azure container client

        Note:
            Silently handles errors to allow bulk operations to continue
        """
        try:
            blob_client = container_client.get_blob_client(blob_path)
            if blob_client.exists():
                blob_client.delete_blob()

        except Exception as e:
            logger.error(f"Error deleting blob and record {blob_path}: {str(e)}")

    async def _prepare_upload_environment(
        self,
        verification_id: Optional[Union[str, PydanticObjectId, int]],
        is_public: bool,
        container_name: Optional[str],
        storage_path: Optional[str],
        use_verification_folder: bool = True,
    ) -> tuple[ContainerClient, str, str]:
        """
        Prepare the upload environment by setting up container client and ensuring folders exist.

        Args:
            verification_id: ID of the verification account uploading files
            is_public: Whether files should be public
            container_name: Optional custom container name
            storage_path: Optional folder path to upload to
            use_verification_folder: Whether to use verification-specific folder structure

        Returns:
            tuple[ContainerClient, str, str]: Container client, container name, and verification folder path
        """
        if not container_name:
            container_name = self._get_default_container_name(is_public)
        
        container_client = self._get_container_client(container_name, is_public)

        verification_folder_path = ""
        if use_verification_folder and verification_id:
            verification_folder_path = self._get_verification_folder_path(str(verification_id))
            await self._ensure_folder_exists(
                container_client=container_client,
                folder_path=verification_folder_path,
                verification_id=verification_id,
                is_public=is_public,
                container_name=container_name,
            )

        if storage_path:
            await self._ensure_folder_path_exists(
                container_client=container_client,
                verification_id=verification_id,
                storage_path=storage_path,
                is_public=is_public,
                container_name=container_name,
                use_verification_folder=use_verification_folder,
            )

        return container_client, container_name, verification_folder_path

    async def _upload_single_file_to_storage(
        self,
        file: UploadFile,
        container_client: ContainerClient,
        verification_id: Optional[Union[str, PydanticObjectId, int]],
        is_public: bool,
        container_name: str,
        verification_folder_path: str,
        storage_path: Optional[str],
        expires_at: Optional[datetime],
        metadata: Optional[Dict],
        custom_filename: Optional[str] = None,
        timestamp_required: bool = True,
        is_replace: bool = False,
    ) -> tuple[BlobStorageCreate, str]:
        """
        Upload a single file to blob storage and prepare database record.
        
        Args:
            file: The file to upload
            container_client: The Azure container client
            verification_id: ID of the verification account uploading the file
            is_public: Whether the file should be public
            container_name: Name of the container
            verification_folder_path: Verification account's folder path (empty for public files)
            storage_path: Optional folder path to upload to
            expires_at: Optional expiration date
            metadata: Optional metadata
            custom_filename: Optional custom filename to use instead of the original
            timestamp_required: Whether to add timestamp prefix to filename
            
        Returns:
            tuple[BlobStorageCreate, str]: Database record data and full blob path
        """
        content = await file.read()
        
        # Determine the final filename to use for file type detection and storage
        final_filename = self._resolve_final_filename(file.filename, custom_filename)
        
        file_type = self._get_file_type(final_filename)
        mime_type = self._get_mime_type(final_filename)
        blob_path = self._get_blob_path(file.filename, custom_filename, timestamp_required)
        
        if verification_folder_path:
            full_blob_path = f"{verification_folder_path}/{storage_path}/{blob_path}" if storage_path else f"{verification_folder_path}/{blob_path}"
        else:
            full_blob_path = f"{storage_path}/{blob_path}" if storage_path else blob_path
        
        blob_client = container_client.get_blob_client(full_blob_path)
        blob_client.upload_blob(content, overwrite=True)

        self._set_blob_metadata(
            blob_client=blob_client,
            file_name=final_filename,
            file_type=file_type,
            mime_type=mime_type,
            file_size=len(content),
            verification_id=verification_id,
            is_public=is_public,
            container_name=container_name,
            expires_at=expires_at,
            metadata=metadata,
        )
        file_data = BlobStorageCreate(
            file_name=final_filename,
            file_type=file_type,
            mime_type=mime_type,
            file_size=len(content),
            storage_path=full_blob_path,
            expires_at=expires_at,
            verification_id=verification_id,
            is_public=is_public,
            container_name=container_name,
            file_metadata=metadata or {},
        )
        
        return file_data, full_blob_path

    async def upload_file(
        self,
        file: UploadFile,
        request_data: RequestData,
        verification_id: Optional[Union[str, PydanticObjectId, int]] = None,
    ) -> BlobStorage:
        """
        Upload a single file to blob storage and database.

        Args:
            file: The file to upload
            verification_id: ID of the user uploading the file
            request_data: JSON string containing upload parameters:
                - expires_at: Optional expiration date
                - file_metadata: Optional metadata
                - is_public: Whether the file should be public
                - container_name: Optional custom container name
                - storage_path: Optional folder path to upload to

        Returns:
            BlobStorage: The created database record

        Raises:
            HTTPException: If there's an error during upload
        """
        container_client, container_name, verification_folder_path = await self._prepare_upload_environment(
            verification_id, request_data.is_public, request_data.container_name, request_data.storage_path, request_data.verification_folder
        )

        file_data, full_blob_path = await self._upload_single_file_to_storage(
            file,
            container_client,
            verification_id,
            request_data.is_public,
            container_name,
            verification_folder_path,
            request_data.storage_path,
            request_data.expires_at,
            request_data.file_metadata,
            request_data.custom_filename,
            request_data.timestamp_required,
            request_data.is_replace,
        )
        if request_data.is_replace:
            get_file = await self.get_by_attr("verification_id", verification_id)
            if get_file:
                return await self.update(get_file["id"], file_data)
            else:
                return await self.create(file_data)
        else:
            return await self.create(file_data)

    async def get_file_url(
        self,
        file_id: str,
        verification_id: Optional[Union[str, PydanticObjectId, int]] = None,
        token_expiry: timedelta = timedelta(hours=1, minutes=0, seconds=0)
    ) -> str:
        """
        Get the URL for a file.

        Args:
            file_id: UUID of the file
            verification_id: ID of the requesting user

        Returns:
            str: The URL to access the file

        Raises:
            NotFoundError: If the file doesn't exist
        """
        blob = await self.get_by_id(file_id, verification_id, is_safe=True)
        if not blob:
            raise NotFoundError(detail=f"File with ID {file_id} not found")

        container_client = self._get_container_client(
            blob["container_name"], blob["is_public"]
        )

        blob_client = container_client.get_blob_client(blob["storage_path"])
        if not blob_client.exists():
            raise NotFoundError(detail=f"File {blob['storage_path']} not found in storage")

        return self._generate_sas_url(blob_client, blob["is_public"], token_expiry)

    async def get_file(self, file_id: str, verification_id: Optional[Union[str, PydanticObjectId, int]] = None) -> tuple[BlobStorage, Any]:
        """
        Get a file by ID with streaming download.

        Args:
            file_id: UUID of the file
            verification_id: ID of the requesting user

        Returns:
            tuple[BlobStorage, Any]: The file record and a streaming download object

        Raises:
            NotFoundError: If the file doesn't exist
        """
        blob = await self.get_by_id(file_id, verification_id, is_safe=True)
        if not blob:
            raise NotFoundError(detail=f"File with ID {file_id} not found")

        container_client = self._get_container_client(
            blob["container_name"], blob["is_public"]
        )

        blob_client = container_client.get_blob_client(blob["storage_path"])
        if not blob_client.exists():
            raise NotFoundError(detail=f"File {blob['storage_path']} not found in storage")

        download_stream = blob_client.download_blob()
        return blob, download_stream

    async def get_file_chunked(
        self,
        file_id: str,
        verification_id: Optional[Union[str, PydanticObjectId, int]] = None,
        chunk_size: int = 8192,
        start_byte: Optional[int] = None,
        end_byte: Optional[int] = None,
    ) -> tuple[BlobStorage, Any]:
        """
        Get a file by ID with chunked streaming download for large files.

        Args:
            file_id: UUID of the file
            verification_id: ID of the requesting user
            chunk_size: Size of chunks to read (default: 8KB)
            start_byte: Optional start byte for range requests
            end_byte: Optional end byte for range requests

        Returns:
            tuple[BlobStorage, Any]: The file record and a chunked streaming download object

        Raises:
            NotFoundError: If the file doesn't exist
        """
        blob = await self.get_by_id(file_id, verification_id, is_safe=True)
        if not blob:
            raise NotFoundError(detail=f"File with ID {file_id} not found")

        container_client = self._get_container_client(
            blob["container_name"], blob["is_public"]
        )

        blob_client = container_client.get_blob_client(blob["storage_path"])
        if not blob_client.exists():
            raise NotFoundError(detail=f"File {blob['storage_path']} not found in storage")

        if start_byte is not None or end_byte is not None:
            download_stream = blob_client.download_blob(
                start=start_byte,
                length=end_byte - start_byte + 1 if end_byte else None
            )
        else:
            download_stream = blob_client.download_blob()

        return blob, download_stream

    async def get_file_in_memory(self, file_id: str, verification_id: Optional[Union[str, PydanticObjectId, int]] = None, max_size_mb: int = 10) -> tuple[BlobStorage, bytes]:
        """
        Get a file by ID, loading it into memory only if it's smaller than the specified limit.

        Args:
            file_id: UUID of the file
            verification_id: ID of the requesting user
            max_size_mb: Maximum file size in MB to load into memory (default: 10MB)

        Returns:
            tuple[BlobStorage, bytes]: The file record and its contents (if small enough)

        Raises:
            NotFoundError: If the file doesn't exist
            ValidationError: If the file is too large to load into memory
        """
        blob = await self.get_by_id(file_id, verification_id, is_safe=True)
        if not blob:
            raise NotFoundError(detail=f"File with ID {file_id} not found")

        max_size_bytes = max_size_mb * 1024 * 1024
        if blob["file_size"] > max_size_bytes:
            raise ValidationError(
                detail=f"File size ({blob['file_size']} bytes) exceeds memory limit ({max_size_bytes} bytes). "
                       f"Use get_file() for streaming download instead."
            )

        container_client = self._get_container_client(
            blob["container_name"], blob["is_public"]
        )

        blob_client = container_client.get_blob_client(blob["storage_path"])
        if not blob_client.exists():
            raise NotFoundError(detail=f"File {blob['storage_path']} not found in storage")

        download_stream = blob_client.download_blob()
        return blob, download_stream.readall()

    async def delete_file(self, file_id: str, verification_id: Optional[Union[str, PydanticObjectId, int]] = None) -> None:
        """
        Delete a file or folder.
        """
        blob = await self.get_by_id(file_id, verification_id)
        if not blob:
            raise NotFoundError(detail=f"File with ID {file_id} not found")

        container_client = self._get_container_client(
            blob["container_name"], blob["is_public"]
        )

        blob_client = container_client.get_blob_client(blob["storage_path"])
        if not blob.get("is_folder", False):
            if blob_client.exists():
                blob_client.delete_blob()
        else:
            if blob_client.exists():
                blob_client.delete_blob()

        await self.delete(blob["id"])

    async def get_file_details(
        self,
        file_id: str,
        verification_id: Optional[Union[str, PydanticObjectId, int]] = None,
        token_expiry: timedelta = timedelta(hours=1, minutes=0, seconds=0)
    ) -> BlobStorageResponse:
        """
        Get file details including URL by file ID.

        Args:
            file_id: UUID of the file
            verification_id: ID of the requesting user

        Returns:
            BlobStorageResponse: Detailed file information including URL

        Raises:
            NotFoundError: If the file doesn't exist
        """
        blob = await self.get_by_id(file_id, verification_id, is_safe=True)
        if not blob:
            raise NotFoundError(detail=f"File with ID {file_id} not found")

        container_client = self._get_container_client(
            blob["container_name"], blob["is_public"]
        )

        blob_client = container_client.get_blob_client(blob["storage_path"])
        if not blob_client.exists():
            raise NotFoundError(detail=f"File {blob['storage_path']} not found in storage")

        blob_properties = blob_client.get_blob_properties()

        url = self._generate_sas_url(blob_client, blob["is_public"], token_expiry)

        return BlobStorageResponse(
            id=blob["uuid"],
            file_name=blob["file_name"],
            file_type=blob["file_type"],
            mime_type=blob["mime_type"],
            file_size=blob["file_size"],
            storage_path=blob["storage_path"],
            expires_at=blob["expires_at"],
            verification_id=blob["verification_id"],
            is_public=blob["is_public"],
            container_name=blob["container_name"],
            file_metadata=blob["file_metadata"],
            url=url,
            created_at=blob["created_at"],
            updated_at=blob["updated_at"],
            last_modified=blob_properties.last_modified,
            etag=blob_properties.etag,
            content_length=blob_properties.size,
            content_type=blob_properties.content_settings.content_type,
        )

    async def get_files_by_type(self, file_type: FileType, verification_id: Optional[Union[str, PydanticObjectId, int]] = None) -> List[BlobStorage]:
        """
        Get files by type for a specific user.

        Args:
            file_type: Type of files to retrieve
            verification_id: ID of the user

        Returns:
            List[BlobStorage]: List of files of the specified type
        """
        find_query = FilterSchema(
                operator="and",
                conditions=[
                    {"field": "file_type", "operator": "eq", "value": file_type},
                    {"field": "verification_id", "operator": "eq", "value": str(verification_id) if verification_id else None}
                ]
            )
        query = await self.get_all(find=ListFilter(filters=find_query))
        return query["founds"]

    async def get_all_files(self, verification_id: Optional[Union[str, PydanticObjectId, int]] = None) -> List[BlobStorage]:
        """
        Get all files for a specific user.

        Args:
            verification_id: ID of the user

        Returns:
            List[BlobStorage]: List of all user's files
        """
        find_query = FilterSchema(
            operator="and",
            conditions=[
                {"field": "verification_id", "operator": "eq", "value": str(verification_id) if verification_id else None},
                {"field": "file_type", "operator": "ne", "value": "folder"}
            ]
        )
        query = await self.get_all(find=ListFilter(filters=find_query))
        return query["founds"]

    async def get_public_files(self, verification_id: Optional[Union[str, PydanticObjectId, int]] = None) -> List[BlobStorage]:
        """
        Get all public files for a specific user.

        Args:
            verification_id: ID of the user

        Returns:
            List[BlobStorage]: List of user's public files
        """
        find_query = FilterSchema(
                operator="and",
                conditions=[
                    {"field": "is_public", "operator": "eq", "value": True},
                    {"field": "verification_id", "operator": "eq", "value": str(verification_id) if verification_id else None},
                    {"field": "file_type", "operator": "ne", "value": "folder"}
                ]
            )
        query = await self.get_all(find=ListFilter(filters=find_query))
        return query["founds"]

    async def get_expired_files(self, verification_id: Optional[Union[str, PydanticObjectId, int]] = None) -> List[BlobStorage]:
        """
        Get all expired files for a specific user.

        Args:
            verification_id: ID of the user

        Returns:
            List[BlobStorage]: List of user's expired files
        """
        find_query = FilterSchema(
                operator="and",
                conditions=[
                {"field": "expires_at", "operator": "lt", "value": datetime.now(UTC)},
                {"field": "verification_id", "operator": "eq", "value": str(verification_id) if verification_id else None}
                ]
            )
        query = await self.get_all(find=ListFilter(filters=find_query))
        return query["founds"]

    async def upload_multiple_files(
        self,
        files: List[UploadFile],
        verification_id: Optional[Union[str, PydanticObjectId, int]] = None,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict] = None,
        is_public: bool = True,
        container_name: Optional[str] = None,
        storage_paths: Optional[List[str]] = None,
        max_concurrency: Optional[int] = None,
        custom_filenames: Optional[List[str]] = None,
        timestamp_required: bool = True,
        verification_folder: bool = True,
    ) -> List[BlobStorage]:
        """
        Upload multiple files to blob storage and database concurrently.

        Args:
            files: List of files to upload
            verification_id: ID of the verification account uploading files
            expires_at: Optional expiration date for files
            metadata: Optional metadata to apply to all files
            is_public: Whether files should be public
            container_name: Optional custom container name
            storage_paths: Optional list of storage paths for each file (can be shorter than files list)
            max_concurrency: Maximum number of concurrent uploads (default: unlimited)
            custom_filenames: Optional list of custom filenames (can be shorter than files list)
            timestamp_required: Whether to add timestamp prefix to filenames
            verification_folder: Whether to use verification-specific folder structure

        Returns:
            List[BlobStorage]: List of created database records

        Raises:
            HTTPException: If there's an error during upload

        Note:
            - If storage_paths is shorter than files list, remaining files will be uploaded to root/verification folder
            - If custom_filenames is shorter than files list, remaining files will use their original filenames
        """
        try:
            # Determine if we're using individual paths or bulk upload
            use_individual_paths = storage_paths is not None and len(storage_paths) > 0
            
            if use_individual_paths:
                # Individual upload with different storage paths
                # Extend storage_paths with None values if shorter than files list
                extended_storage_paths = storage_paths.copy()
                if len(extended_storage_paths) < len(files):
                    extended_storage_paths.extend([None] * (len(files) - len(extended_storage_paths)))
                
                # Extend custom_filenames with None values if shorter than files list
                extended_custom_filenames = None
                if custom_filenames:
                    extended_custom_filenames = custom_filenames.copy()
                    if len(extended_custom_filenames) < len(files):
                        extended_custom_filenames.extend([None] * (len(files) - len(extended_custom_filenames)))
                
                upload_results = []
                
                for i, file in enumerate(files):
                    storage_path = extended_storage_paths[i] if i < len(extended_storage_paths) else None
                    custom_filename = extended_custom_filenames[i] if extended_custom_filenames and i < len(extended_custom_filenames) else None
                    
                    # Prepare individual upload environment
                    container_client, container_name_resolved, verification_folder_path = await self._prepare_upload_environment(
                        verification_id, is_public, container_name, storage_path, verification_folder
                    )
                    
                    # Upload individual file
                    file_data, _ = await self._upload_single_file_to_storage(
                        file,
                        container_client,
                        verification_id,
                        is_public,
                        container_name_resolved,
                        verification_folder_path,
                        storage_path,
                        expires_at,
                        metadata,
                        custom_filename,
                        timestamp_required,
                    )
                    
                    upload_results.append(file_data)
                
                # Create database records for all uploaded files
                return await self.bulk_create(upload_results)
                
            else:
                # Bulk upload with shared storage path (original behavior)
                container_client, container_name_resolved, verification_folder_path = await self._prepare_upload_environment(
                    verification_id, is_public, container_name, None, verification_folder
                )

                # Extend custom_filenames with None values if shorter than files list
                extended_custom_filenames = None
                if custom_filenames:
                    extended_custom_filenames = custom_filenames.copy()
                    if len(extended_custom_filenames) < len(files):
                        extended_custom_filenames.extend([None] * (len(files) - len(extended_custom_filenames)))

                upload_coroutines = []
                for i, file in enumerate(files):
                    custom_filename = extended_custom_filenames[i] if extended_custom_filenames and i < len(extended_custom_filenames) else None
                    coro = self._upload_single_file_to_storage(
                        file,
                        container_client,
                        verification_id,
                        is_public,
                        container_name_resolved,
                        verification_folder_path,
                        None,  # No storage path for bulk upload
                        expires_at,
                        metadata,
                        custom_filename,
                        timestamp_required,
                    )
                    upload_coroutines.append(coro)

                if max_concurrency and max_concurrency > 0:
                    semaphore = asyncio.Semaphore(max_concurrency)
                    
                    async def limited_upload(coro):
                        async with semaphore:
                            return await coro
                    
                    limited_coroutines = [limited_upload(coro) for coro in upload_coroutines]
                    upload_results = await asyncio.gather(*limited_coroutines, return_exceptions=True)
                else:
                    upload_results = await asyncio.gather(*upload_coroutines, return_exceptions=True)

                files_data = []
                for i, result in enumerate(upload_results):
                    if isinstance(result, Exception):
                        logger.error(f"Error uploading file {files[i].filename}: {str(result)}")
                        continue
                    
                    file_data, _ = result
                    files_data.append(file_data)

                if not files_data:
                    raise ValidationError(detail="No files were successfully uploaded")

                return await self.bulk_create(files_data)

        except Exception as e:
            logger.error(f"Error during upload: {str(e)}")
            raise

    async def create_folder(
        self,
        request_data: CreateFolderRequest,
        verification_id: Optional[Union[str, PydanticObjectId, int]],
    ) -> BlobStorage:
        """
        Create a folder in blob storage.

        Args:
            folder_name: Name of the folder to create
            verification_id: ID of the user creating the folder
            parent_path: Optional parent folder path
            is_public: Whether the folder should be public
            container_name: Optional custom container name
            metadata: Optional additional metadata

        Returns:
            BlobStorage: The created folder record

        Raises:
            ValidationError: If the folder name is invalid
        """
        if not request_data.folder_name or "/" in request_data.folder_name:
            raise ValidationError(detail="Invalid folder name")

        container_name = request_data.container_name
        if container_name is None:
            container_name = self._get_default_container_name(request_data.is_public)

        container_client = self._get_container_client(container_name, request_data.is_public)

        # Only create verification folder if verification_folder is enabled and verification_id is provided
        if request_data.verification_folder and verification_id:
            self._ensure_verification_folder_exists(container_client, verification_id, request_data.is_public, container_name)

        # Apply timestamp to folder name if required
        folder_name = request_data.folder_name
        if request_data.timestamp_required:
            folder_name = self._generate_timestamped_filename(request_data.folder_name)

        path = f"{request_data.parent_path}/{folder_name}" if request_data.parent_path else folder_name
        full_folder_path = self._get_folder_path(str(verification_id) if verification_id else None, path, request_data.verification_folder) if verification_id else path
        folder_marker_path = f"{full_folder_path}/.folder"
        blob_client = container_client.get_blob_client(folder_marker_path)
        
        folder_metadata = {
            "file_name": self._sanitize_metadata_value(folder_name),
            "file_type": "folder",
            "mime_type": "application/x-directory",
            "file_size": "0",
            "verification_id": str(verification_id) if verification_id else "",
            "is_public": str(request_data.is_public),
            "container_name": container_name,
            "is_folder": "true",
        }
        if request_data.metadata:
            for key, value in request_data.metadata.items():
                if isinstance(value, str):
                    folder_metadata[key] = self._sanitize_metadata_value(value)
                else:
                    folder_metadata[key] = str(value)

        try:
            blob_client.upload_blob(b"", overwrite=True)
            blob_client.set_blob_metadata(folder_metadata)
        except Exception as e:
            logger.error(f"Error creating folder marker at '{folder_marker_path}': {e}")
            raise

        folder_data = BlobStorageCreate(
            file_name=folder_name,
            file_type=FileType.FOLDER,
            mime_type="application/x-directory",
            file_size=0,
            storage_path=full_folder_path,
            verification_id=verification_id,
            is_public=request_data.is_public,
            container_name=container_name,
            file_metadata=request_data.metadata or {},
            is_folder=True,
        )

        return await self.create(folder_data)

    async def list_folder_contents(
        self,
        folder_path: str,
        verification_id: Optional[Union[str, PydanticObjectId, int]] = None,
        is_public: bool = True,
        container_name: Optional[str] = None,
    ) -> List[BlobStorage]:
        """
        List contents of a folder.

        Args:
            folder_path: Path of the folder to list
            verification_id: ID of the requesting user
            is_public: Whether the folder is public
            container_name: Optional custom container name

        Returns:
            List[BlobStorage]: List of files and folders in the specified path

        Note:
            Returns both files and subfolders in the specified path
        """
        try:
            if container_name is None:
                container_name = self._get_default_container_name(is_public)
            
            container_client = self._get_container_client(container_name, is_public)

            if verification_id:
                self._ensure_verification_folder_exists(container_client, verification_id, is_public, container_name)

            full_folder_path = self._get_folder_path(str(verification_id) if verification_id else None, folder_path) if not is_public else folder_path

            prefix = f"{full_folder_path}/" if full_folder_path else "" 

            blobs = container_client.list_blobs(name_starts_with=prefix)
            blob_list = list(blobs)

            folders = set()
            file_paths = []
            folder_contents = []

            for blob in blob_list:
                relative_path = blob.name[len(prefix):]
                if not relative_path:
                    continue

                parts = relative_path.split('/')
                if len(parts) > 1:
                    folder_name = parts[0]
                    folder_path = f"{full_folder_path}/{folder_name}"
                    folders.add(folder_path)

                elif not blob.name.endswith('/.folder'):
                    file_paths.append(blob.name)

            all_paths = file_paths + list(folders)

            if all_paths:
                find_query = FilterSchema(
                    operator=LogicalOperator.AND,
                    conditions=[
                        FieldOperatorCondition(
                            field="storage_path",
                            operator=Operator.IN,
                            value=all_paths
                        ),
                        FieldOperatorCondition(
                            field="verification_id",
                            operator=Operator.EQ,
                            value=str(verification_id) if verification_id else None
                        ),
                        FieldOperatorCondition(
                            field="is_public",
                            operator=Operator.EQ,
                            value=is_public
                        )
                    ]
                )
                db_records = await self._get_all_paginated(find_query)
                
                db_lookup = {record["storage_path"]: record for record in db_records}

            else:
                db_lookup = {}

            missing_files = []
            for blob in blob_list:
                relative_path = blob.name[len(prefix):]
                if not relative_path:
                    continue

                parts = relative_path.split('/')
                if len(parts) > 1:
                    continue
                elif not blob.name.endswith('/.folder'):
                    if blob.name in db_lookup:
                        folder_contents.append(db_lookup[blob.name])
                    else:
                        missing_files.append(blob.name)

            if missing_files:
                missing_metadata = await self._batch_get_blob_metadata(container_client, missing_files)
                
                for blob_name, metadata in missing_metadata.items():
                    try:
                        blob_data = BlobStorage(
                            id=str(PydanticObjectId()),
                            file_name=metadata.get("file_name", os.path.basename(blob_name)),
                            file_type=metadata.get("file_type", "file"),
                            mime_type=metadata.get("mime_type", "application/octet-stream"),
                            file_size=int(metadata.get("file_size", "0")),
                            storage_path=blob_name,
                            verification_id=metadata.get("verification_id", str(verification_id) if verification_id else None),
                            is_public=metadata.get("is_public", str(is_public)).lower() == "true",
                            container_name=metadata.get("container_name", container_name),
                            file_metadata=metadata,
                            is_folder=False,
                            created_at=datetime.now(UTC),
                            updated_at=datetime.now(UTC),
                        )
                        folder_contents.append(blob_data)
                    except Exception as e:
                        logger.error(f"Error processing blob {blob_name}: {str(e)}")
                        continue

            for folder_path in folders:
                if folder_path in db_lookup:
                    folder_contents.append(db_lookup[folder_path])

                else:
                    folder_name = os.path.basename(folder_path)
                    folder_data = BlobStorage(
                        id=str(PydanticObjectId()),
                        file_name=folder_name,
                        file_type="folder",
                        mime_type="folder",
                        file_size=0,
                        storage_path=folder_path,
                        verification_id=str(verification_id) if verification_id else None,
                        is_public=is_public,
                        container_name=container_name,
                        file_metadata={},
                        is_folder=True,
                        created_at=datetime.now(UTC),
                        updated_at=datetime.now(UTC),
                    )
                    folder_contents.append(folder_data)

            return folder_contents

        except Exception as e:
            logger.error(f"Error in list_folder_contents: {str(e)}")
            raise

    async def _get_all_paginated(
        self,
        find_query: FilterSchema,
        page_size: int = 100,
        timeout: int = 30,
        max_pages: int = 1000,
    ) -> List[Any]:
        """
        Helper method to get all records across multiple pages, with timeout and max page safeguards.

        Args:
            find_query: The filter query to use
            page_size: Number of records per page
            timeout: Maximum time in seconds to spend paginating
            max_pages: Maximum number of pages to fetch

        Returns:
            List[Any]: Combined list of all records across all pages
        """
        all_records = []
        current_page = 1
        start_time = time.monotonic()
        while current_page <= max_pages:
            if time.monotonic() - start_time > timeout:
                logger.warning(f"Pagination timeout after {timeout} seconds on page {current_page}")
                break
            try:
                result = await self.get_all(find=ListFilter(filters=find_query, page=current_page, page_size=page_size))
            except Exception as e:
                logger.error(f"Exception during pagination on page {current_page}: {e}")
                break
            if not result["founds"]:
                break
                
            all_records.extend(result["founds"])
            if len(result["founds"]) < page_size:
                break
                
            current_page += 1
            
        return all_records

    async def delete_folder_recursive(
        self,
        folder_path: str,
        verification_id: Optional[Union[str, PydanticObjectId, int]] = None,
        is_public: bool = True,
        container_name: Optional[str] = None,
    ) -> bool:
        """Delete a folder and all its contents recursively."""
        try:
            if container_name is None:
                container_name = self._get_default_container_name(is_public)

            container_client = self._get_container_client(container_name, is_public)

            if is_public:
                full_folder_path = folder_path
            else:
                full_folder_path = self._get_folder_path(str(verification_id) if verification_id else None, folder_path)
                stripped_path = full_folder_path.strip("/").split("/")
                full_folder_path = full_folder_path if len(stripped_path) > 1 else stripped_path[0]

            find_query = FilterSchema(
                operator=LogicalOperator.AND,
                conditions=[
                    FieldOperatorCondition(
                        field="storage_path",
                        operator=Operator.LIKE,
                        value=f"{full_folder_path}//*" if full_folder_path != "/" else "/*"
                    ),
                    FieldOperatorCondition(
                        field="verification_id",
                        operator=Operator.EQ,
                        value=str(verification_id) if verification_id else None
                    ),
                    FieldOperatorCondition(
                        field="is_public",
                        operator=Operator.EQ,
                        value=is_public
                    )
                ]
            )

            db_records = await self._get_all_paginated(find_query)
            delete_coros = [self._delete_blob_and_record(blob["storage_path"] if not blob["is_folder"] else blob["storage_path"] + ".folder", container_client) for blob in db_records]
            await asyncio.gather(*delete_coros, return_exceptions=True)

            await self.bulk_delete(conditions=find_query)

            return True

        except Exception as e:
            logger.error(f"Error in delete_folder_recursive: {str(e)}")
            raise

    async def delete_folder(
        self,
        folder_path: str,
        verification_id: Optional[Union[str, PydanticObjectId, int]] = None,
        is_public: bool = True,
        container_name: Optional[str] = None,
    ) -> bool:
        """
        Delete a folder and all its contents.
        """
        try:
            await self.delete_folder_recursive(
                folder_path=folder_path,
                verification_id=verification_id,
                is_public=is_public,
                container_name=container_name,
            )

            return True

        except Exception as e:
            logger.error(f"Error in delete_folder: {str(e)}")
            raise

    async def update_metadata(
        self,
        file_id: str,
        new_metadata: Dict[str, Any],
        new_filename: Optional[str] = None,
        verification_id: Optional[Union[str, PydanticObjectId, int]] = None,
    ) -> BlobStorage:
        """
        Update metadata and/or filename for a file or folder in both blob storage and the database.
        
        Args:
            file_id: ID of the file to update
            new_metadata: New metadata to apply
            new_filename: Optional new filename to set
            verification_id: ID of the user requesting the update
            
        Returns:
            BlobStorage: Updated file record
        """
        blob = await self.get_by_id(file_id, verification_id)
        if not blob:
            raise NotFoundError(detail=f"File with ID {file_id} not found")

        container_client = self._get_container_client(blob["container_name"], blob["is_public"])
        old_blob_client = container_client.get_blob_client(blob["storage_path"])
        current_metadata = old_blob_client.get_blob_properties().metadata
        
        # Prepare database update data
        update_data = {}
        new_storage_path = blob["storage_path"]
        
        # Handle filename update - this requires copying the blob to a new location
        if new_filename and new_filename != blob["file_name"]:
            # Resolve the final filename using the same logic as file creation
            # Use the current filename as the "original" to preserve extension if needed
            final_filename = self._resolve_final_filename(blob["file_name"], new_filename)
            
            # Update file type and MIME type based on final filename
            new_file_type = self._get_file_type(final_filename)
            new_mime_type = self._get_mime_type(final_filename)
            
            # Generate new blob path with the resolved filename
            new_blob_name = self._generate_timestamped_filename(final_filename)
            
            # Construct new storage path maintaining the directory structure
            storage_path_parts = blob["storage_path"].split("/")
            if len(storage_path_parts) > 1:
                # Replace only the filename part (last part) with new blob name
                storage_path_parts[-1] = new_blob_name
                new_storage_path = "/".join(storage_path_parts)
            else:
                # If no directory structure, just use the new blob name
                new_storage_path = new_blob_name
            
            # Update blob metadata with final filename
            current_metadata["file_name"] = final_filename
            current_metadata["file_type"] = new_file_type.value
            current_metadata["mime_type"] = new_mime_type
            
            # Handle additional metadata updates
            if new_metadata:
                updated_metadata = {**current_metadata, **new_metadata}
            else:
                updated_metadata = current_metadata
            
            # Rename the blob in storage
            rename_success = await self._rename_blob_in_storage(
                container_client=container_client,
                old_storage_path=blob["storage_path"],
                new_storage_path=new_storage_path,
                metadata=updated_metadata
            )
            
            if not rename_success:
                raise InternalServerError(detail="Failed to rename file in blob storage")
            
            # Update database record with new path and final filename
            update_data.update({
                "file_name": final_filename,
                "file_type": new_file_type,
                "mime_type": new_mime_type,
                "storage_path": new_storage_path,
                "file_metadata": updated_metadata
            })
        else:
            # No filename change, just update metadata
            if new_metadata:
                updated_metadata = {**current_metadata, **new_metadata}
                
                # Sanitize updated metadata for Azure Storage
                sanitized_metadata = {}
                for key, value in updated_metadata.items():
                    if isinstance(value, str):
                        sanitized_metadata[key] = self._sanitize_metadata_value(value)
                    else:
                        sanitized_metadata[key] = str(value)
                
                update_data["file_metadata"] = updated_metadata
                
                # Update blob metadata in Azure Storage
                old_blob_client.set_blob_metadata(sanitized_metadata)
        
        # Update database record
        if update_data:
            await self.update(blob["id"], update_data)

        return await self.get_by_id(file_id, verification_id)

    async def _rename_blob_in_storage(
        self,
        container_client: ContainerClient,
        old_storage_path: str,
        new_storage_path: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Rename a blob in Azure Storage by copying to new location and deleting the old one.
        
        Args:
            container_client: The Azure container client
            old_storage_path: Current blob path
            new_storage_path: New blob path
            metadata: Metadata to set on the new blob
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            old_blob_client = container_client.get_blob_client(old_storage_path)
            new_blob_client = container_client.get_blob_client(new_storage_path)
            
            # Check if old blob exists
            if not old_blob_client.exists():
                logger.error(f"Source blob {old_storage_path} does not exist")
                return False
            
            # Copy the blob content to the new location
            copy_source = old_blob_client.url
            copy_operation = new_blob_client.start_copy_from_url(copy_source)
            
            # Wait for copy to complete
            max_wait_time = 30  # 30 seconds timeout
            wait_time = 0
            while copy_operation['copy_status'] == 'pending' and wait_time < max_wait_time:
                await asyncio.sleep(1)
                wait_time += 1
                try:
                    copy_props = new_blob_client.get_blob_properties()
                    copy_operation = {'copy_status': copy_props.copy.status}
                except Exception as e:
                    logger.error(f"Error checking copy status: {str(e)}")
                    return False
            
            if copy_operation['copy_status'] != 'success':
                logger.error(f"Blob copy failed with status: {copy_operation['copy_status']}")
                return False
            
            # Set metadata on the new blob
            # Sanitize metadata for Azure Storage
            sanitized_metadata = {}
            for key, value in metadata.items():
                if isinstance(value, str):
                    sanitized_metadata[key] = self._sanitize_metadata_value(value)
                else:
                    sanitized_metadata[key] = str(value)
            
            new_blob_client.set_blob_metadata(sanitized_metadata)
            
            # Delete the old blob
            try:
                old_blob_client.delete_blob()
            except Exception as e:
                logger.warning(f"Failed to delete old blob {old_storage_path}: {str(e)}")
                # Don't fail the operation if we can't delete the old blob
            
            return True
            
        except Exception as e:
            logger.error(f"Error renaming blob from {old_storage_path} to {new_storage_path}: {str(e)}")
            return False

    async def _batch_get_blob_metadata(self, container_client: ContainerClient, blob_names: List[str]) -> Dict[str, Dict]:
        """
        Batch retrieve metadata for multiple blobs concurrently.

        Args:
            container_client: The Azure container client
            blob_names: List of blob names

        Returns:
            Dict[str, Dict]: Dictionary of blob names and their metadata
        """
        async def get_single_blob_metadata(blob_name: str) -> tuple[str, Dict]:
            try:
                blob_client = container_client.get_blob_client(blob_name)
                metadata = blob_client.get_blob_properties().metadata
                return blob_name, metadata
            except Exception as e:
                logger.error(f"Error getting metadata for {blob_name}: {str(e)}")
                return blob_name, {}

        metadata_coroutines = [get_single_blob_metadata(blob_name) for blob_name in blob_names]
        results = await asyncio.gather(*metadata_coroutines, return_exceptions=True)
        
        metadata_dict = {}
        for result in results:
            if isinstance(result, Exception):
                continue
            blob_name, metadata = result
            metadata_dict[blob_name] = metadata
            
        return metadata_dict
