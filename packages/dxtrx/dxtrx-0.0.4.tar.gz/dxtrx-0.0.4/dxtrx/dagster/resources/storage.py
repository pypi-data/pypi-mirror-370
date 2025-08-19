import os
import fsspec
import tempfile
import shutil
import dagster as dg
import gzip
import bz2
import lzma
import hashlib
from pathlib import Path

from typing import Iterator, Optional
from datetime import datetime
from contextlib import contextmanager
from pydantic import PrivateAttr, BaseModel

from dxtrx.utils.hash import hash_bytes_sha256, hash_file_streaming_sha256
from dxtrx.utils.logging import get_logger

class CopyFileResult(BaseModel):
    """
    Represents the result of a file copy operation.
    
    Attributes:
        file_name (str): Name of the copied file
        full_destination_path (str): Complete path where the file was copied to
        source_path (str): Original path of the source file
        file_size_mb (float): Size of the file in megabytes
        upload_ts (datetime): Timestamp when the file was uploaded
        file_sha256 (str): SHA-256 hash of the file contents
    """
    file_name: str
    full_destination_path: str
    source_path: str
    file_size_mb: float
    upload_ts: datetime
    file_sha256: str

class StorageResource(dg.ConfigurableResource):
    """
    A configurable resource for handling file storage operations using fsspec.
    This class provides a unified interface for file operations across different storage protocols.
    
    Attributes:
        protocol (str): The storage protocol to use (default: "file")
        root_path (str): The root path for remote storage operations (e.g., bucket paths)
        local_tmp_root_path (str): The root path for local temporary file downloads (default: "/tmp")
    """
    protocol: str = "file"
    root_path: str
    local_tmp_root_path: str
    
    _client: fsspec.filesystem = PrivateAttr()

    def setup_for_execution(self, context: dg.InitResourceContext):
        """Initialize the storage resource for execution with a logger and fsspec client.
        
        Args:
            context (dg.InitResourceContext): The Dagster context
        """
        if type(context) is dict and len(context.keys()) == 0:
            self._logger = get_logger(f"{self.__class__.__name__}_logger")
        else:
            self._logger = dg.get_dagster_logger()
        self._client = fsspec.filesystem(self.protocol)

    def _get_fsspec_full_path(self, path: str):
        """Construct the full fsspec path by combining protocol and root path.
        
        Args:
            path (str): The path to construct the full fsspec path for
            
        Returns:
            str: The full fsspec path
        """
        return f"{self.protocol}://{self.root_path}/{path}"
    
    def _check_if_path_includes_protocol(self, path: str) -> bool:
        """Check if the path includes a protocol.
        
        Args:
            path (str): The path to check if it includes a protocol
            
        """
        return "://" in path
    
    def _get_absolute_path_for_file_destination(self, fsspec_path: str) -> str:
        """
        Convert fsspec path to absolute path for local file system.
        Handles different file protocol formats.
        
        Args:
            fsspec_path (str): The fsspec path to convert
            
        Returns:
            str: The absolute path
            
        Raises:
            ValueError: If the protocol is not supported
        """
        if self.protocol == "file" and "file:///" in fsspec_path:
            return fsspec_path
        elif self.protocol == "file" and "file://" in fsspec_path and not fsspec_path.startswith("file:///"):
            return os.path.abspath(fsspec_path.replace("file://", ""))
        else:
            return fsspec_path
        
    def get_full_path(self, path: str):
        """Get the complete path for a given relative path.
        
        Args:
            path (str): The relative path to get the complete path for
            
        Returns:
            str: The complete path
        """
        full_path = self._get_fsspec_full_path(path)
        return self._get_absolute_path_for_file_destination(full_path)
    
    def _mkdirs_if_not_exists(self, path: str):
        """Create directories if they don't exist (only for local file system).
        
        Args:
            path (str): The path to create directories for
        """
        if self.protocol == "file":
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)

    def _detect_compression_type(self, file_path: str) -> Optional[str]:
        """Detect compression type based on file extension.
        
        Args:
            file_path (str): The file path to check for compression
            
        Returns:
            Optional[str]: The compression type ('gz', 'bz2', 'xz') or None if not compressed
        """
        path = Path(file_path)
        if path.suffix == ".gz":
            return "gz"
        elif path.suffix == ".bz2":
            return "bz2"
        elif path.suffix == ".xz":
            return "xz"
        return None

    def _decompress_file(self, compressed_path: str, compression_type: str) -> str:
        """Decompress a file and return the path to the decompressed file.
        
        Args:
            compressed_path (str): Path to the compressed file
            compression_type (str): Type of compression ('gz', 'bz2', 'xz')
            
        Returns:
            str: Path to the decompressed file
            
        Raises:
            ValueError: If compression type is not supported
            Exception: If decompression fails
        """
        compressed_path_obj = Path(compressed_path)
        
        # Remove the compression extension to get the decompressed filename
        if compression_type == "gz" and compressed_path_obj.suffix == ".gz":
            decompressed_path = str(compressed_path_obj.with_suffix(''))
        elif compression_type == "bz2" and compressed_path_obj.suffix == ".bz2":
            decompressed_path = str(compressed_path_obj.with_suffix(''))
        elif compression_type == "xz" and compressed_path_obj.suffix == ".xz":
            decompressed_path = str(compressed_path_obj.with_suffix(''))
        else:
            raise ValueError(f"Unsupported compression type: {compression_type}")

        self._logger.info(f"Decompressing {compressed_path} to {decompressed_path}")

        try:
            # Open the appropriate decompression stream
            if compression_type == "gz":
                open_func = gzip.open
            elif compression_type == "bz2":
                open_func = bz2.open
            elif compression_type == "xz":
                open_func = lzma.open
            else:
                raise ValueError(f"Unsupported compression type: {compression_type}")

            # Decompress the file
            with open_func(compressed_path, 'rb') as compressed_file:
                with open(decompressed_path, 'wb') as decompressed_file:
                    shutil.copyfileobj(compressed_file, decompressed_file)

            return decompressed_path

        except Exception as e:
            # Clean up partial decompressed file if it exists
            if os.path.exists(decompressed_path):
                try:
                    os.remove(decompressed_path)
                except:
                    pass
            raise Exception(f"Failed to decompress {compressed_path}: {e}")

    def copy_file(self, source_path: str, destination_path: str) -> CopyFileResult:
        """
        Copy a file from source to destination.
        
        Args:
            source_path (str): Path of the source file
            destination_path (str): Path where the file should be copied to
            
        Returns:
            CopyFileResult: Information about the copied file including metadata
        """
        self._mkdirs_if_not_exists(destination_path)
        fsspec_destination_path = self._get_fsspec_full_path(destination_path)
        display_destination_path = self._get_absolute_path_for_file_destination(fsspec_destination_path)

        self._logger.info(f"Copying file {source_path} to {display_destination_path}")

        with fsspec.open(source_path, "rb", expand=False) as source_file:
            with fsspec.open(fsspec_destination_path, "wb", expand=False) as destination_file:
                # Read the entire file into memory - note: this may not be suitable for very large files
                data = source_file.read()
                file_size_mb = len(data) / 1024 / 1024
                file_sha256 = hash_bytes_sha256(data)
                destination_file.write(data)

                del data  # Free up memory

        return CopyFileResult(
            file_name=destination_path.split("/")[-1],
            full_destination_path=display_destination_path,
            source_path=source_path,
            file_size_mb=file_size_mb,
            upload_ts=datetime.now(tz=None),
            file_sha256=file_sha256
        )

    def list_files(self, path: str):
        """List all files in the specified path.
        
        Args:
            path (str): The path to list files from
            
        Returns:
            list: A list of file paths
        """
        return self._client.ls(path)

    def get_file_bytes(self, path: str) -> bytes:
        """Download and return the contents of a file.
        
        Args:
            path (str): The path to get the file bytes from
            
        Returns:
            bytes: The file contents
        """
        with fsspec.open(path, "rb") as file:
            return file.read()

    def delete_file(self, path: str):
        """Delete a file at the specified path.
        
        Args:
            path (str): The path to delete the file from
        """
        self._client.rm(path)

    def upload_file(self, path: str, file_content: str):
        """Upload content to a file at the specified path.
        
        Args:
            path (str): The path to upload the file to
            file_content (str): The content to upload to the file
        """
        with fsspec.open(path, "w") as file:
            file.write(file_content)

    def exists(self, path: str) -> bool:
        """Check if a file exists at the specified path.
        
        Args:
            path (str): The path to check if the file exists at
            
        Returns:
            bool: True if the file exists, False otherwise
        """
        fsspec_destination_path = self._get_fsspec_full_path(path)
        return self._client.exists(fsspec_destination_path)
    
    def get_file_details(self, path: str) -> dict:
        """Get detailed information about a file.
        
        Args:
            path (str): The path to get the file details for
            
        Returns:
            dict: Detailed information about the file
        """
        fsspec_destination_path = self._get_fsspec_full_path(path)
        return self._client.info(fsspec_destination_path)
    
    def get_sha256(self, path: str):
        """Calculate and return the SHA-256 hash of a file's contents.
        
        Args:
            path (str): The path to get the SHA-256 hash for
            
        Returns:
            str: The SHA-256 hash of the file contents
        """
        fsspec_destination_path = self._get_fsspec_full_path(path)
        with fsspec.open(fsspec_destination_path, "rb", expand=False) as source_file:
            file_sha256 = hash_file_streaming_sha256(source_file)
            return file_sha256
        
    def _get_predictable_temp_dir(self, remote_path: str = None) -> str:
        """Create a predictable temporary directory based on the local_tmp_root_path and optionally remote_path.
        
        Args:
            remote_path (str, optional): The remote path to include in the hash for uniqueness
        
        Returns:
            str: The path to the predictable temporary directory
        """
        # Create a hash of the root_path to make it predictable but unique
        root_hash = hashlib.md5(self.root_path.encode()).hexdigest()[:8]
        
        # Create temp directory name based on protocol and root_path hash
        if remote_path:
            # Include remote_path in the hash for path-specific predictable directories
            remote_hash = hashlib.md5(remote_path.encode()).hexdigest()[:8]
            temp_dir_name = f"dxtr_storage_{self.protocol}_{root_hash}_{remote_hash}"
        else:
            temp_dir_name = f"dxtr_storage_{self.protocol}_{root_hash}"
        
        # Use configured local_tmp_root_path as base instead of root_path
        predictable_temp_dir = os.path.join(self.local_tmp_root_path, temp_dir_name)
        
        # Ensure the directory exists
        os.makedirs(predictable_temp_dir, exist_ok=True)
        
        return predictable_temp_dir

    @contextmanager
    def download_to_temp_file(
        self,
        remote_path: str,
        *,
        suffix: str = "",
        delete: bool = True,
        skip_if_exists: bool = False,
        local_tmp_path_root: str = None,
        auto_decompress: bool = False,
    ) -> Iterator[str]:
        """
        Materialize *remote_path* in a local temporary file or directory and yield the path.
        The file/directory is deleted automatically when the context exits (unless
        ``delete=False``).

        **Path Resolution**: The method intelligently determines whether the remote_path 
        refers to a file or directory and creates appropriate local paths:
        - **Protocol Detection**: Automatically detects and uses the appropriate fsspec client (gs://, s3://, file://, etc.)
        - **Directory Detection**: Paths ending with "/" are automatically treated as directories
        - **Directories**: Use predictable temp directories based on remote_path hash
        - **Files**: Preserve original filename when possible, fallback to "model" for files without clear names
        - **URL Cleanup**: Parameters and fragments are automatically stripped from filenames

        **Auto-Decompression**: When ``auto_decompress=True``, files with supported 
        compression extensions (.gz, .bz2, .xz) are automatically decompressed. 
        The compressed file is downloaded first, then decompressed to a separate file.
        The yielded path points to the decompressed file. Both the compressed and 
        decompressed files are kept during execution and cleaned up on exit when ``delete=True``.
        If ``skip_if_exists=True``, existing compressed files are reused and only 
        decompressed if the decompressed version doesn't exist.

        Example
        -------
        >>> with storage.temp_download("models/model.pkl") as local_path:
        ...     model = joblib.load(local_path)
        >>> with storage.temp_download("models/model.bin.gz", auto_decompress=True) as local_path:
        ...     # local_path points to the decompressed model.bin file
        ...     model = load_model(local_path)
        >>> with storage.temp_download("models/") as local_dir:
        ...     # local_dir is a directory containing all files from models/
        >>> with storage.temp_download("gs://bucket/mlflow-artifacts/6/.../xgboost_model/") as model_dir:
        ...     # model_dir contains the MLflow model directory structure
        
        Args:
            remote_path (str): The path to download the file or directory from
            suffix (str): The suffix to add to the temporary file (ignored for directories)
            delete (bool): Whether to delete the temporary file/directory when the context exits.
                          For compressed files with auto_decompress=True, both the compressed 
                          and decompressed files are deleted.
            skip_if_exists (bool): Whether to skip download if target already exists locally.
                                  For compressed files, checks for the compressed file existence.
                                  If found, reuses it and decompresses only if needed.
            local_tmp_path_root (str): Optional root directory for temporary files. If not provided,
                                     a predictable temporary directory based on the storage local_tmp_root_path will be used.
                                     For predictable directories, the remote_path is also hashed to ensure
                                     each unique remote path gets its own predictable location.
            auto_decompress (bool): Whether to automatically decompress supported compressed files.
                                   Defaults to False for backward compatibility.
            
        Returns:
            Iterator[str]: The path to the temporary file or directory. For compressed files
                          with auto_decompress=True, this is the path to the decompressed file.
                          For directories, this is the path to the directory containing all downloaded files.
        """
        # Allow callers to pass either a full fsspec URI or a path relative to
        # the configured root.
        if not self._check_if_path_includes_protocol(remote_path):
            remote_path = self._get_fsspec_full_path(remote_path)

        # Get the appropriate client for this path (handles different protocols)
        path_client = self._get_client_for_path(remote_path)
        self._logger.debug(f"Using fsspec client for path {remote_path}: {type(path_client).__name__}")

        # Check if the remote path is a directory using fsspec
        is_directory = False
        
        # 🚨 Force is_directory=True if remote_path ends with "/" or has no basename
        # This handles cases like ".../xgboost_model/" which should be treated as directories
        if remote_path.rstrip().endswith("/") or not os.path.basename(remote_path.rstrip("/")):
            is_directory = True
            self._logger.info(f"✅ Forced directory mode due to trailing slash or empty basename: {remote_path}")
        
        # Only try fsspec detection if we haven't already determined it's a directory
        if not is_directory:
            try:
                remote_info = path_client.info(remote_path)
                is_directory = remote_info.get('type') == 'directory'
                self._logger.debug(f"info() result for {remote_path}: {remote_info}")
                if is_directory:
                    self._logger.info(f"✅ Detected {remote_path} as directory via info()")
            except Exception as e:
                self._logger.debug(f"Could not get info for {remote_path}: {e}. Trying alternative directory detection.")
                
                # Alternative directory detection for cloud storage (like GCS)
                # Try to list the path - if it returns multiple items, it's likely a directory
                try:
                    contents = path_client.ls(remote_path)
                    self._logger.debug(f"ls() result for {remote_path}: {contents}")
                    # If ls returns multiple items or the path with a trailing slash, it's a directory
                    if len(contents) > 1 or (len(contents) == 1 and contents[0] != remote_path):
                        is_directory = True
                        self._logger.info(f"✅ Detected {remote_path} as directory via ls() with {len(contents)} items")
                    else:
                        # Additional check: try listing with trailing slash
                        try:
                            slash_path = remote_path.rstrip('/') + '/'
                            slash_contents = path_client.ls(slash_path)
                            self._logger.debug(f"ls() with trailing slash for {slash_path}: {slash_contents}")
                            if len(slash_contents) > 0:
                                is_directory = True
                                remote_path = slash_path  # Use the slash version for download
                                self._logger.info(f"✅ Detected {remote_path} as directory via ls() with trailing slash")
                        except Exception as slash_e:
                            self._logger.debug(f"Could not list with trailing slash {slash_path}: {slash_e}")
                except Exception as ls_e:
                    self._logger.debug(f"Could not list {remote_path}: {ls_e}. Assuming it's a file.")
                    is_directory = False

        self._logger.info(f"🔍 Final decision: is_directory = {is_directory} for {remote_path}")

        if is_directory:
            self._logger.info(f"📁 Starting directory download for {remote_path}")
            # Handle directory download
            if local_tmp_path_root:
                os.makedirs(local_tmp_path_root, exist_ok=True)
                temp_dir = tempfile.mkdtemp(dir=local_tmp_path_root)
            else:
                # Use predictable directory based on remote_path
                temp_dir = self._get_predictable_temp_dir(remote_path)
            
            self._logger.info(f"📁 Created temp directory: {temp_dir}")
            
            try:
                # Check if we should skip download if directory already has content
                if skip_if_exists and os.path.exists(temp_dir) and os.listdir(temp_dir):
                    self._logger.info(f"Skipping download of {remote_path} - directory {temp_dir} already exists and is not empty")
                    yield temp_dir
                else:
                    self._logger.info(f"📁 Downloading directory {remote_path} to {temp_dir}")
                    # Ensure the target directory is empty for fsspec.get()
                    if os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir)
                    os.makedirs(temp_dir, exist_ok=True)
                    
                    # Download all files in the directory recursively
                    # For GCS, we need to ensure the path ends with / for directory downloads
                    download_path = remote_path.rstrip('/') + '/'
                    target_dir = temp_dir.rstrip('/') + '/'
                    path_client.get(download_path, target_dir, recursive=True)
                    self._logger.info(f"✅ Successfully downloaded directory {remote_path}")
                    yield temp_dir
            except Exception as e:
                self._logger.error(f"❌ Failed to download directory from {remote_path}: {e}")
                raise FileNotFoundError(f"Failed to download directory from {remote_path}: {e}")
            finally:
                if delete and os.path.exists(temp_dir):
                    self._logger.info(f"🗑️ Cleaning up directory {temp_dir}")
                    shutil.rmtree(temp_dir)
        else:
            self._logger.info(f"📄 Starting file download for {remote_path}")
            # Handle single file download
            
            # Determine final file paths
            if local_tmp_path_root:
                os.makedirs(local_tmp_path_root, exist_ok=True)
                # Use NamedTemporaryFile for custom tmp directory to maintain existing behavior
                temp_kwargs = {"delete": False, "suffix": suffix, "dir": local_tmp_path_root}
                tmp_file = tempfile.NamedTemporaryFile(**temp_kwargs)
                base_tmp_path = tmp_file.name
                tmp_file.close()  # Close the file handle but keep the file
            else:
                # Use predictable directory and filename based on remote_path
                predictable_temp_dir = self._get_predictable_temp_dir(remote_path)
                
                # Better filename resolution based on whether it's a file or directory
                # Get the basename after stripping trailing slashes
                remote_filename = os.path.basename(remote_path.rstrip("/"))
                
                # Preserve the original filename better by handling query parameters and fragments
                # Remove URL query parameters and fragments if present
                if '?' in remote_filename:
                    remote_filename = remote_filename.split('?')[0]
                if '#' in remote_filename:
                    remote_filename = remote_filename.split('#')[0]
                
                # Apply better fallback logic based on file vs directory context
                # Since we're in the file download branch, we know this should be a file
                if not remote_filename or remote_filename == '/':
                    # Use "model" as default for files instead of "downloaded_file"
                    remote_filename = "model"
                elif "." not in remote_filename:
                    # If no extension detected, it might be a model file without extension
                    # Keep the original name but consider it might need an extension later
                    pass  # Keep the remote_filename as is
                
                base_tmp_path = os.path.join(predictable_temp_dir, remote_filename + suffix)
            
            # Check if auto_decompress is enabled and file is compressed
            compression_type = None
            if auto_decompress:
                compression_type = self._detect_compression_type(remote_path)
            
            # Determine paths for compressed and decompressed files
            if compression_type:
                # For compressed files with auto_decompress=True
                compressed_path = base_tmp_path
                decompressed_path = self._get_decompressed_filename(base_tmp_path, compression_type)
                final_path = decompressed_path
            else:
                # For uncompressed files or when auto_decompress=False
                compressed_path = base_tmp_path
                decompressed_path = None
                final_path = base_tmp_path
            
            # Check if we should skip download (compressed file already exists)
            if skip_if_exists and os.path.exists(compressed_path) and os.path.getsize(compressed_path) > 0:
                self._logger.info(f"Skipping download of {remote_path} - compressed file {compressed_path} already exists")
                
                # If auto_decompress is enabled and decompressed file doesn't exist, decompress it
                if compression_type and decompressed_path and (not os.path.exists(decompressed_path) or os.path.getsize(decompressed_path) == 0):
                    self._logger.info(f"Decompressing existing file {compressed_path} to {decompressed_path}")
                    try:
                        self._decompress_file(compressed_path, compression_type)
                    except Exception as e:
                        self._logger.error(f"Failed to decompress existing file {compressed_path}: {e}")
                        # Fall through to re-download
                        pass
                    else:
                        # Successfully decompressed, yield the decompressed path
                        try:
                            yield final_path
                            return
                        finally:
                            # Cleanup logic
                            if delete:
                                if decompressed_path and os.path.exists(decompressed_path):
                                    os.remove(decompressed_path)
                                if os.path.exists(compressed_path):
                                    os.remove(compressed_path)
                
                # If no decompression needed or decompressed file already exists, just yield
                if not compression_type or (decompressed_path and os.path.exists(decompressed_path) and os.path.getsize(decompressed_path) > 0):
                    try:
                        yield final_path
                        return
                    finally:
                        # Cleanup logic
                        if delete:
                            if decompressed_path and os.path.exists(decompressed_path):
                                os.remove(decompressed_path)
                            if os.path.exists(compressed_path):
                                os.remove(compressed_path)
            
            # Download the file using streaming to avoid loading large files into memory
            try:
                self._logger.debug(f"Starting streaming download from {remote_path} to {compressed_path}")
                # Stream the file directly from remote to local using fsspec
                with fsspec.open(remote_path, "rb") as remote_file, open(compressed_path, "wb") as local_file:
                    shutil.copyfileobj(remote_file, local_file)
                self._logger.info(f"✅ Successfully streamed file from {remote_path} to {compressed_path}")
            except Exception as e:
                raise FileNotFoundError(f"Failed to download file from {remote_path}: {e}")
            
            # If auto_decompress is enabled and file is compressed, decompress it
            if compression_type and decompressed_path:
                try:
                    self._decompress_file(compressed_path, compression_type)
                    self._logger.info(f"Successfully decompressed {compression_type} file to {decompressed_path}")
                except Exception as e:
                    # Clean up compressed file and re-raise
                    if os.path.exists(compressed_path):
                        os.remove(compressed_path)
                    raise Exception(f"Failed to decompress {compressed_path}: {e}")
            
            try:
                yield final_path
            finally:
                # Smart cleanup: delete both files if they exist and delete=True
                if delete:
                    # Delete decompressed file if it exists
                    if decompressed_path and os.path.exists(decompressed_path):
                        os.remove(decompressed_path)
                    # Delete compressed file
                    if os.path.exists(compressed_path):
                        os.remove(compressed_path)

    def _get_decompression_func(self, compression_type: str):
        """Get the appropriate decompression function for the given compression type.
        
        Args:
            compression_type (str): The compression type ('gz', 'bz2', 'xz')
            
        Returns:
            callable: The decompression function that can wrap a file-like object
            
        Raises:
            ValueError: If compression type is not supported
        """
        decompression_map = {
            "gz": gzip.open,
            "bz2": bz2.open,
            "xz": lzma.open,
        }
        
        if compression_type not in decompression_map:
            raise ValueError(f"Unsupported compression type: {compression_type}")
            
        return decompression_map[compression_type]

    def _get_decompressed_filename(self, compressed_path: str, compression_type: str) -> str:
        """Get the decompressed filename for the given compressed file and compression type.
        
        Args:
            compressed_path (str): The path to the compressed file
            compression_type (str): The compression type ('gz', 'bz2', 'xz')
            
        Returns:
            str: The decompressed filename
        """
        compressed_path_obj = Path(compressed_path)
        
        # Remove the compression extension to get the decompressed filename
        if compression_type == "gz" and compressed_path_obj.suffix == ".gz":
            decompressed_path = str(compressed_path_obj.with_suffix(''))
        elif compression_type == "bz2" and compressed_path_obj.suffix == ".bz2":
            decompressed_path = str(compressed_path_obj.with_suffix(''))
        elif compression_type == "xz" and compressed_path_obj.suffix == ".xz":
            decompressed_path = str(compressed_path_obj.with_suffix(''))
        else:
            raise ValueError(f"Unsupported compression type: {compression_type}")

        return decompressed_path

    def _get_client_for_path(self, path: str):
        """Get the appropriate fsspec client for the given path.
        
        If the path includes a protocol (e.g., gs://, s3://), create a client for that protocol.
        Otherwise, use the configured client.
        
        Args:
            path (str): The path to get the client for
            
        Returns:
            fsspec.AbstractFileSystem: The appropriate fsspec client
        """
        if self._check_if_path_includes_protocol(path):
            # Extract protocol from the path
            protocol = path.split("://")[0]
            self._logger.debug(f"Creating fsspec client for protocol: {protocol}")
            return fsspec.filesystem(protocol)
        else:
            # Use the configured client
            return self._client