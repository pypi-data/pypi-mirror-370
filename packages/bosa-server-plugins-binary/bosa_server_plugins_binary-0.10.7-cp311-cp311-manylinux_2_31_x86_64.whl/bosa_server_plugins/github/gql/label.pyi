from pydantic import BaseModel

class GQLLabel(BaseModel):
    """Label model."""
    id: str
    name: str
    color: str
    description: str | None
    is_default: bool
    @classmethod
    def from_dict(cls, data: dict) -> GQLLabel:
        """Create a GQLLabel from a dictionary.

        Args:
            data: The dictionary to create the label from.

        Returns:
            GQLLabel: The created label.
        """

label_fragment: str
