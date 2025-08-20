from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GCSCredentialType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GCS_CREDENTIAL_TYPE_UNSPECIFIED: _ClassVar[GCSCredentialType]
    GCS_CREDENTIAL_TYPE_HMAC_ACCESS_KEY: _ClassVar[GCSCredentialType]

class AzureSecretType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AZURE_SECRET_TYPE_UNSPECIFIED: _ClassVar[AzureSecretType]
    AZURE_SECRET_TYPE_ACCOUNT_ACCESS_KEY: _ClassVar[AzureSecretType]
    AZURE_SECRET_TYPE_SHARED_ACCESS_SIGNATURE: _ClassVar[AzureSecretType]
GCS_CREDENTIAL_TYPE_UNSPECIFIED: GCSCredentialType
GCS_CREDENTIAL_TYPE_HMAC_ACCESS_KEY: GCSCredentialType
AZURE_SECRET_TYPE_UNSPECIFIED: AzureSecretType
AZURE_SECRET_TYPE_ACCOUNT_ACCESS_KEY: AzureSecretType
AZURE_SECRET_TYPE_SHARED_ACCESS_SIGNATURE: AzureSecretType

class S3Credentials(_message.Message):
    __slots__ = ("access_key_id", "region")
    ACCESS_KEY_ID_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    access_key_id: str
    region: str
    def __init__(self, access_key_id: _Optional[str] = ..., region: _Optional[str] = ...) -> None: ...

class GCSCredentials(_message.Message):
    __slots__ = ("service_account_json", "access_key_id", "credential_type")
    SERVICE_ACCOUNT_JSON_FIELD_NUMBER: _ClassVar[int]
    ACCESS_KEY_ID_FIELD_NUMBER: _ClassVar[int]
    CREDENTIAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    service_account_json: str
    access_key_id: str
    credential_type: GCSCredentialType
    def __init__(self, service_account_json: _Optional[str] = ..., access_key_id: _Optional[str] = ..., credential_type: _Optional[_Union[GCSCredentialType, str]] = ...) -> None: ...

class AzureBlobCredentials(_message.Message):
    __slots__ = ("account_url", "secret_type")
    ACCOUNT_URL_FIELD_NUMBER: _ClassVar[int]
    SECRET_TYPE_FIELD_NUMBER: _ClassVar[int]
    account_url: str
    secret_type: AzureSecretType
    def __init__(self, account_url: _Optional[str] = ..., secret_type: _Optional[_Union[AzureSecretType, str]] = ...) -> None: ...

class DataConnectorParameters(_message.Message):
    __slots__ = ("s3_credentials", "gcs_credentials", "azure_blob_credentials")
    S3_CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    GCS_CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    AZURE_BLOB_CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    s3_credentials: S3Credentials
    gcs_credentials: GCSCredentials
    azure_blob_credentials: AzureBlobCredentials
    def __init__(self, s3_credentials: _Optional[_Union[S3Credentials, _Mapping]] = ..., gcs_credentials: _Optional[_Union[GCSCredentials, _Mapping]] = ..., azure_blob_credentials: _Optional[_Union[AzureBlobCredentials, _Mapping]] = ...) -> None: ...
