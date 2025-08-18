import copy as libcopy
import re
import struct
import warnings
from collections.abc import Sequence
from typing import Any, Literal, Optional, Union

import numpy
import tidy3d

from .cache import _mode_overlap_cache, cache_s_matrix, cache_time_stepper
from .extension import (
    Component,
    GaussianPort,
    Model,
    Port,
    Reference,
    SMatrix,
    TimeSeries,
    TimeStepper,
    _connect_s_matrices,
    frequency_classification,
    register_model_class,
)
from .tidy3d_model import (
    _align_and_overlap,
    _align_and_overlap_analytical,
    _ModeSolverRunner,
)
from .time_stepper_model import TimeStepperRunner


def _gather_status(*runners: Any) -> dict[str, Any]:
    """Create an overall status based on a collection of Tidy3D runners."""
    num_tasks = 0
    progress = 0
    message = "success"
    tasks = {}
    for task in runners:
        task_status = task.status
        inner_tasks = task_status.get("tasks", {})
        tasks.update(inner_tasks)
        task_weight = max(1, len(inner_tasks))
        num_tasks += task_weight
        if message != "error":
            if task_status["message"] == "error":
                message = "error"
            elif task_status["message"] == "running":
                message = "running"
                progress += task_weight * task_status["progress"]
            elif task_status["message"] == "success":
                progress += task_weight * 100
    if message == "running":
        progress /= num_tasks
    else:
        progress = 100
    return {"progress": progress, "message": message, "tasks": tasks}


class _CircuitModelRunner:
    def __init__(
        self,
        runners: dict[Any, Any],
        frequencies: Sequence[float],
        component_name: str,
        ports: dict[str, Port],
        port_connections: dict[str, tuple[int, str, int]],
        connections: Sequence[tuple[tuple[int, str, int], tuple[int, str, int]]],
        instance_port_data: Sequence[tuple[Any, Any]],
    ) -> None:
        self.runners = runners
        self.frequencies = frequencies
        self.component_name = component_name
        self.ports = ports
        self.port_connections = port_connections
        self.connections = connections
        self.instance_port_data = instance_port_data
        self._s_matrix = None

    @property
    def status(self) -> dict[str, Any]:
        return _gather_status(*self.runners.values())

    @staticmethod
    def get_mode_factor(runners, instance_port_data):
        """Fix port phases if a rotation is applied."""
        mode_factor = {}
        for index, (instance_ports, instance_keys) in enumerate(instance_port_data):
            # Check if reference is needed
            if instance_ports is None:
                continue

            for port_name, port in instance_ports:
                for mode in range(port.num_modes):
                    mode_factor[(index, f"{port_name}@{mode}")] = 1.0

            if instance_keys is not None:
                for port_name, port in instance_ports:
                    key = instance_keys.get(port_name)
                    if key is None:
                        continue
                    if isinstance(key, tuple):
                        overlap = _mode_overlap_cache[key]
                        if overlap is None:
                            overlap = _align_and_overlap(
                                runners[(index, port_name, 0)].data,
                                runners[(index, port_name, 1)].data,
                            )[0]
                            _mode_overlap_cache[key] = overlap
                    else:
                        # Reference Gaussian
                        overlap = numpy.array([_align_and_overlap_analytical(port, key)])

                    for mode in range(port.num_modes):
                        mode_factor[(index, f"{port_name}@{mode}")] = overlap[mode]
        return mode_factor

    @property
    def s_matrix(self) -> SMatrix:
        if self._s_matrix is None:
            s_dict = {}
            mode_factor = self.get_mode_factor(
                runners=self.runners, instance_port_data=self.instance_port_data
            )
            for index, (instance_ports, _) in enumerate(self.instance_port_data):
                # Check if reference is needed
                if instance_ports is None:
                    continue

                s_matrix = self.runners[index].s_matrix
                if s_matrix is None:
                    return None

                # Fix port phases if a rotation is applied
                for (i, j), s_ji in s_matrix.elements.items():
                    s_dict[(index, i), (index, j)] = (
                        s_ji * mode_factor[(index, i)] / mode_factor[(index, j)]
                    )

            s_dict = _connect_s_matrices(s_dict, self.connections, len(self.instance_port_data))

            # Build S matrix with desired ports
            ports = {
                (index, f"{ref_name}@{n}"): f"{port_name}@{n}"
                for (index, ref_name, modes), port_name in self.port_connections.items()
                for n in range(modes)
            }

            elements = {
                (ports[i], ports[j]): s_ji
                for (i, j), s_ji in s_dict.items()
                if i in ports and j in ports
            }
            self._s_matrix = SMatrix(self.frequencies, elements, self.ports)

        return self._s_matrix


