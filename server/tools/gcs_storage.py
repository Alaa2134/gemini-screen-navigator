"""
Google Cloud Storage Tool
Handles file uploads and downloads to Google Cloud Storage
"""

import logging
import os
from typing import Optional, Dict, Any
from pathlib import Path
from google.cloud import storage
from datetime import timedelta

logger = logging.getLogger(__name__)


class GCSStorageError(Exception):
    \"\"\"Raised when GCS operations fail\"\"\"
    pass


class GCSStorage:
    \"\"\"Handles Google Cloud Storage operations\"\"\"
    
    def __init__(self, project_id: str, bucket_name: str):
        \"\"\"
        Initialize GCS storage
        
        Args:
            project_id: Google Cloud project ID
            bucket_name: GCS bucket name
        \"\"\"
        self.project_id = project_id
        self.bucket_name = bucket_name
        
        try:
            self.client = storage.Client(project=project_id)
            self.bucket = self.client.bucket(bucket_name)
            logger.info(f\"GCS Storage initialized: {bucket_name}\")
        except Exception as e:
            logger.error(f\"Failed to initialize GCS: {str(e)}\")
            raise GCSStorageError(f\"GCS initialization failed: {str(e)}\")
    
    def upload_file(
        self,
        local_path: str,
        remote_path: str,
        content_type: Optional[str] = None,
        public: bool = False
    ) -> Dict[str, Any]:
        \"\"\"
        Upload file to GCS
        
        Args:
            local_path: Local file path
            remote_path: Remote path in bucket
            content_type: MIME type
            public: Make file publicly accessible
        
        Returns:
            Dict with upload result
        \"\"\"
        try:
            local_file = Path(local_path)
            if not local_file.exists():
                raise FileNotFoundError(f\"File not found: {local_path}\")
            
            # Create blob
            blob = self.bucket.blob(remote_path)
            
            # Set content type
            if content_type:
                blob.content_type = content_type
            
            # Upload file
            blob.upload_from_filename(local_path)
            
            # Make public if requested
            if public:
                blob.make_public()
            
            # Get URL
            if public:
                url = blob.public_url
            else:
                url = f\"gs://{self.bucket_name}/{remote_path}\"
            
            result = {
                \"success\": True,
                \"local_path\": local_path,
                \"remote_path\": remote_path,
                \"url\": url,
                \"size\": local_file.stat().st_size,
                \"content_type\": blob.content_type
            }
            
            logger.info(f\"File uploaded: {remote_path} ({result['size']} bytes)\")
            return result
        
        except Exception as e:
            logger.error(f\"File upload failed: {str(e)}\")
            raise GCSStorageError(f\"Upload failed: {str(e)}\")
    
    def upload_bytes(
        self,
        data: bytes,
        remote_path: str,
        content_type: str = \"application/octet-stream\",
        public: bool = False
    ) -> Dict[str, Any]:
        \"\"\"
        Upload bytes to GCS
        
        Args:
            data: Bytes to upload
            remote_path: Remote path in bucket
            content_type: MIME type
            public: Make file publicly accessible
        
        Returns:
            Dict with upload result
        \"\"\"
        try:
            blob = self.bucket.blob(remote_path)
            blob.content_type = content_type
            
            # Upload bytes
            blob.upload_from_string(data)
            
            # Make public if requested
            if public:
                blob.make_public()
            
            # Get URL
            if public:
                url = blob.public_url
            else:
                url = f\"gs://{self.bucket_name}/{remote_path}\"
            
            result = {
                \"success\": True,
                \"remote_path\": remote_path,
                \"url\": url,
                \"size\": len(data),
                \"content_type\": content_type
            }
            
            logger.info(f\"Bytes uploaded: {remote_path} ({len(data)} bytes)\")
            return result
        
        except Exception as e:
            logger.error(f\"Bytes upload failed: {str(e)}\")
            raise GCSStorageError(f\"Upload failed: {str(e)}\")
    
    def download_file(
        self,
        remote_path: str,
        local_path: str
    ) -> Dict[str, Any]:
        \"\"\"
        Download file from GCS
        
        Args:
            remote_path: Remote path in bucket
            local_path: Local path to save
        
        Returns:
            Dict with download result
        \"\"\"
        try:
            blob = self.bucket.blob(remote_path)
            
            # Create local directory if needed
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Download file
            blob.download_to_filename(local_path)
            
            result = {
                \"success\": True,
                \"remote_path\": remote_path,
                \"local_path\": local_path,
                \"size\": blob.size
            }
            
            logger.info(f\"File downloaded: {remote_path}\")
            return result
        
        except Exception as e:
            logger.error(f\"File download failed: {str(e)}\")
            raise GCSStorageError(f\"Download failed: {str(e)}\")
    
    def get_signed_url(
        self,
        remote_path: str,
        expiration_hours: int = 24
    ) -> str:
        \"\"\"
        Get signed URL for file
        
        Args:
            remote_path: Remote path in bucket
            expiration_hours: URL expiration time in hours
        
        Returns:
            Signed URL
        \"\"\"
        try:
            blob = self.bucket.blob(remote_path)
            url = blob.generate_signed_url(
                version=\"v4\",
                expiration=timedelta(hours=expiration_hours),
                method=\"GET\"
            )
            return url
        
        except Exception as e:
            logger.error(f\"Failed to generate signed URL: {str(e)}\")
            raise GCSStorageError(f\"Signed URL generation failed: {str(e)}\")
    
    def list_files(self, prefix: str = \"\") -> list:
        \"\"\"
        List files in bucket with optional prefix
        
        Args:
            prefix: Optional prefix filter
        
        Returns:
            List of file names
        \"\"\"
        try:
            blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)
            files = [blob.name for blob in blobs]
            logger.info(f\"Listed {len(files)} files with prefix '{prefix}'\")
            return files
        
        except Exception as e:
            logger.error(f\"Failed to list files: {str(e)}\")
            raise GCSStorageError(f\"List files failed: {str(e)}\")
    
    def delete_file(self, remote_path: str) -> bool:
        \"\"\"
        Delete file from GCS
        
        Args:
            remote_path: Remote path in bucket
        
        Returns:
            True if successful
        \"\"\"
        try:
            blob = self.bucket.blob(remote_path)
            blob.delete()
            logger.info(f\"File deleted: {remote_path}\")
            return True
        
        except Exception as e:
            logger.error(f\"File deletion failed: {str(e)}\")
            raise GCSStorageError(f\"Deletion failed: {str(e)}\")
    
    def delete_folder(self, prefix: str) -> int:
        \"\"\"
        Delete all files with given prefix
        
        Args:
            prefix: Folder prefix
        
        Returns:
            Number of files deleted
        \"\"\"
        try:
            blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)
            count = 0
            for blob in blobs:
                blob.delete()
                count += 1
            logger.info(f\"Deleted {count} files with prefix '{prefix}'\")
            return count
        
        except Exception as e:
            logger.error(f\"Folder deletion failed: {str(e)}\")
            raise GCSStorageError(f\"Folder deletion failed: {str(e)}\")


# Global instance
_gcs_storage = None


def get_gcs_storage(
    project_id: Optional[str] = None,
    bucket_name: Optional[str] = None
) -> GCSStorage:
    \"\"\"Get or create global GCSStorage instance\"\"\"
    global _gcs_storage
    if _gcs_storage is None:
        project_id = project_id or os.getenv(\"GCP_PROJECT_ID\")
        bucket_name = bucket_name or os.getenv(\"GCS_BUCKET_NAME\", \"gemini-navigator\")
        
        if not project_id:
            raise GCSStorageError(\"GCP_PROJECT_ID not set\")
        
        _gcs_storage = GCSStorage(project_id, bucket_name)
    return _gcs_storage
