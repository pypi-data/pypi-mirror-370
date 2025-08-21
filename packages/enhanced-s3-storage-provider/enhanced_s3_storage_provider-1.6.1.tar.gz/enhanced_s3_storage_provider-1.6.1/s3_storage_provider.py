# -*- coding: utf-8 -*-
# Copyright 2018 New Vector Ltd
# Copyright 2021 The Matrix.org Foundation C.I.C.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import threading
import re
import time
import asyncio
from typing import Dict, Any, Optional, Set, List
from twisted.internet import reactor, defer, threads
from twisted.python.failure import Failure
from multiprocessing.pool import ThreadPool
from concurrent.futures import ThreadPoolExecutor

import boto3
import logging
from minio import Minio
from minio.error import S3Error
from synapse.logging.context import LoggingContext, make_deferred_yieldable
from synapse.rest.media.v1._base import Responder
from synapse.rest.media.v1.storage_provider import StorageProvider

# Try to import current_context from the new location, fall back to the old one
try:
    from synapse.logging.context import current_context
except ImportError:
    current_context = LoggingContext.current_context

logger = logging.getLogger("synapse.s3")

READ_CHUNK_SIZE = 8 * 1024 * 1024  # 8 MB

def parse_duration(duration_str: str) -> Optional[int]:
    """Parse a duration string into milliseconds.
    
    Supports formats:
    - Nd: N days
    - Nh: N hours
    - Nm: N minutes
    - Ns: N seconds
    - N: plain milliseconds
    
    Returns milliseconds or None if invalid
    """
    if duration_str is None:
        return None
        
    if isinstance(duration_str, (int, float)):
        return int(duration_str)
        
    duration_str = str(duration_str).strip().lower()
    if not duration_str:
        return None
        
    # Try to parse as plain milliseconds first
    try:
        return int(duration_str)
    except ValueError:
        pass
        
    # Parse duration with unit
    match = re.match(r'^(\d+)(d|h|m|s|min)$', duration_str)
    if not match:
        logger.warning("Invalid duration format: %s", duration_str)
        return None
        
    value, unit = match.groups()
    value = int(value)
    
    # Convert to milliseconds
    if unit == 'd':
        return value * 24 * 60 * 60 * 1000
    elif unit == 'h':
        return value * 60 * 60 * 1000
    elif unit == 'm' or unit == 'min':
        return value * 60 * 1000
    elif unit == 's':
        return value * 1000
    
    return None

