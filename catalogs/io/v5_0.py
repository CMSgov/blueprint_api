import json

from datetime import datetime
from pathlib import Path
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field, UUID4, ValidationError  # pylint: disable=no-name-in-module


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


class Part(BaseModel):
    id: str
    name: str
    props: Optional[list[Prop]] = []
    parts: Optional[list["Part"]] = []
    prose: Optional[str]


class Control(BaseControl):
    props: Optional[list[Prop]] = []
    links: Optional[list[Link]] = []
    parts: Optional[list[Part]] = []

    def _get_prop(self, key: str, default: str = "") -> str:
        prop = next(filter(lambda prop_: prop_.name == key, self.props), None)

        if prop:
            return prop.value

        return default

    @property
    def label(self) -> str:
        return self._get_prop("label", self.title)

    @property
    def sort_id(self) -> str:
        return self._get_prop("sort-id", self.title)

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


class CatalogModel(BaseModel):
    uuid: UUID4
    metadata: CatalogMeta
    groups: list[Family]

    @property
    def controls(self) -> list[Control]:
        return [item for group in self.groups for item in group.controls]

    @classmethod
    def from_json(cls, json_file: Union[str, Path]):
        with open(json_file, "rb") as file:
            data = json.load(file)

        try:
            return cls(**data)
        except ValidationError:  # Try nested "catalog" field
            return cls(**data["catalog"])
