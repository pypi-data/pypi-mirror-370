from typing import List

from kumoapi.source_table import (
    DataSourceType,
    FileType,
    S3SourceTableRequest,
    SourceTableConfigRequest,
    SourceTableConfigResponse,
)
from typing_extensions import override

from kumoai import global_state
from kumoai.connector.base import Connector


class FileUploadConnector(Connector):
    r"""Defines a connector to files directly uploaded to Kumo, either as
    'parquet' or 'csv' (non-partitioned) data.

    To get started with file upload, please first upload a table with
    the :meth:`~kumoai.connector.upload_table` method. You can then access
    this table behind the file upload connector as follows:

    .. code-block:: python

        import kumoai
        from kumoai.connector import upload_table

        # Upload the table; assume it is stored at `/data/users.parquet`
        upload_table(name="users", path="/data/users.parquet")

        # Create the file upload connector:
        connector = kumoai.FileUploadConnector(file_type="parquet")

        # Check that the file upload connector has a `users` table:
        assert connector.has_table("users")

    Args:
        file_type: The file type of uploaded data. Can be either ``"csv"``
            or ``"parquet"``.
    """
    def __init__(self, file_type: str) -> None:
        r"""Creates the connector to uploaded files of type
        :obj:`file_type`.
        """
        assert file_type.lower() in {'parquet', 'csv'}
        self._file_type = file_type.lower()

    @property
    def name(self) -> str:
        return f'{self._file_type}_upload_connector'

    @override
    @property
    def source_type(self) -> DataSourceType:
        return DataSourceType.S3

    @property
    def file_type(self) -> FileType:
        return (FileType.PARQUET
                if self._file_type == 'parquet' else FileType.CSV)

    def _get_table_config(self, table_name: str) -> SourceTableConfigResponse:
        req = SourceTableConfigRequest(connector_id=self.name,
                                       table_name=table_name,
                                       source_type=self.source_type,
                                       file_type=None)
        return global_state.client.source_table_api.get_table_config(req)

    @override
    def _source_table_request(self,
                              table_names: List[str]) -> S3SourceTableRequest:
        return S3SourceTableRequest(s3_root_dir="", connector_id=self.name,
                                    table_names=table_names, file_type=None)
