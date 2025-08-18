import queue
import warnings as _warn
from collections.abc import Sequence
from typing import Any, Optional

import numpy

from .cache import cache_time_stepper
from .extension import (
    Component,
    Model,
    SMatrix,
    TimeDomainModel,
    TimeSeries,
    TimeStepper,
    pole_residue_fit,
)


class BufferedTimeStepper(TimeStepper):
    """A TimeStepper that wraps an existing TimeStepper, adding time delays
    to the inputs and outputs.

    Args:
        time_step (double): The interval between time steps (in seconds).
        time_index (int): The time index of the time stepper.
        time_stepper (TimeStepper): The time stepper to wrap with delays.
        input_delays: Dictionary mapping port names to delays (in seconds),
          applied to the inputs at these ports.
        output_delays: Dictionary mapping port names to delays (in seconds),
          applied to the outputs at these ports.
    """

    def __init__(self, time_step, time_index, time_stepper, input_delays=None, output_delays=None):
        super().__init__(
            time_step=time_step,
            time_index=time_index,
            time_stepper=time_stepper,
            input_delays=input_delays,
            output_delays=output_delays,
        )
        self.time_stepper = time_stepper
        self.input_delays = input_delays
        self.output_delays = output_delays
        self.output_buffer = {}
        self.input_buffer = {}

    def _buffer_put(self, buffer, delays, value):
        for key, val in value.items():
            if key not in buffer:
                delay = 0
                if isinstance(delays, dict):
                    delay = delays.get(key, 0)
                elif isinstance(delays, float):
                    delay = delays
                buffer_len = int(delay / self.time_stepper.time_step)
                buffer[key] = queue.Queue()
                for _ in range(buffer_len):
                    buffer[key].put(0)
            buffer[key].put(val)
        # anything not explicitly provided is zero
        for key in buffer.keys():
            if key not in value:
                buffer[key].put(0)

    def _buffer_get(self, buffer):
        value = {}
        for key, val in buffer.items():
            value[key] = val.get()
        return value

    def step_single(self, inputs):
        self._buffer_put(self.input_buffer, self.input_delays, inputs)
        inputs_buffered = self._buffer_get(self.input_buffer)
        outputs = self.time_stepper.step_single(inputs_buffered)
        self._buffer_put(self.output_buffer, self.output_delays, outputs)
        outputs_buffered = self._buffer_get(self.output_buffer)
        return outputs_buffered

    def reset(self):
        super().reset()
        self.output_buffer = {}
        self.input_buffer = {}


class TimeStepperModelResult:
    """Convenience class to return time stepper model results immediately.

    If a time stepper model computes a time stepper in a single step, it can
    use this class to return the required object with the results.

    Args:
        time_stepper: Time stepper to be returned as a result.
        status: Dictionary with ``'progress'`` and ``'message'``.
    """

    def __init__(
        self,
        time_stepper: TimeStepper,
        status: Optional[dict[str, Any]] = None,
    ) -> None:
        self.status = {"progress": 100, "message": "success"} if status is None else status
        self.time_stepper = time_stepper


class TimeStepperRunner:
    """A runner used internally to run a TimeStepper."""

    def __init__(self, time_stepper, inputs=None):
        self.time_stepper = time_stepper
        self.num_inputs = 0
        self.num_outputs = 0

        import threading

        self.inputs = queue.Queue()
        self.outputs = queue.Queue()

        self.thread = threading.Thread(
            daemon=True,
            target=self.run,
        )
        self.thread.start()

        if inputs is not None:
            self.put(inputs)

    def put(self, inputs):
        if isinstance(inputs, TimeSeries):
            vals = inputs.values_list
            for curr_inputs in vals:
                self.inputs.put(curr_inputs)
            self.num_inputs += len(vals)
        else:
            self.inputs.put(inputs)
            self.num_inputs += 1

    def get(self):
        return self.outputs.get()

    def shutdown(self):
        self.time_stepper.shutdown()

    @property
    def status(self):
        if self.num_inputs == 0:
            return {"progress": 0, "message": "running"}
        if self.num_outputs == self.num_inputs:
            return {"progress": 100, "message": "success"}
        progress = 100 * self.num_outputs / self.num_inputs
        return {"progress": progress, "message": "running"}

    def run(self):
        while True:
            try:
                inputs = self.inputs.get()
            except queue.ShutDown:
                return
            outputs = self.time_stepper.step_single(inputs=inputs)
            self.outputs.put(outputs)
            self.time_stepper.time_index += 1
            self.num_outputs += 1
            self.inputs.task_done()


