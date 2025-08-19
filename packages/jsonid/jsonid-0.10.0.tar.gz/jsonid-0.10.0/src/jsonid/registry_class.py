"""Dataclasses for the registry objects."""

from dataclasses import dataclass, field
from typing import Final, Optional

import yaml

try:
    import helpers
except ModuleNotFoundError:
    try:
        from src.jsonid import helpers
    except ModuleNotFoundError:
        from jsonid import helpers


JSON_ID: Final[int] = "jrid:0000:json"
JSONL_ID: Final[int] = "jrid:0000:jsonl"
YAML_ID: Final[int] = "jrid:0000:yaml"
TOML_ID: Final[int] = "jrid:0000:toml"


@dataclass
class RegistryEntry:  # pylint: disable=R0902
    """Class that represents information that might be derived from
    a registry.
    """

    identifier: str = ""
    name: list = field(default_factory=list)
    version: Optional[str | None] = None
    description: list = field(default_factory=list)
    pronom: str = ""
    wikidata: str = ""
    loc: str = ""
    archive_team: str = ""
    rfc: str = ""
    mime: list[str] = field(default_factory=list)
    markers: list[dict] = field(default_factory=list)
    depth: int = 0
    additional: str = ""
    encoding: str = ""

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __str__(self):
        """Return summary string."""
        if self.identifier in (JSON_ID, JSONL_ID, YAML_ID, TOML_ID):
            data = {
                "identifiers": [
                    {"rfc": self.rfc},
                    {"pronom": self.pronom},
                    {"loc": self.loc},
                    {"wikidata": self.wikidata},
                ],
                "documentation": [
                    {"archive_team": self.archive_team},
                ],
                "mime": self.mime,
                "name": self.name,
                "depth": self.depth,
                "additional": self.additional,
                "encoding": self.encoding,
            }
            return yaml.dump(data, indent=2, allow_unicode=True).strip()
        data = {
            "identifiers": [
                {"rfc": self.rfc},
                {"pronom": self.pronom},
                {"loc": self.loc},
                {"wikidata": self.wikidata},
            ],
            "documentation": [
                {"archive_team": self.archive_team},
            ],
            "mime": self.mime,
            "name": self.name,
            "additional": self.additional,
            "encoding": self.encoding,
            "description": self.description,
        }
        return yaml.dump(data, indent=2, allow_unicode=True).strip()

    def json(self):
        """Override default __dict__ behavior."""
        obj = self
        new_markers = []
        for marker in obj.markers:
            try:
                replace_me = marker["ISTYPE"]
                replace_me = helpers.substitute_type_text(replace_me)
                marker["ISTYPE"] = replace_me
                new_markers.append(marker)
            except (KeyError, AttributeError):
                new_markers.append(marker)
        if not new_markers:
            return obj.__dict__
        obj.markers = new_markers
        return obj.__dict__