class S3StorageProviderBackend(StorageProvider):
    def multipart_upload(self, file_path, bucket, key, extra_args=None, chunk_size=READ_CHUNK_SIZE):
        """
        Perform a manual multipart upload to S3 for better compatibility with S3-like backends.
        """

        extra_args = extra_args or {}
        file_size = os.path.getsize(file_path)
        logger.debug(f"Starting multipart upload: file={file_path}, size={file_size}, chunk_size={chunk_size}")

        # Use single-part upload for files < 5GB
        if file_size < 8 * 1024 * 1024:
            s3_client = self._get_s3_client()
            with open(file_path, "rb") as f:
                s3_client.put_object(Bucket=bucket, Key=key, Body=f, **extra_args)
            logger.debug(f"Single-part upload completed for {file_path}")
            return

        # Use MinIO for multipart upload for files >= 5GB
        endpoint = self.api_kwargs.get("endpoint_url", "")
        access_key = self.api_kwargs.get("aws_access_key_id", "")
        secret_key = self.api_kwargs.get("aws_secret_access_key", "")
        secure = endpoint.startswith("https://")
        minio_client = Minio(
            endpoint.replace("https://", "").replace("http://", ""),
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        try:
            with open(file_path, "rb") as f:
                minio_client.put_object(
                    bucket_name=bucket,
                    object_name=key,
                    data=f,
                    length=file_size,
                    part_size=chunk_size,
                )
            logger.info(f"MinIO multipart upload complete for {file_path}")
        except S3Error as e:
            logger.error(f"MinIO multipart upload failed for {key}: {e}")
            raise
    """Storage provider for S3 storage.

    Args:
        hs (HomeServer): Homeserver instance
        config: The config dict from the homeserver config
    """

    def __init__(self, hs, config):
        StorageProvider.__init__(self)
        self.hs = hs

        # Get paths from Synapse config
        self.media_store_path = hs.config.media.media_store_path
        try:
            self.uploads_path = hs.config.media.uploads_path
        except AttributeError:
            self.uploads_path = os.path.join(self.media_store_path, "uploads")
            logger.info("uploads_path not found in config, using: %s", self.uploads_path)

        self.cache_directory = self.media_store_path

        # Initialize storage settings with null values
        self.store_local = None
        self.store_remote = None
        self.store_synchronous = None
        self.local_media_lifetime = None
        self.remote_media_lifetime = None

        # Parse boolean values from config
        def parse_bool(value):
            if value is None:
                return None
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ("true", "yes", "1", "on")
            return bool(value)

        # Get settings directly from config
        self.store_local = parse_bool(config.get("store_local"))
        self.store_remote = parse_bool(config.get("store_remote"))
        self.store_synchronous = parse_bool(config.get("store_synchronous"))
        
        # Auto-restore configuration
        self.auto_restore_enabled = parse_bool(config.get("auto_restore", True))  # Default enabled
        self.auto_restore_startup = parse_bool(config.get("auto_restore_startup", True))
        self.auto_restore_monitor_interval = config.get("auto_restore_monitor_interval", 300)  # 5 minutes
        self.auto_restore_batch_size = config.get("auto_restore_batch_size", 50)  # Files per batch

        # Get media retention settings with duration parsing
        media_retention = config.get("media_retention", {})
        if isinstance(media_retention, dict):
            self.local_media_lifetime = parse_duration(media_retention.get("local_media_lifetime"))
            self.remote_media_lifetime = parse_duration(media_retention.get("remote_media_lifetime"))
        else:
            logger.warning("media_retention config is not a dictionary: %s", media_retention)

        logger.info(
            "S3 Storage Provider initialized with store_local=%s, store_remote=%s, store_synchronous=%s",
            self.store_local,
            self.store_remote,
            self.store_synchronous,
        )
        logger.info(
            "Media retention settings: local=%s, remote=%s milliseconds",
            self.local_media_lifetime,
            self.remote_media_lifetime,
        )

        # S3 configuration
        s3_config = config.get("config", {})
        if not s3_config:
            logger.warning("No config block found, falling back to root-level settings")
            self.bucket = config.get("bucket")
            self.api_kwargs = {
                "region_name": config.get("region_name"),
                "endpoint_url": config.get("endpoint_url"),
                "aws_access_key_id": config.get("access_key_id"),
                "aws_secret_access_key": config.get("secret_access_key"),
            }
            self.prefix = config.get("prefix", "")
            self.extra_args = config.get("extra_args", {})
        else:
            self.bucket = s3_config.get("bucket")
            self.api_kwargs = {
                "region_name": s3_config.get("region_name"),
                "endpoint_url": s3_config.get("endpoint_url"),
                "aws_access_key_id": s3_config.get("access_key_id"),
                "aws_secret_access_key": s3_config.get("secret_access_key"),
            }
            self.prefix = s3_config.get("prefix", "")
            self.extra_args = s3_config.get("extra_args", {})

        if not self.bucket:
            raise Exception("S3 bucket must be specified in config block")
        
        self.api_kwargs = {k: v for k, v in self.api_kwargs.items() if v is not None}
        
        if self.prefix and not self.prefix.endswith("/"):
            self.prefix += "/"

        self._s3_client = None
        self._s3_client_lock = threading.Lock()
        self._s3_pool = ThreadPool(1)
        self._pending_files = {}
        
        # Auto-restore components
        self._restore_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="s3-restore")
        self._restore_thread = None
        self._restore_stop_event = threading.Event()
        self._s3_file_cache = {}  # Cache of S3 files to avoid repeated listing
        self._cache_last_updated = 0
        self._cache_ttl = 3600  # Cache TTL in seconds (1 hour)
        
        logger.info("S3 Storage Provider initialized with bucket: %s", self.bucket)
        logger.info("Using media_store_path: %s", self.media_store_path)
        logger.info("Using uploads_path: %s", self.uploads_path)
        logger.info("Auto-restore enabled: %s (startup=%s, interval=%ds)", 
                   self.auto_restore_enabled, self.auto_restore_startup, self.auto_restore_monitor_interval)
        
        # Start auto-restore system if enabled
        if self.auto_restore_enabled:
            self._start_auto_restore_system()

    def _get_s3_client(self):
        """Get or create an S3 client."""
        if self._s3_client is None:
            with self._s3_client_lock:
                if self._s3_client is None:
                    self._s3_client = boto3.client(
                        "s3",
                        **self.api_kwargs,
                        config=boto3.session.Config(signature_version='s3v4'),
                    )
        return self._s3_client

    def _start_auto_restore_system(self):
        """Start the auto-restore monitoring system."""
        logger.info("Starting S3 auto-restore system")
        
        # Perform startup restoration if enabled
        if self.auto_restore_startup:
            reactor.callInThread(self._perform_startup_restore)
        
        # Start monitoring thread
        self._restore_thread = threading.Thread(
            target=self._auto_restore_monitor_loop,
            name="s3-auto-restore-monitor",
            daemon=True
        )
        self._restore_thread.start()
        logger.info("Auto-restore monitor thread started")

    def _perform_startup_restore(self):
        """Perform initial restore of all missing files at startup."""
        logger.info("Performing startup restore from S3")
        try:
            start_time = time.time()
            restored_count = 0
            
            # Update S3 cache first
            self._update_s3_file_cache()
            
            # Check both media_store_path and uploads_path
            paths_to_check = [self.media_store_path]
            if self.uploads_path != self.media_store_path:
                paths_to_check.append(self.uploads_path)
            
            for base_path in paths_to_check:
                if os.path.exists(base_path):
                    missing_files = self._find_missing_files(base_path)
                    if missing_files:
                        logger.info("Found %d missing files in %s", len(missing_files), base_path)
                        restored = self._restore_files_batch(missing_files)
                        restored_count += restored
                    
            duration = time.time() - start_time
            logger.info("Startup restore completed: %d files restored in %.2fs", restored_count, duration)
            
        except Exception as e:
            logger.error("Error during startup restore: %s", str(e))

    def _auto_restore_monitor_loop(self):
        """Main monitoring loop that runs in background thread."""
        logger.info("Auto-restore monitor loop started (interval: %ds)", self.auto_restore_monitor_interval)
        
        while not self._restore_stop_event.wait(self.auto_restore_monitor_interval):
            try:
                self._check_and_restore_missing_files()
            except Exception as e:
                logger.error("Error in auto-restore monitor loop: %s", str(e))
                
        logger.info("Auto-restore monitor loop stopped")

    def _check_and_restore_missing_files(self):
        """Check for missing files and restore them from S3."""
        logger.debug("Checking for missing files to restore")
        
        # Update S3 cache if needed
        current_time = time.time()
        if current_time - self._cache_last_updated > self._cache_ttl:
            self._update_s3_file_cache()
        
        total_restored = 0
        paths_to_check = [self.media_store_path]
        if self.uploads_path != self.media_store_path:
            paths_to_check.append(self.uploads_path)
            
        for base_path in paths_to_check:
            if os.path.exists(base_path):
                missing_files = self._find_missing_files(base_path)
                if missing_files:
                    logger.info("Found %d missing files in %s", len(missing_files), base_path)
                    restored = self._restore_files_batch(missing_files)
                    total_restored += restored
                    
        if total_restored > 0:
            logger.info("Restored %d missing files from S3", total_restored)

    def _update_s3_file_cache(self):
        """Update the cache of files available in S3."""
        logger.debug("Updating S3 file cache")
        try:
            s3_client = self._get_s3_client()
            self._s3_file_cache.clear()
            
            paginator = s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(Bucket=self.bucket, Prefix=self.prefix)
            
            file_count = 0
            for page in page_iterator:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        key = obj['Key']
                        # Remove prefix to get relative path
                        if key.startswith(self.prefix):
                            relative_path = key[len(self.prefix):]
                            self._s3_file_cache[relative_path] = {
                                'size': obj['Size'],
                                'last_modified': obj['LastModified']
                            }
                            file_count += 1
                            
            self._cache_last_updated = time.time()
            logger.debug("S3 file cache updated: %d files", file_count)
            
        except Exception as e:
            logger.error("Failed to update S3 file cache: %s", str(e))

    def _find_missing_files(self, base_path: str) -> List[str]:
        """Find files that exist in S3 but are missing locally."""
        missing_files = []
        
        for s3_relative_path in self._s3_file_cache.keys():
            local_path = os.path.join(base_path, s3_relative_path)
            
            # Only check files that should be in this base path
            if not local_path.startswith(base_path):
                continue
                
            if not os.path.exists(local_path):
                missing_files.append(s3_relative_path)
                
        return missing_files

    def _restore_files_batch(self, missing_files: List[str]) -> int:
        """Restore a batch of missing files from S3."""
        restored_count = 0
        
        # Process files in batches to avoid overwhelming the system
        for i in range(0, len(missing_files), self.auto_restore_batch_size):
            batch = missing_files[i:i + self.auto_restore_batch_size]
            
            # Submit restore tasks to thread pool
            future_to_path = {}
            for relative_path in batch:
                future = self._restore_executor.submit(self._restore_single_file, relative_path)
                future_to_path[future] = relative_path
            
            # Wait for batch completion
            for future in future_to_path:
                try:
                    if future.result():  # Returns True if successful
                        restored_count += 1
                except Exception as e:
                    path = future_to_path[future]
                    logger.error("Failed to restore file %s: %s", path, str(e))
                    
        return restored_count

    def _restore_single_file(self, relative_path: str) -> bool:
        """Restore a single file from S3 to local storage."""
        try:
            # Determine the correct local path
            local_path = os.path.join(self.media_store_path, relative_path)
            
            # Check if this should go to uploads_path instead
            if (self.uploads_path != self.media_store_path and 
                relative_path.startswith('uploads/')):
                # Remove 'uploads/' prefix and use uploads_path
                upload_relative = relative_path[8:]  # Remove 'uploads/'
                local_path = os.path.join(self.uploads_path, upload_relative)
            
            # Skip if file already exists (race condition protection)
            if os.path.exists(local_path):
                return False
                
            # Create directory if needed
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Download from S3
            s3_client = self._get_s3_client()
            s3_key = self.prefix + relative_path
            
            logger.debug("Restoring file: %s -> %s", s3_key, local_path)
            s3_client.download_file(self.bucket, s3_key, local_path)
            
            logger.debug("Successfully restored file: %s", relative_path)
            return True
            
        except Exception as e:
            logger.error("Failed to restore file %s: %s", relative_path, str(e))
            return False

    def _cleanup_empty_directories(self, path):
        """Recursively remove empty directories."""
        directory = os.path.dirname(path)
        while directory and directory.startswith(self.media_store_path):
            try:
                os.rmdir(directory)
                logger.debug("Removed empty directory: %s", directory)
            except OSError:
                break  # Directory not empty or already removed
            directory = os.path.dirname(directory)

    def shutdown(self):
        """Shutdown the auto-restore system and cleanup resources."""
        logger.info("Shutting down S3 Storage Provider")
        
        if self.auto_restore_enabled and self._restore_thread:
            logger.info("Stopping auto-restore system")
            self._restore_stop_event.set()
            
            # Wait for monitor thread to stop (with timeout)
            if self._restore_thread.is_alive():
                self._restore_thread.join(timeout=5)
                if self._restore_thread.is_alive():
                    logger.warning("Auto-restore monitor thread did not stop gracefully")
            
            # Shutdown executor
            if self._restore_executor:
                self._restore_executor.shutdown(wait=False)
                logger.info("Auto-restore executor shutdown")
        
        # Close S3 client if exists
        if self._s3_client:
            try:
                self._s3_client.close()
            except Exception as e:
                logger.debug("Error closing S3 client: %s", str(e))
            self._s3_client = None
            
        logger.info("S3 Storage Provider shutdown complete")

    async def store_file(self, path: str, file_info: Dict[str, Any]) -> None:
        """Store a file in S3 and handle local storage based on config."""
        if not self.media_store_path:
            logger.error("No media_store_path configured")
            raise Exception("No media_store_path configured")

        local_path = os.path.join(self.media_store_path, path)
        abs_path = os.path.abspath(local_path)
        
        try:
            logger.info("Processing file %s with store_local=%s", path, self.store_local)

            # First, ensure the file exists
            if not os.path.exists(local_path):
                logger.error("File %s does not exist at %s", path, local_path)
                raise Exception(f"File {path} does not exist at {local_path}")

            # Upload to S3 if store_remote is True or None (default to True)
            if self.store_remote is not False:
                s3_path = self.prefix + path
                try:
                    # Use manual multipart upload for better compatibility
                    self.multipart_upload(local_path, self.bucket, s3_path, self.extra_args)
                    logger.info("Successfully uploaded %s to S3 at %s", path, s3_path)

                    # Handle remote media lifetime
                    if self.remote_media_lifetime is not None and self.remote_media_lifetime > 0:
                        # Convert milliseconds to seconds
                        retention_seconds = self.remote_media_lifetime / 1000.0
                        logger.info(
                            "File %s in S3 will be deleted after %s seconds",
                            s3_path,
                            retention_seconds
                        )
                        # Schedule S3 deletion
                        reactor.callLater(
                            retention_seconds,
                            self._delete_s3_file,
                            s3_path
                        )
                except Exception as e:
                    logger.error("Failed to upload %s to S3: %s", path, str(e))
                    raise

            # Handle local file based on store_local and retention settings
            if self.store_local is False:
                # If store_local is explicitly False, delete immediately
                try:
                    os.remove(local_path)
                    logger.info("Removed local file after S3 upload: %s", local_path)
                    self._cleanup_empty_directories(local_path)
                    return
                except Exception as e:
                    logger.error("Failed to remove local file %s: %s", local_path, str(e))
                    raise
            else:
                # If store_local is True, handle retention
                retention_period = self.local_media_lifetime
                if retention_period is not None:
                    if retention_period == 0:
                        # Immediate deletion if retention is 0
                        try:
                            os.remove(local_path)
                            logger.info("Removed local file immediately (retention=0): %s", local_path)
                            self._cleanup_empty_directories(local_path)
                        except Exception as e:
                            logger.error("Failed to remove local file %s: %s", local_path, str(e))
                            raise
                    else:
                        # Schedule deletion after retention period (convert from milliseconds to seconds)
                        retention_seconds = retention_period / 1000.0
                        delete_time = reactor.seconds() + retention_seconds
                        self._pending_files[abs_path] = (delete_time, True)
                        logger.info(
                            "File %s will be deleted after %s seconds (store_local=%s)",
                            local_path,
                            retention_seconds,
                            self.store_local
                        )
                        
                        # Schedule the actual deletion
                        reactor.callLater(
                            retention_seconds,
                            self._delete_file_after_retention,
                            abs_path,
                            local_path
                        )
                else:
                    logger.info(
                        "File %s will be kept indefinitely (store_local=%s, no retention)",
                        local_path,
                        self.store_local
                    )

        except Exception as e:
            logger.error("Failed to process %s: %s", path, str(e))
            raise

    def _delete_file_after_retention(self, abs_path: str, local_path: str) -> None:
        """Delete a file after its retention period has expired."""
        try:
            if os.path.exists(local_path):
                os.remove(local_path)
                logger.info("Deleted file after retention period: %s", local_path)
                self._cleanup_empty_directories(local_path)
            if abs_path in self._pending_files:
                del self._pending_files[abs_path]
        except Exception as e:
            logger.error("Failed to delete file %s after retention: %s", local_path, str(e))

    def _delete_s3_file(self, s3_path: str) -> None:
        """Delete a file from S3 after its retention period."""
        try:
            s3_client = self._get_s3_client()
            s3_client.delete_object(Bucket=self.bucket, Key=s3_path)
            logger.info("Deleted file from S3 after retention period: %s", s3_path)
        except Exception as e:
            logger.error("Failed to delete file %s from S3: %s", s3_path, str(e))

    async def fetch(self, path: str, file_info: Optional[Dict[str, Any]] = None) -> Optional[Responder]:
        """Fetch the file with the given path from S3.
        
        Args:
            path: The path of the file to fetch
            file_info: Optional metadata about the file being fetched
            
        Returns:
            Returns a Responder object or None if not found
        """
        logger.info("Fetching %s from S3", path)
        
        s3_path = self.prefix + path
        try:
            s3_client = self._get_s3_client()
            deferred = defer.Deferred()
            
            # Run the S3 download in a thread
            reactor.callInThread(
                s3_download_task,
                s3_client,
                self.bucket,
                s3_path,
                self.extra_args,
                deferred,
                current_context(),
            )
            
            responder = await make_deferred_yieldable(deferred)
            return responder
            
        except Exception as e:
            logger.error("Failed to fetch %s from S3: %s", path, str(e))
            raise