def _compare_angles(a: float, b: float) -> bool:
    r = (a - b) % 360
    return r <= 1e-12 or 360 - r <= 1e-12


# Return a flattening key (for caching) if flattening is required, and
# a bool indicating whether phase correction is required
def _analyze_transform(
    reference: Reference,
    classification: Literal["optical", "electrical"],
    frequencies: Sequence[float],
) -> tuple[Union[tuple[Union[tuple[float, float], None], float, bool], None], bool]:
    technology = reference.component.technology

    background_medium = technology.get_background_medium(classification)
    extrusion_media = [e.get_medium(classification) for e in technology.extrusion_specs]

    uniform = background_medium.is_spatially_uniform and all(
        medium.is_spatially_uniform for medium in extrusion_media
    )

    translated = not numpy.allclose(reference.origin, (0, 0), atol=1e-12)
    rotated = not _compare_angles(reference.rotation, 0)

    if not uniform and (translated or rotated):
        return (
            tuple(reference.origin.tolist()),
            reference.rotation,
            reference.x_reflection,
        ), None

    if reference.x_reflection:
        return (None, reference.rotation, reference.x_reflection), None

    # _align_and_overlap only works for rotations that are a multiple of 90°
    rotation_fraction = reference.rotation % 90
    is_multiple_of_90 = rotation_fraction < 1e-12 or (90 - rotation_fraction < 1e-12)
    if not is_multiple_of_90:
        return (None, reference.rotation, reference.x_reflection), None

    # _align_and_overlap does not support angled ports either
    ports = reference.component.select_ports(classification)
    for port in ports.values():
        if isinstance(port, GaussianPort):
            if frequencies is None:
                raise ValueError("Must specify 'frequencies' to obtain time stepper.")
            _, _, _, theta, _ = port._axis_aligned_properties(frequencies)
        else:
            _, _, _, theta, _ = port._axis_aligned_properties()
        if theta != 0.0:
            return (None, reference.rotation, reference.x_reflection), None

    translated_mask = any(e.mask_spec.uses_translation() for e in technology.extrusion_specs)
    if translated_mask and rotated:
        return (None, reference.rotation, reference.x_reflection), None

    fully_anisotropic = background_medium.is_fully_anisotropic or any(
        medium.is_fully_anisotropic for medium in extrusion_media
    )
    in_plane_isotropic = (
        not fully_anisotropic
        and (
            not isinstance(background_medium, tidy3d.AnisotropicMedium)
            or background_medium.xx == background_medium.yy
        )
        and all(
            (not isinstance(medium, tidy3d.AnisotropicMedium) or medium.xx == medium.yy)
            for medium in extrusion_media
        )
    )

    if (fully_anisotropic and rotated) or (
        not in_plane_isotropic and rotated and not _compare_angles(reference.rotation, 180)
    ):
        return (None, reference.rotation, reference.x_reflection), None

    return None, rotated


def _validate_update_dict(
    updates: dict[Union[str, re.Pattern, int, tuple[re.Pattern, int], None], Any],
) -> list[tuple[Union[str, re.Pattern, int, tuple[re.Pattern, int], None], Any]]:
    """Validate keys in updates dictionary and puth them in canonical form."""
    valid_updates = []
    for key, value in updates.items():
        if len(key) == 0:
            raise KeyError("Empty key in 'updates' is not allowed.")
        valid_key = []
        expect_int = False
        for i, k in enumerate(key):
            if k is None:
                if len(valid_key) == 0 or valid_key[-1] is not None:
                    valid_key.append(None)
                expect_int = False
            elif isinstance(k, str):
                valid_key.append((re.compile(k), -1))
                expect_int = True
            elif isinstance(k, re.Pattern):
                valid_key.append((re.compile(k), -1))
                expect_int = True
            elif isinstance(k, int) and expect_int:
                valid_key[-1] = (valid_key[-1][0], k)
                expect_int = False
            elif (
                isinstance(k, tuple)
                and len(k) == 2
                and isinstance(k[0], re.Pattern)
                and isinstance(k[1], int)
            ):
                valid_key.append(k)
            else:
                raise RuntimeError(
                    f"Invalid value in position {i} in key {tuple(key)}: {k}. Expected a "
                    "string, a compiled regular expression pattern, "
                    + ("an integer, " if expect_int else "")
                    + "or 'None'."
                )
        valid_updates.append((tuple(valid_key), value))
    return valid_updates


