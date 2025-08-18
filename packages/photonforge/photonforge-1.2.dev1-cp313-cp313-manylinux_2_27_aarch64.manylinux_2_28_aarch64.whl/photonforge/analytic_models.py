import copy as libcopy
import io
import json
import struct
import time
import zlib
from collections.abc import Sequence
from typing import Any, Literal, Optional, Union

import numpy

from .cache import cache_s_matrix
from .extension import (
    Component,
    Model,
    Port,
    PortSpec,
    Reference,
    SMatrix,
    _as_bytes,
    _from_bytes,
    config,
    frequency_classification,
    register_model_class,
)
from .tidy3d_model import _ModeSolverRunner
from .utils import C_0
from .time_stepper_model import SMatrixTimeStepperModel

_ComplexArray = Union[complex, numpy.ndarray]


def _ensure_correct_shape(x: Any) -> numpy.ndarray:
    y = numpy.array(x)
    if y.ndim <= 1:
        y = y.reshape((-1, 1))
    return y


class ModelResult:
    """Convenience class to return S matrix results immediately.

    If a model performs S matrix calculations in a single step, it can
    use this class to return the required object with the results.

    Args:
        s_matrix: S matrix dictionary to be returned as a result.
        status: Dictionary with ``'progress'`` and ``'message'``.
    """

    def __init__(self, s_matrix: SMatrix, status: Optional[dict[str, Any]] = None) -> None:
        self.status = {"progress": 100, "message": "success"} if status is None else status
        self.s_matrix = s_matrix


class TerminationModel(SMatrixTimeStepperModel, Model):
    r"""Analytic model for a 1-port device.

    Args:
        r: Reflection coefficient for the first port. For multimode ports, a
          sequence of coefficients must be provided.

    Notes:
        For multimode ports, mixed-mode coefficients are zero (not included
        in the result). Dispersion can be included in the model by setting
        the coefficients to a 2D array with shape (M, N), in which M is the
        number of modes, and N the length of the frequency sequence used in
        the S matrix computation.
    """

    def __init__(self, r: _ComplexArray = 0, **kwargs) -> None:
        super().__init__(r=r, **kwargs)
        self.coeff = _ensure_correct_shape(r)

    def __copy__(self) -> "TerminationModel":
        copy = TerminationModel()
        copy.parametric_function = self.parametric_function
        copy.parametric_kwargs = self.parametric_kwargs
        copy.coeff = self.coeff
        return copy

    def __deepcopy__(self, memo: Optional[dict] = None) -> "TerminationModel":
        copy = TerminationModel()
        copy.parametric_function = self.parametric_function
        copy.parametric_kwargs = libcopy.deepcopy(self.parametric_kwargs)
        copy.coeff = numpy.copy(self.coeff)
        return copy

    def __str__(self) -> str:
        return "TerminationModel"

    def __repr__(self) -> str:
        return f"TerminationModel(r={self.coeff!r})"

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
        if len(component_ports) != 1:
            raise RuntimeError(
                f"TerminationModel can only be used on components with 1 port. "
                f"'{component.name}' has {len(component_ports)} {classification} ports."
            )

        name, port = next(iter(component_ports.items()))

        shape = (self.coeff.shape[0], len(frequencies))
        r = numpy.array(numpy.broadcast_to(self.coeff, shape))

        if r.shape[0] < port.num_modes:
            raise RuntimeError(
                f"The first dimension of 'r' in the model for '{component.name}' must be "
                f"{port.num_modes} to account for all modes in the component's ports."
            )

        elements = {(f"{name}@{mode}", f"{name}@{mode}"): r[mode] for mode in range(port.num_modes)}
        return ModelResult(SMatrix(frequencies, elements, {name: port}))

    @property
    def as_bytes(self) -> bytes:
        """Serialize this model."""
        version = 0
        mem_io = io.BytesIO()
        numpy.save(mem_io, self.coeff, allow_pickle=False)
        coeff_bytes = mem_io.getvalue()
        return struct.pack("<BQ", version, len(coeff_bytes)) + coeff_bytes

    @classmethod
    def from_bytes(cls, byte_repr: bytes) -> "TerminationModel":
        """De-serialize this model."""
        size = struct.calcsize("<BQ")
        version, length = struct.unpack("<BQ", byte_repr[:size])
        if version != 0:
            raise RuntimeError("Unsuported TerminationModel version.")
        if len(byte_repr) != size + length:
            raise ValueError("Unexpected byte representation for TerminationModel")
        mem_io = io.BytesIO()
        mem_io.write(byte_repr[size:])
        mem_io.seek(0)
        coeff = numpy.load(mem_io)
        return cls(coeff)


