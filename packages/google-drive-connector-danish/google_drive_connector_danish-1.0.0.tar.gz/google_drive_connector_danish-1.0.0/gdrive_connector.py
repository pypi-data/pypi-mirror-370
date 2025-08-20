import os
import io
import logging
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("google_drive_connector.log"),
        logging.StreamHandler()
    ]
)


class GoogleDriveConnector:
    """
    A utility class to interact with Google Drive using OAuth 2.0 credentials.
    
    This class supports:
    - Uploading and downloading files
    - Creating and deleting folders
    - Uploading and downloading folders recursively
    - Listing files with optional folder filter
    
    File/folder references can be passed by either their ID or name.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        access_token: str,
        refresh_token: str,
        token_uri: str,
        scopes: List[str],
    ) -> None:
        """
        Initialize the Google Drive API client with OAuth2 credentials.
        
        Automatically refreshes credentials if expired.
        """
        try:
            creds = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri=token_uri,
                client_id=client_id,
                client_secret=client_secret,
                scopes=scopes,
            )

            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    logging.info("Refreshing expired Google Drive credentials...")
                    creds.refresh(Request())

            self.service = build("drive", "v3", credentials=creds)
            logging.info("Google Drive client initialized successfully.")
        except Exception as e:
            logging.error("Failed to initialize Google Drive client: %s", e)
            raise

    # ==============================
    # Internal helper methods
    # ==============================

    def _find_files_by_name(self, name: str, mime_type: Optional[str] = None) -> List[Dict]:
        """
        Find all files in Google Drive that match the given name and optional mime_type.
        
        Args:
            name: Name of the file/folder to search.
            mime_type: Optional mime type filter.
            
        Returns:
            A list of file dictionaries (id, name, mimeType).
        """
        try:
            q = f"name = '{name}'"
            if mime_type:
                q += f" and mimeType = '{mime_type}'"

            results = self.service.files().list(
                q=q,
                fields="files(id, name, mimeType)",
                spaces="drive"
            ).execute()

            files = results.get("files", [])
            if not files:
                logging.warning("No files found with name: %s", name)
            return files
        except Exception as e:
            logging.error("Error while searching for files with name '%s': %s", name, e)
            raise

    def _ensure_file_id(self, file_id_or_name: str) -> str:
        """
        Ensure we return a valid file ID given either an ID or a name.
        Raises FileNotFoundError if not found.
        """
        try:
            if len(file_id_or_name) < 25:  # crude ID vs name check
                matches = self._find_files_by_name(file_id_or_name)
                if not matches:
                    raise FileNotFoundError(f"No file found with name: {file_id_or_name}")
                if len(matches) > 1:
                    logging.warning("Multiple files found with name '%s'. Using first match.", file_id_or_name)
                return matches[0]["id"]
            return file_id_or_name
        except Exception as e:
            logging.error("Failed to resolve file ID for '%s': %s", file_id_or_name, e)
            raise

    def _ensure_folder_id(self, folder_id_or_name: str) -> str:
        """
        Ensure we return a valid folder ID given either an ID or a name.
        Raises FileNotFoundError if not found.
        """
        try:
            if len(folder_id_or_name) < 25:
                matches = self._find_files_by_name(folder_id_or_name, mime_type="application/vnd.google-apps.folder")
                if not matches:
                    raise FileNotFoundError(f"No folder found with name: {folder_id_or_name}")
                if len(matches) > 1:
                    logging.warning("Multiple folders found with name '%s'. Using first match.", folder_id_or_name)
                return matches[0]["id"]
            return folder_id_or_name
        except Exception as e:
            logging.error("Failed to resolve folder ID for '%s': %s", folder_id_or_name, e)
            raise

    # ==============================
    # Public API methods
    # ==============================

    def list_files(self, folder_id_or_name: Optional[str] = None, page_size: int = 10) -> List[Dict]:
        """
        List files in Google Drive, optionally inside a specific folder.
        
        Args:
            folder_id_or_name: Folder ID or name to list contents from.
            page_size: Max number of files to return.
        
        Returns:
            List of files with (id, name, mimeType).
        """
        try:
            if folder_id_or_name:
                folder_id = self._ensure_folder_id(folder_id_or_name)
                query = f"'{folder_id}' in parents"
                results = self.service.files().list(
                    q=query,
                    pageSize=page_size,
                    fields="files(id, name, mimeType)"
                ).execute()
            else:
                results = self.service.files().list(
                    pageSize=page_size,
                    fields="files(id, name, mimeType)"
                ).execute()
            files = results.get("files", [])
            logging.info("Listed %d files from folder '%s'", len(files), folder_id_or_name or "root")
            return files
        except Exception as e:
            logging.error("Error listing files: %s", e)
            raise

    def upload_file(self, file_path: str, mime_type: Optional[str] = None, folder_id_or_name: Optional[str] = None) -> str:
        """
        Upload a single file to Google Drive.
        
        Args:
            file_path: Local path of the file.
            mime_type: Optional MIME type.
            folder_id_or_name: Folder ID or name to upload into.
        
        Returns:
            File ID of the uploaded file.
        """
        try:
            file_metadata = {"name": os.path.basename(file_path)}
            if folder_id_or_name:
                folder_id = self._ensure_folder_id(folder_id_or_name)
                file_metadata["parents"] = [folder_id]
            media = MediaFileUpload(file_path, mimetype=mime_type)
            uploaded_file = self.service.files().create(
                body=file_metadata, media_body=media, fields="id"
            ).execute()
            file_id = uploaded_file.get("id")
            logging.info("Uploaded file '%s' (ID: %s)", file_path, file_id)
            return file_id
        except Exception as e:
            logging.error("Failed to upload file '%s': %s", file_path, e)
            raise

    def download_file(self, file_id_or_name: str, destination_path: str) -> str:
        """
        Download a file from Google Drive.
        
        Args:
            file_id_or_name: File ID or name to download.
            destination_path: Local path to save the file.
        
        Returns:
            Local path of downloaded file.
        """
        try:
            file_id = self._ensure_file_id(file_id_or_name)
            request = self.service.files().get_media(fileId=file_id)
            with io.FileIO(destination_path, "wb") as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        logging.info("Download progress: %d%%", int(status.progress() * 100))
            logging.info("Downloaded file '%s' to '%s'", file_id_or_name, destination_path)
            return destination_path
        except Exception as e:
            logging.error("Failed to download file '%s': %s", file_id_or_name, e)
            raise

    def create_folder(self, folder_name: str, parent_id_or_name: Optional[str] = None) -> str:
        """
        Create a new folder in Google Drive.
        
        Args:
            folder_name: Name of the new folder.
            parent_id_or_name: Optional parent folder.
        
        Returns:
            ID of the created folder.
        """
        try:
            file_metadata = {"name": folder_name, "mimeType": "application/vnd.google-apps.folder"}
            if parent_id_or_name:
                parent_id = self._ensure_folder_id(parent_id_or_name)
                file_metadata["parents"] = [parent_id]
            folder = self.service.files().create(body=file_metadata, fields="id").execute()
            folder_id = folder.get("id")
            logging.info("Created folder '%s' (ID: %s)", folder_name, folder_id)
            return folder_id
        except Exception as e:
            logging.error("Failed to create folder '%s': %s", folder_name, e)
            raise

    def delete_file_or_folder(self, file_id_or_name: str) -> bool:
        """
        Delete a file or folder in Google Drive.
        
        Args:
            file_id_or_name: File/folder ID or name.
        
        Returns:
            True if successful.
        """
        try:
            file_id = self._ensure_file_id(file_id_or_name)
            self.service.files().delete(fileId=file_id).execute()
            logging.info("Deleted file/folder '%s'", file_id_or_name)
            return True
        except Exception as e:
            logging.error("Failed to delete '%s': %s", file_id_or_name, e)
            raise

    def _download_folder_recursive(self, folder_id: str, destination_path: str) -> None:
        """Helper: Recursively download folder contents."""
        try:
            os.makedirs(destination_path, exist_ok=True)
            query = f"'{folder_id}' in parents"
            results = self.service.files().list(q=query, fields="files(id, name, mimeType)").execute()
            for item in results.get("files", []):
                if item["mimeType"] == "application/vnd.google-apps.folder":
                    logging.info("Recursively downloading subfolder '%s'", item["name"])
                    self._download_folder_recursive(item["id"], os.path.join(destination_path, item["name"]))
                else:
                    self.download_file(item["id"], os.path.join(destination_path, item["name"]))
        except Exception as e:
            logging.error("Failed to download folder recursively: %s", e)
            raise

    def download_folder(self, folder_id_or_name: str, destination_path: str) -> bool:
        """
        Download all contents of a folder (recursively).
        
        Args:
            folder_id_or_name: Folder ID or name.
            destination_path: Local destination path.
        
        Returns:
            True if successful.
        """
        try:
            folder_id = self._ensure_folder_id(folder_id_or_name)
            self._download_folder_recursive(folder_id, destination_path)
            logging.info("Downloaded folder '%s' to '%s'", folder_id_or_name, destination_path)
            return True
        except Exception as e:
            logging.error("Failed to download folder '%s': %s", folder_id_or_name, e)
            raise

    def upload_folder(self, local_folder_path: str, drive_parent_folder_id_or_name: Optional[str] = None) -> bool:
        """
        Upload a local folder (with subfolders and files) to Google Drive.
        
        Args:
            local_folder_path: Path of local folder.
            drive_parent_folder_id_or_name: Parent folder in Drive (optional).
        
        Returns:
            True if successful.
        """
        try:
            parent_id = None
            if drive_parent_folder_id_or_name:
                parent_id = self._ensure_folder_id(drive_parent_folder_id_or_name)

            folder_name = os.path.basename(os.path.normpath(local_folder_path))
            target_folder_id = self.create_folder(folder_name, parent_id_or_name=parent_id)

            for filename in os.listdir(local_folder_path):
                file_path = os.path.join(local_folder_path, filename)
                if os.path.isfile(file_path):
                    self.upload_file(file_path, folder_id_or_name=target_folder_id)
                elif os.path.isdir(file_path):
                    logging.info("Recursively uploading subfolder '%s'", filename)
                    self.upload_folder(file_path, drive_parent_folder_id_or_name=target_folder_id)

            logging.info("Uploaded folder '%s' successfully", local_folder_path)
            return True
        except Exception as e:
            logging.error("Failed to upload folder '%s': %s", local_folder_path, e)
            raise
