"""
Object Storage Service for handling image uploads and retrieval
Supports both Replit cloud storage and local filesystem storage
"""
import os
import tempfile
import base64
import uuid
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import json
import logging
import httpx

logger = logging.getLogger(__name__)

class LocalStorageService:
    """Local filesystem-based storage service for development"""
    
    def __init__(self):
        # Create local storage directories
        self.base_dir = Path("uploads")
        self.private_dir = self.base_dir / "private" 
        self.public_dir = self.base_dir / "public"
        
        # Ensure directories exist
        self.base_dir.mkdir(exist_ok=True)
        self.private_dir.mkdir(exist_ok=True) 
        self.public_dir.mkdir(exist_ok=True)
    
    async def get_upload_url(self, filename: str) -> str:
        """Generate a local file path for upload (simulates presigned URL)"""
        unique_filename = f"{uuid.uuid4()}-{filename}"
        file_path = self.private_dir / unique_filename
        
        # Return a local file URL that the frontend can use
        return f"/local-upload/{unique_filename}"
    
    async def save_uploaded_file(self, filename: str, file_data: bytes) -> str:
        """Save file data to local storage"""
        file_path = self.private_dir / filename
        
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        return str(file_path)
    
    async def get_image_url(self, object_path: str) -> Optional[str]:
        """Get local file URL for accessing an image"""
        try:
            # Extract filename from object path
            filename = Path(object_path).name
            file_path = self.private_dir / filename
            
            if file_path.exists():
                return f"/local-files/{filename}"
            return None
        except Exception as e:
            logger.error(f"Failed to get local image URL: {e}")
            return None


class ObjectStorageService:
    """Service for managing object storage operations - supports both cloud and local"""
    
    def __init__(self):
        # Try to detect if we're running on Replit with object storage
        self.bucket_id = os.environ.get('DEFAULT_OBJECT_STORAGE_BUCKET_ID')
        self.is_replit = bool(self.bucket_id)
        
        if self.is_replit:
            # Replit cloud storage setup
            self.private_dir = os.environ.get('PRIVATE_OBJECT_DIR', '.private')
            self.public_paths = os.environ.get('PUBLIC_OBJECT_SEARCH_PATHS', '').split(',')
            self.replit_sidecar_endpoint = "http://127.0.0.1:1106"
            logger.info("Using Replit cloud object storage")
        else:
            # Local filesystem storage setup
            self.local_storage = LocalStorageService()
            logger.info("Using local filesystem storage (uploads directory)")
    
    def _parse_bucket_path(self, path: str) -> Dict[str, str]:
        """Parse a bucket path into bucket name and object name"""
        if not path.startswith("/"):
            path = f"/{path}"
        
        path_parts = path.split("/")
        if len(path_parts) < 3:
            raise ValueError("Invalid path: must contain at least a bucket name")
        
        bucket_name = path_parts[1]
        object_name = "/".join(path_parts[2:])
        
        return {"bucket_name": bucket_name, "object_name": object_name}
    
    async def get_upload_url(self, filename: str) -> str:
        """
        Get a presigned upload URL for an image (cloud) or local path (local)
        
        Args:
            filename: Name for the uploaded file
            
        Returns:
            Upload URL or local path
        """
        if not self.is_replit:
            # Use local storage
            return await self.local_storage.get_upload_url(filename)
            
        try:
            # Replit cloud storage
            unique_filename = f"{uuid.uuid4()}-{filename}"
            object_path = f"{self.private_dir}/uploads/{unique_filename}"
            
            # Parse the path
            path_info = self._parse_bucket_path(f"/{self.bucket_id}/{object_path}")
            
            # Get signed URL from Replit sidecar
            request_data = {
                "bucket_name": path_info["bucket_name"], 
                "object_name": path_info["object_name"],
                "method": "PUT",
                "expires_at": "3600"  # 1 hour from now
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.replit_sidecar_endpoint}/object-storage/signed-object-url",
                    headers={"Content-Type": "application/json"},
                    json=request_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["signed_url"]
                else:
                    raise Exception(f"Failed to get signed URL: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Failed to get upload URL for {filename}: {e}")
            raise
    
    async def get_image_url(self, object_path: str) -> Optional[str]:
        """Get a signed URL (cloud) or local file URL (local) for accessing an image"""
        if not self.is_replit:
            # Use local storage
            return await self.local_storage.get_image_url(object_path)
            
        try:
            # Replit cloud storage
            path_info = self._parse_bucket_path(f"/{self.bucket_id}/{object_path}")
            
            # Get signed URL from Replit sidecar
            request_data = {
                "bucket_name": path_info["bucket_name"],
                "object_name": path_info["object_name"],
                "method": "GET",
                "expires_at": "3600"  # 1 hour from now
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.replit_sidecar_endpoint}/object-storage/signed-object-url",
                    headers={"Content-Type": "application/json"},
                    json=request_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["signed_url"]
                else:
                    return None
            
        except Exception as e:
            logger.error(f"Failed to get image URL for {object_path}: {e}")
            return None

def get_storage_service():
    """Get an instance of the object storage service"""
    try:
        return ObjectStorageService()
    except Exception as e:
        logger.warning(f"Failed to initialize object storage service: {e}")
        # Fallback to local storage only
        service = ObjectStorageService.__new__(ObjectStorageService)
        service.is_replit = False
        service.local_storage = LocalStorageService()
        return service
    
    def encode_image_for_llm(self, image_data: bytes) -> str:
        """Encode image data as base64 for LLM consumption"""
        return base64.b64encode(image_data).decode('utf-8')
    
    async def download_image(self, url: str) -> Optional[bytes]:
        """Download image from URL and return bytes"""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.content
                return None
        except Exception as e:
            logger.error(f"Failed to download image from {url}: {e}")
            return None

# Global instance
storage_service = None

def get_storage_service() -> ObjectStorageService:
    """Get the global storage service instance"""
    global storage_service
    if storage_service is None:
        storage_service = ObjectStorageService()
    return storage_service