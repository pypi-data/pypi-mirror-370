import logging
import time
from collections.abc import Callable
from functools import lru_cache
from typing import Any, Iterator

from requests import Session, Response
from requests.adapters import HTTPAdapter
from simple_salesforce import Salesforce, SFType, SalesforceError
from tenacity import RetryCallState
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from pmsintegration.core.addepar.connector import response_handler
from pmsintegration.core.core_models import SalesforceAddeparIdLink
from pmsintegration.core.observability.metrics_relay import SalesforceMetricsHook
from pmsintegration.core.salesforce.connector.salesforce_config import SalesforceSimpleConnectorConfig
from pmsintegration.platform import utils, errors

_log = logging.getLogger(__name__)

# Default retry configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY_SECONDS = 2.0
addepar_id = None


def _create_http_session(transport_config: dict[str, Any]) -> Session:
    s = SalesforceMetricsHook(namespace=transport_config.get("namespace", "salesforce"))
    s.verify = transport_config.get("verify", True)
    pool_maxsize = transport_config.get("pool_maxsize", 20)
    if pool_maxsize:
        s.mount("https://", HTTPAdapter(pool_maxsize=pool_maxsize, pool_connections=pool_maxsize))

    return s


def set_adpr_id(id):
    global adpr_id
    adpr_id = id


