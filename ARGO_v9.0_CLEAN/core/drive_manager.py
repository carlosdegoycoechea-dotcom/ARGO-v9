"""
ARGO - Drive Manager
Wrapper for Google Drive synchronization
"""
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from tools.google_drive_sync import GoogleDriveSync
from core.logger import get_logger

logger = get_logger("DriveManager")


class DriveManager:
    """
    Drive Manager - Simplified interface for Google Drive sync

    This is a wrapper around GoogleDriveSync to provide per-project
    synchronization functionality.
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

        if not self.credentials_path.exists():
            raise FileNotFoundError(f"Google credentials not found: {credentials_path}")

        logger.info(f"DriveManager initialized with credentials: {credentials_path}")

    def sync_folder(
        self,
        folder_id: str,
        project_id: str,
        local_path: Optional[str] = None
    ) -> List[Dict]:
        """
        Sync a Google Drive folder to local project

        Args:
            folder_id: Google Drive folder ID
            project_id: Project ID for database registration
            local_path: Optional local path (defaults to project path)

        Returns:
            List of synced file metadata dicts
        """
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload
        import io

        logger.info(f"Syncing Drive folder {folder_id} for project {project_id}")

        try:
            # Initialize Drive service
            credentials = service_account.Credentials.from_service_account_file(
                str(self.credentials_path),
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )

            service = build('drive', 'v3', credentials=credentials)

            # List files in folder
            query = f"'{folder_id}' in parents and trashed=false"
            results = service.files().list(
                q=query,
                fields="files(id, name, mimeType, modifiedTime, size)",
                pageSize=100
            ).execute()

            files = results.get('files', [])
            synced_files = []

            # Download each file
            for drive_file in files:
                # Skip folders
                if drive_file['mimeType'] == 'application/vnd.google-apps.folder':
                    continue

                file_id = drive_file['id']
                filename = drive_file['name']

                # Determine local path
                if local_path:
                    target_dir = Path(local_path)
                else:
                    # Default to project documents folder
                    target_dir = Path(f"data/projects/{project_id}/documents")

                target_dir.mkdir(parents=True, exist_ok=True)
                target_file = target_dir / filename

                # Download file
                logger.info(f"Downloading: {filename}")

                try:
                    request = service.files().get_media(fileId=file_id)

                    with io.FileIO(str(target_file), 'wb') as fh:
                        downloader = MediaIoBaseDownload(fh, request)
                        done = False
                        while not done:
                            status, done = downloader.next_chunk()

                    # Register in database if available
                    if self.db:
                        try:
                            file_ext = target_file.suffix.lower().strip('.')

                            self.db.register_file(
                                project_id=project_id,
                                filename=filename,
                                file_path=str(target_file),
                                file_type=file_ext,
                                file_hash="",  # Could compute hash if needed
                                file_size=int(drive_file.get('size', 0)),
                                chunk_count=0,  # Not chunked yet
                                metadata={
                                    "drive_folder_id": folder_id,
                                    "drive_file_id": file_id,
                                    "synced_at": datetime.now().isoformat()
                                }
                            )
                            logger.debug(f"Registered {filename} in database")
                        except Exception as db_error:
                            logger.warning(f"Could not register {filename} in DB: {db_error}")

                    synced_files.append({
                        'name': filename,
                        'path': str(target_file),
                        'drive_id': file_id,
                        'size': drive_file.get('size', 0),
                        'modified': drive_file.get('modifiedTime', '')
                    })

                except Exception as e:
                    logger.error(f"Error downloading {filename}: {e}")

            logger.info(f"Successfully synced {len(synced_files)} files")
            return synced_files

        except Exception as e:
            logger.error(f"Drive sync failed: {e}")
            raise

    def list_files(self, folder_id: str) -> List[Dict]:
        """
        List files in a Google Drive folder

        Args:
            folder_id: Google Drive folder ID

        Returns:
            List of file metadata dicts
        """
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        try:
            credentials = service_account.Credentials.from_service_account_file(
                str(self.credentials_path),
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )

            service = build('drive', 'v3', credentials=credentials)

            query = f"'{folder_id}' in parents and trashed=false"
            results = service.files().list(
                q=query,
                fields="files(id, name, mimeType, modifiedTime, size)",
                pageSize=100
            ).execute()

            return results.get('files', [])

        except Exception as e:
            logger.error(f"Error listing Drive folder: {e}")
            return []
