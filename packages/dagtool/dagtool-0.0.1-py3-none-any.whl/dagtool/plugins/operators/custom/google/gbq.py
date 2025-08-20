import os
from collections.abc import Sequence
from typing import TYPE_CHECKING

from airflow.models.baseoperator import BaseOperator
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryInsertJobOperator,
)
from airflow_common.storage.cloud.google.gcs import GCSFileUtils

if TYPE_CHECKING:
    from airflow.utils.context import Context

AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME")


class IcebergToBigquery(BaseOperator):
    """Create or Replace Iceberg External table to Google BigQuery."""

    template_fields: Sequence[str] = (
        "iceberg_table_uri",
        "bigquery_full_table_name",
        "biglake_connection_id",
        "schema_json_file_path",
    )
    template_ext: Sequence[str] = (".json",)

    def __init__(
        self,
        *,
        iceberg_table_uri: str,
        bigquery_full_table_name: str,
        biglake_connection_id: str,
        bq_location: str = "asia-southeast1",
        gcp_conn_id: str = "google_cloud_default",
        iceberg_metadata_version: str = "latest",
        schema_json_file_path: str | None = None,
        impersonation_chain: str | Sequence[str] | None = None,
        **kwargs: dict,
    ) -> None:
        """Initiate IcebergToBigquery Attributes

        Args:
            iceberg_table_uri (str): GCS URI to iceberg table eg. gs://bucket/prefix/table_name
            bigquery_full_table_name (str): Bigquery table full name eg. project_id.dataset.table_name
            biglake_connection_id (str): External connection name for creating biglake table
                                        (must create this manually before calling via this module)
            bq_location (str): Location of the bigquery table. Defaults to "asia-southeast1".
            gcp_conn_id: (str) The connection ID used to connect to Google Cloud.
            iceberg_metadata_version (str): Iceberg table metadata version to sync eg. 1, 2 or latest.
                                        Defaults to "latest".
            schema_json_file_path (str, optional): BigQuery table schema json file path
            impersonation_chain (str, Sequence[str], optional): Optional service account to impersonate using short-term
                                credentials, or chained list of accounts required to get the access_token
                                of the last account in the list, which will be impersonated in the request.
                                If set as a string, the account must grant the originating account
                                the Service Account Token Creator IAM role.
                                If set as a sequence, the identities from the list must grant
                                Service Account Token Creator IAM role to the directly preceding identity, with first
                                account from the list granting this role to the originating account (templated).
            kwargs (dict): Extra BashOperator parameters
        """
        super().__init__(**kwargs)
        self.bigquery_full_table_name = bigquery_full_table_name
        self.biglake_connection_id = biglake_connection_id
        self.bq_location = bq_location
        self.gcp_conn_id = gcp_conn_id
        self.iceberg_table_uri = iceberg_table_uri
        self.iceberg_metadata_version = iceberg_metadata_version
        self.schema_json_file_path = schema_json_file_path
        self.impersonation_chain = impersonation_chain

    def _generate_create_iceberg_table_query(
        self,
        metadata_version: int,
    ) -> str:
        sql = f"""
            CREATE OR REPLACE EXTERNAL TABLE {self.bigquery_full_table_name}
            WITH CONNECTION `{self.biglake_connection_id}`
            OPTIONS (
                    format = 'ICEBERG',
                    uris = ["{self.iceberg_table_uri}/metadata/v{metadata_version}.metadata.json"]
            )
            """
        self.log.info("Query to sync iceberg to bigquery\n%s", sql)
        return sql

    def _get_hook(self) -> BigQueryHook:
        return BigQueryHook(
            gcp_conn_id=self.gcp_conn_id,
            impersonation_chain=self.impersonation_chain,
        )

    def execute(self, context: "Context") -> None:
        """Execute IcebergToBigquery to create or replace external table in BigQuery

        Args:
            context (Context): Airflow Contexts
        """
        if self.iceberg_metadata_version == "latest":
            metadata_version = GCSFileUtils().read_file_from_uri(
                gs_uri=self.iceberg_table_uri + "/metadata/version-hint.text"
            )
        else:
            metadata_version = self.iceberg_metadata_version

        self.log.info(
            "Syncing Iceberg from uri %s version %s to bigquery %s",
            self.iceberg_table_uri,
            metadata_version,
            self.bigquery_full_table_name,
        )
        query = self._generate_create_iceberg_table_query(metadata_version)

        # Use the Opertator execution instead of hook because of configuration preparation in the Operator.
        BigQueryInsertJobOperator(
            task_id=f"{self.task_id}_bq_job",
            configuration={
                "query": {
                    "query": query,
                    "useLegacySql": False,
                    "priority": "BATCH",
                }
            },
            location=self.bq_location,
        ).execute(context)

        if self.schema_json_file_path:
            project_id, bq_dataset, table = self.bigquery_full_table_name.split(
                "."
            )
            # table_resource ref: https://cloud.google.com/bigquery/docs/reference/rest/v2/tables#resource:-table
            bq_hook = self._get_hook()

            bq_hook.update_table(
                table_resource={
                    "description": self.schema_json_file_path["description"],
                    "schema": {"fields": self.schema_json_file_path["schema"]},
                },
                fields=["description", "schema"],
                dataset_id=bq_dataset,
                table_id=table,
                project_id=project_id,
            )
