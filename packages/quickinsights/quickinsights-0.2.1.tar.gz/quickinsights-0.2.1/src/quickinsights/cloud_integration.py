"""
Cloud integration utilities for QuickInsights.

This module provides utilities for integrating with cloud storage services including:
- AWS S3
- Azure Blob Storage
- Google Cloud Storage
- Cloud data processing
"""

import os
import json
from typing import Any, Dict, List, Optional, Union, BinaryIO
from pathlib import Path

# Cloud integration constants
DEFAULT_CHUNK_SIZE = 1024 * 1024  # 1MB
SUPPORTED_CLOUDS = ["aws", "azure", "gcp"]


def get_cloud_utils():
    """Lazy import for cloud utilities."""
    return {
        "get_aws_status": get_aws_status,
        "get_azure_status": get_azure_status,
        "get_gcp_status": get_gcp_status,
        "upload_to_cloud": upload_to_cloud,
        "download_from_cloud": download_from_cloud,
        "list_cloud_files": list_cloud_files,
        "process_cloud_data": process_cloud_data,
    }


def get_aws_status() -> Dict[str, bool]:
    """
    Check AWS S3 availability and configuration.

    Returns:
        Dictionary with AWS feature availability
    """
    status = {
        "boto3_available": False,
        "s3_available": False,
        "credentials_configured": False,
        "bucket_access": False,
    }

    try:
        import boto3

        status["boto3_available"] = True

        try:
            s3 = boto3.client("s3")
            status["s3_available"] = True

            # Check if credentials are configured
            try:
                s3.list_buckets()
                status["credentials_configured"] = True
                status["bucket_access"] = True
            except Exception:
                status["credentials_configured"] = False
                status["bucket_access"] = False

        except Exception:
            status["s3_available"] = False

    except ImportError:
        pass

    return status


def get_azure_status() -> Dict[str, bool]:
    """
    Check Azure Blob Storage availability and configuration.

    Returns:
        Dictionary with Azure feature availability
    """
    status = {
        "azure_storage_available": False,
        "blob_service_available": False,
        "connection_string_configured": False,
        "container_access": False,
    }

    try:
        from azure.storage.blob import BlobServiceClient

        status["azure_storage_available"] = True

        try:
            # Check if connection string is configured
            connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            if connection_string:
                status["connection_string_configured"] = True
                status["blob_service_available"] = True

                # Try to create a client to test access
                try:
                    blob_service_client = BlobServiceClient.from_connection_string(
                        connection_string
                    )
                    # List containers to test access
                    containers = blob_service_client.list_containers()
                    next(containers, None)  # Just check if we can iterate
                    status["container_access"] = True
                except Exception:
                    status["container_access"] = False

        except Exception:
            status["blob_service_available"] = False

    except ImportError:
        pass

    return status


def get_gcp_status() -> Dict[str, bool]:
    """
    Check Google Cloud Storage availability and configuration.

    Returns:
        Dictionary with GCP feature availability
    """
    status = {
        "google_cloud_storage_available": False,
        "storage_client_available": False,
        "credentials_configured": False,
        "bucket_access": False,
    }

    try:
        from google.cloud import storage

        status["google_cloud_storage_available"] = True

        try:
            # Check if credentials are configured
            try:
                storage_client = storage.Client()
                # List buckets to test access
                buckets = list(storage_client.list_buckets(max_results=1))
                status["credentials_configured"] = True
                status["storage_client_available"] = True
                status["bucket_access"] = True
            except Exception:
                status["credentials_configured"] = False
                status["bucket_access"] = False

        except Exception:
            status["storage_client_available"] = False

    except ImportError:
        pass

    return status


