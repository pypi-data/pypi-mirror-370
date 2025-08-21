import copy
from typing import TypeVar, Type, Any, Dict, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    AliasGenerator,
    field_validator,
    Field,
    model_validator,
    create_model,
)
from pydantic.fields import FieldInfo  # noqa
from pydantic_extra_types import pendulum_dt

from pmsintegration.core import custom_fields
from pmsintegration.platform import errors


class CustomAttributeValue(BaseModel):
    date: pendulum_dt.DateTime | None = None
    value: str | bool | None = None
    weight: float = 1.0

    @classmethod
    def create(cls, value: str = None, date: pendulum_dt.DateTime = None, weight: float = 1.0):
        if value is not None and date is not None:
            raise errors.IllegalArgumentException("either value and date must be set")
        # Do we want to set all 3 always?
        return cls(value=value or date, weight=weight)


class LenientEntity(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True,
        populate_by_name=True,
        extra="allow")

    def init(self, relationships):
        ...


class Raw(LenientEntity):
    ...


class TypedLenientEntity(LenientEntity):
    id: str | int | None = Field(exclude=True, default=None)
    type: str | None = Field(exclude=True, default=None)

    def __hash__(self):
        return hash(f"{self.type}|{self.id}")

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id and self.type == other.type


LET = TypeVar("LET", bound=LenientEntity)


class SalesforceAddeparIdLink(BaseModel):
    salesforce_object_name: str
    salesforce_addepar_id_field_name: str
    record_id: str
    addepar_id: str | int


