import copy as libcopy
import io
import struct
import warnings
from collections.abc import Sequence
from typing import Any, Literal, Optional

import numpy

from .analytic_models import ModelResult
from .cache import cache_s_matrix
from .extension import (
    Component,
    Model,
    SMatrix,
    _as_bytes,
    _from_bytes,
    frequency_classification,
    pole_residue_fit,
    register_model_class,
)
from .time_stepper_model import SMatrixTimeStepperModel

InterpolationMethod = Literal[
    "linear", "barycentric", "cubicspline", "pchip", "akima", "makima", "poleresidue"
]
InterpolationCoords = Literal["real_imag", "mag_phase"]
SMatrixElements = dict[tuple[str, str], numpy.ndarray]


def _s_matrix_elements(
    s_array: numpy.ndarray, keys: Optional[dict[tuple[str, str], int]]
) -> SMatrixElements:
    if keys is None:
        return s_array
    return {key: s_array[:, index] for key, index in keys.items()}


class DataModel(SMatrixTimeStepperModel, Model):
    r"""Model based on existing S matrix data.

    Args:
        s_matrix: Model data as an :class:`SMatrix` instance.
        s_array: Complex array with dimensions ``(F, N, N)``, in which
          ``N`` is the number of ports.
        frequencies: Frequency array with length ``F``.
        ports: List of port names. If not set, the *sorted* list of port
          components is used.
        interpolation_method: Interpolation method used for sampling
          frequencies. See table below for options.
        interpolation_coords: Coordinate system used for interpolation. One
          of ``"mag_phase"`` or ``"real_imag"``. Not used for
          ``"poleresidue"`` interpolation.
        poleresidue_kwargs: Keyword arguments to :func:`pole_residue_fit`
          used when using ``"poleresidue"`` interpolation.

    When ``s_matrix`` is provided, ``s_array``, ``frequencies``, and
    ``ports`` should be ``None``, otherwise only ``ports`` is optional.

    ====================  ================================================
    Interpolation method  Description
    ====================  ================================================
    ``"linear"``          Linear interpolation between neighboring points
    ``"poleresidue"``     Pole-residue fitting
    ``"barycentric"``     Barycentric Lagrange interpolation
    ``"cubicspline"``     Cubic spline interpolation
    ``"pchip"``           Piecewise cubic Hermite interpolating polynomial
    ``"akima"``           Akima interpolation
    ``"makima"``          Modified Akima interpolation
    ====================  ================================================

    Important:
        Use of any interpolation method other than ``"linear"`` or
        ``"poleresidue"`` requires scipy >= 1.7, and ``"makima"`` requires
        scipy >= 1.13.

    Note:
        The conversion from array to dictionary for ``s_data`` is
        equivalent to ``s_dict[(ports[i], ports[j])] = s_array[:, j, i]``.

    See also:
        `Data Model guide <../guides/Data_Model.ipynb>`__
    """

    def __init__(
        self,
        s_matrix: Optional[SMatrix] = None,
        s_array: Optional[numpy.ndarray] = None,
        frequencies: Optional[numpy.ndarray] = None,
        ports: Optional[Sequence[str]] = None,
        interpolation_method: InterpolationMethod = "linear",
        interpolation_coords: InterpolationCoords = "mag_phase",
        poleresidue_kwargs: dict[str, Any] = {},
    ):
        if interpolation_method not in InterpolationMethod.__args__:
            raise TypeError(
                "'interpolation_method' must be one of '"
                + "', '".join(InterpolationMethod.__args__)
                + "'."
            )
        if interpolation_coords not in InterpolationCoords.__args__:
            raise TypeError(
                "'interpolation_coords' must be one of '"
                + "', '".join(InterpolationCoords.__args__)
                + "'."
            )
        super().__init__(
            s_matrix=s_matrix,
            s_array=s_array,
            frequencies=frequencies,
            ports=ports,
            interpolation_method=interpolation_method,
            interpolation_coords=interpolation_coords,
            poleresidue_kwargs=poleresidue_kwargs,
        )

        self.interpolation_method = interpolation_method
        self.interpolation_coords = interpolation_coords
        self.poleresidue_kwargs = poleresidue_kwargs
        self._poleresidue_matrix = None

        if s_matrix is None and (s_array is None or frequencies is None):
            raise RuntimeError(
                "Please provide either 's_matrix' or both 's_array' and 'frequencies'."
            )

        if s_matrix is not None:
            if ports is not None:
                warnings.warn(
                    "Argument 'ports' is ignored when 's_matrix' is provided. Using names from "
                    "'s_matrix.ports' instead.",
                    stacklevel=2,
                )
            if s_array is not None:
                warnings.warn(
                    "Argument 's_array' is ignored when 's_matrix' is provided.", stacklevel=2
                )
            if frequencies is not None:
                warnings.warn(
                    "Argument 'frequencies' is ignored when 's_matrix' is provided.", stacklevel=2
                )
            self.frequencies = s_matrix.frequencies
            self.ports = sorted(s_matrix.ports)
            elements = s_matrix.elements
            sorted_keys = sorted(elements.keys())
            self.keys = {k: i for i, k in enumerate(sorted_keys)}
            self.s_array = numpy.array([elements[k] for k in sorted_keys], dtype=complex).T
        else:
            self.frequencies = numpy.array(frequencies, dtype=float, ndmin=1)
            self.ports = ports
            self.keys = None
            self.s_array = numpy.array(s_array, dtype=complex)
            shape = self.s_array.shape
            if len(shape) != 3 or shape[1] != shape[2] or shape[0] != self.frequencies.size:
                raise RuntimeError(
                    "S matrix must be of shape (F, N, N), with F being the length of frequencies."
                )
            if ports is not None and len(ports) != self.s_array.shape[2]:
                raise RuntimeError(
                    "The number of port names must match the S matrix dimension "
                    f"({self.s_array.shape[2]})."
                )

        if (numpy.diff(self.frequencies) < 0).any():
            sort_indices = numpy.argsort(self.frequencies)
            self.frequencies = self.frequencies[sort_indices]
            self.s_array = self.s_array[sort_indices]

    def __copy__(self) -> "DataModel":
        if self.keys:
            elements = _s_matrix_elements(self.s_array, self.keys)
            s_matrix = SMatrix(self.frequencies, elements, dict.fromkeys(self.ports))
            return DataModel(
                s_matrix=s_matrix,
                interpolation_method=self.interpolation_method,
                interpolation_coords=self.interpolation_coords,
            )
        copy = DataModel(
            frequencies=self.frequencies,
            s_array=self.s_array,
            ports=self.ports,
            interpolation_method=self.interpolation_method,
            interpolation_coords=self.interpolation_coords,
            poleresidue_kwargs=self.poleresidue_kwargs,
        )
        copy.parametric_function = self.parametric_function
        copy.parametric_kwargs = self.paramteric_kwargs
        return copy

    def __deepcopy__(self, memo: Optional[dict] = None) -> "DataModel":
        if self.keys is not None:
            elements = _s_matrix_elements(self.s_array, self.keys)
            s_matrix = SMatrix(self.frequencies, elements, dict.fromkeys(self.ports))
            return DataModel(
                s_matrix=s_matrix,
                interpolation_method=self.interpolation_method,
                interpolation_coords=self.interpolation_coords,
                poleresidue_kwargs=libcopy.deepcopy(self.poleresidue_kwargs),
            )
        copy = DataModel(
            frequencies=numpy.copy(self.frequencies),
            s_array=numpy.copy(self.s_array),
            ports=libcopy.deepcopy(self.ports),
            interpolation_method=self.interpolation_method,
            interpolation_coords=self.interpolation_coords,
            poleresidue_kwargs=libcopy.deepcopy(self.poleresidue_kwargs),
        )
        copy.parametric_function = self.parametric_function
        copy.parametric_kwargs = libcopy.deepcopy(self.paramteric_kwargs)
        return copy

    def __str__(self) -> str:
        return "DataModel"

    def __repr__(self) -> str:
        if self.keys is not None:
            elements = _s_matrix_elements(self.s_array, self.keys)
            s_matrix = SMatrix(self.frequencies, elements, dict.fromkeys(self.ports))
            return (
                f"DataModel(s_matrix={s_matrix!r}, "
                f"interpolation_method={self.interpolation_method!r}, "
                f"interpolation_coords={self.interpolation_coords!r}, "
                f"poleresidue_kwargs={self.poleresidue_kwargs!r})"
            )
        return (
            f"DataModel(frequencies={self.frequencies!r}, "
            f"s_array={self.s_array!r}, ports={self.ports!r}, "
            f"interpolation_method={self.interpolation_method!r}, "
            f"interpolation_coords={self.interpolation_coords!r}, "
            f"poleresidue_kwargs={self.poleresidue_kwargs!r})"
        )

    @cache_s_matrix
    def start(
        self, component: Component, frequencies: Sequence[float], **kwargs: Any
    ) -> ModelResult:
        """Start computing the S matrix response from a component.

        Args:
            component: Component from which to compute the S matrix.
            frequencies: Sequence of frequencies at which to perform the
              computation.
            **kwargs: Unused.

        Returns:
           Model result with attributes ``status`` and ``s_matrix``.
        """
        classification = frequency_classification(frequencies)
        component_ports = {
            name: port.copy(True) for name, port in component.select_ports(classification).items()
        }
        if self.ports is None:
            names = sorted(component_ports)
        else:
            names = self.ports
            if not all(name in component_ports for name in names):
                raise RuntimeError(
                    f"Not all port names defined in DataModel match the {classification} port "
                    f"names in component '{component.name}'."
                )

        if self.keys is None:
            ports = tuple(
                f"{name}@{mode}"
                for name in names
                for mode in range(component_ports[name].num_modes)
            )
            if len(ports) != self.s_array.shape[2]:
                raise RuntimeError(
                    f"DataModel S matrix has dimension {self.s_array.shape[2]}, but component "
                    f"'{component.name}' has {len(ports)} ports/modes."
                )
            elements = {
                (port_in, port_out): numpy.copy(self.s_array[:, j, i])
                for i, port_in in enumerate(ports)
                for j, port_out in enumerate(ports)
            }
        else:
            elements = {}
            for port_in in names:
                for port_out in names:
                    for mode_in in range(component_ports[port_in].num_modes):
                        for mode_out in range(component_ports[port_out].num_modes):
                            key = (f"{port_in}@{mode_in}", f"{port_out}@{mode_out}")
                            index = self.keys.get(key)
                            if index is not None:
                                elements[key] = numpy.copy(self.s_array[:, index])

        frequencies = numpy.array(frequencies, dtype=float, ndmin=1)

        if len(elements) == 0:
            return ModelResult(SMatrix(frequencies, elements, component_ports))

        if self.interpolation_method == "poleresidue":
            if (
                self._poleresidue_matrix is None
                or self._poleresidue_matrix.ports != component_ports
            ):
                s_matrix = SMatrix(self.frequencies, elements, component_ports)
                self._poleresidue_matrix, _ = pole_residue_fit(s_matrix, **self.poleresidue_kwargs)
            return ModelResult(self._poleresidue_matrix(frequencies))

        if frequencies.size == self.frequencies.size:
            if numpy.allclose(self.frequencies, frequencies):
                return ModelResult(SMatrix(frequencies, elements, component_ports))

            if numpy.allclose(self.frequencies, frequencies[::-1]):
                elements = {k: v[::-1] for k, v in elements.items()}
                return ModelResult(SMatrix(frequencies, elements, component_ports))

        if self.interpolation_method == "barycentric":
            from scipy.interpolate import BarycentricInterpolator  # noqa: PLC0415

            interpolator = BarycentricInterpolator(self.frequencies)

        for k in elements:
            s = elements[k]
            if self.interpolation_coords == "real_imag":
                y = numpy.vstack((s.real, s.imag))
            elif self.interpolation_coords == "mag_phase":
                y = numpy.vstack((numpy.abs(s), numpy.unwrap(numpy.angle(s))))

            if self.interpolation_method == "linear":
                y = [
                    numpy.interp(frequencies, self.frequencies, y[0]),
                    numpy.interp(frequencies, self.frequencies, y[1]),
                ]
            elif self.interpolation_method == "barycentric":
                interpolator.set_yi(y, axis=1)
                y = interpolator(frequencies)
            elif self.interpolation_method == "cubicspline":
                from scipy.interpolate import CubicSpline  # noqa: PLC0415

                y = CubicSpline(self.frequencies, y, axis=1)(frequencies)
            elif self.interpolation_method == "pchip":
                from scipy.interpolate import PchipInterpolator  # noqa: PLC0415

                y = PchipInterpolator(self.frequencies, y, axis=1)(frequencies)
            elif self.interpolation_method == "akima":
                from scipy.interpolate import Akima1DInterpolator  # noqa: PLC0415

                y = Akima1DInterpolator(self.frequencies, y, axis=1)(frequencies)
            elif self.interpolation_method == "makima":
                from scipy.interpolate import Akima1DInterpolator  # noqa: PLC0415

                y = Akima1DInterpolator(self.frequencies, y, axis=1, method="makima")(frequencies)

            if self.interpolation_coords == "real_imag":
                elements[k] = y[0] + 1j * y[1]
            elif self.interpolation_coords == "mag_phase":
                elements[k] = y[0] * numpy.exp(1j * y[1])

        return ModelResult(SMatrix(frequencies, elements, component_ports))

    @property
    def as_bytes(self) -> bytes:
        """Serialize this model."""
        obj = [
            ("frequencies", self.frequencies),
            ("s_array", self.s_array),
            ("keys", self.keys),
            ("ports", self.ports),
            ("interpolation_method", self.interpolation_method),
            ("interpolation_coords", self.interpolation_coords),
            ("poleresidue_kwargs", self.poleresidue_kwargs),
        ]
        return b"\x01" + _as_bytes(obj)

    @classmethod
    def from_bytes(cls, byte_repr: bytes) -> "DataModel":
        """De-serialize this model."""
        version = byte_repr[0]
        if version == 1:
            obj = dict(_from_bytes(byte_repr[1:]))
            keys = obj.pop("keys")
            if keys is not None:
                elements = _s_matrix_elements(numpy.array(obj.pop("s_array")), keys)
                ports = dict.fromkeys(obj.pop("ports"))
                s_matrix = SMatrix(obj.pop("frequencies"), elements, ports)
                obj["s_matrix"] = s_matrix

        elif version == 0:
            head_size = 1 + struct.calcsize("<2Q")
            keys_len, ports_len = struct.unpack("<2Q", byte_repr[1:head_size])
            num_parts = 2 * keys_len + ports_len + 4
            lengths_size = struct.calcsize(f"<{num_parts}Q")
            lengths = struct.unpack(
                f"<{num_parts}Q", byte_repr[head_size : head_size + lengths_size]
            )
            cursor = head_size + lengths_size

            if cursor + sum(lengths) != len(byte_repr):
                raise RuntimeError("Invalid byte representation for DataModel.")

            keys = None if keys_len == 0 else {}
            ports = None if ports_len == 0 else []

            for _ in range(keys_len):
                p0 = byte_repr[cursor : cursor + lengths[0]].decode("utf-8")
                cursor += lengths[0]
                p1 = byte_repr[cursor : cursor + lengths[1]].decode("utf-8")
                cursor += lengths[1]
                keys[(p0, p1)] = len(keys)
                lengths = lengths[2:]

            for _ in range(ports_len):
                ports.append(byte_repr[cursor : cursor + lengths[0]].decode("utf-8"))
                cursor += lengths[0]
                lengths = lengths[1:]

            mem_io = io.BytesIO()
            mem_io.write(byte_repr[cursor : cursor + lengths[0]])
            mem_io.seek(0)
            frequencies = numpy.load(mem_io)
            cursor += lengths[0]

            mem_io = io.BytesIO()
            mem_io.write(byte_repr[cursor : cursor + lengths[1]])
            mem_io.seek(0)
            s_array = numpy.load(mem_io)
            cursor += lengths[1]

            interpolation_method = byte_repr[cursor : cursor + lengths[2]].decode("utf-8")
            cursor += lengths[2]

            interpolation_coords = byte_repr[cursor : cursor + lengths[3]].decode("utf-8")
            cursor += lengths[3]

            if keys is not None:
                elements = _s_matrix_elements(s_array, keys)
                s_matrix = SMatrix(frequencies, elements, dict.fromkeys(ports))
                obj = {
                    "s_matrix": s_matrix,
                    "interpolation_method": interpolation_method,
                    "interpolation_coords": interpolation_coords,
                }
            else:
                obj = {
                    "frequencies": frequencies,
                    "s_array": s_array,
                    "ports": ports,
                    "interpolation_method": interpolation_method,
                    "interpolation_coords": interpolation_coords,
                }

        else:
            raise RuntimeError("Unsuported DataModel version.")

        return cls(**obj)


register_model_class(DataModel)
