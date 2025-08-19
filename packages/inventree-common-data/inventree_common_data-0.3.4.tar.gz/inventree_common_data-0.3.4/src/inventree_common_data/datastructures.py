"""Data structures for the Inventree Common Data plugin."""

import json
from pathlib import Path
from typing import Union
from uuid import uuid4

import yaml
from pydantic import AnyUrl, BaseModel, Field
from typing_extensions import Annotated


class SelectionListEntryModel(BaseModel):
    """Model that describes an entry in a SelectionList."""

    value: Union[str, float, int]
    label: str
    description: str


class SourceModel(BaseModel):
    """Model that describes the source of a SelectionList."""

    text: str
    url: Union[AnyUrl, None] = None


class SelectionListModel(BaseModel):
    """Model that describes the definition of a SelectionList."""

    name: str
    description: str
    source: Union[SourceModel, None] = None
    default: Union[str, int, None] = None
    entries: list[SelectionListEntryModel]


class FileSourceSelectionListModel(BaseModel):
    """Model that describes the files that are sources for SeclectionLists."""

    name: str
    version: str
    identifier: Annotated[str, Field(default_factory=lambda: uuid4().hex)]
    path: Union[Path, None] = None
    data: Union[SelectionListModel, None] = None

    def __str__(self) -> str:
        """Return short string representation."""
        return f"{self.identifier}_{self.version}_{self.name}"

    def load(self) -> Union[SelectionListModel, None]:
        """Load the data from the file."""
        if self.data is None and self.path is not None and self.path.exists():
            self.data = SelectionListModel.model_validate(
                yaml.safe_load(self.path.open())
            )
        return self.data

    def get_source_string(self) -> str:
        """Get a string representation of the source."""
        return "_".join([self.identifier, self.version, self.name])


if __name__ == "__main__":
    """Generate schema for the data model if called directly."""
    main_model_schema = FileSourceSelectionListModel.model_json_schema()
    Path("schema.json").write_text(json.dumps(main_model_schema, indent=2))