class SalesforceSimpleConnector:
    def __init__(self, config: SalesforceSimpleConnectorConfig):
        self._client = Salesforce(
            **config.create_auth_dict(),
            **config.as_dict(),
            session=_create_http_session(config.transport)
        )
        self.max_retries = getattr(config, 'max_retries', DEFAULT_MAX_RETRIES)
        self.retry_delay_seconds = getattr(config, 'retry_delay_seconds', DEFAULT_RETRY_DELAY_SECONDS)

    @property
    def client(self):
        return self._client

    def execute_scalar_query(
            self,
            query: str,
            row_mapper: Callable[[dict[str, Any]], Any] = lambda r: r,
            **kwargs
    ) -> dict[str, Any]:
        results = self._client.query(query, **kwargs)

        utils.check(results.get("totalSize") == 1, "Query did not return 1 row")
        return row_mapper(results.get("records")[0])

    def get_tenant_id(self):
        query = """
        SELECT Id FROM Organization LIMIT 1
        """.strip()
        return self.execute_scalar_query(query, lambda r: r["Id"])

    def execute_query(
            self,
            query: str,
            row_mapper: Callable[[dict[str, Any]], Any] = lambda r: r,
            **kwargs
    ) -> Iterator[Any]:
        for r in self._client.query_all_iter(query, **kwargs):
            yield row_mapper(r)

    def list_object_types(self):
        results = self._client.describe()
        return [so.get("name") for so in results.get("sobjects")]

    @lru_cache()
    def _lookup_sf_type(self, object_name: str):
        sf_type: SFType = getattr(self._client, object_name)
        _log.info(f"SFType: {SFType} | Object: {object_name}")
        if not isinstance(sf_type, SFType):
            raise errors.IllegalArgumentException(f"'{object_name}' seems to be an invalid Salesforce object name")
        # Issue a call to check if the given object_name is valid
        sf_type.metadata()
        return sf_type

    def get_object(
            self,
            object_name: str,
            record_id: str,
            **kwargs
    ):
        """
        Fetches an sObject details with the given recordId.

        :param object_name: Name of Salesforce object (e.g., Account)
        :record_id -- the recordId of the SObject to get
        """
        sf_object = self._lookup_sf_type(object_name)
        _log.info(f"Fetching Salesforce {object_name} object record with recordId: {record_id}")
        try:
            record = sf_object.get(
                record_id,
                headers=kwargs,
            )
            if not isinstance(record, dict) or "Id" not in record:
                _log.warning(f"Invalid record format for {object_name} {record_id}: {record}")
                return None

            _log.info(f"{record_id} data fetched successfully")
            _log.info(f"Record : {record}")

            return record
        except SalesforceError as e:
            if e.status == 404:
                _log.warning(f"Record {record_id} not found")
                return None
            _log.error(f"Error occurred during Salesforce record Fetch : {e}")
            raise

    def create_object(
            self,
            object_name: str,
            data: dict[str, any],
            **kwargs
    ):
        """Creates an sObject with the given fields.

        :param object_name: Name of Salesforce object (e.g., Account)
        :param data: Fields to create the object
        """
        sf_object = self._lookup_sf_type(object_name)
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json"
        }
        headers.update(kwargs.get("headers", {}))  # Merge with any passed headers
        _log.info(f"Creating Salesforce {object_name} object record with data: {data}, headers: {headers}")
        try:
            response = sf_object.create(
                data,
                headers=kwargs,
            )
            if not response["success"]:
                _log.error(f"Create failed: {response['errors']}")
                raise ValueError(f"Create failed: {response['errors']}")

            _log.info(f"{object_name} created successfully")
            _log.info(f"Create response: {response}")
            return response
        except SalesforceError as e:
            _log.error(f"Error occurred during Salesforce create: {e}")
            raise

    def _log_retry_attempt(self, retry_state: RetryCallState, object_name: str, record_id: str | None = None,
                           num_records: int | None = None) -> None:
        """Log a retry attempt for an update or bulk update operation."""
        attempt = retry_state.attempt_number
        error = str(retry_state.outcome.exception()) if retry_state.outcome else "Unknown"

        if num_records is not None:
            _log.warning(
                f"Bulk API call retry attempt {attempt}/{self.max_retries} for {num_records} {object_name} "
                f"records due to error: {error}"
            )
        else:
            _log.warning(
                f"Retry attempt {attempt}/{self.max_retries} for {object_name} #{record_id} "
                f"due to error: {error}"
            )
        response_handler.set_http_error_text(error_string=f"{adpr_id}:SF:{error}")
        set_adpr_id(None)

    def _log_retry_success(self, retry_state: RetryCallState, object_name: str, record_id: str | None = None,
                           num_records: int | None = None) -> None:
        """Log a successful update after retries."""
        attempt = retry_state.attempt_number - 1

        if num_records is not None:
            _log.warning(
                f"Bulk update API call succeeded, on retry attempt {attempt}/{self.max_retries} "
                f"for {num_records} {object_name} "
            )
        else:
            _log.info(
                f"Update API call succeeded, on retry attempt {attempt}/{self.max_retries} "
                f"for {object_name} #{record_id}"
            )

    def _log_final_failure(self, retry_state: RetryCallState, object_name: str, record_id: str | None = None,
                           num_records: int | None = None) -> None:
        """Log final failure after all retries."""
        error = str(retry_state.outcome.exception()) if retry_state.outcome else "Unknown"
        if num_records is not None:
            _log.warning(
                f"All {self.max_retries} API call retry attempts failed for "
                f"{num_records} {object_name} Bulk records: {error}"
            )
        else:
            _log.error(
                f"All {self.max_retries} API call retry attempts failed for "
                f"{adpr_id} - {object_name} #{record_id}: {error}"
            )

    def update_object(
            self,
            object_name: str,
            record_id: str,
            data: dict[str, Any],
            **kwargs
    ):
        """Performs an object update with the given changed fields.

        :param object_name: Name of salesforce object. For example: Account
        :param record_id: Salesforce record id
        :param data: List of changed fields
        """

        @retry(
            stop=stop_after_attempt(self.max_retries + 1),
            wait=wait_fixed(self.retry_delay_seconds),
            retry=retry_if_exception_type(Exception),
            before_sleep=lambda retry_state: self._log_retry_attempt(
                retry_state, object_name, record_id=record_id
            ),
            after=lambda retry_state: self._log_retry_success(
                retry_state, object_name, record_id=record_id
            ),
            retry_error_callback=lambda retry_state: self._log_final_failure(
                retry_state, object_name, record_id=record_id
            ),
            reraise=True
        )
        def _update_with_retry():
            sf_object = self._lookup_sf_type(object_name)
            _log.info(f"Sending data to Salesforce {data} | RecordID: {record_id}")
            set_adpr_id(data)
            response: Response = sf_object.update(
                record_id,
                data,
                headers=kwargs,
                raw_response=True
            )
            _log.info(f"{object_name} #{record_id} updated with status: {response.status_code}")
            response.raise_for_status()
            response_handler.set_http_error_text(error_string=None)
            response_handler.set_http_error_code(error_code=None)

        _update_with_retry()

    def link_id(self, link: SalesforceAddeparIdLink) -> None:
        """Link a Salesforce record to an Addepar ID."""
        self.update_object(
            link.salesforce_object_name,
            link.record_id,
            data={link.salesforce_addepar_id_field_name: link.addepar_id}
        )

    def unlink_id(self, link: SalesforceAddeparIdLink):
        self.update_object(
            link.salesforce_object_name,
            link.record_id,
            data={link.salesforce_addepar_id_field_name: None}
        )

    def restful(
            self,
            path: str,
            params: dict[str, Any] = None,
            method: str = 'GET',
            **kwargs: Any
    ):
        return self._client.restful(path, params, method, **kwargs)

    def _validate_bulk_update_input(
            self, data: list[dict[str, Any]]
    ) -> None:
        """Validate that all records have a valid 'Id' field."""
        invalid_records = [
            (idx, record) for idx, record in enumerate(data)
            if 'Id' not in record or not str(record['Id']).strip()
        ]
        if invalid_records:
            error_msgs = "\n".join(
                f"Record at index {idx} is missing a valid 'Id': {record}"
                for idx, record in invalid_records
            )
            raise ValueError(f"Invalid records found:\n{error_msgs}")

    def _process_bulk_update_results(
            self,
            results: list[dict[str, Any]],
            remaining_records: list[dict[str, Any]],
            all_results: list[dict[str, Any]],
            object_name: str,
            attempt: int
    ) -> tuple[list[dict[str, Any]], bool]:
        """Process bulk update results, filtering failed records for retry."""
        all_results.extend([result for result in results if result['success']])
        failed_indices = [i for i, result in enumerate(results) if not result['success']]
        if not failed_indices:
            _log.info(f"Bulk update API call completed for {len(remaining_records)} records")
            return [], True
        remaining_records[:] = [remaining_records[i] for i in failed_indices]
        _log.warning(
            f"Attempt {attempt + 1}/{self.max_retries}: "
            f"{len(remaining_records)} {object_name} records failed. Retrying failed records."
        )
        return remaining_records, False

    def bulk_update(
            self,
            object_name: str,
            data: list[dict[str, Any]],
            **kwargs
    ) -> list[dict[str, Any]]:
        """
        Perform a bulk update, retrying only failed records,for a given Salesforce object using the Bulk API v1.

        Parameters:
            object_name (str): The API name of the Salesforce object (e.g., 'Contact', 'Account').
            data (list[dict[str, Any]]): A list of dictionaries representing the records to update.
                                         Each dict must include a non-empty 'Id' key.
            max_retries: Number of retry attempts (defaults to self.max_retries).
            retry_delay_seconds: Delay between retries (defaults to self.retry_delay_seconds).
            **kwargs: Additional keyword arguments passed to the underlying Bulk API call,
                      such as batch_size or use_serial.

        Returns:
            list[dict[str, Any]]: A list of result dictionaries, each with:
                - 'Id': The Salesforce record ID (if the update succeeded).
                - 'success': A boolean indicating the update status.
                - 'errors': A list of any error messages encountered during the update.

        Raises:
            ValueError: If any record is missing a valid 'Id' field.

        Example:
            results = client.bulk_update('Contact', [
                {'Id': '003XXXXXXXXXXXXAAA', 'Email': 'test@example.com'},
                {'Id': '003XXXXXXXXXXXXBBB', 'Phone': '1234567890'}
            ])
        """
        self._lookup_sf_type(object_name)
        self._validate_bulk_update_input(data)
        if not data:
            return []

        all_results: list[dict[str, Any]] = []
        remaining_records = data.copy()

        @retry(
            stop=stop_after_attempt(self.max_retries + 1),
            wait=wait_fixed(self.retry_delay_seconds),
            retry=retry_if_exception_type(Exception),
            before_sleep=lambda retry_state: self._log_retry_attempt(
                retry_state, object_name, num_records=len(remaining_records)
            ),
            after=lambda retry_state: self._log_retry_success(
                retry_state, object_name, num_records=len(remaining_records)
            ),
            retry_error_callback=lambda retry_state: self._log_final_failure(
                retry_state, object_name, num_records=len(remaining_records)
            ),
            reraise=True
        )
        def execute_bulk_update(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
            """Execute a single bulk update attempt."""
            if not records:
                return []

            bulk_handler = getattr(self._client.bulk, object_name)
            _log.info(f"Sending {len(records)} {object_name} records to Salesforce")
            results = bulk_handler.update(records, **kwargs)
            _log.info(f"Bulk update API call completed for {len(records)} {object_name} records")

            return results

        for attempt in range(self.max_retries):
            try:
                results = execute_bulk_update(remaining_records)
                if results:
                    remaining_records, is_complete = self._process_bulk_update_results(
                        results, remaining_records, all_results, object_name, attempt
                    )
                    if is_complete:
                        return all_results
                time.sleep(self.retry_delay_seconds)

                if attempt + 1 == self.max_retries and results:
                    all_results.extend([result for result in results if not result['success']])

            except Exception as e:
                error_text = f"SF: {str(e)}"
                _log.error(f"Bulk update failed: {error_text}")

        _log.error(f"All {self.max_retries} retries failed for {len(remaining_records)} records")
        return all_results

    def bulk_delete(
            self,
            object_name: str,
            data: list[dict[str, Any]],
            **kwargs
    ) -> list[dict[str, Any]]:
        """
        Perform a bulk delete for a given Salesforce object using the Bulk API v1.

        Parameters:
            object_name (str): The API name of the Salesforce object (e.g., 'Contact', 'Account').
            data (list[dict[str, Any]]): A list of dictionaries representing the records to delete.
                                         Each dict must include a non-empty 'Id' key.
            **kwargs: Additional keyword arguments passed to the underlying Bulk API call,
                      such as batch_size or use_serial.

        Returns:
            list[dict[str, Any]]: A list of result dictionaries, each with:
                - 'Id': The Salesforce record ID (if to delete succeeded).
                - 'success': A boolean indicating the update status.
                - 'errors': A list of any error messages encountered during the delete.

        Raises:
            ValueError: If any record is missing a valid 'Id' field.

        Example:
            results = client.bulk_update('Contact', [
                {'Id': '003XXXXXXXXXXXXAAA', 'Email': 'test@example.com'},
                {'Id': '003XXXXXXXXXXXXBBB', 'Phone': '1234567890'}
            ])
        """
        self._lookup_sf_type(object_name)

        # Collect records with invalid or missing Ids
        invalid_records = [
            (idx, record) for idx, record in enumerate(data)
            if 'Id' not in record or not str(record['Id']).strip()
        ]

        if invalid_records:
            error_msgs = "\n".join(
                f"Record at index {idx} is missing a valid 'Id': {record}"
                for idx, record in invalid_records
            )
            raise ValueError(f"Invalid records found:\n{error_msgs}")

        if data:
            bulk_handler = getattr(self._client.bulk, object_name)
            return bulk_handler.delete(data, **kwargs)
        return []
