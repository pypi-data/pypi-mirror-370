import time
from pydantic import Field
from typing import TYPE_CHECKING, Any

from ...types.responses import DefaultResponse
from ...enums import Services
from ..base import BaleMethod


class EditName(BaleMethod):
    """
    Edits the name of a user.

    Returns:
        aiobale.types.responses.DefaultResponse: The response indicating the success or failure of the operation.
    """

    __service__ = Services.USER.value
    __method__ = "EditName"

    __returning__ = DefaultResponse

    name: str = Field(..., alias="1")
    """
    The new name to be set for the user.
    """

    if TYPE_CHECKING:
        # This init is only used for type checking and IDE autocomplete.
        # It will not be included in runtime behavior.
        def __init__(
            __pydantic__self__, *, name: str, **__pydantic_kwargs: Any
        ) -> None:
            super().__init__(name=name, **__pydantic_kwargs)
