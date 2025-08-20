# Repository: https://gitlab.com/quantify-os/quantify
# Licensed according to the LICENSE file on the main branch
"""The module contains definitions for device elements."""

from __future__ import annotations

from typing import Any

from qcodes.instrument.base import Instrument

from quantify.helpers.importers import export_python_object_to_path_string
from quantify.json_utils import JSONSerializableMixin


class DeviceElement(JSONSerializableMixin, Instrument):
    """
    Create a device element for managing parameters.

    The :class:`~DeviceElement` is responsible for compiling operations applied to that
    specific device element from the quantum-circuit to the quantum-device
    layer.
    """

    def __init__(self, name: str, **kwargs) -> None:  # noqa: ANN003, D107
        if "-" in name or "_" in name:
            raise ValueError(
                f"Invalid DeviceElement name '{name}'. Hyphens and "
                f"underscores are not allowed due to naming conventions"
            )
        super().__init__(name, **kwargs)

    def __getstate__(self) -> dict:  # type: ignore
        """
        Serialize :class:`~DeviceElement` and derived classes.

        Serialization is performed by converting submodules into a dict containing
        the name of the device element and a dict for each submodule containing its
        parameter names and corresponding values.
        """
        snapshot = self.snapshot()

        element_data: dict[str, Any] = {"name": self.name}
        for submodule_name, submodule_data in snapshot["submodules"].items():
            element_data[submodule_name] = {
                name: data["value"]
                for name, data in submodule_data["parameters"].items()
            }

        state = {
            "deserialization_type": export_python_object_to_path_string(self.__class__),
            "mode": "__init__",
            "data": element_data,
        }
        return state
