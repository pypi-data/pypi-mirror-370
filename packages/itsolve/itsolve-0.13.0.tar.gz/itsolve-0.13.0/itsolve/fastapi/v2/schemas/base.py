from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Schema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        validate_by_name=True,
        frozen=True,
        extra="ignore",
        validate_by_alias=True,
        alias_generator=to_camel,
        revalidate_instances="subclass-instances",
        serialize_by_alias=True,
    )
