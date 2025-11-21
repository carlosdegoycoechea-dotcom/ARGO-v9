"""
ARGO - Drive Manager FIXED
Unified Google Drive synchronization with RECURSIVE folder support

CRITICAL FIXES:
- Recursive folder traversal (downloads ALL subfolders)
- Unified with GoogleDriveSync capabilities
- Full path preservation for categorization
- Integration with RAG pipeline
"""
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import hashlib
import io

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from core.logger import get_logger

logger = get_logger("DriveManager")


class DriveManager:
    """
    Unified Drive Manager with recursive synchronization
    
    Features:
    - Recursive folder traversal (all subfolders)
    - Hash-based change detection
    - Automatic categorization by folder structure
    - Database integration for tracking
    """

    def __init__(self, credentials_path: str, db_manager=None):
        """
        Initialize Drive Manager
        
        Args:
            credentials_path: Path to google_credentials.json
            db_manager: UnifiedDatabase instance (optional)
        """
        self.credentials_path = Path(credentials_path)
        self.db = db_manager
        self.service = None
        
        if not self.credentials_path.exists():
            raise FileNotFoundError(f"Google credentials not found: {credentials_path}")
        
        # Initialize Drive service
        self._init_drive_service()
        
        logger.info(f"DriveManager initialized with credentials: {credentials_path}")

    def _init_drive_service(self):
        """Initialize Google Drive API service"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                str(self.credentials_path),
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            
            self.service = build('drive', 'v3', credentials=credentials)
            logger.info("Google Drive service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Drive service: {e}")
            self.service = None
            raise

    def sync_folder(
        self,
        folder_id: str,
        project_id: str,
        local_path: Optional[str] = None,
        force: bool = False
    ) -> List[Dict]:
        """
        Sync a Google Drive folder RECURSIVELY to local project
        
        Args:
            folder_id: Google Drive folder ID (root folder)
            project_id: Project ID for database registration
            local_path: Optional local path (defaults to project documents/)
            force: Force re-download all files (ignore hash checks)
        
        Returns:
            List of synced file metadata dicts with full paths
        """
        if not self.service:
            raise RuntimeError("Drive service not initialized")

        # Clean folder_id (remove leading/trailing spaces)
        folder_id = folder_id.strip()

        logger.info(f"Starting RECURSIVE sync of Drive folder {folder_id} for project {project_id}")
        
        # Determine base local path
        if local_path:
            base_local_path = Path(local_path)
        else:
            base_local_path = Path(f"data/projects/{project_id}/documents")
        
        base_local_path.mkdir(parents=True, exist_ok=True)
        
        # List ALL files recursively
        all_files = self._list_files_recursive(
            folder_id=folder_id,
            path=""  # Start with empty path
        )
        
        logger.info(f"Found {len(all_files)} files (including subfolders)")
        
        synced_files = []
        skipped_files = []
        
        # Download each file preserving folder structure
        for drive_file in all_files:
            try:
                result = self._sync_single_file(
                    drive_file=drive_file,
                    base_local_path=base_local_path,
                    project_id=project_id,
                    force=force
                )
                
                if result['action'] == 'downloaded' or result['action'] == 'updated':
                    synced_files.append(result)
                elif result['action'] == 'skipped':
                    skipped_files.append(result)
                    
            except Exception as e:
                logger.error(f"Error syncing {drive_file['name']}: {e}")
        
        logger.info(
            f"Sync completed: {len(synced_files)} files synced, "
            f"{len(skipped_files)} skipped (unchanged)"
        )
        
        return synced_files

    def _list_files_recursive(
        self,
        folder_id: str,
        path: str = ""
    ) -> List[Dict]:
        """
        List ALL files in folder and subfolders RECURSIVELY
        
        Args:
            folder_id: Drive folder ID
            path: Current relative path (for tracking structure)
        
        Returns:
            List of file metadata dicts with 'drive_path' field
        """
        all_files = []
        
        try:
            # Query for ALL items in this folder
            query = f"'{folder_id}' in parents and trashed=false"
            
            page_token = None
            while True:
                results = self.service.files().list(
                    q=query,
                    fields="nextPageToken, files(id, name, mimeType, modifiedTime, md5Checksum, size)",
                    pageSize=1000,
                    pageToken=page_token
                ).execute()
                
                items = results.get('files', [])
                
                for item in items:
                    # Build full relative path
                    item_path = f"{path}/{item['name']}" if path else item['name']
                    
                    if item['mimeType'] == 'application/vnd.google-apps.folder':
                        # 🔴 CRITICAL: RECURSE into subfolder
                        logger.debug(f"Recursing into subfolder: {item_path}")
                        
                        subfolder_files = self._list_files_recursive(
                            folder_id=item['id'],
                            path=item_path
                        )
                        all_files.extend(subfolder_files)
                        
                    else:
                        # Regular file - add with full path
                        item['drive_path'] = item_path
                        all_files.append(item)
                        logger.debug(f"Found file: {item_path}")
                
                # Handle pagination
                page_token = results.get('nextPageToken')
                if not page_token:
                    break
            
            return all_files
            
        except Exception as e:
            logger.error(f"Error listing Drive folder {folder_id}: {e}")
            return []

    def _sync_single_file(
        self,
        drive_file: Dict,
        base_local_path: Path,
        project_id: str,
        force: bool = False
    ) -> Dict:
        """
        Sync a single file from Drive to local storage
        
        Args:
            drive_file: Drive file metadata (must have 'drive_path')
            base_local_path: Base local directory path
            project_id: Project ID
            force: Force download even if hash matches
        
        Returns:
            Dict with sync result and file info
        """
        file_id = drive_file['id']
        filename = drive_file['name']
        drive_path = drive_file['drive_path']  # Full relative path with folders
        drive_hash = drive_file.get('md5Checksum', '')
        
        # Construct local path preserving folder structure
        local_file_path = base_local_path / drive_path
        local_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file exists and hasn't changed
        if local_file_path.exists() and not force:
            local_hash = self._compute_file_hash(str(local_file_path))
            
            if local_hash == drive_hash:
                logger.debug(f"Skipping unchanged file: {drive_path}")
                return {
                    'action': 'skipped',
                    'name': filename,
                    'path': str(local_file_path),
                    'drive_path': drive_path,
                    'drive_id': file_id
                }
        
        # Download file
        logger.info(f"Downloading: {drive_path}")
        
        try:
            request = self.service.files().get_media(fileId=file_id)
            
            with io.FileIO(str(local_file_path), 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        progress = int(status.progress() * 100)
                        logger.debug(f"Download progress: {progress}%")
            
            # Register in database if available
            if self.db:
                try:
                    file_ext = local_file_path.suffix.lower().strip('.')
                    file_size = int(drive_file.get('size', 0))
                    
                    # Check if already registered
                    existing = self.db.get_file_by_path(project_id, drive_path)
                    
                    if existing:
                        # Update existing record
                        self.db.update_file(
                            existing['id'],
                            file_hash=drive_hash,
                            file_size=file_size,
                            status="pending",  # Will be indexed by RAG
                            metadata={
                                "drive_folder_structure": drive_path,
                                "drive_file_id": file_id,
                                "synced_at": datetime.now().isoformat()
                            }
                        )
                        logger.debug(f"Updated file record: {filename}")
                    else:
                        # Create new record
                        self.db.add_file(
                            project_id=project_id,
                            filename=filename,
                            file_path=drive_path,  # Store relative path
                            file_type=file_ext,
                            file_hash=drive_hash,
                            file_size=file_size,
                            status="pending",
                            metadata={
                                "drive_folder_structure": drive_path,
                                "drive_file_id": file_id,
                                "synced_at": datetime.now().isoformat()
                            }
                        )
                        logger.debug(f"Registered new file: {filename}")
                        
                except Exception as db_error:
                    logger.warning(f"Could not register {filename} in DB: {db_error}")
            
            action = 'updated' if local_file_path.exists() else 'downloaded'
            
            return {
                'action': action,
                'name': filename,
                'path': str(local_file_path),
                'drive_path': drive_path,
                'drive_id': file_id,
                'size': drive_file.get('size', 0),
                'modified': drive_file.get('modifiedTime', '')
            }
            
        except Exception as e:
            logger.error(f"Error downloading {filename}: {e}")
            return {
                'action': 'error',
                'name': filename,
                'error': str(e)
            }

    def _compute_file_hash(self, filepath: str) -> str:
        """Compute MD5 hash of file (matches Drive's md5Checksum)"""
        md5 = hashlib.md5()
        
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    md5.update(chunk)
            return md5.hexdigest()
        except Exception as e:
            logger.error(f"Error computing hash for {filepath}: {e}")
            return ""

    def list_files(self, folder_id: str, recursive: bool = True) -> List[Dict]:
        """
        List files in a Google Drive folder
        
        Args:
            folder_id: Google Drive folder ID
            recursive: If True, list files in subfolders too
        
        Returns:
            List of file metadata dicts
        """
        if not self.service:
            raise RuntimeError("Drive service not initialized")
        
        if recursive:
            return self._list_files_recursive(folder_id, "")
        else:
            # Non-recursive: only immediate children
            try:
                query = f"'{folder_id}' in parents and trashed=false"
                results = self.service.files().list(
                    q=query,
                    fields="files(id, name, mimeType, modifiedTime, size)",
                    pageSize=100
                ).execute()
                
                return results.get('files', [])
                
            except Exception as e:
                logger.error(f"Error listing Drive folder: {e}")
                return []

    def get_folder_stats(self, folder_id: str) -> Dict:
        """
        Get statistics about a Drive folder
        
        Args:
            folder_id: Google Drive folder ID
        
        Returns:
            Dict with file counts, total size, etc.
        """
        if not self.service:
            raise RuntimeError("Drive service not initialized")
        
        try:
            all_files = self._list_files_recursive(folder_id, "")
            
            total_size = sum(int(f.get('size', 0)) for f in all_files)
            
            # Count by type
            type_counts = {}
            for f in all_files:
                ext = Path(f['name']).suffix.lower()
                type_counts[ext] = type_counts.get(ext, 0) + 1
            
            return {
                'total_files': len(all_files),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'file_types': type_counts,
                'has_subfolders': any('/' in f['drive_path'] for f in all_files)
            }
            
        except Exception as e:
            logger.error(f"Error getting folder stats: {e}")
            return {
                'total_files': 0,
                'error': str(e)
            }