class CircuitTimeStepper(TimeStepper):
    """Time stepper for a circuit model."""

    def __init__(
        self,
        time_steppers,
        time_step,
        time_index,
        carrier_frequency,
        component_name,
        ports,
        port_connections,
        connections,
        instance_port_data,
        mode_factor,
        s_matrix,
        s_fit,
        monitors,
        port_state={},
    ) -> None:
        super().__init__(
            time_steppers=time_steppers,
            time_step=time_step,
            time_index=time_index,
            carrier_frequency=carrier_frequency,
            component_name=component_name,
            ports=ports,
            port_connections=port_connections,
            connections=connections,
            instance_port_data=instance_port_data,
            mode_factor=mode_factor,
            s_matrix=s_matrix,
            s_fit=s_fit,
            monitors=monitors,
            port_state=port_state,
        )
        self.time_steppers = time_steppers
        self.carrier_frequency = carrier_frequency
        self.component_name = component_name
        self.ports = ports
        self.port_connections = port_connections
        self.connections = connections
        self.instance_port_data = instance_port_data
        self.mode_factor = mode_factor
        self.s_matrix = s_matrix
        self.s_fit = s_fit
        self.monitors = monitors

        self.port_state = port_state

        # calculate port mapping and monitor port mapping
        ports = {
            (index, f"{ref_name}@{n}"): f"{port_name}@{n}"
            for (index, ref_name, modes), port_name in self.port_connections.items()
            for n in range(modes)
        }
        self._ports = ports
        monitor_ports = {}
        num_modes = {}
        for index, (instance_ports, _) in enumerate(self.instance_port_data):
            # Check if reference is needed
            if instance_ports is None:
                continue

            for ref_name, port in instance_ports:
                num_modes[(index, ref_name)] = port.num_modes

            curr_monitors = monitors.get(index, {})
            for ref_name, _ in instance_ports:
                for key, value in curr_monitors.items():
                    if key[0][0].match(ref_name):
                        for n in range(num_modes[(index, ref_name)]):
                            monitor_ports[(index, f"{ref_name}@{n}")] = f"{value}@{n}"

        self._monitor_ports = monitor_ports
        self._num_modes = num_modes

    def start(self, inputs: TimeSeries) -> TimeStepperRunner:
        """Start computing the time stepper result from the given input.

        Args:
            inputs: Time series of inputs for the time stepper.
            **kwargs: Unused.

        Returns:
           Time stepper runner with attribute ``status`` and functions
           ``put``, ``get``, and ``shutdown``.
        """
        self.runners = {}
        for key, time_stepper in self.time_steppers.items():
            self.runners[key] = time_stepper.start(inputs=None)
        return TimeStepperRunner(time_stepper=self, inputs=inputs)

    def shutdown(self):
        """Shut down the time stepper, cleaning up any runners."""
        for key in self.time_steppers.keys():
            self.runners[key].shutdown()
        self.runners = {}

    def reset(self):
        """Reset the state of the time stepper."""
        super().reset()
        for time_stepper in self.time_steppers.values():
            time_stepper.reset()
        self.port_state = {}

    @property
    def rms_error(self):
        """The rms error between the circuit S matrix obtained from
        frequency-domain simulation and the circuit S matrix obtained
        from fitting that data."""
        err = None
        if self.s_matrix is not None:
            err = 0
            keys = self.s_matrix.elements.keys() | self.s_fit.elements.keys()
            for key in keys:
                square = (
                    numpy.abs(self.s_matrix.elements.get(key, 0) - self.s_fit.elements.get(key, 0))
                    ** 2
                )
                err += numpy.sum(square)
            err /= len(self.s_matrix.frequencies) * len(keys)
            err = numpy.sqrt(err)
        return err

    def step_single(self, inputs: dict[str, complex]) -> dict[str, complex]:
        """Take a single step.

        Args:
            inputs: Dictionary mapping port names to input values.

        Returns:
            Dictionary mapping port names to output values.
        """

        new_port_state = {}
        outputs = {}

        # apply input to curr_port_state
        for (index, ref_name), port_name in self._ports.items():
            if port_name in inputs:
                self.port_state[(index, ref_name)] = inputs[port_name]
            elif (index, ref_name) not in self.port_state:
                self.port_state[(index, ref_name)] = 0

        for index, (instance_ports, _) in enumerate(self.instance_port_data):
            # Check if reference is needed
            if instance_ports is None:
                continue

            # map port_state to curr_inputs
            curr_inputs = {
                ref_name: val * self.mode_factor.get((index, ref_name), 1.0)
                for (idx, ref_name), val in self.port_state.items()
                if idx == index
            }
            self.runners[index].inputs.put(curr_inputs)

        # block for runners to finish
        for index, (instance_ports, _) in enumerate(self.instance_port_data):
            if instance_ports is None:
                continue

            curr_outputs = self.runners[index].outputs.get()
            for key, val in curr_outputs.items():
                new_port_state[(index, key)] = val / self.mode_factor.get((index, key), 1.0)

        # now apply connections
        connected_port_state = {}
        for (idx1, port_name1, _), (idx2, port_name2, _) in self.connections:
            num_modes_curr = self._num_modes[(idx1, port_name1)]
            for mode in range(num_modes_curr):
                if (idx1, f"{port_name1}@{mode}") in new_port_state:
                    connected_port_state[(idx2, f"{port_name2}@{mode}")] = new_port_state[
                        (idx1, f"{port_name1}@{mode}")
                    ]
                if (idx2, f"{port_name2}@{mode}") in new_port_state:
                    connected_port_state[(idx1, f"{port_name1}@{mode}")] = new_port_state[
                        (idx2, f"{port_name2}@{mode}")
                    ]

        self.port_state = dict(connected_port_state)

        # store outputs
        for (index, ref_name), port_name in self._ports.items():
            if (index, ref_name) in new_port_state:
                outputs[port_name] = new_port_state[(index, ref_name)]
            else:
                outputs[port_name] = 0
        for (index, ref_name), port_name in self._monitor_ports.items():
            if (index, ref_name) in new_port_state:
                outputs[port_name] = new_port_state[(index, ref_name)]
            else:
                outputs[port_name] = 0

        # pass on outputs from subcircuits
        for index, (_, _) in enumerate(self.instance_port_data):
            for mon_name in self.monitors[index].values():
                mode_ind = 0
                while True:
                    name = f"{mon_name}@{mode_ind}"
                    val = new_port_state.get((index, name), None)
                    if val is None or name in outputs:
                        break
                    outputs[name] = val
                    mode_ind += 1

        return outputs