class SalesforceAddeparEntity(TypedLenientEntity):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            serialization_alias=custom_fields.alias,
            alias=custom_fields.alias,
        )
    )
    __salesforce_object_name__: str = None
    __salesforce_addepar_id_field_name__: str = "Addepar_ID__c"
    salesforce_link: list[CustomAttributeValue] | str | None = None
    corient_salesforce_id: list[CustomAttributeValue] | str = None
    corient_client_status: list[CustomAttributeValue] | str = None
    corient_custodian: list[CustomAttributeValue] | str = None
    corient_billing_account_level_fee: list[CustomAttributeValue] | str = None
    corient_billing_account_level_fee_2: list[CustomAttributeValue] | str = None
    corient_erisa_flag: bool | list[CustomAttributeValue] | str = None
    corient_managedunmanaged: list[CustomAttributeValue] | str = None
    wrap_fee_program: list[CustomAttributeValue] | str = None
    sma_program: list[CustomAttributeValue] | str = None
    margin_account: bool | list[CustomAttributeValue] | str = None
    affiliated_flag: bool | list[CustomAttributeValue] | str | None = None
    corient_office_region: list[CustomAttributeValue] | str | None = None
    office_l2: list[CustomAttributeValue] | str | None = None
    office_l1: list[CustomAttributeValue] | str | None = None
    legacy_office: list[CustomAttributeValue] | str | None = None
    client_owner: list[CustomAttributeValue] | str | None = None

    @field_validator("corient_office_region", mode="before")
    def _preprocess_corient_office_region(cls, v):
        return [CustomAttributeValue(value=v)] if isinstance(v, str) else v

    @field_validator("office_l2", mode="before")
    def _preprocess_office_l2(cls, v):
        return [CustomAttributeValue(value=v)] if isinstance(v, str) else v

    @field_validator("office_l1", mode="before")
    def _preprocess_office_l1(cls, v):
        return [CustomAttributeValue(value=v)] if isinstance(v, str) else v

    @field_validator("legacy_office", mode="before")
    def _preprocess_legacy_office(cls, v):
        return [CustomAttributeValue(value=v)] if isinstance(v, str) else v

    @field_validator("client_owner", mode="before")
    def _preprocess_client_owner(cls, v):
        return [CustomAttributeValue(value=v)] if isinstance(v, str) else v

    @field_validator("affiliated_flag", mode="before")
    def _preprocess_affiliated_flag(cls, v):
        return [CustomAttributeValue(value=v)] if isinstance(v, str) else v

    @field_validator("salesforce_link", mode="before")
    def _preprocess_salesforce_link(cls, v):
        return [CustomAttributeValue(value=v)] if isinstance(v, str) else v

    @field_validator("corient_salesforce_id", mode="before")
    def _preprocess_corient_salesforce_id(cls, v):
        return [CustomAttributeValue(value=v)] if isinstance(v, str) else v

    @field_validator("corient_client_status", mode="before")
    def _preprocess_corient_client_status(cls, v):
        return [CustomAttributeValue(value=v)] if isinstance(v, str) else v

    @field_validator("corient_custodian", mode="before")
    def _preprocess_corient_custodian(cls, v):
        return [CustomAttributeValue(value=v)] if isinstance(v, str) else v

    @field_validator("corient_billing_account_level_fee", mode="before")
    def _preprocess_corient_billing_account_level_fee(cls, v):
        return [CustomAttributeValue(value=v)] if isinstance(v, str) else v

    @field_validator("corient_billing_account_level_fee_2", mode="before")
    def _preprocess_corient_billing_account_level_fee_2(cls, v):
        return [CustomAttributeValue(value=v)] if isinstance(v, str) else v

    @field_validator("corient_erisa_flag", mode="before")
    def _preprocess_corient_erisa_flag(cls, v):
        return [CustomAttributeValue(value=v)] if isinstance(v, bool) else v

    @field_validator("corient_managedunmanaged", mode="before")
    def _preprocess_corient_managedunmanaged(cls, v):
        return [CustomAttributeValue(value=v)] if isinstance(v, str) else v

    @field_validator("wrap_fee_program", mode="before")
    def _preprocess_wrap_fee_program(cls, v):
        return [CustomAttributeValue(value=v)] if isinstance(v, str) else v

    @field_validator("sma_program", mode="before")
    def _preprocess_sma_program(cls, v):
        return [CustomAttributeValue(value=v)] if isinstance(v, str) else v

    @field_validator("margin_account", mode="before")
    def _preprocess_margin_account(cls, v):
        return [CustomAttributeValue(value=v)] if isinstance(v, bool) else v

    def get_corient_office_region(self) -> object:
        return self.corient_office_region[0].value

    def get_office_l2(self) -> object:
        return self.office_l2[0].value

    def get_office_l1(self) -> object:
        return self.office_l1[0].value

    def get_legacy_office(self) -> object:
        return self.legacy_office[0].value

    def get_client_owner(self) -> object:
        return self.client_owner[0].value

    def get_affiliated_flag(self) -> object:
        return self.affiliated_flag[0].value

    def get_salesforce_link(self) -> object:
        return self.salesforce_link[0].value

    def get_corient_salesforce_id(self) -> object:
        """Return salesforce id.

        We know that the custom field is always going to be populated the salesforce id/record id in the
        first value
        """
        return self.corient_salesforce_id[0].value

    def get_corient_client_status(self) -> object:
        return self.corient_client_status[0].value

    def get_corient_custodian(self) -> object:
        return self.corient_custodian[0].value

    def get_corient_billing_account_level_fee(self) -> object:
        return self.corient_billing_account_level_fee[0].value

    def get_corient_billing_account_level_fee_2(self) -> object:
        return self.corient_billing_account_level_fee_2[0].value

    def get_corient_corient_erisa_flag(self) -> object:
        return self.corient_erisa_flag[0].value

    def get_corient_managedunmanaged(self) -> object:
        return self.corient_managedunmanaged[0].value

    def get_corient_wrap_fee_program(self) -> object:
        return self.wrap_fee_program[0].value

    def get_corient_sma_program(self) -> object:
        return self.sma_program[0].value

    def get_corient_margin_account(self) -> object:
        return self.margin_account[0].value

    def new_salesforce_addepar_id_link(self):
        return SalesforceAddeparIdLink(
            salesforce_object_name=self.__salesforce_object_name__,
            salesforce_addepar_id_field_name=self.__salesforce_addepar_id_field_name__,
            record_id=self.corient_salesforce_id[0].value,
            addepar_id=self.id,
        )

    def new_salesforce_addepar_contact_id_link(self):
        return SalesforceAddeparIdLink(
            salesforce_object_name=self.__salesforce_object_name__,
            salesforce_addepar_id_field_name=self.__salesforce_addepar_id_field_name__,
            record_id=self.external_user_id,
            addepar_id=self.id,
        )

    @classmethod
    def validate_at_least_one_field(cls, values):
        if not any(value is not None for value in values.values()):
            raise ValueError("Error in")
        return values

    @classmethod
    def create_update_model(cls) -> Type["SalesforceAddeparEntity"]:
        update_model_name = cls.__name__ + "Update"
        fields: dict[str, FieldInfo] = cls.__pydantic_fields__

        def _copy_field_info_with_default(f):
            cloned = copy.copy(f)
            if cloned.is_required():
                cloned.default = None
            return cloned

        mutable_fields: Dict[str, Any] = {
            name: (Optional[info.annotation], _copy_field_info_with_default(info))
            for name, info in fields.items()
        }

        update_model = create_model(
            update_model_name,
            **mutable_fields,
            __base__=cls,
        )
        return update_model


class GenericSalesforceAddeparEntity(SalesforceAddeparEntity):
    # Specify/override this attribute in the specific impl
    __x_model_type__ = "__model_type__"
    x_model_type: str | None = Field(alias="model_type", default=None)
    fin_serv_status: str | None = Field(exclude=True, default=None)

    def is_deleted(self):
        # TODO Review this condition
        return self.fin_serv_status == "Inactive"

    @model_validator(mode="before")
    def add_processed_attribute(cls, values: dict) -> dict:
        if cls.__x_model_type__ != '__model_type__':
            values["x_model_type"] = cls.__x_model_type__
        return values
