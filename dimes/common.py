from typing import Union
from dataclasses import dataclass

import koozie


@dataclass
class LineProperties:
    color: Union[str, None] = None
    line_type: Union[str, None] = None
    marker_symbol: Union[str, None] = None
    marker_size: Union[int, None] = None
    marker_line_color: Union[str, None] = None
    marker_fill_color: Union[str, None] = None
    is_visible: bool = True

    def get_line_mode(self):
        if all(
            variables is None
            for variables in (
                self.marker_size,
                self.marker_symbol,
                self.marker_line_color,
                self.marker_fill_color,
            )
        ):
            return "lines"
        else:
            return "lines+markers"


class DimensionalData:
    def __init__(
        self,
        data_values: list,
        name: Union[str, None] = None,
        native_units: str = "",
        display_units: Union[str, None] = None,
    ):
        self.data_values = data_values
        self.native_units = native_units
        self.dimensionality = koozie.get_dimensionality(self.native_units)
        self.name = (
            name
            if name is not None
            else str(self.dimensionality).title().replace("[", "").replace("]", "")
        )
        self.set_display_units(display_units)

    def set_display_units(self, units: Union[str, None] = None) -> None:
        """Set the display units for this axis"""
        if units is None:
            self.display_units = self.native_units
        else:
            self.display_units = units
            display_units_dimensionality = koozie.get_dimensionality(self.display_units)
            if self.dimensionality != display_units_dimensionality:
                raise Exception(
                    f"display_units, {self.display_units}, dimensionality ({display_units_dimensionality}) does not match native_units, {self.native_units}, dimensionality ({self.dimensionality})"
                )
