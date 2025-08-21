from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Type, TypeVar

from ...record.dto import KintoneRecordField, KintoneRecordCreatorField, KintoneRecordModifierField, \
    KintoneRecordSingleLineTextField, KintoneRecordNumberField, KintoneRecordCalcField, KintoneRecordCheckBoxField, \
    KintoneRecordRadioButtonField, KintoneRecordMultiSelectField, KintoneRecordDropDownField, \
    KintoneRecordUserSelectField, KintoneRecordOrgSelectField, KintoneRecordGroupSelectField, KintoneRecordLinkField, \
    KintoneRecordCategoryField, KintoneRecordStatusField, KintoneRecordAssigneeField, KintoneRecordCreatedTimeField, \
    KintoneRecordUpdatedTimeField, KintoneRecordDateField, KintoneRecordDateTimeField, KintoneRecordTimeField


class KintoneChartModes(Enum):
    NORMAL = "NORMAL"
    STACKED = "STACKED"
    PERCENTAGE = "PERCENTAGE"


class KintoneDateFreqs(Enum):
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"
    QUARTER = "QUARTER"


class KintoneTimeFreqs(Enum):
    HOUR = "HOUR"
    MINUTE = "MINUTE"


_GroupableFieldType = TypeVar(
    "_GroupableFieldType",
    KintoneRecordCreatorField,
    KintoneRecordModifierField,
    KintoneRecordSingleLineTextField,
    KintoneRecordNumberField,
    KintoneRecordCalcField,
    KintoneRecordCheckBoxField,
    KintoneRecordRadioButtonField,
    KintoneRecordMultiSelectField,
    KintoneRecordDropDownField,
    KintoneRecordUserSelectField,
    KintoneRecordOrgSelectField,
    KintoneRecordGroupSelectField,
    KintoneRecordLinkField,
    KintoneRecordCategoryField,
    KintoneRecordStatusField,
    KintoneRecordAssigneeField
)
_DateGroupableFieldType = TypeVar(
    "_DateGroupableFieldType",
    KintoneRecordCreatedTimeField,
    KintoneRecordUpdatedTimeField,
    KintoneRecordDateField,
    KintoneRecordDateTimeField
)
_TimeGroupableFieldType = TypeVar(
    "_TimeGroupableFieldType",
    KintoneRecordCreatedTimeField,
    KintoneRecordUpdatedTimeField,
    KintoneRecordTimeField,
    KintoneRecordDateTimeField
)
_DateTimeGroupableFieldType = TypeVar(
    "_DateTimeGroupableFieldType",
    KintoneRecordCreatedTimeField,
    KintoneRecordUpdatedTimeField,
    KintoneRecordDateTimeField
)
_CalculableFieldType = TypeVar(
    "_CalculableFieldType",
    KintoneRecordNumberField,
    KintoneRecordCalcField
)
_ComparableFieldType = TypeVar(
    "_ComparableFieldType",
    KintoneRecordNumberField,
    KintoneRecordCalcField,
    KintoneRecordDateField,
    KintoneRecordTimeField,
    KintoneRecordDateTimeField,
    KintoneRecordCreatedTimeField,
    KintoneRecordUpdatedTimeField
)


class _KintoneGrouper:
    # noinspection PyUnusedLocal
    def __init__(self, code: str, field_type: Type[KintoneRecordField]):
        self._code: str = code

    def to_json(self) -> dict:
        return {"code": self._code}


class KintoneDateGrouper(_KintoneGrouper):
    def __init__(self, code: str, field_type: Type[_DateGroupableFieldType], freq: KintoneDateFreqs):
        super().__init__(code, field_type)
        self._freq: KintoneDateFreqs = freq

    def to_json(self) -> dict:
        return {"code": self._code, "per": self._freq.value}


class KintoneTimeGrouper(_KintoneGrouper):
    def __init__(self, code: str, field_type: Type[_TimeGroupableFieldType], freq: KintoneTimeFreqs):
        super().__init__(code, field_type)
        self._freq: KintoneTimeFreqs = freq

    def to_json(self) -> dict:
        return {"code": self._code, "per": self._freq.value}


class KintoneDateTimeGrouper(_KintoneGrouper):
    def __init__(self, code: str, field_type: Type[_DateTimeGroupableFieldType], freq: KintoneDateFreqs | KintoneTimeFreqs):
        super().__init__(code, field_type)
        self._freq: KintoneDateFreqs | KintoneTimeFreqs = freq

    def to_json(self) -> dict:
        return {"code": self._code, "per": self._freq.value}


