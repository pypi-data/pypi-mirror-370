from io import BytesIO
from os import PathLike
from typing import Any, Callable, Dict, Literal, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field


class StyleProperty(BaseModel):
    name: str
    display: str
    value_map: Dict[str, str] = Field(default_factory=dict)


class Style(BaseModel):
    class Config:
        frozen = True

    text_align: Optional[
        Literal[
            "left",
            "center",
            "right",
        ]
    ] = Field(default=None)
    align: Optional[
        Literal[
            "left",
            "center",
            "right",
        ]
    ] = Field(default=None)
    padding: Optional[str] = Field(default=None)
    padding_left: Optional[str] = Field(default=None)
    padding_right: Optional[str] = Field(default=None)
    padding_top: Optional[str] = Field(default=None)
    padding_bottom: Optional[str] = Field(default=None)
    font_size: Optional[float] = Field(default=None)
    font_color: Optional[str] = Field(default=None)
    font_family: Optional[str] = Field(default=None)
    bold: Optional[bool] = Field(default=None)
    border: Optional[str] = Field(default=None)
    border_left: Optional[str] = Field(default=None)
    border_right: Optional[str] = Field(default=None)
    border_top: Optional[str] = Field(default=None)
    border_bottom: Optional[str] = Field(default=None)
    border_style: Optional[str] = Field(default=None)
    border_color: Optional[str] = Field(default=None)
    background_color: Optional[str] = Field(default=None)
    text_wrap: Optional[bool] = Field(default=None)

    def merge(self, other: "Style") -> "Style":
        self_dict = self.model_dump(exclude_none=True)
        other_dict = other.model_dump(exclude_none=True)
        self_dict.update(other_dict)
        return self.model_validate(self_dict)


class Component(BaseModel):
    style: Style = Field(default_factory=Style)

    class Config:
        arbitrary_types_allowed = True


class Text(Component):
    text: str
    width: float = Field(default=1)
    height: float = Field(default=1)


class Link(Component):
    text: str
    href: str
    width: float = Field(default=1)
    height: float = Field(default=1)


class Fill(Component):
    width: str = Field(default="100%")
    height: str = Field(default="20px")


class Image(Component):
    data: Union[PathLike, bytes, bytearray, BytesIO]
    format: Literal["png", "jpeg", "jpg", "gif", "svg"] = Field(default="png")
    width: str = Field(default="800px")
    height: Optional[str] = Field(default=None)


class Table(Component):
    data: pd.DataFrame
    header_style: Dict[str, Style] = Field(default_factory=dict)
    body_style: Style = Field(default_factory=Style)
    column_style: Dict[str, Union[Style, Callable[[Any], Style]]] = Field(
        default_factory=dict
    )
    column_widths: Dict[str, float] = Field(default_factory=dict)
    row_style: Dict[int, Style] = Field(default_factory=dict)
    max_col_width: Optional[float] = Field(default=None)
    header_filters: bool = Field(default=True)
    default_style: bool = Field(default=True)
    auto_width_tuning: float = Field(default=5)
    auto_width_padding: float = Field(default=5)
    merge_equal_headers: bool = Field(default=True)

    def with_stripes(
        self,
        color: str = "#D0D0D0",
        pattern: Literal["even", "odd"] = "odd",
    ) -> "Table":
        return self.model_copy(
            update=dict(
                row_style={
                    idx: (
                        self.row_style.get(idx, Style()).merge(
                            Style(background_color=color)
                        )
                        if (pattern == "odd" and idx % 2 != 0)
                        or (pattern == "even" and idx % 2 == 0)
                        else self.row_style.get(idx, Style())
                    )
                    for idx in range(self.data.shape[0])
                }
            )
        )
