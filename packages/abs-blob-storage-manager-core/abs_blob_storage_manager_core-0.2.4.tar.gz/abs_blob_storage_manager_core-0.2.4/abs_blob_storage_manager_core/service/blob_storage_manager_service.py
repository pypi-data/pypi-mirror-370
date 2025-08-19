from typing import Any, List, Optional, Dict, Union
from datetime import timedelta

from fastapi import UploadFile
from beanie import PydanticObjectId

from abs_blob_storage_manager_core.schema.blob_storage_schema import (
    BlobStorage,
    BlobStorageResponse,
    FileType,
    MultipleBlobStorageResponse,
    RequestData,
    CreateFolderRequest,
)
from abs_exception_core.exceptions import ValidationError
from abs_blob_storage_manager_core.repository.blob_storage_manager_repository import BlobStorageRepository
from abs_nosql_repository_core.service import BaseService
from abs_utils.logger import setup_logger


logger = setup_logger(__name__)


class BlobStorageManagerService(BaseService):
    SUPPORTED_CONTENT_TYPES = [
        # Documents
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        # Images
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        # Videos
        "video/mp4",
        "video/quicktime",
        "video/x-msvideo",
        # Audio
        "audio/mpeg",
        "audio/wav",
        "audio/ogg",
        # Archives
        "application/zip",
        "application/x-rar-compressed",
        "application/x-7z-compressed",
    ]
    
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

    def __init__(self, blob_storage_repository: BlobStorageRepository):
        self.repository = blob_storage_repository
        super().__init__(blob_storage_repository)

    def _validate_file(self, file: UploadFile) -> None:
        """
        Validate a single file for upload.
        
        Args:
            file: The file to validate
            
        Raises:
            ValidationError: If validation fails
        """
        if not file:
            raise ValidationError(detail="No file provided")

        try:
            file.file.seek(0, 2)
            size = file.file.tell()
            file.file.seek(0)

            if size > self.MAX_FILE_SIZE:
                raise ValidationError(
                    detail=f"File size exceeds maximum limit of {self.MAX_FILE_SIZE/1024/1024}MB"
                )

            content_type = file.content_type
            if not content_type:
                raise ValidationError(detail="File content type not detected")

            if content_type not in self.SUPPORTED_CONTENT_TYPES:
                raise ValidationError(
                    detail=f"Unsupported file type: {content_type}. Supported types: {', '.join(self.SUPPORTED_CONTENT_TYPES)}"
                )

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(detail=f"Error validating file: {str(e)}")

    async def upload_file(
        self,
        file: UploadFile,
        request_data: RequestData,
        verification_id: Optional[Union[str, PydanticObjectId, int]] = None,
    ) -> BlobStorage:
        """
        Upload a single file to blob storage with validation.
        
        Args:
            file: The file to upload
            request_data: Upload configuration data
            verification_id: ID of the user uploading the file
            
        Returns:
            BlobStorage: The created database record
            
        Raises:
            ValidationError: If file validation fails
        """
        self._validate_file(file)

        return await self.repository.upload_file(
            file=file, verification_id=verification_id, request_data=request_data
        )

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
            verification_id: ID of the requesting user (None for anonymous access)
            token_expiry: Token expiry time for SAS URLs
            
        Returns:
            str: The URL to access the file
        """
        return await self.repository.get_file_url(file_id, verification_id, token_expiry)

    async def get_file(self, file_id: str, verification_id: Optional[Union[str, PydanticObjectId, int]] = None) -> tuple[BlobStorage, Any]:
        """Get a file by ID with streaming download."""
        return await self.repository.get_file(file_id, verification_id)

    async def get_file_chunked(
        self,
        file_id: str,
        verification_id: Optional[Union[str, PydanticObjectId, int]] = None,
        chunk_size: int = 8192,
        start_byte: Optional[int] = None,
        end_byte: Optional[int] = None,
    ) -> tuple[BlobStorage, Any]:
        """Get a file by ID with chunked streaming download for large files."""
        return await self.repository.get_file_chunked(
            file_id, verification_id, chunk_size, start_byte, end_byte
        )

    async def get_file_in_memory(
        self, file_id: str, verification_id: Optional[Union[str, PydanticObjectId, int]] = None, max_size_mb: int = 10
    ) -> tuple[BlobStorage, bytes]:
        """Get a file by ID, loading it into memory only if it's smaller than the specified limit."""
        return await self.repository.get_file_in_memory(file_id, verification_id, max_size_mb)

    async def delete_file(self, file_id: str, verification_id: Optional[Union[str, PydanticObjectId, int]] = None) -> None:
        """Delete a file."""
        await self.repository.delete_file(file_id, verification_id)

    async def get_file_details(
        self,
        file_id: str,
        verification_id: Optional[Union[str, PydanticObjectId, int]] = None,
        token_expiry: timedelta = timedelta(hours=1, minutes=0, seconds=0)
    ) -> BlobStorageResponse:
        """Get file details including URL by file ID."""
        return await self.repository.get_file_details(file_id, verification_id, token_expiry)

    async def get_files_by_type(self, file_type: FileType, verification_id: Optional[Union[str, PydanticObjectId, int]] = None) -> List[BlobStorage]:
        """Get files by type for a specific user."""
        return await self.repository.get_files_by_type(file_type, verification_id)

    async def get_all_files(self, verification_id: Optional[Union[str, PydanticObjectId, int]] = None) -> List[BlobStorage]:
        """Get all files for a specific user."""
        return await self.repository.get_all_files(verification_id)

    async def get_public_files(self, verification_id: Optional[Union[str, PydanticObjectId, int]] = None) -> List[BlobStorage]:
        """Get all public files for a specific user."""
        return await self.repository.get_public_files(verification_id)

    async def cleanup_expired_files(self, verification_id: Optional[Union[str, PydanticObjectId, int]] = None) -> int:
        """Clean up expired files for a specific user."""
        expired_files = await self.repository.get_expired_files(verification_id)
        count = 0
        for file in expired_files:
            try:
                await self.delete_file(file["uuid"], verification_id)
                count += 1
            except Exception as e:
                logger.error(f"Error deleting expired file {file['uuid']}: {str(e)}")
        return count

    async def upload_multiple_files(
        self,
        files: List[UploadFile],
        request_data: RequestData,
        verification_id: Optional[Union[str, PydanticObjectId, int]] = None,
        custom_filenames: Optional[List[str]] = None,
        storage_paths: Optional[List[str]] = None,
        max_concurrency: Optional[int] = None,
    ) -> MultipleBlobStorageResponse:
        """
        Upload multiple files to blob storage with validation and concurrent processing.
        
        Args:
            files: List of files to upload
            request_data: Upload configuration data
            verification_id: ID of the verification account uploading files
            custom_filenames: Optional list of custom filenames (can be shorter than files list)
            storage_paths: Optional list of storage paths for each file (can be shorter than files list)
            max_concurrency: Maximum number of concurrent uploads (default: unlimited)
            
        Returns:
            MultipleBlobStorageResponse: Upload results with success/failure details
            
        Note:
            - If storage_paths is shorter than files list, remaining files will be uploaded to root/verification folder
            - If custom_filenames is shorter than files list, remaining files will use their original filenames
        """
        if not files:
            raise ValidationError(detail="No files provided")

        failed_files = []
        valid_files = []

        for file in files:
            try:
                self._validate_file(file)
                valid_files.append(file)
            except ValidationError as e:
                failed_files.append(
                    {
                        "filename": file.filename,
                        "error": str(e.detail),
                    }
                )
            except Exception as e:
                logger.error(f"Error validating file {file.filename}: {str(e)}")
                failed_files.append({"filename": file.filename, "error": str(e)})

        if not valid_files:
            return MultipleBlobStorageResponse(
                files=[],
                total_files=len(files),
                total_size=0,
                success_count=0,
                failed_count=len(files),
                failed_files=failed_files,
            )

        expires_at = request_data.expires_at
        metadata = request_data.file_metadata
        is_public = request_data.is_public
        container_name = request_data.container_name
        
        # Use storage_paths if provided, otherwise fall back to single storage_path from request_data
        final_storage_paths = storage_paths
        if not final_storage_paths and hasattr(request_data, 'storage_path') and request_data.storage_path:
            # If no individual paths provided but request_data has storage_path, use it for all files
            final_storage_paths = [request_data.storage_path] * len(valid_files)

        if container_name is None and is_public:
            container_name = self.repository._public_container
        elif container_name is None and not is_public:
            container_name = self.repository._private_container

        try:
            uploaded_files = await self.repository.upload_multiple_files(
                files=valid_files,
                verification_id=verification_id,
                expires_at=expires_at,
                metadata=metadata,
                is_public=is_public,
                container_name=container_name,
                storage_paths=final_storage_paths,
                max_concurrency=max_concurrency,
                custom_filenames=custom_filenames,
                timestamp_required=request_data.timestamp_required,
                verification_folder=request_data.verification_folder,
            )

            total_size = sum(file["file_size"] for file in uploaded_files)

            return MultipleBlobStorageResponse(
                files=uploaded_files,
                total_files=len(files),
                total_size=total_size,
                success_count=len(uploaded_files),
                failed_count=len(failed_files),
                failed_files=failed_files,
            )

        except Exception as e:
            logger.error(f"Error in bulk upload: {str(e)}")

            return MultipleBlobStorageResponse(
                files=[],
                total_files=len(files),
                total_size=0,
                success_count=0,
                failed_count=len(files),
                failed_files=[
                    {"filename": file.filename, "error": str(e)} for file in files
                ],
            )

    async def create_folder(
        self,
        request_data: CreateFolderRequest,
        verification_id: Optional[Union[str, PydanticObjectId, int]] = None,
    ) -> BlobStorage:
        """Create a folder in blob storage."""
        if not request_data.folder_name or "/" in request_data.folder_name:
            raise ValidationError(detail="Invalid folder name")

        folder_path = f"{request_data.parent_path}/{request_data.folder_name}" if request_data.parent_path else request_data.folder_name
        folder_path = folder_path.strip("/")

        return await self.repository.create_folder(
            request_data=request_data,
            verification_id=verification_id,
        )

    async def list_folder_contents(
        self,
        folder_path: str,
        verification_id: Optional[Union[str, PydanticObjectId, int]] = None,
        is_public: bool = True,
        container_name: Optional[str] = None,
    ) -> List[BlobStorage]:
        """List contents of a folder."""
        try:
            import urllib.parse
            decoded_path = urllib.parse.unquote(folder_path)

            if decoded_path.endswith('/'):
                decoded_path = decoded_path[:-1]

            contents = await self.repository.list_folder_contents(
                folder_path=decoded_path,
                verification_id=verification_id,
                is_public=is_public,
                container_name=container_name,
            )

            return contents

        except Exception as e:
            logger.error(f"Service: Error in list_folder_contents: {str(e)}")
            raise

    async def delete_folder(
        self,
        folder_path: str,
        verification_id: Optional[Union[str, PydanticObjectId, int]] = None,
        is_public: bool = True,
        container_name: Optional[str] = None,
    ) -> None:
        """Delete a folder and its contents."""
        if not folder_path:
            raise ValidationError(detail="Invalid folder path")

        await self.repository.delete_folder(
            folder_path=folder_path,
            verification_id=verification_id,
            is_public=is_public,
            container_name=container_name,
        )

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
            return await self.repository.update_metadata(
                file_id=file_id,
                verification_id=verification_id,
                new_metadata=new_metadata,
                new_filename=new_filename,
            )
