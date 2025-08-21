from abc import ABCMeta, abstractmethod
from typing import Type, Literal

from ..dto import KintoneRecordCreatorField, \
    KintoneRecordCreatedTimeField, KintoneRecordModifierField, KintoneRecordUpdatedTimeField, \
    KintoneRecordDateField, KintoneRecordDateTimeField, KintoneRecordUserSelectField, \
    KintoneRecordField


class _KintoneQueryFunction(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def field_types(cls) -> list[Type[KintoneRecordField]]:
        raise NotImplementedError()

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError()

    def __hash__(self) -> int:
        return hash(str(self))


class _KintoneQueryUserFunction(_KintoneQueryFunction, metaclass=ABCMeta):
    @classmethod
    def field_types(cls) -> list[Type[KintoneRecordField]]:
        return [KintoneRecordCreatorField, KintoneRecordModifierField, KintoneRecordUserSelectField]


class LoginUser(_KintoneQueryUserFunction):
    # noinspection SpellCheckingInspection
    def __str__(self) -> str:
        return "LOGINUSER()"


class PrimaryOrg(_KintoneQueryUserFunction):
    def __str__(self) -> str:
        return "PRIMARY_ORGANIZATION()"


class _KintoneQueryDateFunction(_KintoneQueryFunction, metaclass=ABCMeta):
    @classmethod
    def field_types(cls) -> list[Type[KintoneRecordField]]:
        return [KintoneRecordDateField, KintoneRecordDateTimeField, KintoneRecordCreatedTimeField, KintoneRecordUpdatedTimeField]


class Now(_KintoneQueryDateFunction):
    def __str__(self) -> str:
        return "NOW()"


class Today(_KintoneQueryDateFunction):
    def __str__(self) -> str:
        return "TODAY()"


class Yesterday(_KintoneQueryDateFunction):
    def __str__(self) -> str:
        return "YESTERDAY()"


class Tomorrow(_KintoneQueryDateFunction):
    def __str__(self) -> str:
        return "TOMORROW()"


class FromToday(_KintoneQueryDateFunction):
    def __init__(self, value: int, unit: Literal["days", "weeks", "months", "years"]):
        self._value: int = value
        self._unit: Literal["days", "weeks", "months", "years"] = unit

    def __str__(self) -> str:
        return f"FROM_TODAY({self._value}, {self._unit.upper()})"


class _KintoneQueryDowFunction(_KintoneQueryDateFunction, metaclass=ABCMeta):
    def __init__(self, dow: Literal["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"] | None = None):
        self._dow: Literal["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"] | None = dow

    @classmethod
    @abstractmethod
    def _key(cls) -> str:
        raise NotImplementedError()

    def __str__(self) -> str:
        if self._dow is not None:
            return f"{self._key().upper()}({self._dow.upper()})"
        return f"{self._key().upper()}()"


class ThisWeek(_KintoneQueryDowFunction):
    @classmethod
    def _key(cls) -> str:
        return "THIS_WEEK"


class LastWeek(_KintoneQueryDowFunction):
    @classmethod
    def _key(cls) -> str:
        return "LAST_WEEK"


class NextWeek(_KintoneQueryDowFunction):
    @classmethod
    def _key(cls) -> str:
        return "NEXT_WEEK"


class ThisMonth(_KintoneQueryDateFunction):
    def __str__(self) -> str:
        return "THIS_MONTH()"


class LastMonth(_KintoneQueryDateFunction):
    def __str__(self) -> str:
        return "LAST_MONTH()"


class NextMonth(_KintoneQueryDateFunction):
    def __str__(self) -> str:
        return "NEXT_MONTH()"


class ThisYear(_KintoneQueryDateFunction):
    def __str__(self) -> str:
        return "THIS_YEAR()"


class LastYear(_KintoneQueryDateFunction):
    def __str__(self) -> str:
        return "LAST_YEAR()"


class NextYear(_KintoneQueryDateFunction):
    def __str__(self) -> str:
        return "NEXT_YEAR()"
