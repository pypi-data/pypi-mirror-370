import json
import logging
import time
from functools import lru_cache
from typing import Generator, Type, Callable, Any

import httpx
from httpx import BasicAuth, Timeout, Response

from pmsintegration.core import core_models
from pmsintegration.core.addepar.connector.addepar_config import AddeparRestConnectorConfig
from pmsintegration.core.addepar.connector.api_models import (
    APIData,
    APIVersion,
    Attribute,
    EntityType,
    DataWrapper,
    GroupType
)
from pmsintegration.core.addepar.connector.response_handler import (
    unwrap_json_payload,
    paginate_and_unwrap_json_payload,
    make_json_response_model, make_no_data_json_response_model
)
from pmsintegration.core.core_models import LET
from pmsintegration.core.core_models import TypedLenientEntity
from pmsintegration.core.observability.metrics_relay import MetricsHook
from pmsintegration.platform import utils, errors
from pmsintegration.platform.concurrent_utils import halt_requested

_log = logging.getLogger(__name__)


class Endpoints:
    API_ATTRIBUTES = "/v1/attributes"
    API_ENTITIES = "/v1/entities"
    API_VERSION = "/v1/api_version"
    API_ENTITY_TYPES = "/v1/entity_types"
    API_GROUPS = "/v1/groups"
    API_GROUP_MEMBERS = "/v1/groups/{}/relationships/members"
    API_GROUP_TYPES = "/v1/group_types"
    API_POSITIONS = "/v1/positions"
    API_TRANSACTIONS = "/v1/transactions"
    API_BILLABLE_PORTFOLIO = "/v1/billable_portfolios"

    # CONTACTS APIs
    API_CONTACTS = "/v1/contacts"
    API_CONTACT_UPDATE = API_CONTACTS + "/{}"
    API_CONTACT_VIEW_SET = API_CONTACTS + "/{}/relationships/default_view_set"
    API_CONTACT_ENTITY_AFFILIATIONS = API_CONTACTS + "/{}/relationships/entity_affiliations"
    API_CONTACT_GROUP_AFFILIATIONS = API_CONTACTS + "/{}/relationships/group_affiliations"
    API_CONTACT_TEAM_AFFILIATIONS = API_CONTACTS + "/{}/relationships/team"
    API_CONTACT_RESTORE = API_CONTACTS + "/{}/restore"
    API_CONTACT_REVOKE = API_CONTACTS + "/{}/revoke"
    API_CONTACT_2FA_EXEMPT = API_CONTACTS + "/{}/exempt_two_factor_authentication"
    API_CONTACT_2FA = API_CONTACTS + "/{}/require_two_factor_authentication"
    API_CONTACT_ENABLE_SAML = API_CONTACTS + "/{}/enable_saml"
    API_CONTACT_DISABLE_SAML = API_CONTACTS + "/{}/disable_saml"


