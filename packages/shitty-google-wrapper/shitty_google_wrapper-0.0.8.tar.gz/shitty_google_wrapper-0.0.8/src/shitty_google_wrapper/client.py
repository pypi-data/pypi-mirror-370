import io
import os
import json
import mimetypes
from google.cloud import storage
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# ==============================================================================
#  1. THE REUSABLE API CLIENT CLASS
# ==============================================================================

class GoogleApiClient:
    """
    A client to interact with Google Drive, Sheets, and Publisher APIs.
    Manages services and authentication in a self-contained object.
    """
    def __init__(self, credentialsDict, verbose=False):
        """
        Initializes the client with service account credentials.

        Args:
            credentialsDict (dict): A dictionary of the service account JSON key.
            verbose (bool): If True, prints status messages for operations.
        """
        if not isinstance(credentialsDict, dict) or 'client_email' not in credentialsDict:
            raise ValueError("A valid service account credentials dictionary is required.")

        parsed = {}
        for key in credentialsDict:
            parsed[key] = credentialsDict[key].replace("\n\n", "\n")
        credentialsDict = parsed
        
        self.credsDict = credentialsDict
        self.verbose = verbose

        # Private placeholders for services (will be lazy-loaded)
        self._driveService = None
        self._gspreadService = None
        self._publisherService = None
        self._reportingService = None
        self._storageService = None
        self._storageModule = None

    def _getCreds(self, scopes):
        """Helper to create credentials for specific scopes."""
        return ServiceAccountCredentials.from_json_keyfile_dict(self.credsDict, scopes)

    @property
    def driveService(self):
        """Lazy-loads and returns the Google Drive API service client."""
        if not self._driveService:
            creds = self._getCreds(['https://www.googleapis.com/auth/drive'])
            self._driveService = build('drive', 'v3', credentials=creds)
            if self.verbose: print("[Client] Google Drive service initialized.")
        return self._driveService

    @property
    def gspreadService(self):
        """Lazy-loads and returns the gspread service client."""
        if not self._gspreadService:
            creds = self._getCreds(['https://www.googleapis.com/auth/drive'])
            self._gspreadService = gspread.authorize(creds)
            if self.verbose: print("[Client] gspread service initialized.")
        return self._gspreadService

    @property
    def publisherService(self):
        """Lazy-loads and returns the Android Publisher API service client."""
        if not self._publisherService:
            creds = self._getCreds(['https://www.googleapis.com/auth/androidpublisher'])
            self._publisherService = build('androidpublisher', 'v3', credentials=creds)
            if self.verbose: print("[Client] Android Publisher service initialized.")
        return self._publisherService

    @property
    def reportingService(self):
        """Lazy-loads and returns the reporting service client."""
        if not self._reportingService:
            creds = self._getCreds(['https://www.googleapis.com/auth/playdeveloperreporting'])
            self._reportingService = build('playdeveloperreporting', 'v1beta1', credentials=creds)
            if self.verbose: print("[Client] Google play developer reporting service initialized.")
        return self._reportingService

    @property
    def storageService(self):
        """Lazy-loads and returns the google storage service client."""
        if not self._storageService:
            self._storageService = storage.Client.from_service_account_info(self.credsDict)
            if self.verbose: print("[Client] storage service initialized.")
        return self._storageService

    @property
    def storageModule(self):
        """Lazy-loads and returns the google storage module."""
        if not self._storageModule:
            self._storageModule = storage
            if self.verbose: print("[Client] storage module initialized.")
        return self._storageModule

    def _getFileByName(self, name):
        """
        Internal helper to find a single file or folder by its exact name.
        Raises FileNotFoundError or ValueError for invalid states.
        """
        query = f"name = '{name}' and trashed = false"
        results = self.driveService.files().list(q=query, fields="files(id, name, parents)").execute()
        files = results.get('files', [])

        if not files:
            raise FileNotFoundError(f"No file or folder found with name: '{name}'")
        if len(files) > 1:
            raise ValueError(f"More than one item found with name: '{name}'")
        
        return files[0]

    def _downloadFileContentById(self, fileId):
        """Internal helper to download file content using a file ID."""
        request = self.driveService.files().get_media(fileId=fileId)
        data = io.BytesIO()
        downloader = MediaIoBaseDownload(data, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if self.verbose: print(f"Download {int(status.progress() * 100)}%")
        
        if self.verbose: print(f"File ID {fileId} data downloaded.")
        return data.getvalue().decode('utf-8', 'backslashreplace')

    def downloadFileByName(self, fileName):
        """Downloads a file's content given its name."""
        if self.verbose: print(f"Searching for file '{fileName}'...")
        fileInfo = self._getFileByName(fileName)
        fileId = fileInfo['id']
        
        if self.verbose: print(f"Found file ID: {fileId}. Downloading content...")
        # UPDATED: Now uses the central download helper
        return self._downloadFileContentById(fileId)

    def listFiles(self, folderName=None):
        """Lists files and folders, optionally within a specific folder."""
        query = ""
        if folderName:
            if self.verbose: print(f"Finding folder '{folderName}'...")
            folderInfo = self._getFileByName(folderName)
            query = f"'{folderInfo['id']}' in parents and trashed = false"
        
        results = self.driveService.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType)",
            pageSize=100
        ).execute()
        return results.get('files', [])

    def uploadFile(self, localData, destinationName, destinationFolder=None):
        """
        Uploads data to a file on Google Drive.
        Updates the file if it exists, otherwise creates it.
        Optionally places it in a specified folder.
        """
        # Determine MIME type automatically
        mimeType, _ = mimetypes.guess_type(destinationName)
        if mimeType is None:
            mimeType = 'application/octet-stream' # Default binary type
        
        media = MediaIoBaseUpload(io.BytesIO(localData.encode('utf-8')), mimetype=mimeType, resumable=True)
        
        try:
            # Check if file exists to update it
            existingFile = self._getFileByName(destinationName)
            if self.verbose: print(f"File '{destinationName}' exists. Updating...")
            results = self.driveService.files().update(
                fileId=existingFile['id'],
                media_body=media
            ).execute()
            message = "File updated"
        except FileNotFoundError:
            # File doesn't exist, so create it
            if self.verbose: print(f"File '{destinationName}' not found. Creating...")
            fileMetadata = {'name': destinationName}
            results = self.driveService.files().create(
                body=fileMetadata,
                media_body=media,
                fields='id',
                supportsAllDrives=True
            ).execute()
            message = "File created"

        fileId = results.get('id')
        if self.verbose: print(f"{message}: {results}")

        if destinationFolder:
            self.moveFile(destinationName, destinationFolder)
        
        return fileId

    def deleteFileByName(self, fileName):
        """Finds a file by name and deletes it."""
        if self.verbose: print(f"Finding '{fileName}' to delete...")
        fileInfo = self._getFileByName(fileName)
        self.driveService.files().delete(fileId=fileInfo['id']).execute()
        if self.verbose: print(f"File '{fileName}' (ID: {fileInfo['id']}) deleted successfully.")

    def moveFile(self, fileName, folderName):
        """Moves a file to a specified folder."""
        if self.verbose: print(f"Moving '{fileName}' to folder '{folderName}'...")
        fileInfo = self._getFileByName(fileName)
        folderInfo = self._getFileByName(folderName)

        # Retrieve the file's existing parents to remove them
        previousParents = ",".join(fileInfo.get('parents', []))

        self.driveService.files().update(
            fileId=fileInfo['id'],
            addParents=folderInfo['id'],
            removeParents=previousParents,
            fields='id, parents'
        ).execute()
        if self.verbose: print("Move complete.")

    def getFileWithName(self, name):
        """Finds a file by name, handling cases of zero or multiple matches."""
        results = self.driveService.files().list(
            q=f"name = '{name}' and trashed = false",
            fields="nextPageToken, files(id, name)"
        ).execute()
        response = results.get('files', [])

        if len(response) == 1:
            return response[0]
        elif len(response) == 0:
            print(f"Warning: No files found named '{name}'")
            return None
        else:
            print(f"Warning: More than one file found named '{name}'")
            return None

    def getFileIdWithName(self, name):
        """Gets the ID of a file by its name."""
        data = self.getFileWithName(name)
        if data is None:
            return None
        return data.get("id")
    
    def getFileData(self, fileId):
        """Downloads a file's content given its file ID."""
        if self.verbose: print(f"Downloading content for file ID: {fileId}...")
        return self._downloadFileContentById(fileId)


    # CONSOLE LOGIC IS NOW A METHOD OF THE CLASS
    def runConsole(self):
        """Runs the interactive command-line application using this client instance."""
        print("\nGoogle API Client Initialized. Type 'help' for commands.")

        while True:
            try:
                commandStr = input(">> ").strip()
                if not commandStr:
                    continue

                parts = commandStr.split(maxsplit=2)
                action = parts[0].lower()
                
                if action == 'exit':
                    break
                
                elif action == 'help':
                    print("Commands:\n"
                          "  open <filename>\t\t- Download and print file content\n"
                          "  list [foldername]\t\t- List files in root or a folder\n"
                          "  save <filename> <data>\t- Save data to a file\n"
                          "  delete <filename>\t\t- Delete a file\n"
                          "  move <filename> <foldername>\t- Move a file to a folder\n"
                          "  exit\t\t\t\t- Close the application")

                elif action == 'open':
                    fileContent = self.downloadFileByName(parts[1])
                    print("-" * 20 + f"\n{fileContent}\n" + "-" * 20)

                elif action == 'list':
                    folder = parts[1] if len(parts) > 1 else None
                    files = self.listFiles(folder)
                    if not files:
                        print("No files found.")
                    else:
                        for item in files:
                            print(f"- {item['name']} ({item['mimeType']})")
                
                elif action == 'save':
                    self.uploadFile(localData=parts[2], destinationName=parts[1])
                
                elif action == 'delete':
                    self.deleteFileByName(parts[1])
                
                elif action == 'move':
                    self.moveFile(fileName=parts[1], folderName=parts[2])

                else:
                    print(f"Unknown command: '{action}'. Type 'help' for options.")

            except IndexError:
                print("Error: Not enough arguments for the command. Type 'help'.")
            except (FileNotFoundError, ValueError, gspread.exceptions.SpreadsheetNotFound) as e:
                print(f"ERROR: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")


# ==============================================================================
#  SCRIPT EXECUTION ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    credsPath = 'credentials.json'
    
    try:
        with open(credsPath) as f:
            credentialsDict = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"ERROR: Credentials file not found or invalid. Please create '{credsPath}'.")
        exit()

    # 1. Create an instance of the class
    client = GoogleApiClient(credentialsDict, verbose=True)
    
    # 2. Call the new method on the instance to start the console
    client.runConsole()