class _CircuitTimeStepperModelRunner(_CircuitModelRunner):
    """Runner class for circuit time-stepper model."""

    def __init__(
        self,
        runners,
        time_step,
        time_index,
        carrier_frequency,
        component_name,
        ports,
        port_connections,
        connections,
        instance_port_data,
        frequencies,
        monitors,
    ) -> None:
        self.runners = runners
        self.time_step = time_step
        self.time_index = time_index
        self.carrier_frequency = carrier_frequency
        self.component_name = component_name
        self.ports = ports
        self.port_connections = port_connections
        self.connections = connections
        self.instance_port_data = instance_port_data
        self.frequencies = frequencies
        self.monitors = monitors

        self._time_stepper = None
        self._s_matrix = None
        self._s_fit = None

    @property
    def status(self):
        return _gather_status(*self.runners.values())

    @property
    def time_stepper(self):
        if self._time_stepper is None:
            time_steppers = {}
            for index in range(len(self.instance_port_data)):
                time_steppers[index] = libcopy.deepcopy(self.runners[index].time_stepper)
                time_steppers[index].reset()
            mode_factor = _CircuitModelRunner.get_mode_factor(
                runners=self.runners, instance_port_data=self.instance_port_data
            )

            self._time_stepper = CircuitTimeStepper(
                time_steppers=time_steppers,
                time_step=self.time_step,
                time_index=self.time_index,
                carrier_frequency=self.carrier_frequency,
                component_name=self.component_name,
                ports=self.ports,
                port_connections=self.port_connections,
                connections=self.connections,
                instance_port_data=self.instance_port_data,
                mode_factor=mode_factor,
                s_matrix=self.s_matrix,
                s_fit=self.s_fit,
                monitors=self.monitors,
            )
        return self._time_stepper

    @property
    def s_fit(self) -> SMatrix:
        if self._s_fit is None:
            s_dict = {}
            mode_factor = self.get_mode_factor(
                runners=self.runners, instance_port_data=self.instance_port_data
            )
            for index, (instance_ports, _) in enumerate(self.instance_port_data):
                # Check if reference is needed
                if instance_ports is None:
                    continue

                s_matrix = None
                if hasattr(self.runners[index], "s_fit"):
                    s_matrix = self.runners[index].s_fit
                elif hasattr(self.runners[index], "s_matrix"):
                    s_matrix = self.runners[index].s_matrix
                if s_matrix is None:
                    return None

                # Fix port phases if a rotation is applied
                for (i, j), s_ji in s_matrix.elements.items():
                    s_dict[(index, i), (index, j)] = (
                        s_ji * mode_factor[(index, i)] / mode_factor[(index, j)]
                    )

            s_dict = _connect_s_matrices(s_dict, self.connections, len(self.instance_port_data))

            # Build S matrix with desired ports
            ports = {
                (index, f"{ref_name}@{n}"): f"{port_name}@{n}"
                for (index, ref_name, modes), port_name in self.port_connections.items()
                for n in range(modes)
            }

            elements = {
                (ports[i], ports[j]): s_ji
                for (i, j), s_ji in s_dict.items()
                if i in ports and j in ports
            }
            self._s_fit = SMatrix(self.frequencies, elements, self.ports)

        return self._s_fit


