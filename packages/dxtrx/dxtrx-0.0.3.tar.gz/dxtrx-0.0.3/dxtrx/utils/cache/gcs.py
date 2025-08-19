import json
import bz2
import gzip
import asyncio
import google.cloud.storage


class GCSCache:
    """Filesystem and object storage based cache with compression support."""

    def __init__(self, fs, cache_root: str, compression: str = "bz2"):
        """
        Initialize the filesystem cache.

        Args:
            fs: Filesystem object (e.g., from fsspec)
            cache_root: Root directory for cache files
            compression: Compression method ("bz2" or "gzip")
        """
        self.fs = fs
        self.cache_root = cache_root
        self.compression = compression
        
        if cache_root.startswith("gs://"):
            self.gcs_client = google.cloud.storage.Client()

        if compression not in ("bz2", "gzip"):
            raise ValueError(f"Unsupported compression: {compression}")

    async def read(self, path: str) -> dict:
        """Read and decompress cache data from file."""
        full_path = self._get_full_path(path)

        def _read_sync():
            # Try different reading approaches for GCS
            if full_path.startswith("gs://") and hasattr(self, 'gcs_client'):
                # Use GCS client directly to bypass fsspec truncation issue
                try:
                    bucket_name, *blob_parts = full_path.replace("gs://", "").split("/")
                    blob_name = "/".join(blob_parts)
                    bucket = self.gcs_client.bucket(bucket_name)
                    blob = bucket.blob(blob_name)
                    
                    content_bytes = blob.download_as_bytes()
                    
                    # Try to parse as JSON directly (auto-decompressed)
                    try:
                        content = content_bytes.decode("utf-8")
                        return json.loads(content)
                    except json.JSONDecodeError as e:
                        # Fall back to compression logic below with the GCS data
                        data = content_bytes
                except Exception as e:
                    # Fall back to regular read
                    pass
            
            with self.fs.open(full_path, "rb") as f:
                data = f.read()

            # Try expected decompression
            try:
                if self.compression == "bz2":
                    return json.loads(bz2.decompress(data).decode("utf-8"))
                elif self.compression == "gzip":
                    return json.loads(gzip.decompress(data).decode("utf-8"))
            except Exception as e1:
                
                # Fallback: maybe data is already decompressed
                try:
                    return json.loads(data.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as e2:
                    raise ValueError(
                        f"Cache data is neither valid {self.compression} compressed data nor valid JSON.\n"
                        f"Decompression error: {e1}\n"
                        f"JSON decode error: {e2}\n"
                        f"Raw prefix: {data[:128]}"
                    )

        return await asyncio.to_thread(_read_sync)


    async def write(self, path: str, data: dict):
        """Compress and write cache data to file."""
        full_path = self._get_full_path(path)

        def _write_sync():
            if self.compression == "bz2":
                compressed = bz2.compress(json.dumps(data).encode("utf-8"))
            elif self.compression == "gzip":
                compressed = gzip.compress(json.dumps(data).encode("utf-8"))

            with self.fs.open(full_path, "wb") as f:
                f.write(compressed)
                
            if self.compression == "gzip" and full_path.startswith("gs://"):
                bucket_name, *blob_parts = full_path.replace("gs://", "").split("/")
                blob_name = "/".join(blob_parts)
                bucket = self.gcs_client.bucket(bucket_name)
                blob = bucket.blob(blob_name)

                blob.content_type = "application/json"
                blob.content_encoding = "gzip"
                blob.patch()

        await asyncio.to_thread(_write_sync)

    def _get_full_path(self, path: str) -> str:
        """Generate cache file path based on parameters."""
        return f"{self.cache_root}/{path}"