class SMatrixTimeStepper(TimeStepper):
    """Time stepper based on a pole-residue matrix.
    The same time stepper can be reused, calling ``step`` again,
    and the internal state will persist.

    Args:
        s_matrix: The s-matrix used to generate the time-domain model.
        time_domain_model: The time-domain model underlying the time stepper.
        time_step (double): The interval between time steps (in seconds).
        time_index (int): The time index of the time stepper.
        carrier_frequency (double): The carrier frequency used to construct
          the time stepper. The carrier should be omitted from the input signal
          as it is handled automatically by the time stepper.
          Can be overridden by individual models or references.
    """

    def __init__(
        self,
        s_matrix,
        time_domain_model,
        time_step,
        time_index,
        carrier_frequency,
        model,
        component,
        fit_kwargs=None,
    ):
        super().__init__(
            s_matrix=s_matrix,
            time_domain_model=time_domain_model,
            fit_kwargs=fit_kwargs,
            time_step=time_step,
            time_index=time_index,
            carrier_frequency=carrier_frequency,
            model=model,
            component=component,
        )
        self.s_matrix = s_matrix
        self.time_domain_model = time_domain_model
        self.fit_kwargs = fit_kwargs
        self.carrier_frequency = carrier_frequency
        self.model = model
        self.component = component

    @property
    def s_fit(self):
        """The S matrix fit to the simulated frequency-domain S matrix."""
        freqs = self.s_matrix.frequencies - self.carrier_frequency
        s_fit = self.time_domain_model.pole_residue_matrix(freqs)
        s_fit = SMatrix(
            frequencies=self.s_matrix.frequencies, elements=s_fit.elements, ports=s_fit.ports
        )
        return s_fit

    @property
    def rms_error(self):
        """The rms error between the fit S matrix and the simulated S matrix."""
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
        return self.time_domain_model.step(inputs=inputs)

    def reset(self):
        """Reset the state of the time stepper."""
        super().reset()
        self.time_domain_model.reset()