class TwoPortModel(SMatrixTimeStepperModel, Model):
    r"""Analytic model for a 2-port component.

    .. math:: S = \begin{bmatrix}
                     r_0  &   t  \\
                      t   &  r_1 \\
                  \end{bmatrix}

    Args:
        t: Transmission coefficient. For multimode ports, a sequence of
          coefficients must be provided.
        r0: Reflection coefficient for the first port. For multimode ports,
          a sequence of coefficients must be provided.
        r1: Reflection coefficient for the second port. For multimode ports,
          a sequence of coefficients must be provided.
        ports: List of port names. If not set, the *sorted* list of port
          names from the component is used.

    Notes:
        For multimode ports, mixed-mode coefficients are zero (not included
        in the result). Dispersion can be included in the model by setting
        the coefficients to a 2D array with shape (M, N), in which M is the
        number of modes, and N the length of the frequency sequence used in
        the S matrix computation.
    """

    def __init__(
        self,
        t: _ComplexArray = 1,
        r0: _ComplexArray = 0,
        r1: _ComplexArray = 0,
        ports: Optional[Sequence[str]] = None,
        **kwargs,
    ) -> None:
        super().__init__(t=t, r0=r0, r1=r1, ports=ports, **kwargs)
        self.coeffs = (
            _ensure_correct_shape(t),
            _ensure_correct_shape(r0),
            _ensure_correct_shape(r1),
        )
        self.ports = ports
        if ports is not None and len(ports) != 2:
            raise TypeError(
                f"TwoPortModel can only be used on components with 2 ports. "
                f"Argument 'ports' has length {len(ports)}."
            )

    def __copy__(self) -> "TwoPortModel":
        copy = TwoPortModel()
        copy.parametric_function = self.parametric_function
        copy.parametric_kwargs = self.parametric_kwargs
        copy.coeffs = self.coeffs
        copy.ports = self.ports
        return copy

    def __deepcopy__(self, memo: Optional[dict] = None) -> "TwoPortModel":
        copy = TwoPortModel()
        copy.parametric_function = self.parametric_function
        copy.parametric_kwargs = libcopy.deepcopy(self.parametric_kwargs)
        copy.coeffs = tuple(numpy.copy(c) for c in self.coeffs)
        copy.ports = libcopy.deepcopy(self.ports)
        return copy

    def __str__(self) -> str:
        return "TwoPortModel"

    def __repr__(self) -> str:
        return (
            f"TwoPortModel(t={self.coeffs[0]!r}, r0={self.coeffs[1]!r}, "
            f"r1={self.coeffs[2]!r}, ports={self.ports!r})"
        )

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
        if len(component_ports) != 2:
            raise RuntimeError(
                f"TwoPortModel can only be used on components with 2 ports. "
                f"'{component.name}' has {len(component_ports)} {classification} ports."
            )

        if self.ports is None:
            names = sorted(component_ports)
        else:
            names = self.ports
            if not all(name in component_ports for name in names):
                raise RuntimeError(
                    f"Not all port names defined in TwoPortModel match the {classification} port "
                    f"names in component '{component.name}'."
                )

        num_modes = component_ports[names[0]].num_modes
        if not all(port.num_modes == num_modes for port in component_ports.values()):
            raise RuntimeError(
                f"TwoPortModel requires that all component ports have the same number of "
                f"modes. Ports from '{component.name}' support different numbers of modes."
            )

        shape = (self.coeffs[0].shape[0], len(frequencies))
        t = numpy.array(numpy.broadcast_to(self.coeffs[0], shape))
        r0 = numpy.array(numpy.broadcast_to(self.coeffs[1], shape))
        r1 = numpy.array(numpy.broadcast_to(self.coeffs[2], shape))

        if t.shape[0] < num_modes:
            raise RuntimeError(
                f"The first dimension of 't' in the model for '{component.name}' must "
                f"be {num_modes} to account for all modes in the component's ports."
            )
        if r0.shape[0] < num_modes:
            raise RuntimeError(
                f"The first dimension of 'r0' in the model for '{component.name}' must "
                f"be {num_modes} to account for all modes in the component's ports."
            )
        if r1.shape[0] < num_modes:
            raise RuntimeError(
                f"The first dimension of 'r1' in the model for '{component.name}' must "
                f"be {num_modes} to account for all modes in the component's ports."
            )

        s = (
            (r0, t),
            (t, r1),
        )
        elements = {
            (f"{port_in}@{mode}", f"{port_out}@{mode}"): s[j][i][mode]
            for i, port_in in enumerate(names)
            for j, port_out in enumerate(names)
            for mode in range(component_ports[port_in].num_modes)
        }
        return ModelResult(SMatrix(frequencies, elements, component_ports))

    @property
    def as_bytes(self) -> bytes:
        """Serialize this model."""
        version = 0
        all_bytes = []
        for coeff in self.coeffs:
            mem_io = io.BytesIO()
            numpy.save(mem_io, coeff, allow_pickle=False)
            all_bytes.append(mem_io.getvalue())
        all_bytes.extend(
            [b"", b""] if self.ports is None else [p.encode("utf8") for p in self.ports]
        )
        return struct.pack("<B5Q", version, *[len(b) for b in all_bytes]) + b"".join(all_bytes)

    @classmethod
    def from_bytes(cls, byte_repr: bytes) -> "TwoPortModel":
        """De-serialize this model."""
        size = struct.calcsize("<B5Q")
        version, *lengths = struct.unpack("<B5Q", byte_repr[:size])
        if version != 0:
            raise RuntimeError("Unsuported TwoPortModel version.")
        coeffs = []
        for length in lengths[:3]:
            mem_io = io.BytesIO()
            mem_io.write(byte_repr[size : size + length])
            mem_io.seek(0)
            coeffs.append(numpy.load(mem_io))
            size += length
        if all(length == 0 for length in lengths[3:]):
            ports = None
        else:
            ports = []
            for length in lengths[3:]:
                ports.append(byte_repr[size : size + length].decode("utf8"))
                size += length
        return cls(*coeffs, ports)


