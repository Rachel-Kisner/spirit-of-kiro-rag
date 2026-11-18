
# 1 - Import Pydantic components
from pydantic import BaseModel, Field


# 2 - Define the common structure for extracted items
class ExtractedItem(BaseModel):
    name: str = Field(
        description="The name of the extracted item"
    )

    category: str = Field(
        description="The category of the extracted item"
    )

    description: str = Field(
        description="A short description based only on the source document"
    )

    source_location: str | None = Field(
        default=None,
        description="The section or heading where the information appears"
    )

    source_file: str | None = Field(  # NEW
        default=None,  # NEW
        description="The name of the source document"  # NEW
    )


# 3 - Define the Technology data model
class TechnologyItem(ExtractedItem):
    """Represents a technology or service used in the project."""


# 4 - Define the Architecture data model
class ArchitectureItem(ExtractedItem):
    """Represents an architectural component or pattern."""


# 5 - Define the Rule data model
class RuleItem(ExtractedItem):
    """Represents a development rule or convention."""


# 6 - Define the complete extraction result
class ExtractedData(BaseModel):
    technologies: list[TechnologyItem] = Field(
        default_factory=list,
        description="All technologies identified in the document"
    )

    architecture: list[ArchitectureItem] = Field(
        default_factory=list,
        description="All architectural components and patterns identified"
    )

    rules: list[RuleItem] = Field(
        default_factory=list,
        description="All development rules and conventions identified"
    )