def s3_download_task(s3_client, bucket, key, extra_args, deferred, parent_logcontext):
    """Downloads a file from S3 in a separate thread."""
    with LoggingContext(parent_context=parent_logcontext):
        logger.info("Fetching %s from S3", key)
        try:
            if "SSECustomerKey" in extra_args and "SSECustomerAlgorithm" in extra_args:
                resp = s3_client.get_object(
                    Bucket=bucket,
                    Key=key,
                    SSECustomerKey=extra_args["SSECustomerKey"],
                    SSECustomerAlgorithm=extra_args["SSECustomerAlgorithm"],
                )
            else:
                resp = s3_client.get_object(Bucket=bucket, Key=key)
                
        except s3_client.exceptions.NoSuchKey:
            logger.info("Media %s not found in S3", key)
            reactor.callFromThread(deferred.callback, None)
            return
        except Exception as e:
            logger.error("Error downloading %s from S3: %s", key, str(e))
            reactor.callFromThread(deferred.errback, Failure())
            return

        producer = _S3Responder()
        reactor.callFromThread(deferred.callback, producer)
        _stream_to_producer(reactor, producer, resp["Body"], timeout=90.0)

class _S3Responder(Responder):
    """A Responder that streams from S3."""
    
    def __init__(self):
        self.wakeup_event = threading.Event()
        self.stop_event = threading.Event()
        self.consumer = None
        self.deferred = defer.Deferred()
        
    def write_to_consumer(self, consumer):
        """Start streaming the S3 response to the consumer."""
        self.consumer = consumer
        consumer.registerProducer(self, True)
        self.wakeup_event.set()
        return make_deferred_yieldable(self.deferred)
        
    def resumeProducing(self):
        """Resume producing data to the consumer."""
        self.wakeup_event.set()
        
    def pauseProducing(self):
        """Pause producing data to the consumer."""
        self.wakeup_event.clear()
        
    def stopProducing(self):
        """Stop producing data to the consumer."""
        self.stop_event.set()
        self.wakeup_event.set()
        if not self.deferred.called:
            self.deferred.errback(Exception("Consumer asked to stop producing"))
            
    def _write(self, chunk):
        """Write a chunk of data to the consumer."""
        if self.consumer and not self.stop_event.is_set():
            self.consumer.write(chunk)
            
    def _error(self, failure):
        """Signal an error to the consumer."""
        if self.consumer:
            self.consumer.unregisterProducer()
            self.consumer = None
        if not self.deferred.called:
            self.deferred.errback(failure)
            
    def _finish(self):
        """Signal completion to the consumer."""
        if self.consumer:
            self.consumer.unregisterProducer()
            self.consumer = None
        if not self.deferred.called:
            self.deferred.callback(None)

def _stream_to_producer(reactor, producer, body, timeout=None):
    """Stream the S3 response body to the producer."""
    try:
        while not producer.stop_event.is_set():
            if not producer.wakeup_event.is_set():
                ret = producer.wakeup_event.wait(timeout)
                if not ret:
                    raise Exception("Timed out waiting to resume")
                    
            if producer.stop_event.is_set():
                return
                
            chunk = body.read(READ_CHUNK_SIZE)
            if not chunk:
                return
                
            reactor.callFromThread(producer._write, chunk)
            
    except Exception:
        reactor.callFromThread(producer._error, Failure())
    finally:
        reactor.callFromThread(producer._finish)
        if body:
            body.close()