class PowerSplitterModel(SMatrixTimeStepperModel, Model):
    r"""Analytic model for a 3-port power splitter.

    .. math:: S = \begin{bmatrix}
                     r_0  &   t   &   t   \\
                      t   &  r_1  &   i   \\
                      t   &   i   &  r_1  \\
                  \end{bmatrix}

    Args:
        t: Transmission coefficient. For multimode ports, a sequence of
          coefficients must be provided.
        i: Isolation coefficient. For multimode ports, a sequence of
          coefficients must be provided.
        r0: Reflection coefficient for the first port. For multimode ports,
          a sequence of coefficients must be provided.
        r1: Reflection coefficient for the remaining ports. For multimode
          ports, a sequence of coefficients must be provided.
        ports: List of port names. If not set, the *sorted* list of port
          names from the component is used.

    Notes:
        For multimode ports, mixed-mode coefficients are zero (not included
        in the result). Dispersion can be included in the model by setting
        the coefficients to a 2D array with shape (M, N), in which M is the
        number of modes, and N the length of the frequency sequence used in
        the S matrix computation.
    """

    def __init__(
        self,
        t: _ComplexArray = 2**-0.5,
        i: _ComplexArray = 0,
        r0: _ComplexArray = 0,
        r1: _ComplexArray = 0,
        ports: Optional[Sequence[str]] = None,
        **kwargs,
    ) -> None:
        super().__init__(t=t, i=i, r0=r0, r1=r1, ports=ports, **kwargs)
        self.coeffs = (
            _ensure_correct_shape(t),
            _ensure_correct_shape(i),
            _ensure_correct_shape(r0),
            _ensure_correct_shape(r1),
        )
        self.ports = ports
        if ports is not None and len(ports) != 3:
            raise TypeError(
                f"PowerSplitterModel can only be used on components with 3 ports. "
                f"Argument 'ports' has length {len(ports)}."
            )

    def __copy__(self) -> "PowerSplitterModel":
        copy = PowerSplitterModel()
        copy.parametric_function = self.parametric_function
        copy.parametric_kwargs = self.parametric_kwargs
        copy.coeffs = self.coeffs
        copy.ports = self.ports
        return copy

    def __deepcopy__(self, memo: Optional[dict] = None) -> "PowerSplitterModel":
        copy = PowerSplitterModel()
        copy.parametric_function = self.parametric_function
        copy.parametric_kwargs = libcopy.deepcopy(self.parametric_kwargs)
        copy.coeffs = tuple(numpy.copy(c) for c in self.coeffs)
        copy.ports = libcopy.deepcopy(self.ports)
        return copy

    def __str__(self) -> str:
        return "PowerSplitterModel"

    def __repr__(self) -> str:
        return (
            f"PowerSplitterModel(t={self.coeffs[0]!r}, i={self.coeffs[1]!r}, "
            f"r0={self.coeffs[2]!r}, r1={self.coeffs[3]!r}, ports={self.ports!r})"
        )

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
        if len(component_ports) != 3:
            raise RuntimeError(
                f"PowerSplitterModel can only be used on components with 3 ports. "
                f"'{component.name}' has {len(component_ports)} {classification} ports."
            )

        if self.ports is None:
            names = sorted(component_ports)
        else:
            names = self.ports
            if not all(name in component_ports for name in names):
                raise RuntimeError(
                    f"Not all port names defined in PowerSplitterModel match the {classification} "
                    f"port names in component '{component.name}'."
                )

        num_modes = component_ports[names[0]].num_modes
        if not all(port.num_modes == num_modes for port in component_ports.values()):
            raise RuntimeError(
                f"PowerSplitterModel requires that all component ports have the same number of "
                f"modes. Ports from '{component.name}' support different numbers of modes."
            )

        shape = (self.coeffs[0].shape[0], len(frequencies))
        t = numpy.array(numpy.broadcast_to(self.coeffs[0], shape))
        i = numpy.array(numpy.broadcast_to(self.coeffs[1], shape))
        r0 = numpy.array(numpy.broadcast_to(self.coeffs[2], shape))
        r1 = numpy.array(numpy.broadcast_to(self.coeffs[3], shape))

        if t.shape[0] < num_modes:
            raise RuntimeError(
                f"The first dimension of 't' in the model for '{component.name}' must "
                f"be {num_modes} to account for all modes in the component's ports."
            )
        if i.shape[0] < num_modes:
            raise RuntimeError(
                f"The first dimension of 'i' in the model for '{component.name}' must "
                f"be {num_modes} to account for all modes in the component's ports."
            )
        if r0.shape[0] < num_modes:
            raise RuntimeError(
                f"The first dimension of 'r0' in the model for '{component.name}' must "
                f"be {num_modes} to account for all modes in the component's ports."
            )
        if r1.shape[0] < num_modes:
            raise RuntimeError(
                f"The first dimension of 'r1' in the model for '{component.name}' must "
                f"be {num_modes} to account for all modes in the component's ports."
            )

        s = (
            (r0, t, t),
            (t, r1, i),
            (t, i, r1),
        )
        elements = {
            (f"{port_in}@{mode}", f"{port_out}@{mode}"): s[j][i][mode]
            for i, port_in in enumerate(names)
            for j, port_out in enumerate(names)
            for mode in range(component_ports[port_in].num_modes)
        }
        return ModelResult(SMatrix(frequencies, elements, component_ports))

    @property
    def as_bytes(self) -> bytes:
        """Serialize this model."""
        version = 0
        all_bytes = []
        for coeff in self.coeffs:
            mem_io = io.BytesIO()
            numpy.save(mem_io, coeff, allow_pickle=False)
            all_bytes.append(mem_io.getvalue())
        all_bytes.extend(
            [b"", b"", b""] if self.ports is None else [p.encode("utf8") for p in self.ports]
        )
        return struct.pack("<B7Q", version, *[len(b) for b in all_bytes]) + b"".join(all_bytes)

    @classmethod
    def from_bytes(cls, byte_repr: bytes) -> "PowerSplitterModel":
        """De-serialize this model."""
        size = struct.calcsize("<B7Q")
        version, *lengths = struct.unpack("<B7Q", byte_repr[:size])
        if version != 0:
            raise RuntimeError("Unsuported PowerSplitterModel version.")
        coeffs = []
        for length in lengths[:4]:
            mem_io = io.BytesIO()
            mem_io.write(byte_repr[size : size + length])
            mem_io.seek(0)
            coeffs.append(numpy.load(mem_io))
            size += length
        if all(length == 0 for length in lengths[4:]):
            ports = None
        else:
            ports = []
            for length in lengths[4:]:
                ports.append(byte_repr[size : size + length].decode("utf8"))
                size += length
        return cls(*coeffs, ports)


