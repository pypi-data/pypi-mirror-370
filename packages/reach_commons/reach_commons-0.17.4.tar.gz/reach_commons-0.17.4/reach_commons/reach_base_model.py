from datetime import date, datetime, time, timezone
from typing import Any

from bson import ObjectId
from pydantic import BaseModel
from pydantic.v1 import validator
from pydantic_core import core_schema


class ReachUTCTimezoneModel(BaseModel):
    class Config:
        json_encoders = {
            datetime: lambda v: v.astimezone(timezone.utc).isoformat(
                timespec="microseconds"
            )
        }


class ReachBaseModel(BaseModel):
    def model_dump(self, *args, **kwargs):
        original_dict = super().model_dump(*args, **kwargs)

        def convert_value(value):
            if isinstance(value, datetime):
                return value.isoformat()
            elif isinstance(value, date):
                return value.isoformat()
            elif isinstance(value, time):
                return value.strftime("%H:%M:%S")
            elif isinstance(value, dict):
                return {k: convert_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [convert_value(item) for item in value]
            return value

        return {key: convert_value(value) for key, value in original_dict.items()}


class ReachDeserializeBaseModel(BaseModel):
    @validator("*", pre=True, always=True)
    def deserialize_values(cls, value, field):
        if isinstance(value, str):
            try:
                if field.type_ == datetime:
                    return datetime.fromisoformat(value)
                elif field.type_ == date:
                    return date.fromisoformat(value)
                elif field.type_ == time:
                    return datetime.strptime(value, "%H:%M:%S").time()
            except ValueError:
                pass  # Handle the case where the string is not in the expected format
        return value


class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(ObjectId),
                    core_schema.chain_schema(
                        [
                            core_schema.str_schema(),
                            core_schema.no_info_plain_validator_function(cls.validate),
                        ]
                    ),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, value) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")

        return ObjectId(value)