class _SMatrixTimeStepperModelRunner:
    """Runner used to compute an SMatrixTimeStepper."""

    def __init__(
        self,
        model,
        component,
        time_step,
        time_index,
        carrier_frequency,
        frequencies,
        fit_kwargs,
        **kwargs,
    ):
        self.model = model
        self.component = component
        self.time_step = time_step
        self.time_index = time_index
        self.carrier_frequency = carrier_frequency
        self.fit_kwargs = fit_kwargs

        self._status = None
        self.s_matrix = None
        self.time_stepper = None

        self.s_matrix_runner = self.model.start(
            component=self.component,
            frequencies=frequencies,
            **kwargs,
        )
        import threading

        self.thread_s_matrix = threading.Thread(daemon=True, target=self.get_s_matrix)
        self.thread_s_matrix.start()
        self.thread_time_stepper = threading.Thread(daemon=True, target=self.get_time_stepper)
        self.thread_time_stepper.start()

    def get_pole_residue_fit_kwargs_list(self):
        min_poles = 0
        max_poles = 6
        rms_error_tolerance = 1e-4
        passive = True
        stable = True

        if self.carrier_frequency != 0:
            real = False
        else:
            real = True

        delays = self.delays
        delays_scales = [0, 0.8, 1]
        delays_list = [{key: scale * val for key, val in delays.items()} for scale in delays_scales]
        feedthrough_list = [True, False]

        fit_kwargs = self.fit_kwargs or {}

        if "min_poles" in fit_kwargs:
            min_poles = fit_kwargs["min_poles"]
        if "max_poles" in fit_kwargs:
            max_poles = fit_kwargs["max_poles"]
        num_poles_list = range(min_poles, max_poles + 1)

        if "rms_error_tolerance" in fit_kwargs:
            rms_error_tolerance = fit_kwargs["rms_error_tolerance"]
        if "delays" in fit_kwargs:
            delays_list = [fit_kwargs["delays"]]
        if "feedthrough" in fit_kwargs:
            feedthrough_list = [fit_kwargs["feedthrough"]]
        if "real" in fit_kwargs:
            real = fit_kwargs["real"]
        if "passive" in fit_kwargs:
            passive = fit_kwargs["passive"]
        if "stable" in fit_kwargs:
            stable = fit_kwargs["stable"]

        fit_kwargs_list = [
            {
                "delays": delays,
                "feedthrough": feedthrough,
                "min_poles": num_poles,
                "max_poles": num_poles,
                "real": real,
                "rms_error_tolerance": rms_error_tolerance,
                "stable": stable,
                "passive": False,
            }
            for num_poles in num_poles_list
            for delays in delays_list
            for feedthrough in feedthrough_list
        ]
        self.rms_error_tolerance = rms_error_tolerance
        self.passive = passive
        return fit_kwargs_list

    def get_s_matrix(self):
        import time

        while self.s_matrix_runner.status["message"] == "running":
            time.sleep(0.3)

        if self.s_matrix_runner.status["message"] == "error":
            self._status = self.s_matrix_runner.status
            return

        s_matrix_unshifted = self.s_matrix_runner.s_matrix
        frequencies_shifted = s_matrix_unshifted.frequencies - self.carrier_frequency
        s_matrix_shifted = SMatrix(
            frequencies=frequencies_shifted,
            elements=s_matrix_unshifted.elements,
            ports=s_matrix_unshifted.ports,
        )

        self.delays = s_matrix_shifted.estimate_delays(lossless=True)

        self.num_complete = 0
        self.pole_residue_fit_kwargs_list = self.get_pole_residue_fit_kwargs_list()
        self.num_to_fit = numpy.sum(
            [1 + fit_kwargs["max_poles"] ** 3 for fit_kwargs in self.pole_residue_fit_kwargs_list]
        )
        self.s_matrix = s_matrix_unshifted
        self.s_matrix_shifted = s_matrix_shifted

    def get_time_stepper(self):
        import time

        while self.s_matrix is None:
            time.sleep(0.3)

        s_matrix_shifted = self.s_matrix_shifted

        if self.passive is True or self.passive == "auto":
            keys = list(s_matrix_shifted.elements.keys())
            input_keys = list({key[0] for key in keys})
            output_keys = list({key[1] for key in keys})
            freqs = self.s_matrix.frequencies
            s_flat = numpy.zeros((len(freqs), len(output_keys), len(input_keys)), dtype=complex)
            for j, input_key in enumerate(input_keys):
                for k, output_key in enumerate(output_keys):
                    s_entry = s_matrix_shifted.elements.get((input_key, output_key), None)
                    if s_entry is not None:
                        for i in range(len(freqs)):
                            s_flat[i, k, j] = s_entry[i]
            bad_freqs = []
            singvals = numpy.linalg.svd(s_flat, compute_uv=False)
            warn_threshold = 1e-2
            for i, freq in enumerate(freqs):
                if numpy.any(singvals[i] > 1 + warn_threshold):
                    bad_freqs.append(freq)
            if len(bad_freqs) > 0:
                _warn.warn(
                    (
                        f"S matrix is not passive for '{self.component}'. "
                        f"Largest singular value is '{numpy.max(singvals):.4f}'."
                    ),
                    RuntimeWarning,
                    3,
                )

        rms_error_tolerance = self.rms_error_tolerance
        best_pr_nonpassive = None
        best_err_nonpassive = None
        best_fit_kwargs_nonpassive = None
        best_pr_passive = None
        best_err_passive = None
        best_fit_kwargs_passive = None
        for fit_kwargs in self.pole_residue_fit_kwargs_list:
            import warnings

            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore", message="^.*Desired RMS error tolerance not reached.*$"
                )
                warnings.filterwarnings(
                    "ignore", message="^.*Passivity enforcement failed: result is not passive.*$"
                )
                pr, err = pole_residue_fit(s_matrix_shifted, **fit_kwargs)
                if best_err_nonpassive is None or err < best_err_nonpassive:
                    best_err_nonpassive = err
                    best_pr_nonpassive = pr
                    best_fit_kwargs_nonpassive = fit_kwargs
                if self.passive is not False:
                    passive = pr.enforce_passivity(
                        frequencies=s_matrix_shifted.frequencies,
                        real=fit_kwargs["real"],
                        feedthrough=fit_kwargs["feedthrough"],
                    )
                    if passive:
                        err = pr.get_rms_error(s_matrix_shifted)
                        if best_err_passive is None or err < best_err_passive:
                            best_err_passive = err
                            best_pr_passive = pr
                            best_fit_kwargs_passive = fit_kwargs
                if best_err_passive is not None and best_err_passive < rms_error_tolerance:
                    break
                if self.passive is False:
                    if (
                        best_err_nonpassive is not None
                        and best_err_nonpassive < rms_error_tolerance
                    ):
                        break

            self.num_complete += 1 + fit_kwargs["max_poles"] ** 3

        # order of preference for passive == "auto" or False:
        #  1. passive pole-res with small enough error
        #  2. whichever model has the smallest error
        # for passive == True, always use passive pole-res
        time_domain_model = None
        # prefer passive pole-residue
        if self.passive is True or (
            best_err_passive is not None and best_err_passive < rms_error_tolerance
        ):
            pole_residue_matrix = best_pr_passive
            best_fit_kwargs = best_fit_kwargs_passive
            passive = True
            time_domain_model = TimeDomainModel(
                pole_residue_matrix=pole_residue_matrix, time_step=self.time_step
            )
        # allow other models
        elif self.passive is not True:
            if best_err_nonpassive is not None:
                pole_residue_matrix = best_pr_nonpassive
                best_fit_kwargs = best_fit_kwargs_nonpassive
                passive = False
                time_domain_model = TimeDomainModel(
                    pole_residue_matrix=pole_residue_matrix, time_step=self.time_step
                )

        if time_domain_model is None:
            self._status = {"progress": 100, "message": "error"}
            raise RuntimeError(f"Unable to obtain a fit for '{self.component}'.")
        if self.passive == "auto":
            if passive is False:
                _warn.warn(f"Fit is not passive for '{self.component}'.", RuntimeWarning, 3)

        time_stepper = SMatrixTimeStepper(
            s_matrix=self.s_matrix,
            time_domain_model=time_domain_model,
            fit_kwargs=best_fit_kwargs,
            time_step=self.time_step,
            carrier_frequency=self.carrier_frequency,
            model=self.model,
            component=self.component,
            time_index=self.time_index,
        )
        error = time_stepper.rms_error
        if error > rms_error_tolerance:
            _warn.warn(
                f"Fitting error '{error:.6f}' larger than 'rms_error_tolerance' "
                f"for '{self.component}'.",
                RuntimeWarning,
                3,
            )
        self.time_stepper = time_stepper

    @property
    def status(self):
        if self._status is not None:
            return self._status
        if self.s_matrix is None:
            progress = 0.5 * self.s_matrix_runner.status["progress"]
            return {"progress": progress, "message": "running"}
        if self.time_stepper is None:
            fit_progress = self.num_complete / self.num_to_fit
            return {"progress": 50 + 50 * fit_progress, "message": "running"}
        return {"progress": 100, "message": "success"}

    @property
    def s_fit(self):
        if self.time_stepper is None:
            return None
        return self.time_stepper.s_fit