class AddeparRestAPIClient:
    def __init__(self, config: AddeparRestConnectorConfig):
        self._config = config
        self._base_url = utils.ensure_endswith(config.endpoint.rstrip("/"), "/api")
        hooks = MetricsHook(namespace="addepar")
        self._httpx = httpx.Client(
            base_url=self._base_url,
            auth=BasicAuth(config.addepar_api_key, config.addepar_api_token),
            # transport=MetricsTransport(httpx.HTTPTransport()),
            headers={
                "Addepar-Firm": str(config.addepar_firm),
                "Content-Type": "application/vnd.api+json",
                "Accept": "application/vnd.api+json",
            },
            event_hooks={
                "request": [hooks.on_request],
                "response": [hooks.on_response],
                "error": [hooks.on_exception]
            },
            timeout=Timeout(
                read=config.read_timeout_in_seconds,
                connect=config.connect_timeout_in_seconds,
                write=config.read_timeout_in_seconds,
                pool=config.read_timeout_in_seconds,
            ),
            **config.transport
        )
        self._attribute_mapping: dict[str, str] = {}

    def get_base_url(self):
        return self._base_url

    def http_request_handler(self, method: str, url: str, **kwargs: object) -> Response:
        """
        Sends an HTTP request using the configured httpx client.

        Args:
            method (str): The HTTP method (e.g., "GET", "POST", "PUT", "DELETE").
            url (str): The target URL for the request.
            **kwargs: Additional keyword arguments passed to httpx (e.g., headers, params, json, timeout).

        Returns:
            httpx.Response: The response object from the HTTP request.

        Raises:
            httpx.RequestError: If an error occurs while making the request (e.g., network failure).
            httpx.HTTPStatusError: If the response contains an HTTP error status.
        """
        response = self._httpx.request(method, url, **kwargs)
        if response.status_code in (429, 502):
            for attempt in range(3):
                _log.warning(f"Retrying due to staus code: {response.status_code}")
                retry_after = int(response.headers.get("Retry-After", "30"))
                time.sleep(retry_after)
                response = self._httpx.request(method, url, **kwargs)
                if response.status_code not in (429, 502):
                    break

        return response

    def get_api_version(self) -> APIVersion:
        """Get the  Addepar current API version
        """
        return unwrap_json_payload(
            self.http_request_handler("GET", Endpoints.API_VERSION),
            APIVersion
        )

    def get_attributes(self,
                       category: str | None = None,
                       usage: str | None = None,
                       output_type: str | None = None,
                       ) -> Generator[Attribute, str, None]:
        """Retrieve all attributes available to the user.

        This method returns a list of attributes that belong to a particular category, usage, and output type.
        The parameters can be used to filter the attributes.

        :param category: Optional. The category of the attributes to retrieve. Can be None to include all categories.
        For examples: Cash Flows, Security Details, Holding Details, etc.
        :param usage: Optional. The usage of the attributes to filter by. Can be None to include all usages. For
        examples: columns, groupings, filters, position_custom_attributes, entity_custom_attributes,entity_attributes
        :param output_type: Optional. The output type of the attributes. Can be None to include all output types. For
        examples: Word, Boolean, Percent, Date, Currency, List, Number.

        :return: A list of attributes that match the given filters. If no filters are provided, returns all attributes.
        :rtype: list
        """

        params = {}
        if category:
            params["filter[category]"] = category
        if usage:
            params["filter[usage]"] = usage
        if output_type:
            params["filter[output_type]"] = output_type

        return paginate_and_unwrap_json_payload(
            self.http_request_handler(method="GET", url=Endpoints.API_ATTRIBUTES, params=params),
            Attribute,
            self._httpx
        )

    def get_entities(self,
                     entity_type: Type[LET],
                     linking_status: str | None = None,
                     created_before: str | None = None,
                     created_after: str | None = None,
                     modified_before: str | None = None,
                     modified_after: str | None = None,
                     fields_entities: str | None = None,
                     transform: Callable[[LET], Any] | None = None
                     ) -> Generator[LET, str, None]:
        """Retrieve all attributes available to the user with additional filtering options.
        This method returns a list of attributes that belong to a particular category, usage, and output type,
        and allows for additional filtering based on linking status, creation/modification date ranges,
        and specific fields for entities.
        :param transform: Callable parameter that is used in paginate function to get whole object
        :param entity_type: Required. Entity Type.
        :param linking_status: Optional. Filter based on linking status ('linked' or 'unlinked').
        :param created_before: Optional. Filter for entities created before a specific date. Can be None to include all.
        :param created_after: Optional. Filter for entities created after a specific date. Can be None to include all.
        :param modified_before: Optional. Filter for entities modified before a specific date.
        :param modified_after: Optional. Filter for entities modified after a specific date. Can be None to include all.
        :param fields_entities: Optional. Fields to include in the entity response (e.g., 'model_type,ownership_type').
        :return: A list of attributes that match the given filters.
        :rtype: list
        """
        params = {}
        if linking_status:
            params["filter[linking_status]"] = linking_status
        if created_before:
            params["filter[created_before]"] = created_before
        if created_after:
            params["filter[created_after]"] = created_after
        if modified_before:
            params["filter[modified_before]"] = modified_before
        if modified_after:
            params["filter[modified_after]"] = modified_after
        if fields_entities:
            params["fields[entities]"] = fields_entities

        return paginate_and_unwrap_json_payload(
            self.http_request_handler(method="GET", url=Endpoints.API_ENTITIES, params=params),
            entity_type,
            self._httpx,
            transform
        )

    def create_entity(self, request_id: str, payload: DataWrapper) -> APIData | list[APIData]:
        """Create a new entity in Addepar.

        :param request_id: A unique, randomly generated ID that identifies the attempt.
                           This is critical for preventing duplicate object creation.
        :param payload: The payload containing the entity object or list of entity objects.

        :return: An entity_create_response upon successful entity creation.
        """
        return self._perform_request(
            "POST",
            Endpoints.API_ENTITIES,
            request_id,
            payload
        )

    def get_entity_types(self) -> Generator[EntityType, str, None]:
        """Discover the available entity types including associated attributes, attributes required for creation,
         and which attributes are editable.

         """
        params = {}
        return paginate_and_unwrap_json_payload(
            self.http_request_handler(method="GET", url=Endpoints.API_ENTITY_TYPES, params=params),
            EntityType,
            self._httpx
        )

    def update_entity(self, request_id: str, payload: DataWrapper) -> APIData | list[APIData]:
        """Update an existing entity in Addepar.

        :param request_id: A unique, randomly generated ID that identifies the attempt.
                           This is critical for preventing duplicate object creation.
        :param payload: The payload containing the entity object or list of entity objects.

        :return: An entity_update_response upon successful entity update.
        """
        return self._perform_request(
            "PATCH",
            Endpoints.API_ENTITIES,
            request_id,
            payload)

    def delete_entity(self, request_id: str, payload: DataWrapper) -> APIData | list[APIData]:
        """Delete an existing entity or existing entities from Addepar.

        :param request_id: A unique, randomly generated ID that identifies the attempt.
                           This is critical for preventing duplicate object creation.
        :param payload: The payload containing the entity id or list of entity ids.

        :return: An entity_delete_response upon successful entity update.
        """
        return self._perform_request(
            "DELETE",
            Endpoints.API_ENTITIES,
            request_id,
            payload
        )

    @lru_cache(1024)
    def lookup_custom_field_name(self, field_name: str) -> str:
        """Lookup custom field name

        :param field_name: Name of custom field
        :return custom_<field_name>_<field_id>
        """
        mapping = self._attribute_mapping

        mapped_field_name = mapping.get(field_name)
        if mapped_field_name:
            return mapped_field_name
        _custom = "_custom_"
        for attribute in self.get_attributes():
            attribute_id = attribute.id
            if attribute_id.startswith(_custom):
                inferred_field_name = (
                    attribute_id
                    .removeprefix(_custom)
                    .removesuffix(f"_{attribute.spec_id}")
                )
            else:
                inferred_field_name = attribute_id
            conflicting_api_field_name = mapping.get(inferred_field_name)
            if conflicting_api_field_name:
                raise errors.IllegalStateException(
                    f"There seems conflicting field names: {conflicting_api_field_name}, {attribute_id}")
            mapping[inferred_field_name] = attribute_id

        api_field_name = mapping.get(field_name)
        if not api_field_name:
            raise errors.IllegalArgumentException(f"'{field_name}' is not known in the attribute universe")
        return api_field_name

    def get_groups(self,
                   group_type: Type[LET],
                   created_before: str | None = None,
                   created_after: str | None = None,
                   modified_before: str | None = None,
                   modified_after: str | None = None,
                   fields_groups: str | None = None,
                   transform: Callable[[LET], Any] | None = None
                   ) -> Generator[LET, str, None]:
        """
        Retrieve all attributes available to the user with additional filtering options.
        This method returns a list of attributes that belong to a particular category, usage, and output type,
        and allows for additional filtering based on linking status, creation/modification date ranges,
        and specific fields for groups.
        :param transform: Callable parameter that is used in paginate function to get whole object
        :param group_type: Required. Group Type.
        :param created_before: Optional. Filter for entities created before a specific date. Can be None to include all.
        :param created_after: Optional. Filter for entities created after a specific date. Can be None to include all.
        :param modified_before: Optional. Filter for entities modified before a specific date.
        :param modified_after: Optional. Filter for entities modified after a specific date. Can be None to include all.
        :param fields_groups: Optional. Fields to include in the entity response (e.g., 'model_type,ownership_type').
        :return: A list of attributes that match the given filters.
        :rtype: list
        """

        params = {}
        filters = {
            "filter[created_before]": created_before,
            "filter[created_after]": created_after,
            "filter[modified_before]": modified_before,
            "filter[modified_after]": modified_after,
            "fields[groups]": fields_groups,
        }

        for key, value in filters.items():
            if value is not None:
                params[key] = value

        return paginate_and_unwrap_json_payload(
            self.http_request_handler(method="GET", url=Endpoints.API_GROUPS, params=params),
            group_type,
            self._httpx,
            transform
        )

    def get_group_types(
            self,
            is_permissioned_resource: bool = None,
    ) -> Generator[GroupType, str, None]:
        """Retrieve all group types for the firm.

        :param: is_permissioned_resource:
            If true, users will need access to groups of this type. This is referred to as "Explicit access" in Addepar.
            If false, users will need to have access to each individual member of a group to access groups of this type.
             This is referred to as "Implicit access" in Addepar.
         """
        params = {}
        if is_permissioned_resource is not None:
            params["filter[is_permissioned_resource]"] = str(is_permissioned_resource).lower()

        return paginate_and_unwrap_json_payload(
            self.http_request_handler(method="GET", url=Endpoints.API_GROUP_TYPES, params=params),
            GroupType,
            self._httpx
        )

    def create_group(self, request_id: str, payload: DataWrapper) -> APIData | list[APIData]:
        return self._perform_request(
            "POST",
            Endpoints.API_GROUPS,
            request_id,
            payload
        )

    def update_group(self, request_id: str, payload: DataWrapper) -> APIData | list[APIData]:
        """Update an existing group in Addepar.

        :param request_id: A unique, randomly generated ID that identifies the attempt.
                           This is critical for preventing duplicate object creation.
        :param payload: The payload containing the entity object or list of entity objects.

        :return: An entity_update_response upon successful entity update.
        """
        return self._perform_request(
            "PATCH",
            Endpoints.API_GROUPS,
            request_id,
            payload)

    def delete_groups(self, request_id: str, payload: DataWrapper) -> APIData | list[APIData]:
        """Delete an existing group or existing groups from Addepar.

        :param request_id: A unique, randomly generated ID that identifies the attempt.
                           This is critical for preventing duplicate object creation.
        :param payload: The payload containing the entity id or list of group ids.

        :return: A group_delete_response upon successful group delete.
        """
        return self._perform_request(
            "DELETE",
            Endpoints.API_GROUPS,
            request_id,
            payload
        )

    def create_billable_portfolio(self, request_id: str, payload: DataWrapper) -> APIData | list[APIData]:
        return self._perform_request_no_data_response(
            "POST",
            Endpoints.API_BILLABLE_PORTFOLIO,
            request_id,
            payload)

    def _perform_request_no_data_response(
            self,
            method: str,
            endpoint: str,
            request_id: str,
            payload: DataWrapper
    ) -> APIData | list[APIData]:
        if not request_id:
            msg = "request_id must be unique and not null. Currently uniqueness check "
            "is not implemented"
            raise errors.IllegalArgumentException(msg)

        json_payload = payload.model_dump(exclude_unset=True, by_alias=True)

        _log.info("Request payload:")
        _log.info(json.dumps(json_payload, indent=2))
        _log.info(f"Request method : {method}")
        _log.info("---")

        try:
            # get the inferred type
            inferred_type = payload.infer_attributes_type()

            # Validate before passing it
            safe_type = inferred_type if isinstance(inferred_type, type) else None

            return make_no_data_json_response_model(
                self.http_request_handler(
                    method,
                    endpoint,
                    json=json_payload,
                ),
                safe_type,  # Only pass None or a proper class type
                isinstance(payload.data, list)
            ).data
        except Exception as e:
            _log.error(
                f"_perform_request_no_data_response failed. "
                f"Inferred type was: {type(inferred_type)}. "
                f"Error: {e}"
            )
            raise

    def _perform_request(
            self,
            method: str,
            endpoint: str,
            request_id: str,
            payload: DataWrapper
    ) -> APIData | list[APIData]:
        if not request_id:
            msg = "request_id must be unique and not null. Currently uniqueness check "
            "is not implemented"
            raise errors.IllegalArgumentException(msg)

        json_payload = payload.model_dump(exclude_unset=True, by_alias=True)

        _log.info("Request payload:")
        _log.info(json.dumps(json_payload, indent=2))
        _log.info(f"Request method : {method}")
        _log.info("---")

        try:
            return make_json_response_model(
                self.http_request_handler(method=method, url=endpoint, json=json_payload),
                payload.infer_attributes_type(),
                isinstance(payload.data, list)
            ).data
        except Exception as e:
            _log.error(f"Exception occurred while sending to Addepar: {e}")

    def add_group_relationship(
            self,
            request_id: str,
            group_id: str,
            payload: DataWrapper
    ) -> APIData:
        json_payload = payload.model_dump(exclude_unset=True, by_alias=True)

        _log.info(f"Request ({request_id} payload:")
        _log.info(json.dumps(json_payload, indent=2))
        _log.info("---")
        return self._perform_request(
            "POST",
            Endpoints.API_GROUP_MEMBERS.format(group_id),
            request_id,
            payload
        )

    def get_group_members(self, group_id: str, _rt: Type[core_models.LET]) -> list[TypedLenientEntity]:
        return make_json_response_model(
            self.http_request_handler(
                method="GET",
                url=Endpoints.API_GROUP_MEMBERS.format(group_id),
            ),
            _rt,
            True,
        ).data

    def replace_group_members(self, request_id: str, group_id: str, payload: DataWrapper):
        json_payload = payload.model_dump(exclude_unset=True, by_alias=True)

        _log.info(f"Request ({request_id} payload:")
        _log.info(json.dumps(json_payload, indent=2))
        _log.info("---")
        response = self.http_request_handler(
            method="PATCH",
            url=Endpoints.API_GROUP_MEMBERS.format(group_id),
            json=json_payload,
        )
        response.raise_for_status()

    def delete_group_members(self, request_id: str, group_id: str, payload: DataWrapper):
        json_payload = payload.model_dump(exclude_unset=True, by_alias=True)

        _log.info(f"Request ({request_id} payload:")
        _log.info(json.dumps(json_payload, indent=2))
        _log.info("---")
        response = self.http_request_handler(
            method="DELETE",
            url=Endpoints.API_GROUP_MEMBERS.format(group_id),
            json=json_payload,
        )
        response.raise_for_status()

    def get_positions(self,
                      entity_type: Type[LET],
                      created_before: str | None = None,
                      created_after: str | None = None,
                      modified_before: str | None = None,
                      modified_after: str | None = None,
                      fields_positions: str | None = None,
                      transform: Callable[[LET], Any] | None = None
                      ) -> Generator[LET, str, None]:
        """Retrieve all attributes available to the user with additional filtering options.
        This method returns a list of attributes that belong to a particular category, usage, and output type,
        and allows for additional filtering based on linking status, creation/modification date ranges,
        and specific fields for positions.
        :param transform: Callable parameter that is used in paginate
        :param entity_type: Required. Entity Type.
        :param created_before: Optional. Filter for position created before a specific date. Can be None to include all.
        :param created_after: Optional. Filter for position created after a specific date. Can be None to include all.
        :param modified_before: Optional. Filter for position modified before a specific date.
        :param modified_after: Optional. Filter for position modified after a specific date. Can be None to include all.
        :param fields_positions: Optional. Fields to include in the position response
        (e.g., 'model_type,ownership_type').
        :return: A list of attributes that match the given filters.
        :rtype: list
        """
        params = {}
        filters = {
            "filter[created_before]": created_before,
            "filter[created_after]": created_after,
            "filter[modified_before]": modified_before,
            "filter[modified_after]": modified_after,
            "fields[positions]": fields_positions,
        }

        for key, value in filters.items():
            if value is not None:
                params[key] = value

        return paginate_and_unwrap_json_payload(
            self.http_request_handler(method="GET", url=Endpoints.API_POSITIONS, params=params),
            entity_type,
            self._httpx,
            transform
        )

    def create_positions(self, request_id: str, payload: DataWrapper) -> APIData | list[APIData]:
        """Create a new position in Addepar.

        :param request_id: A unique, randomly generated ID that identifies the attempt.
                           This is critical for preventing duplicate object creation.
        :param payload: The payload containing the position object and list of entities.

        :return: An entity_create_response upon successful entity creation.
        """

        return self._perform_request(
            "POST",
            Endpoints.API_POSITIONS,
            request_id,
            payload
        )

    def update_positions(self, request_id: str, payload: DataWrapper) -> APIData | list[APIData]:
        """Create a new position in Addepar.

        :param request_id: A unique, randomly generated ID that identifies the attempt.
                           This is critical for preventing duplicate object creation.
        :param payload: The payload containing the position object and list of entities.

        :return: An entity_create_response upon successful entity creation.
        """
        return self._perform_request(
            "PATCH",
            Endpoints.API_POSITIONS,
            request_id,
            payload
        )

    def delete_positions(self, request_id: str, payload: DataWrapper) -> APIData | list[APIData]:
        """Create a new position in Addepar.

        :param request_id: A unique, randomly generated ID that identifies the attempt.
                           This is critical for preventing duplicate object creation.
        :param payload: The payload containing the position object and list of entities.

        :return: An entity_create_response upon successful entity creation.
        """
        return self._perform_request(
            "DELETE",
            Endpoints.API_POSITIONS,
            request_id,
            payload
        )

    def create_transactions(self, request_id: str, payload: DataWrapper) -> APIData | list[APIData]:
        """Create a new transaction in Addepar.

        :param request_id: A unique, randomly generated ID that identifies the attempt.
                           This is critical for preventing duplicate object creation.
        :param payload: The payload containing the position object and list of entities.

        :return: An entity_create_response upon successful entity creation.
        """

        return self._perform_request(
            "POST",
            Endpoints.API_TRANSACTIONS,
            request_id,
            payload
        )

    def create_contact(self, request_id: str, payload: DataWrapper) -> APIData | list[APIData]:
        """Create a new position in Addepar.

        :param request_id: A unique, randomly generated ID that identifies the attempt.
                           This is critical for preventing duplicate object creation.
        :param payload: The payload containing the position object and list of entities.

        :return: An entity_create_response upon successful entity creation.
        """

        return self._perform_request(
            "POST",
            Endpoints.API_CONTACTS,
            request_id,
            payload
        )

    def update_contact(self, request_id: str, payload: DataWrapper, contact_id: str) -> APIData | list[APIData]:
        """Create a new position in Addepar.

        :param request_id: A unique, randomly generated ID that identifies the attempt.
                           This is critical for preventing duplicate object creation.
        :param contact_id: Unique Addepar ID of an existing Contact
        :param payload: The payload containing the attributes to be updated.

        :return: An update_contact_response upon successful contact update.
        """

        return self._perform_request(
            "PATCH",
            Endpoints.API_CONTACT_UPDATE.format(contact_id),
            request_id,
            payload
        )

    def update_contact_view_set(
            self,
            request_id: str,
            contact_id: str,
            payload: DataWrapper) -> APIData | list[APIData]:
        """Update a contacts default viewset in Addepar.

        :param request_id: A unique, randomly generated ID that identifies the attempt.
                           This is critical for preventing duplicate object creation.
        :param contact_id: Unique Addepar ID of an existing Contact
        :param payload: The payload containing the attributes to be updated.

        :return: An update_contact_response upon successful contact update.
        """

        return self._perform_request(
            "POST",
            Endpoints.API_CONTACT_VIEW_SET.format(contact_id),
            request_id,
            payload
        )

    def update_contact_entity_affiliation(
            self,
            request_id: str,
            contact_id: str,
            payload: DataWrapper) -> APIData | list[APIData]:
        """Set a contact's entity_affiliation in Addepar.

        :param request_id: A unique, randomly generated ID that identifies the attempt.
                           This is critical for preventing duplicate object creation.
        :param contact_id: Unique Addepar ID of an existing Contact
        :param payload: The payload containing the attributes to be updated.

        :return: An update_contact_response upon successful contact update.
        """

        return self._perform_request(
            "PATCH",
            Endpoints.API_CONTACT_ENTITY_AFFILIATIONS.format(contact_id),
            request_id,
            payload
        )

    def contact_2fa_exempt(
            self,
            request_id: str,
            contact_id: str,
            payload: DataWrapper) -> APIData | list[APIData]:
        """2FA-Exempt a contact in Addepar.

        :param request_id: A unique, randomly generated ID that identifies the attempt.
                           This is critical for preventing duplicate object creation.
        :param contact_id: Unique Addepar ID of an existing Contact
        :param payload: The payload containing the attributes to be updated.

        :return: no response upon successful contact update.
        """

        return self._perform_request_no_data_response(
            "PATCH",
            Endpoints.API_CONTACT_2FA_EXEMPT.format(contact_id),
            request_id,
            payload
        )

    def contact_revoke_access(
            self,
            request_id: str,
            contact_id: str,
            payload: DataWrapper) -> APIData | list[APIData]:
        """Revoke access for a contact in Addepar.

        :param request_id: A unique, randomly generated ID that identifies the attempt.
                           This is critical for preventing duplicate object creation.
        :param contact_id: Unique Addepar ID of an existing Contact
        :param payload: The payload containing the attributes to be updated.

        :return: no response upon successful contact update.
        """

        return self._perform_request_no_data_response(
            "PATCH",
            Endpoints.API_CONTACT_REVOKE.format(contact_id),
            request_id,
            payload
        )

    def contact_restore_access(
            self,
            request_id: str,
            contact_id: str,
            payload: DataWrapper) -> APIData | list[APIData]:
        """Restore access for a previously revoked contact in Addepar.

        :param request_id: A unique, randomly generated ID that identifies the attempt.
                           This is critical for preventing duplicate object creation.
        :param contact_id: Unique Addepar ID of an existing Contact
        :param payload: The payload containing the attributes to be updated.

        :return: no response upon successful contact update.
        """

        return self._perform_request_no_data_response(
            "PATCH",
            Endpoints.API_CONTACT_RESTORE.format(contact_id),
            request_id,
            payload
        )

    def delete_contact(
            self,
            request_id: str,
            contact_id: str,
            payload: DataWrapper) -> APIData | list[APIData]:

        return self._perform_request_no_data_response(
            "DELETE",
            Endpoints.API_CONTACT_UPDATE.format(contact_id),
            request_id,
            payload
        )

    def perform_raw_get(
            self,
            endpoint: str,
            **params
    ) -> Generator[bytes, str | None, None]:

        next_url = endpoint

        while next_url:
            response = self.http_request_handler(method="GET", url=next_url, params=params)
            response.raise_for_status()
            data = response.content

            next_link = yield data
            if next_link == "stop":
                _log.info(f"Response explicitly stopped: {endpoint}")
                break

            if halt_requested():
                _log.info("Halt/kill was requested stopping in between")
                break

            next_url = next_link
            params = None  # Only send filters on the first request