def upload_to_cloud(
    file_path: str, cloud_type: str, destination: str, **kwargs
) -> Dict[str, Any]:
    """
    Upload a file to cloud storage.

    Args:
        file_path: Local file path to upload
        cloud_type: Type of cloud ('aws', 'azure', 'gcp')
        destination: Destination path in cloud storage
        **kwargs: Additional cloud-specific parameters

    Returns:
        Dictionary with upload results
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if cloud_type not in SUPPORTED_CLOUDS:
        raise ValueError(f"Unsupported cloud type: {cloud_type}")

    try:
        if cloud_type == "aws":
            return _upload_to_aws(file_path, destination, **kwargs)
        elif cloud_type == "azure":
            return _upload_to_azure(file_path, destination, **kwargs)
        elif cloud_type == "gcp":
            return _upload_to_gcp(file_path, destination, **kwargs)
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "cloud_type": cloud_type,
            "file_path": file_path,
            "destination": destination,
        }


def _upload_to_aws(file_path: str, destination: str, **kwargs) -> Dict[str, Any]:
    """Upload file to AWS S3."""
    try:
        import boto3

        bucket_name = kwargs.get("bucket_name")
        if not bucket_name:
            raise ValueError("bucket_name is required for AWS upload")

        s3_client = boto3.client("s3")

        # Upload file
        s3_client.upload_file(file_path, bucket_name, destination)

        return {
            "success": True,
            "cloud_type": "aws",
            "bucket": bucket_name,
            "key": destination,
            "file_path": file_path,
            "message": "File uploaded successfully to S3",
        }

    except Exception as e:
        raise Exception(f"AWS upload failed: {e}")


def _upload_to_azure(file_path: str, destination: str, **kwargs) -> Dict[str, Any]:
    """Upload file to Azure Blob Storage."""
    try:
        from azure.storage.blob import BlobServiceClient

        connection_string = kwargs.get("connection_string") or os.getenv(
            "AZURE_STORAGE_CONNECTION_STRING"
        )
        if not connection_string:
            raise ValueError("connection_string is required for Azure upload")

        container_name = kwargs.get("container_name")
        if not container_name:
            raise ValueError("container_name is required for Azure upload")

        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(destination)

        # Upload file
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        return {
            "success": True,
            "cloud_type": "azure",
            "container": container_name,
            "blob_name": destination,
            "file_path": file_path,
            "message": "File uploaded successfully to Azure Blob Storage",
        }

    except Exception as e:
        raise Exception(f"Azure upload failed: {e}")


def _upload_to_gcp(file_path: str, destination: str, **kwargs) -> Dict[str, Any]:
    """Upload file to Google Cloud Storage."""
    try:
        from google.cloud import storage

        bucket_name = kwargs.get("bucket_name")
        if not bucket_name:
            raise ValueError("bucket_name is required for GCP upload")

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination)

        # Upload file
        blob.upload_from_filename(file_path)

        return {
            "success": True,
            "cloud_type": "gcp",
            "bucket": bucket_name,
            "blob_name": destination,
            "file_path": file_path,
            "message": "File uploaded successfully to Google Cloud Storage",
        }

    except Exception as e:
        raise Exception(f"GCP upload failed: {e}")


def download_from_cloud(
    cloud_type: str, source: str, local_path: str, **kwargs
) -> Dict[str, Any]:
    """
    Download a file from cloud storage.

    Args:
        cloud_type: Type of cloud ('aws', 'azure', 'gcp')
        source: Source path in cloud storage
        local_path: Local path to save the file
        **kwargs: Additional cloud-specific parameters

    Returns:
        Dictionary with download results
    """
    if cloud_type not in SUPPORTED_CLOUDS:
        raise ValueError(f"Unsupported cloud type: {cloud_type}")

    try:
        if cloud_type == "aws":
            return _download_from_aws(source, local_path, **kwargs)
        elif cloud_type == "azure":
            return _download_from_azure(source, local_path, **kwargs)
        elif cloud_type == "gcp":
            return _download_from_gcp(source, local_path, **kwargs)
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "cloud_type": cloud_type,
            "source": source,
            "local_path": local_path,
        }


def _download_from_aws(source: str, local_path: str, **kwargs) -> Dict[str, Any]:
    """Download file from AWS S3."""
    try:
        import boto3

        bucket_name = kwargs.get("bucket_name")
        if not bucket_name:
            raise ValueError("bucket_name is required for AWS download")

        s3_client = boto3.client("s3")

        # Download file
        s3_client.download_file(bucket_name, source, local_path)

        return {
            "success": True,
            "cloud_type": "aws",
            "bucket": bucket_name,
            "key": source,
            "local_path": local_path,
            "message": "File downloaded successfully from S3",
        }

    except Exception as e:
        raise Exception(f"AWS download failed: {e}")


def _download_from_azure(source: str, local_path: str, **kwargs) -> Dict[str, Any]:
    """Download file from Azure Blob Storage."""
    try:
        from azure.storage.blob import BlobServiceClient

        connection_string = kwargs.get("connection_string") or os.getenv(
            "AZURE_STORAGE_CONNECTION_STRING"
        )
        if not connection_string:
            raise ValueError("connection_string is required for Azure download")

        container_name = kwargs.get("container_name")
        if not container_name:
            raise ValueError("container_name is required for Azure download")

        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(source)

        # Download file
        with open(local_path, "wb") as data:
            data.write(blob_client.download_blob().readall())

        return {
            "success": True,
            "cloud_type": "azure",
            "container": container_name,
            "blob_name": source,
            "local_path": local_path,
            "message": "File downloaded successfully from Azure Blob Storage",
        }

    except Exception as e:
        raise Exception(f"Azure download failed: {e}")


def _download_from_gcp(source: str, local_path: str, **kwargs) -> Dict[str, Any]:
    """Download file from Google Cloud Storage."""
    try:
        from google.cloud import storage

        bucket_name = kwargs.get("bucket_name")
        if not bucket_name:
            raise ValueError("bucket_name is required for GCP download")

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source)

        # Download file
        blob.download_to_filename(local_path)

        return {
            "success": True,
            "cloud_type": "gcp",
            "bucket": bucket_name,
            "blob_name": source,
            "local_path": local_path,
            "message": "File downloaded successfully from Google Cloud Storage",
        }

    except Exception as e:
        raise Exception(f"GCP download failed: {e}")


def list_cloud_files(cloud_type: str, **kwargs) -> Dict[str, Any]:
    """
    List files in cloud storage.

    Args:
        cloud_type: Type of cloud ('aws', 'azure', 'gcp')
        **kwargs: Additional cloud-specific parameters

    Returns:
        Dictionary with file listing results
    """
    if cloud_type not in SUPPORTED_CLOUDS:
        raise ValueError(f"Unsupported cloud type: {cloud_type}")

    try:
        if cloud_type == "aws":
            return _list_aws_files(**kwargs)
        elif cloud_type == "azure":
            return _list_azure_files(**kwargs)
        elif cloud_type == "gcp":
            return _list_gcp_files(**kwargs)
    except Exception as e:
        return {"success": False, "error": str(e), "cloud_type": cloud_type}


def _list_aws_files(**kwargs) -> Dict[str, Any]:
    """List files in AWS S3."""
    try:
        import boto3

        bucket_name = kwargs.get("bucket_name")
        if not bucket_name:
            raise ValueError("bucket_name is required for AWS listing")

        prefix = kwargs.get("prefix", "")

        s3_client = boto3.client("s3")
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        files = []
        if "Contents" in response:
            for obj in response["Contents"]:
                files.append(
                    {
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"].isoformat(),
                    }
                )

        return {
            "success": True,
            "cloud_type": "aws",
            "bucket": bucket_name,
            "prefix": prefix,
            "files": files,
            "count": len(files),
        }

    except Exception as e:
        raise Exception(f"AWS listing failed: {e}")


def _list_azure_files(**kwargs) -> Dict[str, Any]:
    """List files in Azure Blob Storage."""
    try:
        from azure.storage.blob import BlobServiceClient

        connection_string = kwargs.get("connection_string") or os.getenv(
            "AZURE_STORAGE_CONNECTION_STRING"
        )
        if not connection_string:
            raise ValueError("connection_string is required for Azure listing")

        container_name = kwargs.get("container_name")
        if not container_name:
            raise ValueError("container_name is required for Azure listing")

        name_starts_with = kwargs.get("name_starts_with", "")

        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        container_client = blob_service_client.get_container_client(container_name)

        files = []
        for blob in container_client.list_blobs(name_starts_with=name_starts_with):
            files.append(
                {
                    "name": blob.name,
                    "size": blob.size,
                    "last_modified": blob.last_modified.isoformat(),
                }
            )

        return {
            "success": True,
            "cloud_type": "azure",
            "container": container_name,
            "prefix": name_starts_with,
            "files": files,
            "count": len(files),
        }

    except Exception as e:
        raise Exception(f"Azure listing failed: {e}")


def _list_gcp_files(**kwargs) -> Dict[str, Any]:
    """List files in Google Cloud Storage."""
    try:
        from google.cloud import storage

        bucket_name = kwargs.get("bucket_name")
        if not bucket_name:
            raise ValueError("bucket_name is required for GCP listing")

        prefix = kwargs.get("prefix", "")

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)

        files = []
        for blob in bucket.list_blobs(prefix=prefix):
            files.append(
                {
                    "name": blob.name,
                    "size": blob.size,
                    "updated": blob.updated.isoformat(),
                }
            )

        return {
            "success": True,
            "cloud_type": "gcp",
            "bucket": bucket_name,
            "prefix": prefix,
            "files": files,
            "count": len(files),
        }

    except Exception as e:
        raise Exception(f"GCP listing failed: {e}")


def process_cloud_data(
    cloud_type: str, source: str, processor_func: callable, **kwargs
) -> Dict[str, Any]:
    """
    Process data directly from cloud storage.

    Args:
        cloud_type: Type of cloud ('aws', 'azure', 'gcp')
        source: Source path in cloud storage
        processor_func: Function to process the data
        **kwargs: Additional cloud-specific parameters

    Returns:
        Dictionary with processing results
    """
    if cloud_type not in SUPPORTED_CLOUDS:
        raise ValueError(f"Unsupported cloud type: {cloud_type}")

    try:
        # Download to temporary location
        temp_path = f"/tmp/cloud_temp_{os.path.basename(source)}"

        download_result = download_from_cloud(cloud_type, source, temp_path, **kwargs)
        if not download_result["success"]:
            return download_result

        # Process the data
        try:
            result = processor_func(temp_path)

            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)

            return {
                "success": True,
                "cloud_type": cloud_type,
                "source": source,
                "result": result,
                "message": "Data processed successfully from cloud storage",
            }

        except Exception as e:
            # Clean up temporary file on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "cloud_type": cloud_type,
            "source": source,
        }
