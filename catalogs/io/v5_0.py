import json
import logging

from datetime import datetime
from pathlib import Path
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field, UUID4, ValidationError, validator  # pylint: disable=no-name-in-module

logger = logging.getLogger(__name__)


class CatalogMeta(BaseModel):
    class Meta:
        allow_population_by_field_name = True

    title: str
    published: datetime
    last_modified: datetime = Field(..., alias="last-modified")
    version: str
    oscal_version: str = Field(..., alias="oscal-version")


class BaseControl(BaseModel):
    class Meta:
        allow_population_by_field_name = True

    id: str
    item_class: str = Field(..., alias="class")
    title: str


class Prop(BaseModel):
    name: str
    value: str


class Link(BaseModel):
    href: str
    rel: str


# noinspection PyUnresolvedReferences
class FilterMixin:
    def _filter_list_field(self, key: str, field: str):
        return next(filter(lambda item_: item_.name == key, getattr(self, field)), None)

    def _get_prop(self, key: str) -> "Prop":
        return self._filter_list_field(key, field="props")

    def _get_part(self, key: str) -> "Part":
        return self._filter_list_field(key, field="parts")

    @property
    def label(self) -> str:
        prop = self._get_prop("label")

        if not prop:
            return self.id

        return prop.value


class Part(BaseModel, FilterMixin):
    id: str
    name: str
    props: Optional[list[Prop]] = []
    parts: Optional[list["Part"]] = []
    prose: Optional[str] = ""


class Control(BaseControl, FilterMixin):
    family_id: Optional[str] = Field(default="", exclude=True)
    props: Optional[list[Prop]] = []
    links: Optional[list[Link]] = []
    parts: Optional[list[Part]] = []

    @property
    def sort_id(self) -> str:
        prop = self._get_prop("sort-id")

        if not prop:
            return self.title

        return prop.value

    @property
    def statement(self) -> Part:
        return self._get_part("statement")

    @property
    def implementation(self) -> str:
        part = self._get_part("implementation")

        if not part:
            return ""

        return part.prose

    @property
    def guidance(self) -> str:
        part = self._get_part("guidance")

        if not part:
            return ""

        return part.prose

    @property
    def description(self) -> str:
        def _get_prose(item, depth=0):
            depth += 1
            tabs = "\t" * depth

            if prose := getattr(item, "prose", ""):
                prose = f"\n{tabs}{item.label}. {prose}"
                parts.append(prose)

            if parts_ := getattr(item, "parts", []):
                for part in parts_:
                    _get_prose(part, depth)

        parts = []
        _get_prose(self.statement, depth=-3)

        return "".join(parts).strip()

    def to_orm(self) -> dict:
        return {
            "control_id": self.id,
            "control_label": self.label,
            "sort_id": self.sort_id,
            "title": self.title
        }


class Family(BaseControl):
    item_class: Literal["family"] = Field(..., alias="class")
    controls: list[Control]

    @validator("controls")
    def set_family_id(cls, value: list[Control], values) -> list[Control]:  # pylint: disable=no-self-argument
        for item in value:
            if not item.family_id:
                item.family_id = values.get("id")

        return value


class CatalogModel(BaseModel):
    uuid: UUID4
    metadata: CatalogMeta
    groups: list[Family]

    @property
    def controls(self) -> list[Control]:
        return sorted((item for group in self.groups for item in group.controls), key=lambda control: control.sort_id)

    def get_control(self, control_id: str) -> Optional[Control]:
        return next(filter(lambda control: control.id == control_id, self.controls), None)

    def get_next(self, control: Control) -> str:
        try:
            next_idx = self.controls.index(control) + 1
            return self.controls[next_idx].id
        except (ValueError, IndexError):
            return ""

    def control_summary(self, control_id: str) -> dict:
        control = self.get_control(control_id)
        next_id = self.get_next(control)

        return {
            "label": control.label,
            "sort_id": control.sort_id,
            "title": control.title,
            "family": control.family_id,
            "description": control.description,
            "implementation": control.implementation,
            "guidance": control.guidance,
            "next_id": next_id

        }

    @classmethod
    def from_json(cls, json_file: Union[str, Path]):
        with open(json_file, "rb") as file:
            data = json.load(file)

        try:
            return cls(**data)
        except ValidationError:  # Try nested "catalog" field
            return cls(**data["catalog"])