class DirectionalCouplerModel(SMatrixTimeStepperModel, Model):
    r"""Analytic model for a 4-port directional coupler

    .. math:: S = \begin{bmatrix}
                     r  &  i  &  t  &  c  \\
                     i  &  r  &  c  &  t  \\
                     t  &  c  &  r  &  i  \\
                     c  &  t  &  i  &  r  \\
                  \end{bmatrix}

    Args:
        t: Transmission coefficient. For multimode ports, a sequence of
          coefficients must be provided.
        c: Coupling coefficient. For multimode ports, a sequence of
          coefficients must be provided.
        i: Isolation coefficient. For multimode ports, a sequence of
          coefficients must be provided.
        r: Reflection coefficient. For multimode ports, a sequence of
          coefficients must be provided.
        ports: List of port names. If not set, the *sorted* list of port
          names from the component is used.

    Notes:
        For multimode ports, mixed-mode coefficients are zero (not included
        in the result). Dispersion can be included in the model by setting
        the coefficients to a 2D array with shape (M, N), in which M is the
        number of modes, and N the length of the frequency sequence used in
        the S matrix computation.
    """

    def __init__(
        self,
        t: _ComplexArray = 2**-0.5,
        c: _ComplexArray = -1j * 2**-0.5,
        i: _ComplexArray = 0,
        r: _ComplexArray = 0,
        ports: Optional[Sequence[str]] = None,
        **kwargs,
    ) -> None:
        super().__init__(t=t, c=c, i=i, r=r, ports=ports, **kwargs)
        self.coeffs = (
            _ensure_correct_shape(t),
            _ensure_correct_shape(c),
            _ensure_correct_shape(i),
            _ensure_correct_shape(r),
        )
        self.ports = ports
        if ports is not None and len(ports) != 4:
            raise TypeError(
                f"DirectionalCouplerModel can only be used on components with 4 ports. "
                f"Argument 'ports' has length {len(ports)}."
            )

    def __copy__(self) -> "DirectionalCouplerModel":
        copy = DirectionalCouplerModel()
        copy.parametric_function = self.parametric_function
        copy.parametric_kwargs = self.parametric_kwargs
        copy.coeffs = self.coeffs
        copy.ports = self.ports
        return copy

    def __deepcopy__(self, memo: Optional[dict] = None) -> "DirectionalCouplerModel":
        copy = DirectionalCouplerModel()
        copy.parametric_function = self.parametric_function
        copy.parametric_kwargs = libcopy.deepcopy(self.parametric_kwargs)
        copy.coeffs = tuple(numpy.copy(c) for c in self.coeffs)
        copy.ports = libcopy.deepcopy(self.ports)
        return copy

    def __str__(self) -> str:
        return "DirectionalCouplerModel"

    def __repr__(self) -> str:
        return (
            f"DirectionalCouplerModel(t={self.coeffs[0]!r}, c={self.coeffs[1]!r}, "
            f"i={self.coeffs[2]!r}, r={self.coeffs[3]!r}, ports={self.ports!r})"
        )

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
        if len(component_ports) != 4:
            raise RuntimeError(
                f"DirectionalCouplerModel can only be used on components with 4 ports. "
                f"'{component.name}' has {len(component_ports)} {classification} ports."
            )

        if self.ports is None:
            names = sorted(component_ports)
        else:
            names = self.ports
            if not all(name in component_ports for name in names):
                raise RuntimeError(
                    f"Not all port names defined in DirectionalCouplerModel match the "
                    f"{classification} port names in component '{component.name}'."
                )

        num_modes = component_ports[names[0]].num_modes
        if not all(port.num_modes == num_modes for port in component_ports.values()):
            raise RuntimeError(
                f"DirectionalCouplerModel requires that all component ports have the same number "
                f"of modes. Ports from '{component.name}' support different numbers of modes."
            )

        shape = (self.coeffs[0].shape[0], len(frequencies))
        t = numpy.array(numpy.broadcast_to(self.coeffs[0], shape))
        c = numpy.array(numpy.broadcast_to(self.coeffs[1], shape))
        i = numpy.array(numpy.broadcast_to(self.coeffs[2], shape))
        r = numpy.array(numpy.broadcast_to(self.coeffs[3], shape))

        if t.shape[0] < num_modes:
            raise RuntimeError(
                f"The first dimension of 't' in the model for '{component.name}' must "
                f"be {num_modes} to account for all modes in the component's ports."
            )
        if c.shape[0] < num_modes:
            raise RuntimeError(
                f"The first dimension of 'c' in the model for '{component.name}' must "
                f"be {num_modes} to account for all modes in the component's ports."
            )
        if i.shape[0] < num_modes:
            raise RuntimeError(
                f"The first dimension of 'i' in the model for '{component.name}' must "
                f"be {num_modes} to account for all modes in the component's ports."
            )
        if r.shape[0] < num_modes:
            raise RuntimeError(
                f"The first dimension of 'r' in the model for '{component.name}' must "
                f"be {num_modes} to account for all modes in the component's ports."
            )

        s = (
            (r, i, t, c),
            (i, r, c, t),
            (t, c, r, i),
            (c, t, i, r),
        )
        elements = {
            (f"{port_in}@{mode}", f"{port_out}@{mode}"): s[j][i][mode]
            for i, port_in in enumerate(names)
            for j, port_out in enumerate(names)
            for mode in range(component_ports[port_in].num_modes)
        }
        return ModelResult(SMatrix(frequencies, elements, component_ports))

    @property
    def as_bytes(self) -> bytes:
        """Serialize this model."""
        version = 0
        all_bytes = []
        for coeff in self.coeffs:
            mem_io = io.BytesIO()
            numpy.save(mem_io, coeff, allow_pickle=False)
            all_bytes.append(mem_io.getvalue())
        all_bytes.extend(
            [b"", b"", b"", b""] if self.ports is None else [p.encode("utf8") for p in self.ports]
        )
        return struct.pack("<B8Q", version, *[len(b) for b in all_bytes]) + b"".join(all_bytes)

    @classmethod
    def from_bytes(cls, byte_repr: bytes) -> "DirectionalCouplerModel":
        """De-serialize this model."""
        size = struct.calcsize("<B8Q")
        version, *lengths = struct.unpack("<B8Q", byte_repr[:size])
        if version != 0:
            raise RuntimeError("Unsuported DirectionalCouplerModel version.")
        coeffs = []
        for length in lengths[:4]:
            mem_io = io.BytesIO()
            mem_io.write(byte_repr[size : size + length])
            mem_io.seek(0)
            coeffs.append(numpy.load(mem_io))
            size += length
        if all(length == 0 for length in lengths[4:]):
            ports = None
        else:
            ports = []
            for length in lengths[4:]:
                ports.append(byte_repr[size : size + length].decode("utf8"))
                size += length
        return cls(*coeffs, ports)