class CircuitTimeStepperModel:
    """A time stepper model for circuits.
    Constructs time steppers for individual circuit elements and handles
    connections between them.

    Note:
        The connections are not instantaneous; there is a single time step
        delay before the output of one device reaches the input of a connected
        device.
    """

    @cache_time_stepper
    def start_time_stepper(
        self,
        component: Component,
        time_step: float,
        time_index: int,
        carrier_frequency: float,
        frequencies: Optional[Sequence[float]] = None,
        updates: dict = {},
        chain_technology_updates=True,
        verbose: Optional[bool] = None,
        **kwargs,
    ) -> _CircuitTimeStepperModelRunner:
        """Start computing the time stepper for the given component.

        Args:
            component: Component from which to compute the S matrix.
            time_step (double): The interval between time steps in seconds.
            time_index (int): The time index of the time stepper.
            carrier_frequency (double): The carrier frequency used to construct
              the time stepper. The carrier should be omitted from the input signal
              as it is handled automatically by the time stepper.
            frequencies (Sequence[float]): Frequency values at which to
              calculate the scattering parameters (in Hz). The scattering parameters
              are used for fitting in time-stepper models.
              Can be overridden by individual models or references.
            updates: Dictionary of parameter updates to be applied to
              components, technologies, and models for references within the
              main component. See below for further information.
            chain_technology_updates: if set, a technology update will trigger
              an update for all components using that technology.
            verbose: If set, overrides the model's `verbose` attribute and is
              passed to reference models.
            **kwargs: Keyword arguments passed to reference models.

        Returns:
           Resulting time stepper.

        The ``'updates'`` dictionary contains keyword arguments for the
        :func:`Reference.update` function for the references in the component
        dependency tree, such that, when the S parameter of a specific reference
        are computed, that reference can be updated without affecting others
        using the same component.

        Each key in the dictionary is used as a reference specification. It must
        be a tuple with any number of the following:

        - ``name: str | re.Pattern``: selects any reference whose component name
          matches the given regex.

        - ``i: int``, directly following ``name``: limits the selection to
          ``reference[i]`` from the list of references matching the name. A
          negative value will match all list items. Note that each repetiton in
          a reference array counts as a single element in the list.

        - ``None``: matches any reference at any depth.

        Examples:
            >>> updates = {
            ...     # Apply component updates to the first "ARM" reference in
            ...     # the main component
            ...     ("ARM", 0): {"component_updates": {"radius": 10}}
            ...     # Apply model updates to the second "BEND" reference under
            ...     # any "SUB" references in the main component
            ...     ("SUB", "BEND", 1): {"model_updates": {"verbose": False}}
            ...     # Apply technology updates to references with component name
            ...     # starting with "COMP_" prefix, at any subcomponent depth
            ...     (None, "COMP.*"): {"technology_updates": {"thickness": 0.3}}
            ... }
            >>> s_matrix = component.s_matrix(
            ...     frequencies, model_kwargs={"updates": updates}
            ... )

        See also:
            - `Circuit Model guide <../guides/Circuit_Model.ipynb>`__
            - `Cascaded Rings Filter example
              <../examples/Cascaded_Rings_Filter.ipynb>`__
        """

        return self._start(
            component=component,
            frequencies=frequencies,
            updates=updates,
            chain_technology_updates=chain_technology_updates,
            verbose=verbose,
            time_step=time_step,
            time_index=time_index,
            carrier_frequency=carrier_frequency,
            **kwargs,
        )


