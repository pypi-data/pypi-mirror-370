from datetime import date, datetime
from pathlib import Path
from typing import Any, Generic, TypeVar, cast

from google.protobuf.message import Message
from google.protobuf.timestamp_pb2 import Timestamp
from ...private_eye.external.external_pb2 import ExternalData

_TMessage = TypeVar("_TMessage", bound=Message)

_empty_datetime = Timestamp().ToDatetime()
_empty_date = Timestamp().ToDatetime().date()


class _ProtobufMessageProxy(Generic[_TMessage]):
    """
    Proto3 does not have the concept of 'null', or 'not set' for singular fields.
    Whenever we access a property of a Protobuf message class, it will return a default value whenever that property
    has not been set:
    * Empty string for strings
    * 0 for numbers of any sort
    * empty instance of the appropriate message subclass for nested messages
    * False for booleans

    This proxy automatically performs the following in order to make reading these classes easier:
    * Converts empty strings to `None` automatically, as in our case they will have identical meaning
    * Returns `None` instead of an empty message when getting an unset nested message field.
        Note: Timestamp messages are an exception - we always return those, as the default Timestamp value of
              1970-01-01T00:00:00 technically *does* have a business meaning.
    * If attempting to fetch a 'oneof' property directly, it will fetch the property within the 'oneof' which is set,
      or if no property is set, it will return None. This way allows us to handle optional primitive values by wrapping
      then in a oneof field. For example, given the following:
      ```
      oneof patient_dob {
          google.protobuf.Timestamp patient_dob_value = 6;
      }
      ```
      if attempting to fetch `patient_dob`, we shall return the value of `patient_dob_value` if it set, or `None`
      otherwise.
    """

    def __init__(self, proxied: _TMessage):
        if isinstance(proxied, _ProtobufMessageProxy):
            raise ValueError("Proxied class cannot itself be a proxy")
        self.__proxied = proxied

    def __getattr__(self, name: str) -> Any:
        try:
            real_field_name = self.__proxied.WhichOneof(name)
            # In this case we know that we're dealing with a 'oneof' field which hasn't been set,
            # so immediately return None
            if not real_field_name:
                return None
        except ValueError:
            real_field_name = name

        value = getattr(self.__proxied, real_field_name)

        try:
            field = self.__proxied.DESCRIPTOR.fields_by_name[real_field_name]
        except KeyError:
            pass
        else:
            if field.type == field.TYPE_STRING:
                # We convert all empty strings to None
                return value if value else None
            # Timestamp fields are nested message types. However, the default value of Timestamp could have a business
            # meaning, so we treat it as a singular type and do not nullify it
            if field.type == field.TYPE_MESSAGE and not isinstance(value, Timestamp):
                # If there is no value set for the nested message, we return None
                # Otherwise, we wrap the message in a proxy and return it
                if self.__proxied.HasField(real_field_name):
                    return protobuf_proxy(value)
                return None
        # In all other cases we return the original value
        return value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} for {repr(self.__proxied)}"


def protobuf_proxy(value: _TMessage) -> _TMessage:
    if isinstance(value, _ProtobufMessageProxy):
        proxy = value
    else:
        proxy = _ProtobufMessageProxy(value)
    # Clearly _ProtobufMessageProxy will not be 'castable' to the value type in the traditional sense.
    # However, it will contain exactly the same properties and methods in practice as the incoming type,
    # so by the principles of duck typing this cast is valid.
    return cast(_TMessage, proxy)


def read_data_from_file(file: Path) -> ExternalData:
    data = ExternalData()
    with file.open("rb") as f:
        data.ParseFromString(f.read())
    return data


def write_data_to_file(data: ExternalData, file: Path) -> None:
    with file.open("wb") as f:
        f.write(data.SerializeToString())


def timestamp_from_date(dt: date) -> Timestamp:
    if not isinstance(dt, datetime):
        dt = datetime.combine(dt, datetime.min.time())
    ret = Timestamp()
    ret.FromDatetime(dt)
    return ret