class _WaveguideModelRunner:
    def __init__(self, runner, free_space_phase, frequencies, ports) -> None:
        self.runner = runner
        self.free_space_phase = free_space_phase
        self.frequencies = frequencies
        self.ports = ports
        self._s_matrix = None

    @property
    def status(self):
        return self.runner.status

    @property
    def s_matrix(self):
        if self._s_matrix is None:
            data = self.runner.data
            num_modes = next(iter(self.ports.values())).num_modes
            n_complex = data.n_complex.values.T
            s = numpy.exp(1j * self.free_space_phase * n_complex)

            elements = {
                (f"{port_in}@{mode}", f"{port_out}@{mode}"): s[mode]
                for port_in in self.ports
                for port_out in self.ports
                for mode in range(num_modes)
                if port_in != port_out
            }

            self._s_matrix = SMatrix(self.frequencies, elements, self.ports)

        return self._s_matrix


class WaveguideModel(SMatrixTimeStepperModel, Model):
    r"""Analytic model for straight waveguides.

    The component is expected to have 2 ports with identical profiles. The S
    matrix is zero for all reflection or mixed-mode coefficients. Same-mode
    transmission coefficients are modeled by:

    .. math:: S_{jk} = \exp(i 2 \pi f n_c L / c₀)

    with :math:`n_c` the complex effective index for the port profile modes,
    and :math:`L` the waveguide length.

    Args:
        n_complex: Waveguide complex effective index. For multimode models,
          a sequence of indices must be provided, one for each mode. If set
          to ``None``, automatic computation is performed by mode-solving
          the first component port. If desired, the port specification of
          the component port can be overridden by setting ``n_complex`` to
          ``"cross-section"`` (uses :func:`Component.slice_profile`) or to
          a :class:`PortSpec` object.
        length: Physical length of the waveguide. If not provided, the
          distance between ports is be used (assuming a straight waveguide).
        mesh_refinement: Minimal number of mesh elements per wavelength used
          for mode solving.
        verbose: Flag setting the verbosity of mode solver runs.

    Note:
        Dispersion can be included in the model by setting ``n_complex`` to
        a 2D array with shape (M, N), in which M is the number of modes in
        the waveguide, and N the length of the frequency sequence used in
        the S matrix computation.

    See also:
        `Mach-Zehnder Interferometer
        <../examples/MZI.ipynb#Semi-Analytical-Design-Exploration>`__
    """

    def __init__(
        self,
        n_complex: Optional[Union[_ComplexArray, PortSpec, Literal["cross-section"]]] = None,
        length: Optional[float] = None,
        mesh_refinement: Optional[float] = None,
        verbose: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(
            n_complex=n_complex,
            length=length,
            mesh_refinement=mesh_refinement,
            verbose=verbose,
            **kwargs,
        )
        self.n_complex = (
            _ensure_correct_shape(numpy.array(n_complex))
            if self._classify_n_complex(n_complex) is numpy.ndarray
            else n_complex
        )
        self.length = length
        self.mesh_refinement = mesh_refinement
        self.verbose = verbose

    @classmethod
    def _classify_n_complex(cls, n_complex):
        if n_complex is None:
            return None
        elif isinstance(n_complex, str):
            if n_complex == "cross-section":
                return str
            raise ValueError(
                "'n_complex' must be a scalar, array, PortSpec object, or the string "
                "'cross-section'. The string {n_complex!r} is not valid."
            )
        elif isinstance(n_complex, PortSpec):
            return PortSpec
        else:
            return numpy.ndarray

    def __copy__(self) -> "WaveguideModel":
        return WaveguideModel(self.n_complex, self.length, self.mesh_refinement, self.verbose)

    def __deepcopy__(self, memo: Optional[dict] = None) -> "WaveguideModel":
        return WaveguideModel(
            libcopy.deepcopy(self.n_complex),
            self.length,
            self.mesh_refinement,
            self.verbose,
        )

    def __str__(self) -> str:
        return "WaveguideModel"

    def __repr__(self) -> str:
        return (
            f"WaveguideModel(n_complex={self.n_complex!r}, length={self.length!r}, "
            f"mesh_refinement={self.mesh_refinement!r}, verbose={self.verbose!r})"
        )

    @cache_s_matrix
    def start(
        self,
        component: Component,
        frequencies: Sequence[float],
        verbose: Optional[bool] = None,
        cost_estimation: bool = False,
        **kwargs: Any,
    ) -> Union[ModelResult, _WaveguideModelRunner]:
        """Start computing the S matrix response from a component.

        Args:
            component: Component from which to compute the S matrix.
            frequencies: Sequence of frequencies at which to perform the
              computation.
            verbose: If set, overrides the model's `verbose` attribute.
            cost_estimation: If set, simulations are uploaded, but not
              executed. S matrix may *not* be computed.
            **kwargs: Unused.

        Returns:
           Result object with attributes ``status`` and ``s_matrix``.
        """
        classification = frequency_classification(frequencies)
        component_ports = {
            name: port.copy(True) for name, port in component.select_ports(classification).items()
        }
        if len(component_ports) != 2:
            raise RuntimeError(
                f"WaveguideModel can only be used on components with 2 ports. "
                f"'{component.name}' has {len(component_ports)} {classification} ports.",
            )

        port_names = sorted(component_ports)
        port0 = component_ports[port_names[0]]
        port1 = component_ports[port_names[1]]

        if not isinstance(port0, Port) or not isinstance(port1, Port):
            raise RuntimeError(
                "WaveguideModel can only be used on components with planar ports (Port instances)."
            )

        if not port0.can_connect_to(port1):
            raise RuntimeError(
                "WaveguideModel can only be used on components with 2 ports with matching path "
                "profiles."
            )

        length = (
            numpy.sqrt(numpy.sum((port0.center - port1.center) ** 2))
            if self.length is None
            else self.length
        )

        frequencies = numpy.array(frequencies, dtype=float, ndmin=1)

        if verbose is None:
            verbose = self.verbose

        n_type = self._classify_n_complex(self.n_complex)
        if n_type is numpy.ndarray:
            num_modes = port0.num_modes
            zero = numpy.zeros((self.n_complex.shape[0], len(frequencies)))
            coeff = (2.0j * numpy.pi / C_0) * self.n_complex + zero
            if coeff.shape[0] < num_modes:
                raise RuntimeError(
                    f"The first dimension of 'n_complex' in the model for '{component.name}' "
                    f"must be {num_modes} to account for all modes in the component's ports."
                )

            t = numpy.exp(coeff * length * frequencies)
            elements = {
                (f"{port_in}@{mode}", f"{port_out}@{mode}"): t[mode]
                for port_in in port_names
                for port_out in port_names
                for mode in range(num_modes)
                if port_in != port_out
            }
            return ModelResult(SMatrix(frequencies, elements, component_ports))

        free_space_phase = 2.0 * numpy.pi / C_0 * length * frequencies
        for port in component_ports.values():
            if port.spec.polarization != "":
                port.spec = port.spec.copy()
                port.spec.polarization = ""
                port.spec.num_modes += port.spec.added_solver_modes
                port.spec.added_solver_modes = 0

        ms_port = port0.copy(True)
        if n_type is PortSpec:
            ms_port.spec = libcopy.deepcopy(self.n_complex)
        elif n_type is str:
            direction = int((ms_port.input_direction + 45) // 90) % 4
            angle = ms_port.input_direction - 90 * direction
            axis = "x" if direction % 2 == 0 else "y"

            x_length = ms_port.spec.width + 2 * config.tolerance
            x_center = ms_port.center.copy()
            x_center[direction % 2] += config.grid * 2 * (1 - 2 * (direction // 2))
            x_comp = Component().add(
                Reference(
                    Component().add(Reference(component, -ms_port.center)),
                    ms_port.center,
                    -angle,
                )
            )
            ms_port.spec.path_profiles = x_comp.slice_profile(axis, x_center, x_length)
        runner = _ModeSolverRunner(
            ms_port,
            frequencies,
            self.mesh_refinement,
            component.technology,
            cost_estimation=cost_estimation,
            verbose=verbose,
        )
        return _WaveguideModelRunner(runner, free_space_phase, frequencies, component_ports)

    @property
    def as_bytes(self) -> bytes:
        """Serialize this model."""
        obj = [
            ("n_complex", self.n_complex),
            ("length", self.length),
            ("mesh_refinement", self.mesh_refinement),
            ("verbose", self.verbose),
        ]
        return b"\x02" + _as_bytes(obj)

    @classmethod
    def from_bytes(cls, byte_repr: bytes) -> "WaveguideModel":
        """De-serialize this model."""
        version = byte_repr[0]
        if version == 2:
            return cls(**dict(_from_bytes(byte_repr[1:])))
        elif version == 1:
            head_len = struct.calcsize("<BB2d")
            flags, length, mesh_refinement = struct.unpack("<B2d", byte_repr[1:head_len])
            verbose = (flags & 0x01) > 0
            lenght_is_none = (flags & 0x02) > 0
            n_type = {0x00: None, 0x04: str, 0x08: PortSpec, 0x0C: numpy.ndarray}.get(flags & 0x0C)
        elif version == 0:
            head_len = struct.calcsize("<B3?2d")
            n_complex_is_none, lenght_is_none, verbose, length, mesh_refinement = struct.unpack(
                "<3?2d", byte_repr[1:head_len]
            )
            n_type = None if n_complex_is_none else numpy.ndarray
        else:
            raise RuntimeError(
                "This WaveguideModel seems to have been created by a more recent version of "
                "PhotonForge and it is not supported by the this version."
            )

        if mesh_refinement <= 0:
            mesh_refinement = None

        if lenght_is_none:
            length = None

        n_complex = None
        if n_type is PortSpec:
            kwds = json.loads(zlib.decompress(byte_repr[head_len:]).decode("utf-8"))
            profiles = kwds["path_profiles"]
            if isinstance(profiles, dict):
                kwds["path_profiles"] = {
                    k: (v["width"], v["offset"], v["layer"]) for k, v in profiles.items()
                }
            else:
                kwds["path_profiles"] = [(v["width"], v["offset"], v["layer"]) for v in profiles]
            if "electrical_spec" in kwds:
                # The 1e-5 factor is to fix a bug that existed in the json conversion
                kwds.update(
                    {k: numpy.array(v) * 1e-5 for k, v in kwds.pop("electrical_spec").items()}
                )
            n_complex = PortSpec(**kwds)
        elif n_type is str:
            n_complex = "cross-section"
        elif n_type is numpy.ndarray:
            mem_io = io.BytesIO()
            mem_io.write(byte_repr[head_len:])
            mem_io.seek(0)
            n_complex = numpy.load(mem_io)
            if version == 0:
                # Version 0 stored the transformed coefficient
                n_complex *= -0.5j / numpy.pi * C_0

        return cls(n_complex, length, mesh_refinement, verbose)


register_model_class(TerminationModel)
register_model_class(TwoPortModel)
register_model_class(PowerSplitterModel)
register_model_class(DirectionalCouplerModel)
register_model_class(WaveguideModel)