class CircuitModel(CircuitTimeStepperModel, Model):
    """Model based on circuit-level S-parameter calculation.

    The component is expected to be composed of interconnected references.
    Scattering parameters are computed based on the S matrices from all
    references and their interconnections.

    The S matrix of each reference is calculated based on the active model
    of the reference's component. Each calculation is preceded by an update
    to the componoent's technology, the component itself, and its active
    model by calling :attr:`Reference.update`. They are reset to their
    original state after the :func:`CircuitModel.start` function is called.
    Keyword arguents in :attr:`Reference.s_matrix_kwargs` will be passed on
    to :func:`CircuitModel.start`.

    If a reference includes repetitions, it is flattened so that each
    instance is called separatelly.

    Args:
        mesh_refinement: Minimal number of mesh elements per wavelength used
          for mode solving.
        verbose: Flag setting the verbosity of mode solver runs.

    See also:
        `Circuit Model guide <../guides/Circuit_Model.ipynb>`__
    """

    def __init__(
        self,
        mesh_refinement: Optional[float] = None,
        verbose: bool = True,
    ):
        super().__init__(mesh_refinement=mesh_refinement, verbose=verbose)
        self.mesh_refinement = mesh_refinement
        self.verbose = verbose

    def __copy__(self) -> "CircuitModel":
        return CircuitModel(self.mesh_refinement, self.verbose)

    def __deepcopy__(self, memo: Optional[dict] = None) -> "CircuitModel":
        return CircuitModel(self.mesh_refinement, self.verbose)

    def __str__(self) -> str:
        return "CircuitModel"

    def __repr__(self) -> str:
        return "CircuitModel()"

    @cache_s_matrix
    def start(
        self,
        component: Component,
        frequencies: Sequence[float],
        updates: dict[Sequence[Union[str, int, None]], dict[str, dict[str, Any]]] = {},
        chain_technology_updates: bool = True,
        verbose: Optional[bool] = None,
        cost_estimation: bool = False,
        **kwargs: Any,
    ) -> _CircuitModelRunner:
        """Start computing the S matrix response from a component.

        Args:
            component: Component from which to compute the S matrix.
            frequencies: Sequence of frequencies at which to perform the
              computation.
            updates: Dictionary of parameter updates to be applied to
              components, technologies, and models for references within the
              main component. See below for further information.
            chain_technology_updates: if set, a technology update will trigger
              an update for all components using that technology.
            verbose: If set, overrides the model's ``verbose`` attribute and
              is passed to reference models.
            cost_estimation: If set, Tidy3D simulations are uploaded, but not
              executed. S matrix will *not* be computed.
            **kwargs: Keyword arguments passed to reference models.

        Returns:
            Result object with attributes ``status`` and ``s_matrix``.

        The ``'updates'`` dictionary contains keyword arguments for the
        :func:`Reference.update` function for the references in the component
        dependency tree, such that, when the S parameter of a specific reference
        are computed, that reference can be updated without affecting others
        using the same component.

        Each key in the dictionary is used as a reference specification. It must
        be a tuple with any number of the following:

        - ``name: str | re.Pattern``: selects any reference whose component name
          matches the given regex.

        - ``i: int``, directly following ``name``: limits the selection to
          ``reference[i]`` from the list of references matching the name. A
          negative value will match all list items. Note that each repetiton in
          a reference array counts as a single element in the list.

        - ``None``: matches any reference at any depth.

        Examples:
            >>> updates = {
            ...     # Apply component updates to the first "ARM" reference in
            ...     # the main component
            ...     ("ARM", 0): {"component_updates": {"radius": 10}}
            ...     # Apply model updates to the second "BEND" reference under
            ...     # any "SUB" references in the main component
            ...     ("SUB", "BEND", 1): {"model_updates": {"verbose": False}}
            ...     # Apply technology updates to references with component name
            ...     # starting with "COMP_" prefix, at any subcomponent depth
            ...     (None, "COMP.*"): {"technology_updates": {"thickness": 0.3}}
            ... }
            >>> s_matrix = component.s_matrix(
            ...     frequencies, model_kwargs={"updates": updates}
            ... )

        See also:
            - `Circuit Model guide <../guides/Circuit_Model.ipynb>`__
            - `Cascaded Rings Filter example
              <../examples/Cascaded_Rings_Filter.ipynb>`__
        """
        return self._start(
            component=component,
            frequencies=frequencies,
            updates=updates,
            chain_technology_updates=chain_technology_updates,
            verbose=verbose,
            cost_estimation=cost_estimation,
            **kwargs,
        )

    def _start(
        self,
        component: Component,
        frequencies: Sequence[float],
        updates: dict = {},
        chain_technology_updates=True,
        verbose: Optional[bool] = None,
        cost_estimation: bool = False,
        time_step: Optional[float] = None,
        time_index: Optional[int] = None,
        carrier_frequency: Optional[float] = None,
        monitors: dict = {},
        **kwargs: Any,
    ) -> Any:
        """Used to share logic between ``start`` and ``start_time_stepper``."""
        time_domain = time_step is not None
        if verbose is None:
            verbose = self.verbose
            s_matrix_kwargs = {}
        else:
            s_matrix_kwargs = {"verbose": verbose}
        if cost_estimation:
            s_matrix_kwargs["cost_estimation"] = cost_estimation
        if frequencies is not None:
            frequencies = numpy.array(frequencies, dtype=float, ndmin=1)
        if frequencies is not None:
            classification = frequency_classification(frequencies)
        elif carrier_frequency is not None:
            classification = frequency_classification(carrier_frequency)
        elif time_step is not None:
            classification = frequency_classification(1 / time_step)
        else:
            raise ValueError("Must specify 'frequencies' to obtain time stepper.")
        netlist = component.get_netlist()

        _, reference_index_map = component.get_instance_maps()

        # 'inputs' is not supported in CircuitModel
        kwargs = dict(kwargs)
        if "inputs" in kwargs:
            del kwargs["inputs"]

        valid_updates = _validate_update_dict(updates)
        valid_monitors = _validate_update_dict(monitors)
        reference_index = {}

        # Store copies of instance ports and their reference for phase correction
        instance_port_data = [(None, None)] * len(netlist["instances"])

        runners = {}
        flattened_component_cache = {}

        monitors_full = {}

        for index, reference in enumerate(netlist["instances"]):
            ref_component = reference.component
            current_reference_index = reference_index.get(ref_component.name, -1) + 1
            reference_index[ref_component.name] = current_reference_index

            if ref_component.select_active_model(classification) is None:
                # Check if the model is really needed
                if any(
                    index0 == index or index1 == index
                    for (index0, _, _), (index1, _, _) in netlist["connections"]
                ) or any(i == index for i, _, _ in netlist["ports"]):
                    raise RuntimeError(f"Component '{ref_component.name}' has no active model.")
                continue

            ports = ref_component.select_ports(classification)
            instance_port_data[index] = (
                tuple((port_name, port.copy(True)) for port_name, port in ports.items()),
                None,
            )

            # Match updates with current reference
            reference_updates = {}
            technology_updates = {}
            component_updates = {}
            model_updates = {}
            for key, value in valid_updates:
                if key[0] is None:
                    reference_updates[key] = value
                    key = key[1:]
                if len(key) == 0:
                    technology_updates.update(value.get("technology_updates", {}))
                    component_updates.update(value.get("component_updates", {}))
                    model_updates.update(value.get("model_updates", {}))
                elif key[0][0].match(ref_component.name):
                    if key[0][1] < 0 or key[0][1] == current_reference_index:
                        if len(key) == 1:
                            technology_updates.update(value.get("technology_updates", {}))
                            component_updates.update(value.get("component_updates", {}))
                            model_updates.update(value.get("model_updates", {}))
                        else:
                            reference_updates[key[1:]] = value

            reference_monitors = {}
            for key, value in valid_monitors:
                if key[0] is None:
                    reference_monitors[key] = value
                    key = key[1:]
                    monitors_full[index] = value
                if len(key) == 0:
                    pass
                elif key[0][0].match(ref_component.name):
                    if key[0][1] < 0 or key[0][1] == current_reference_index:
                        if len(key) == 1:
                            pass
                        else:
                            reference_monitors[key[1:]] = value
                            monitors_full[index] = value

            # Apply required updates
            reset_list = reference.update(
                technology_updates=technology_updates,
                component_updates=component_updates,
                model_updates=model_updates,
                chain_technology_updates=chain_technology_updates,
            )

            # Account for reference transformations
            inner_component = ref_component
            flattening_key, requires_phase_correction = _analyze_transform(
                reference, classification, frequencies
            )
            if flattening_key is not None:
                flattening_key = (ref_component.as_bytes, *flattening_key)
                inner_component = flattened_component_cache.get(flattening_key)
                if inner_component is None:
                    inner_component = reference.transformed_component(
                        ref_component.name + "-flattened"
                    )
                    flattened_component_cache[flattening_key] = inner_component
            elif requires_phase_correction:
                # S matrix correction factor depends on the mode solver for transformed ports
                port_keys = {}
                for port_name, port in ports.items():
                    if not isinstance(port, Port):
                        # Reference Gaussian
                        port_keys[port_name] = reference[port_name]
                    # No mode solver runs for 1D ports
                    elif port.spec.limits[1] != port.spec.limits[0]:
                        if frequencies is None:
                            raise ValueError("Must specify 'frequencies' to obtain time stepper.")
                        runners[(index, port_name, 0)] = _ModeSolverRunner(
                            port,
                            frequencies[:1],
                            self.mesh_refinement,
                            ref_component.technology,
                            cost_estimation=cost_estimation,
                            verbose=verbose,
                        )
                        runners[(index, port_name, 1)] = _ModeSolverRunner(
                            reference[port_name],
                            frequencies[:1],
                            self.mesh_refinement,
                            ref_component.technology,
                            cost_estimation=cost_estimation,
                            verbose=verbose,
                        )
                        port_keys[port_name] = (
                            ref_component.technology.as_bytes,
                            port.spec.as_bytes,
                            port.input_direction % 360,
                            port.inverted,
                            reference.rotation % 360,
                        )

                instance_port_data[index] = (instance_port_data[index][0], port_keys)

            s_matrix_kwargs["updates"] = {}
            s_matrix_kwargs["chain_technology_updates"] = chain_technology_updates
            s_matrix_kwargs.update(kwargs)
            s_matrix_kwargs.update(reference_updates.pop("s_matrix_kwargs", {}))
            if reference.s_matrix_kwargs is not None:
                s_matrix_kwargs.update(reference.s_matrix_kwargs)
            s_matrix_kwargs["updates"].update(reference_updates)
            s_matrix_kwargs["monitors"] = {}
            s_matrix_kwargs["monitors"].update(reference_monitors)
            monitors_full[index] = reference_monitors

            if time_domain:
                runners[index] = reference.component.select_active_model(
                    classification
                ).start_time_stepper(
                    component=inner_component,
                    time_step=time_step,
                    time_index=time_index,
                    carrier_frequency=carrier_frequency,
                    frequencies=frequencies,
                    **s_matrix_kwargs,
                )
            else:
                runners[index] = reference.component.select_active_model(classification).start(
                    inner_component, frequencies, **s_matrix_kwargs
                )

            # Reset all updates
            for item, kwds in reset_list:
                item.parametric_kwargs = kwds
                item.update()

        if len(runners) == 0:
            warnings.warn(
                f"No subcomponets found in the circuit model for component '{component.name}'.",
                stacklevel=2,
            )

        component_ports = {
            name: port.copy(True) for name, port in component.select_ports(classification).items()
        }
        port_connections = netlist["ports"]
        # In the circuit model, virtual connections behave like real connections
        connections = netlist["connections"] + netlist["virtual connections"]

        if time_domain:
            return _CircuitTimeStepperModelRunner(
                runners=runners,
                time_step=time_step,
                time_index=time_index,
                carrier_frequency=carrier_frequency,
                component_name=component.name,
                ports=component_ports,
                port_connections=port_connections,
                connections=connections,
                instance_port_data=instance_port_data,
                frequencies=frequencies,
                monitors=monitors_full,
            )
        else:
            return _CircuitModelRunner(
                runners,
                frequencies,
                component.name,
                component_ports,
                port_connections,
                connections,
                instance_port_data,
            )

    @property
    def as_bytes(self) -> bytes:
        """Serialize this model."""
        version = 0
        return struct.pack(
            "<B?d",
            version,
            self.verbose,
            0 if self.mesh_refinement is None else self.mesh_refinement,
        )

    @classmethod
    def from_bytes(cls, byte_repr: bytes) -> "CircuitModel":
        """De-serialize this model."""
        (version, verbose, mesh_refinement) = struct.unpack("<B?d", byte_repr)
        if version != 0:
            raise RuntimeError("Unsuported CircuitModel version.")

        if mesh_refinement <= 0:
            mesh_refinement = None
        return cls(mesh_refinement, verbose)


register_model_class(CircuitModel)
