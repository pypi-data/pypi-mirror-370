from __future__ import annotations

from pydantic import Field, model_validator
from typing import Any, Optional, Union, TYPE_CHECKING, List, Dict

from .base import BaleObject
from .thumbnail import Thumbnail
from .file_ext import DocumentsExt
from .gift_packet import GiftPacket
from .service_message import ServiceMessage
from .inline_keyboard import InlineKeyboardMarkup
from ..utils import generate_id


class TextMessage(BaleObject):
    """
    Represents a plain text message content.
    """

    value: str = Field(..., alias="1")
    """The actual text content of the message."""

    if TYPE_CHECKING:

        def __init__(__pydantic__self__, *, value: str, **__pydantic_kwargs) -> None:
            super().__init__(value=value, **__pydantic_kwargs)


class MessageCaption(BaleObject):
    """
    Represents an optional caption attached to media messages.
    """

    content: Optional[str] = Field(None, alias="1")
    """The caption text."""

    mentions: Optional[Union[List, Dict]] = Field(default_factory=dict, alias="2")
    """
    Mentions inside the caption.
    This may include user references or tags.
    Initialized as an empty dict by default.
    """

    ext: Optional[Dict] = Field(default_factory=dict, alias="3")
    """
    Extension metadata related to the caption.
    Used for additional, non-standard information.
    """

    if TYPE_CHECKING:

        def __init__(
            __pydantic__self__,
            *,
            content: Optional[str] = None,
            mentions: Optional[Union[List, Dict]] = None,
            ext: Optional[Dict] = None,
            **__pydantic_kwargs,
        ) -> None:
            super().__init__(
                content=content, mentions=mentions, ext=ext, **__pydantic_kwargs
            )


class DocumentMessage(BaleObject):
    """
    Represents a document or file message content.
    """

    file_id: int = Field(..., alias="1")
    """Unique file identifier."""

    access_hash: int = Field(..., alias="2")
    """Security hash required for accessing the file."""

    size: Optional[int] = Field(None, alias="3")
    """File size in bytes, if known."""

    name: Optional[Union[Dict, str]] = Field(None, alias="4")
    """
    The file name.
    Can be a plain string or a dictionary for localized names.
    """

    mime_type: str = Field(..., alias="5")
    """MIME type describing the file format."""

    thumb: Optional[Thumbnail] = Field(None, alias="6")

    ext: Optional[DocumentsExt] = Field(None, alias="7")
    """Optional additional metadata or extensions."""

    caption: Optional[MessageCaption] = Field(None, alias="8")
    """Caption associated with the document message."""

    if TYPE_CHECKING:

        def __init__(
            __pydantic__self__,
            *,
            file_id: int,
            access_hash: int,
            size: Optional[int] = None,
            name: Union[Dict, str],
            mime_type: str,
            ext: Optional[Dict] = None,
            caption: Optional[MessageCaption] = None,
            thumb: Optional[Thumbnail] = None,
            **__pydantic_kwargs,
        ) -> None:
            super().__init__(
                file_id=file_id,
                access_hash=access_hash,
                size=size,
                name=name,
                mime_type=mime_type,
                ext=ext,
                caption=caption,
                thumb=thumb,
                **__pydantic_kwargs,
            )


class TemplateMessage(BaleObject):
    """
    Represents a template message that can be sent, including its content,
    a unique temporary ID, and optional inline keyboard markup.
    """

    message: MessageContent = Field(..., alias="1")
    """The main content of the message."""

    temp_id: int = Field(default_factory=generate_id, alias="2")
    """A unique temporary identifier for the message, generated automatically."""

    inline_keyboard_markup: Optional[InlineKeyboardMarkup] = Field(None, alias="5")
    """Optional inline keyboard markup to be attached to the message."""

    if TYPE_CHECKING:
        # This __init__ is only used for type checking and IDE autocomplete.
        # It will not be included in runtime behavior.
        def __init__(
            __pydantic__self__,
            *,
            message: MessageContent,
            temp_id: int = ...,
            inline_keyboard_markup: Optional[InlineKeyboardMarkup] = None,
            **__pydantic_kwargs,
        ) -> None:
            super().__init__(
                message=message,
                temp_id=temp_id,
                inline_keyboard_markup=inline_keyboard_markup,
                **__pydantic_kwargs
            )


class MessageContent(BaleObject):
    """
    Container for different types of message content.
    """

    document: Optional[DocumentMessage] = Field(None, alias="4")
    """Optional document content if the message includes a file."""

    empty: bool = Field(False, alias="5")
    """Indicates whether the message is either forwarded or an empty stub."""

    text: Optional[TextMessage] = Field(None, alias="15")
    """Optional text content if the message is a plain text message."""

    service_message: Optional[ServiceMessage] = Field(None, alias="11")
    bot_message: Optional[TemplateMessage] = Field(None, alias="13")
    gift: Optional[GiftPacket] = Field(None, alias="17")

    if TYPE_CHECKING:

        def __init__(
            __pydantic__self__,
            *,
            document: Optional[DocumentMessage] = None,
            epmty: bool = False,
            text: Optional[TextMessage] = None,
            gift: Optional[GiftPacket] = None,
            bot_message: Optional[TemplateMessage] = None,
            **__pydantic_kwargs,
        ) -> None:
            super().__init__(
                document=document,
                text=text,
                epmty=epmty,
                gift=gift,
                bot_message=bot_message,
                **__pydantic_kwargs,
            )

    @model_validator(mode="before")
    @classmethod
    def _check_empty(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        if "5" in data:
            data["5"] = True

        return data
