import json
import logging
from typing import Any, List, Optional, Tuple

logger = logging.getLogger("catalogs.catalogio")


class CatalogTools:
    """Represent a catalog"""

    def __init__(self, source, text=False):
        try:
            self.oscal = self._load_catalog_json(source, text)
        except (IOError, FileNotFoundError, json.decoder.JSONDecodeError) as exc:
            logger.error("Unable to load catalog %s: %s", source, exc)
            raise CatalogLoadError(f"Could not load catalog {source}") from exc

        json.dumps(self.oscal)
        self.status = "ok"
        self.status_message = "Success loading catalog"
        self.catalog_id = self.oscal.get("id")
        self.info = {"groups": self.get_groups()}

    @staticmethod
    def _load_catalog_json(source, text):
        """Read catalog file - JSON"""
        oscal: dict = {}
        if text:
            oscal = json.loads(source)
        else:
            with open(source, "r") as file:
                oscal = json.load(file)
        return oscal.get("catalog")

    @staticmethod
    def find_dict_by_value(search_in, search_key: str, search_value: str):
        """
        Return the dictionary in an array of dictionaries with a key matching a value
        :param search_in: a list of dicts to search in
        :param search_key: the key to search for
        :param search_value: the value to search for
        :return: return a dict containing the search_value
        """
        if search_in is not None:
            results = next(
                (
                    s
                    for s in search_in
                    if search_key in s and s.get(search_key) == search_value
                ),
                None,
            )
        return results

    # Groups
    def get_groups(self) -> List:
        groups: List[dict] = []
        if self.oscal and "groups" in self.oscal:
            groups = self.oscal["groups"]
        return groups

    def get_group_ids(self):
        groups = self.get_groups()
        ids = [item.get("id") for item in groups]
        return ids

    def get_group_title_by_id(self, group_id):
        group = self.find_dict_by_value(self.get_groups(), "id", group_id)
        if group is None:
            return None
        return group.get("title")

    def get_group_id_by_control_id(self, control_id) -> str:
        """Return group id given id of a control"""
        group_ids = self.get_group_ids()
        gid: str = ""
        if group_ids:
            for group in group_ids:
                if group.lower() == control_id[:2].lower():
                    gid = group
        return gid

    # Controls
    def get_controls(self) -> List:
        controls: List[dict] = []
        for group in self.get_groups():
            controls += group.get("controls")
        return controls

    def get_control_ids(self) -> List:
        def _sort(control_id_: str) -> Tuple[str, float]:
            parts = control_id_.split("-")
            sub = float(parts.pop(-1))
            id_ = "-".join(parts)

            return id_, sub

        search_collection = self.get_controls()
        return sorted((item.get("id") for item in search_collection), key=_sort)

    def get_controls_all(self) -> List:
        controls: List[dict] = []
        for group in self.get_groups():
            for control in group.get("controls"):
                controls.append(control)
                if "controls" in control:
                    controls += control.get("controls")
        return controls

    def get_controls_all_ids(self) -> List:
        search_collection = self.get_controls_all()
        return [item["id"] for item in search_collection]

    def get_control_by_id(self, control_id: str) -> dict:
        """
        Return the dictionary in an array of dictionaries with a key matching a value
        """
        search_array = self.get_controls_all()
        search_key = "id"
        search_value = control_id
        result_dict: dict = next(
            (
                s
                for s in search_array
                if search_key in s and s[search_key] == search_value
            ),
            {},
        )
        return result_dict

    def get_next_control_by_id(self, control_id: str):
        search_collection = self.get_control_ids()
        try:
            next_idx = search_collection.index(control_id) + 1
            return search_collection[next_idx]
        except ValueError:
            logger.warning(
                "Cannot determine next control. Provided control does not exist in catalog(s): %s", control_id
            )
            return ""
        except IndexError:  # control_id was at the end of the list
            logger.info("No new controls.")
            return ""

    def get_control_statement(self, control: dict) -> List:
        statement = self.get_control_part_by_name(control, "statement")
        text: List[dict] = []
        if statement:
            if "parts" in statement:
                text = self.__get_parts(statement.get("parts"))
        return text

    def __get_parts(self, parts) -> List:
        section: List[dict] = []
        for part_data in parts:
            part: dict = {"prose": None, "parts": None}
            if "prose" in part_data:
                label = self.get_control_property_by_name(part_data, "label")
                prose = part_data.get("prose")
                part["prose"] = {label: prose}
            subpart: List[dict] = []
            if "parts" in part_data:
                subpart = self.__get_parts(part_data.get("parts"))
            if part:
                part["parts"] = subpart
            section.append(part)
        return section

    # Params
    def get_control_parameters(self, control: dict) -> dict:
        """Return the guidance prose for a control property"""
        return self.__get_control_parameter_values(control)

    def get_control_parameter_label_by_id(self, control: dict, param_id: str) -> str:
        """Return value of a parameter of a control by id of parameter"""
        param = self.find_dict_by_value(control.get("params"), "id", param_id)
        return param.get("label")

    # Props
    def get_control_property_by_name(self, control: dict, property_name: str) -> str:
        """Return value of a property of a control by name of property"""
        value: str = ""
        if control is None:
            return None
        prop: Optional[Any] = None
        # ARS 3.1 uses "properties" but 5.0 uses "props"
        if "properties" in control:
            prop = self.find_dict_by_value(
                control.get("properties"), "name", property_name
            )
        elif "props" in control:
            prop = self.find_dict_by_value(control.get("props"), "name", property_name)
        else:
            logger.warning("Can't find property '%s' in control data", property_name)
        if prop is not None:
            value = prop.get("value")
        return value

    def get_control_part_by_name(self, control: dict, part_name: str) -> dict:
        """Return value of a part of a control by name of part"""
        part: dict = {}
        if "parts" in control:
            part = self.find_dict_by_value(control.get("parts"), "name", part_name)
        return part

    def get_resource_by_uuid(self, uuid: str) -> dict:
        resource: dict = {}
        if "back-matter" in self.oscal and "resources" in self.oscal.get("back-matter"):
            resources = self.oscal.get("back-matter").get("resources")
            resource = self.find_dict_by_value(resources, "uuid", uuid)
        return resource

    @staticmethod
    def __get_control_parameter_values(control) -> dict:
        params: dict = {}
        if "params" in control:
            for param in control.get("params"):
                pid = param.get("id")
                if "values" in param:
                    params[pid] = param.get("values")
                elif "select" in param:
                    select = param.get("select")
                    howmany = select.get("how-many") if "how-many" in select else 1
                    params[pid] = {
                        howmany: select.get("choice"),
                    }
                else:
                    params[pid] = param.get("label")
        return params

    def get_control_data_simplified(self, control_id) -> dict:
        control = self.get_control_by_id(control_id)
        family_id = self.get_group_id_by_control_id(control_id)
        desc = self.get_control_statement(control)
        implementation = self.get_control_part_by_name(control, "implementation")
        guidance = self.get_control_part_by_name(control, "guidance")
        control_data = {
            "label": self.get_control_property_by_name(control, "label"),
            "sort_id": self.get_control_property_by_name(control, "sort-id"),
            "title": control.get("title"),
            "family": self.get_group_title_by_id(family_id),
            "description": self.__get_simplified_prose(desc),
            "implementation": implementation.get("prose") if implementation else "",
            "guidance": guidance.get("prose") if guidance else "",
            "next_id": self.get_next_control_by_id(control_id),
        }

        return control_data

    @staticmethod
    def __get_simplified_prose(prose: list):
        """"""
        if prose:
            text = prose[0]
            key = list(text.get("prose").keys())[0]
            return text.get("prose").get(key)

    @property
    def catalog_title(self) -> str:
        metadata = self.oscal.get("metadata", {})
        return metadata.get("title", "")


class CatalogLoadError(ValueError):
    pass


class MissingControlError(ValueError):
    pass