class KintoneGraphFrame:
    def __init__(self):
        self._groups: list[_KintoneGrouper] = []
        self._aggregations: list[tuple[str, str | None]] = []
        self._sorts: list[tuple[str | None, bool]] = []

    def groupby(self, by: tuple[str, Type[_GroupableFieldType]] | _KintoneGrouper) -> KintoneGraphFrame:
        if isinstance(by, tuple):
            self._groups.append(_KintoneGrouper(code=by[0], field_type=by[1]))
        else:
            self._groups.append(by)
        return self

    @property
    def group_count(self) -> int:
        return len(self._groups)

    def count(self) -> KintoneGraphFrame:
        self._aggregations.append(("COUNT", None))
        return self

    # noinspection PyUnusedLocal
    def sum(self, code: str, field_type: Type[_CalculableFieldType]) -> KintoneGraphFrame:
        self._aggregations.append(("SUM", code))
        return self

    # noinspection PyUnusedLocal
    def average(self, code: str, field_type: Type[_CalculableFieldType]) -> KintoneGraphFrame:
        self._aggregations.append(("AVERAGE", code))
        return self

    # noinspection PyUnusedLocal
    def max(self, code: str, field_type: Type[_ComparableFieldType]) -> KintoneGraphFrame:
        self._aggregations.append(("MAX", code))
        return self

    # noinspection PyUnusedLocal
    def min(self, code: str, field_type: Type[_ComparableFieldType]) -> KintoneGraphFrame:
        self._aggregations.append(("MIN", code))
        return self

    def sort_values(self, by: str | None = None, ascending: bool = True) -> KintoneGraphFrame:
        self._sorts.append((by, ascending))
        return self

    def build(self) -> dict:
        if len(self._groups) <= 0:
            raise ValueError("At least one group is required.")
        elif len(self._groups) > 3:
            raise ValueError("Up to 3 groups are supported.")
        groups: list[dict] = [group.to_json() for group in self._groups]
        aggregations: list[dict] = []
        for agg, code in self._aggregations:
            aggregation: dict = {"type": agg}
            if code is not None:
                aggregation["code"] = code
            aggregations.append(aggregation)
        sorts: list[dict] = []
        for by, ascending in self._sorts:
            order: str = "ASC" if ascending else "DESC"
            if by is None:
                sorts.append({"by": "TOTAL", "order": order})
                continue
            number: int | None = None
            for i, group in enumerate(groups):
                if group["code"] == by:
                    number = i + 1
                    break
            if number is None:
                raise ValueError(f"Group '{by}' is not found.")
            sorts.append({"by": f"GROUP{number}", "order": order})
        if len(sorts) == 0:
            sorts.append({"by": "TOTAL", "order": "ASC"})
        return {
            "groups": groups,
            "aggregations": aggregations,
            "sorts": sorts
        }


@dataclass
class KintoneGraphBuilder:
    name: str
    chart_type: str
    chart_mode: str | None
    data: KintoneGraphFrame

    def build(self) -> dict:
        graph: dict = self.data.build()
        graph.update({
            "chartType": self.chart_type,
            "name": self.name
        })
        if self.chart_mode is not None:
            graph["chartMode"] = self.chart_mode
        return graph


def barplot(name: str, data: KintoneGraphFrame, mode: KintoneChartModes = KintoneChartModes.NORMAL) -> KintoneGraphBuilder:
    # 横棒グラフ
    return KintoneGraphBuilder(name, "BAR", mode.value, data)


def columnplot(name: str, data: KintoneGraphFrame, mode: KintoneChartModes = KintoneChartModes.NORMAL) -> KintoneGraphBuilder:
    # 縦棒グラフ
    return KintoneGraphBuilder(name, "COLUMN", mode.value, data)


def pieplot(name: str, data: KintoneGraphFrame) -> KintoneGraphBuilder:
    # 円グラフ
    return KintoneGraphBuilder(name, "PIE", None, data)


def lineplot(name: str, data: KintoneGraphFrame) -> KintoneGraphBuilder:
    # 折れ線グラフ
    return KintoneGraphBuilder(name, "LINE", None, data)


def pivot_table_plot(name: str, data: KintoneGraphFrame) -> KintoneGraphBuilder:
    # クロス集計表
    if data.group_count < 2:
        raise ValueError("At least two groups are required.")
    return KintoneGraphBuilder(name, "PIVOT_TABLE", None, data)


def tableplot(name: str, data: KintoneGraphFrame) -> KintoneGraphBuilder:
    # 表
    return KintoneGraphBuilder(name, "TABLE", None, data)


def areaplot(name: str, data: KintoneGraphFrame, mode: KintoneChartModes = KintoneChartModes.NORMAL) -> KintoneGraphBuilder:
    # 面グラフ
    return KintoneGraphBuilder(name, "AREA", mode.value, data)


def splineplot(name: str, data: KintoneGraphFrame, mode: KintoneChartModes = KintoneChartModes.NORMAL) -> KintoneGraphBuilder:
    # 曲線グラフ
    return KintoneGraphBuilder(name, "SPLINE", mode.value, data)


def spline_area_plot(name: str, data: KintoneGraphFrame, mode: KintoneChartModes = KintoneChartModes.NORMAL) -> KintoneGraphBuilder:
    # 曲線面グラフ
    return KintoneGraphBuilder(name, "SPLINE_AREA", mode.value, data)
