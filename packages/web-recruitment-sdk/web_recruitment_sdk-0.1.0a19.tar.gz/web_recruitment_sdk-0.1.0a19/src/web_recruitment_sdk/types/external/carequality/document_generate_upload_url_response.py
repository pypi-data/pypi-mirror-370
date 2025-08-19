# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["DocumentGenerateUploadURLResponse"]


class DocumentGenerateUploadURLResponse(BaseModel):
    document_id: str = FieldInfo(alias="documentId")
    """The generated document ID"""

    expires_at: str = FieldInfo(alias="expiresAt")
    """The expiration time of the upload URL in ISO format"""

    file_md5_hash: str = FieldInfo(alias="fileMd5Hash")
    """Expected MD5 hash for client-side validation (if provided)"""

    upload_url: str = FieldInfo(alias="uploadUrl")
    """The signed URL for uploading the document"""