class SMatrixTimeStepperModel(Model):
    """A time stepper model based on a pole-residue matrix.
    Calculates the frequency-domain S matrix, fits a pole-residue matrix to the data,
    and uses the resulting time-domain model to construct a time stepper.

    Args:
        time_domain_model: Override the default pole-residue matrix fitting with
          a custom time-domain model.
        frequencies: frequencies (Sequence[float]): Frequency values at which to
          calculate the scattering parameters (in Hz). The scattering parameters
          are used for fitting in time-stepper models.
        fit_kwargs (dict): Override the default kwargs used to fit the S matrix.
    """

    def __init__(
        self,
        time_domain_model: TimeDomainModel = None,
        frequencies: Optional[Sequence[float]] = None,
        fit_kwargs: Optional[dict] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            time_domain_model=time_domain_model,
            frequencies=frequencies,
            fit_kwargs=fit_kwargs,
            **kwargs,
        )
        self.time_domain_model = time_domain_model
        self.frequencies = frequencies
        self.fit_kwargs = fit_kwargs

    @cache_time_stepper
    def start_time_stepper(
        self,
        component: Component,
        time_step: float,
        time_index: int,
        carrier_frequency: float,
        frequencies: Optional[Sequence[float]] = None,
        **kwargs,
    ) -> _SMatrixTimeStepperModelRunner:
        """Start computing the time stepper for the given component.

        Args:
            component: Component from which to compute the S matrix.
            time_step (double): The interval between time steps (in seconds).
            time_index (int): The time index of the time stepper.
            carrier_frequency (double): The carrier frequency used to construct
              the time stepper. The carrier should be omitted from the input signal
              as it is handled automatically by the time stepper.
              Can be overridden by individual models or references.
            frequencies (Sequence[float]): Frequency values at which to
              calculate the scattering parameters (in Hz). The scattering parameters
              are used for fitting in time-stepper models.
              Can be overridden by individual models or references.
            **kwargs: Unused.

        Returns:
           Resulting time stepper.
        """
        if self.time_domain_model is not None:
            time_stepper = SMatrixTimeStepper(
                s_matrix=None,
                time_domain_model=self.time_domain_model,
                time_step=time_step,
                carrier_frequency=carrier_frequency,
                model=self,
                component=component,
            )
            return TimeStepperModelResult(time_stepper=time_stepper)

        if self.frequencies is not None:
            frequencies = self.frequencies
        elif frequencies is not None:
            frequencies = frequencies
        else:
            raise ValueError("Must specify 'frequencies' to obtain time stepper.")

        return _SMatrixTimeStepperModelRunner(
            model=self,
            component=component,
            time_step=time_step,
            time_index=time_index,
            carrier_frequency=carrier_frequency,
            frequencies=frequencies,
            fit_kwargs=self.fit_kwargs,
        )
