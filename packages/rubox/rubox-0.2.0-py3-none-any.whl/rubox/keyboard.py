# rubox/keyboard.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Union, Dict, Any
from .dict_like import DictLike
from .enums import (
    ChatTypeEnum,
    ButtonTypeEnum,
    ButtonSelectionTypeEnum,
    ButtonSelectionSearchEnum,
    ButtonSelectionGetEnum,
    ButtonCalendarTypeEnum,
    ButtonTextboxTypeKeypadEnum,
    ButtonTextboxTypeLineEnum,
    ButtonLocationTypeEnum,
)

# =============================
# Base & Utility
# =============================

@dataclass
class Location(DictLike):
    longitude: Optional[str] = None
    latitude: Optional[str] = None


@dataclass
class BaseButtonData(DictLike):
    """Base class for button data objects with helper methods."""

    def as_dict(self) -> Dict[str, Any]:
        """Convert to clean dict, removing None values."""
        return {k: v for k, v in self.__dict__.items() if v is not None}


# =============================
# Button Data Types
# =============================

@dataclass
class ButtonSelectionItem(BaseButtonData):
    text: Optional[str] = None
    image_url: Optional[str] = None
    type: Optional[ButtonSelectionTypeEnum] = None


@dataclass
class ButtonSelection(BaseButtonData):
    selection_id: Optional[str] = None
    search_type: Optional[ButtonSelectionSearchEnum] = None
    get_type: Optional[ButtonSelectionGetEnum] = None
    items: List[ButtonSelectionItem] = field(default_factory=list)
    is_multi_selection: bool = False
    columns_count: Optional[int] = None
    title: Optional[str] = None


@dataclass
class ButtonCalendar(BaseButtonData):
    default_value: Optional[str] = None
    type: Optional[ButtonCalendarTypeEnum] = None
    min_year: Optional[int] = None
    max_year: Optional[int] = None
    title: Optional[str] = None


@dataclass
class ButtonNumberPicker(BaseButtonData):
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    default_value: Optional[int] = None
    title: Optional[str] = None


@dataclass
class ButtonStringPicker(BaseButtonData):
    items: List[str] = field(default_factory=list)
    default_value: Optional[str] = None
    title: Optional[str] = None


@dataclass
class ButtonTextbox(BaseButtonData):
    type_line: Optional[ButtonTextboxTypeLineEnum] = None
    type_keypad: Optional[ButtonTextboxTypeKeypadEnum] = None
    place_holder: Optional[str] = None
    title: Optional[str] = None
    default_value: Optional[str] = None


@dataclass
class ButtonLocation(BaseButtonData):
    default_pointer_location: Optional[Location] = None
    default_map_location: Optional[Location] = None
    type: Optional[ButtonLocationTypeEnum] = None
    title: Optional[str] = None
    location_image_url: Optional[str] = None


@dataclass
class JoinChannel(BaseButtonData):
    username: Optional[str] = None
    automatic_join: bool = False

    def __post_init__(self):
        if self.username:
            self.username = self.username.replace('@', '')


@dataclass
class OpenChat(BaseButtonData):
    object_guid: Optional[str] = None
    object_type: Optional[ChatTypeEnum] = None


@dataclass
class ButtonLink(BaseButtonData):
    type: Optional[str] = None
    link_url: Optional[str] = None
    joinchannel_data: Optional[JoinChannel] = None
    open_chat_data: Optional[OpenChat] = None

    def __post_init__(self):
        if not self.link_url:
            return

        RubikaURL = {
            "https://rubika.ir/joing/": "rubika://g.rubika.ir/",
            "https://rubika.ir/joinc/": "rubika://c.rubika.ir/",
            "https://rubika.ir/post/": "rubika://p.rubika.ir/",
        }

        self.link_url = next(
            (self.link_url.replace(p, d, 1) for p, d in RubikaURL.items() if self.link_url.startswith(p)),
            self.link_url
        )

# =============================
# Button & Keypad
# =============================

@dataclass
class Button(DictLike):
    id: Optional[str] = None
    type: Optional[ButtonTypeEnum] = None
    button_text: Optional[str] = None
    button_selection: Optional[ButtonSelection] = None
    button_calendar: Optional[ButtonCalendar] = None
    button_number_picker: Optional[ButtonNumberPicker] = None
    button_string_picker: Optional[ButtonStringPicker] = None
    button_location: Optional[ButtonLocation] = None
    button_textbox: Optional[ButtonTextbox] = None
    button_link: Optional[ButtonLink] = None

    def as_dict(self) -> Dict[str, Any]:
        result = {k: v for k, v in self.__dict__.items() if v is not None}
        for key, value in result.items():
            if isinstance(value, DictLike):
                result[key] = value.as_dict()
            elif isinstance(value, list):
                result[key] = [v.as_dict() if isinstance(v, DictLike) else v for v in value]
        return result


@dataclass
class KeypadRow(DictLike):
    buttons: List[Button] = field(default_factory=list)


@dataclass
class Keypad(DictLike):
    rows: List[KeypadRow] = field(default_factory=list)
    resize_keyboard: bool = False
    on_time_keyboard: bool = False
