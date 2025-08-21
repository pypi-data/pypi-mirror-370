"""Define the runtime interface"""
import numpy as np
from collections import defaultdict
import textwrap
import copy
import re

import time

import logging

logger = logging.getLogger(__name__)

from femtorun.io_spec import IOSpec, IOSpecLegacyPadding

from typing import *
import numpy.typing as npt

NDARRAYINT = npt.NDArray[int]
NDARRAYINT64 = npt.NDArray[np.uint64]
NDARRAYFLOAT = npt.NDArray[np.float64]
VARVALS = Dict[str, NDARRAYINT]
FVARVALS = Dict[str, NDARRAYFLOAT]
LEGACYPAD = Optional[Dict[str, Union[int, Tuple[int], Tuple[int, int]]]]
MaybeFVARVALS = Union[VARVALS, FVARVALS]


class FemtoRunner:
    """Supports input/output padding for all derived runtimes

    Derived runners might pad inputs and outputs internally

    Legacy Args (to be deprecated):
        input_padding (dict {varname : (logical len, padded len)}, or None):
          Padding description for inputs; None for no padding
        output_padding (dict {varname : (logical len, padded len)}, or None):
          Padding description for outputs; None for no padding

    Args:
        io_spec (str or IOSpec obj, optional) : file name of IO spec or IO spec object
        pad (bool, default False) : whether or not to pad inputs/unpad outputs
        quantize (bool, default False) : whether or not to quantize inputs/dequantize outputs

    """

    def __init__(
        self,
        input_padding: LEGACYPAD,
        output_padding: LEGACYPAD,
        io_spec: Optional[Union[str, IOSpec]] = None,
        pad: bool = True,
        quantize: bool = False,
    ):
        self.pad = pad
        self.quantize = quantize

        if io_spec is not None:
            if isinstance(io_spec, str):
                self.io = IOSpec(io_spec)
            else:
                self.io = io_spec
        else:
            # temporary, can remove when argument is deprecated/all runners are converted
            if input_padding is not None and output_padding is not None:
                # legacy padding, ignore pad argument
                self.pad = True
                self.io = IOSpecLegacyPadding(input_padding, output_padding)
            else:
                self.pad = False
                self.io = IOSpecLegacyPadding(None, None)
            assert not quantize  # need real IOSpec for this

    def reset(self, reset_vals=None):
        """Reset (or initialize) the runner

        In hardware, this is the hard reset. In a simulation,
        it could mean resetting memory states, metric counters

        The outer reset() function also calls IOSpec's sim_reset()
        """
        self.io.sim_reset()
        self._reset(reset_vals=reset_vals)

    def _reset(self, reset_vals=None):
        """Reset (or initialize) the runner

        In hardware, this is the hard reset. In a simulation,
        it could mean resetting memory states, metric counters
        """
        raise NotImplementedError("Derived class of FemtoRunner must implement")

    def finish(self):
        raise NotImplementedError("Derived class of FemtoRunner must implement")

    def set_vars(self, set_vals):
        raise NotImplementedError("Derived class of FemtoRunner must implement")

    def get_vars(self, varnames):
        raise NotImplementedError("Derived class of FemtoRunner must implement")

    def get_internals(self) -> MaybeFVARVALS:
        """gets all internal variables that are accessible, per runner setup
        implementation will depend on the derived runner, but typically calls get_vars()
        for some set of variables that are monitored

        Does not necessarily need to be implemented. Returns empty by default.
        """
        return {}

    def _quantize_inputs(self, input_vals: MaybeFVARVALS) -> VARVALS:
        """allows easy interoperability between runners that use real-valued inputs
        and those that dont"""

        # AN 11/27/23, working around bug in FS/FX
        # note that all FRs use integers
        cast_input_vals = {}
        for varname, this_input in input_vals.items():
            if np.issubdtype(this_input.dtype, np.integer):
                cast_input_vals[varname] = this_input
            else:
                this_input_as_int = this_input.astype(int)
                was_actually_int = np.allclose(this_input_as_int, this_input)
                if not was_actually_int:
                    raise ValueError(f"nontrivial float->int conversion for {varname}")
                logger.warning(f"converted {varname}, float-of-ints, to int")
                cast_input_vals[varname] = this_input_as_int
        input_vals = cast_input_vals

        if self.quantize:
            # implement me
            input_vals = input_vals
        return input_vals

    def _dequantize_inputs(self, output_vals: VARVALS) -> MaybeFVARVALS:
        """allows easy interoperability between runners that use real-valued outputs
        and those that dont"""
        if self.quantize:
            # implement me
            output_vals = output_vals
        return output_vals

    def _pad_inputs(self, input_vals: VARVALS) -> VARVALS:
        """allows easy interoperability between runners that need padded inputs
        and those that dont"""
        if not self.pad or self.io.input_padding is None:
            return input_vals
        else:
            # pad zeros
            padded = {}

            for varname, vals in input_vals.items():
                valshape = vals.shape
                logicalshape, padshape = self.io.input_padding[varname]

                # FIXME disabled for now, too much weird stuff getting passed in by legacy runners
                # if logicalshape != valshape:
                #    raise ValueError(
                #        f"was passed an input {varname} that had shape {valshape}, expected {logicalshape}"
                #    )

                padded[varname] = np.zeros(padshape, dtype=int)
                if len(valshape) == 1:
                    padded[varname][: valshape[0]] = input_vals[varname]
                elif len(valshape) == 2:
                    padded[varname][: valshape[0], : valshape[1]] = input_vals[varname]
                else:
                    assert False
            return padded

    def _unpad_outputs(self, output_vals: VARVALS) -> VARVALS:
        """allows easy interoperability between runners that need padded outputs
        and those that dont"""
        if not self.pad or self.io.output_padding is None:
            ret = output_vals
        else:
            unpadded = {}
            for varname, vals in output_vals.items():
                logicalshape, padshape = self.io.output_padding[varname]
                if len(padshape) == 1:
                    unpadded[varname] = np.atleast_1d(output_vals[varname])[
                        : logicalshape[0]
                    ]
                elif len(padshape) == 2:
                    unpadded[varname] = np.atleast_2d(output_vals[varname])[
                        : logicalshape[0], : logicalshape[1]
                    ]
                else:
                    assert False
            ret = unpadded
        return ret

    ####################################################
    # low level APIs, akin to AXIS send/recv in HW
    ####################################################

    def send_inputs(self, inputs: MaybeFVARVALS):
        """Send one or more inputs to the runner

        A derived runner will know what computations are performed after these inputs are recv'd,
        and what outputs are produced, if any.

        Derived class may optionally overload (perhaps taking advantage of self.io)
        but it should be sufficient to overload _send_inputs().
        """
        inputs = self._quantize_inputs(self._pad_inputs(inputs))
        self.io.sim_send_inputs(inputs.keys())
        self._send_inputs(inputs)

    def recv_outputs(self) -> MaybeFVARVALS:
        """recv all outputs that have been produced

        This might return an empty VARVALS, if no ouputs were produced given
        previously delivered inputs.

        Derived class may optionally overload (perhaps taking advantage of self.io)
        but it should be sufficient to overload _recv_outputs().
        """
        output_names = self.io.sim_recv_outputs()
        outputs = self._recv_outputs(output_names)
        if output_names is not None and not set(outputs.keys()) == set(output_names):
            raise RuntimeError(
                f"didn't get all expected outputs\nneeded {output_names}\nbut got {outputs.keys()}"
            )
        return self._dequantize_inputs(self._unpad_outputs(outputs))

    def _send_inputs(self, inputs: MaybeFVARVALS):
        """inner implementation of send_inputs, to be overloaded by base class
        The runner's responsibility does not include quantization or padding
        """
        raise NotImplementedError("Derived class of FemtoRunner must implement")

    def _wait_for_output(self):
        """wait until an output has been produced.
        On hardware, this is equivalent to waiting until the
        the interrupt pin has been asserted, after the output has been produced.
        On a simulator, it's possible that no action is needed for this function,
        it could just be a pass, or an assertion that execution reached a certain point
        """
        raise NotImplementedError("Derived class of FemtoRunner must implement")

    def _recv_outputs(
        self, expected_output_names: Optional[list[str]]
    ) -> MaybeFVARVALS:
        """inner implementation of recv_outputs, to be overloaded by base class
        The runner's responsibility does not include quantization or padding
        Even though the runner receives the list of output names,
        it should not be necessary in most cases
        (the runner should know which outputs can be delivered).
        It can be used as a check
        """
        raise NotImplementedError("Derived class of FemtoRunner must implement")

    ####################################################
    # higher-level APIs
    ####################################################

    def step(self, input_vals: MaybeFVARVALS) -> tuple[MaybeFVARVALS, MaybeFVARVALS]:
        """for models with only a single simple_sequence in their spec,
        execute one timestep, driving input_vals and getting outputs

        Args:
            input_vals (dict {varname (str): val (1d numpy.ndarray)):
                Variable names and their values for one timestep

        Returns:
            (output_vals, internal_vals) tuple(dict, dict)):
                tuple of dictionaries with same format as input_vals,
                Output variables and their values, and
                internal variables and their values
        """
        if not self.io.is_simple:
            raise RuntimeError(
                "tried to call step() for a FemtoRunner with a more complex IO spec. step() is only for networks with 'function-style' inputs->step->outputs dependency."
            )

        self.send_inputs(input_vals)
        internals = self.get_internals()
        return self.recv_outputs(), internals

    def run(
        self, input_val_timeseries: MaybeFVARVALS
    ) -> Union[tuple[VARVALS, VARVALS, VARVALS], tuple[FVARVALS, FVARVALS, FVARVALS]]:
        """Execute several timesteps, iterating through the values of input_val_timeseries
        driving the runner at each timestep. Calls .step() each timestep.

        Args:
            input_val_timeseries (dict {varname (str): value (numpy.ndarray)}):
                keyed by variable names, values are 2d numpy arrays, first dim is time

        Returns:
            (output_vals, internal_vals, output_valid_mask) tuple(dict, dict, dict)):
                tuple of dictionaries with same format as input_vals,
                values for the output variables as well as all internal variables,
                for all timesteps that were run
                output_valid_mask contains a 1D bool array for each key, says whether each output
                was produced on a given timestep
        """

        # check that indexables are all the same length
        first_var_vals = next(iter(input_val_timeseries.values()))
        n_steps = first_var_vals.shape[0]
        if not all(val.shape[0] == n_steps for val in input_val_timeseries.values()):
            raise ValueError("Input sequence lengths don't match for all variables")

        # run simulation, calling step, building up lists for outputs and internal states
        output_vals = {}
        output_valid_mask = {}
        internal_vals = {}

        for i in range(n_steps):
            step_inputs = {
                varname: values[i] for varname, values in input_val_timeseries.items()
            }

            step_out, step_internals = self.step(step_inputs)

            for varname, val in step_out.items():
                if varname not in output_vals:
                    output_vals[varname] = np.zeros(
                        (n_steps, *val.shape), dtype=val.dtype
                    )
                    output_valid_mask[varname] = np.zeros(n_steps, dtype=bool)
                output_vals[varname][i] = val
                output_valid_mask[varname][i] = True

            for varname, val in step_internals.items():
                if varname not in internal_vals:
                    assert i == 0, "should have all internal values, every step"
                    internal_vals[varname] = np.zeros(
                        (n_steps, *val.shape), dtype=val.dtype
                    )
                internal_vals[varname][i] = val

        FemtoRunner.check_mask_complete(output_valid_mask)  # XXX for now

        return output_vals, internal_vals, output_valid_mask

    @classmethod
    def compare_outputs(
        cls,
        name_A: str,
        output_A: VARVALS,
        name_B: str,
        output_B: VARVALS,
        error_tolerance: Optional[Union[float, int]] = None,
        logstr: str = "compare_outputs",
    ) -> int:
        """
        Compare two {name -> np.ndarray} maps.

        Rules
        -----
        * Same key set is **required** (compare_internals already enforces this).
        * Rank must match.
        * If more than one axis length differs → error.
        * If exactly one axis length differs → slice both arrays to
        `min(dim_A, dim_B)` on that axis and compare values.
        * Optional absolute `error_tolerance`.
        * Returns 0 on success, −1 on any mismatch (shape or value).
        """
        shape_dict = lambda x: {k: v.shape for k, v in x.items()}
        contents_str = (
            f"{logstr}: {name_A} vs {name_B}\n"
            f"{name_A} shapes:\n{textwrap.indent(str(shape_dict(output_A)), '  ')}\n"
            f"{name_B} shapes:\n{textwrap.indent(str(shape_dict(output_B)), '  ')}\n"
        )

        # ------------------------------------------------------------------ keys
        if set(output_A.keys()) != set(output_B.keys()):
            logger.debug(contents_str)
            logger.error(
                f"Key mismatch between {name_A} and {name_B}\n"
                f"{name_A}: {sorted(output_A.keys())}\n"
                f"{name_B}: {sorted(output_B.keys())}"
            )
            return -1

        # ---------------------------------------------------------------- shapes
        bad_shape_multi, bad_shape_rank = [], []
        slice_spec = {}  # per-key slice tuples (Ellipsis == exact match)

        for k in output_A:
            a, b = output_A[k], output_B[k]

            if a.ndim != b.ndim:
                bad_shape_rank.append((k, a.shape, b.shape))
                continue

            diff_axes = [
                i for i, (sa, sb) in enumerate(zip(a.shape, b.shape)) if sa != sb
            ]

            if len(diff_axes) == 0:  # identical
                slice_spec[k] = (Ellipsis,)
            elif len(diff_axes) == 1:  # one-axis mismatch → make slice
                ax = diff_axes[0]
                overlap = min(a.shape[ax], b.shape[ax])
                slicer = [slice(None)] * a.ndim
                slicer[ax] = slice(0, overlap)
                slice_spec[k] = tuple(slicer)
            else:  # >1 axis mismatch
                bad_shape_multi.append((k, a.shape, b.shape))

        if bad_shape_rank or bad_shape_multi:
            msg = "Shape mismatches:\n"
            for k, sA, sB in bad_shape_rank:
                msg += f"  {k}: rank differs {sA} vs {sB}\n"
            for k, sA, sB in bad_shape_multi:
                msg += f"  {k}: >1 axis differ {sA} vs {sB}\n"
            logger.debug(contents_str)
            logger.error(msg)
            return -1

        # ------------------------------------------------------------- values
        bad_value = []

        for k in output_A:
            a, b = output_A[k], output_B[k]
            sl = slice_spec[k]
            a_sub, b_sub = a[sl], b[sl]

            if error_tolerance is None:
                equal = np.all(a_sub == b_sub)
            else:
                equal = np.all(np.abs(a_sub - b_sub) <= error_tolerance)

            if not equal:
                bad_value.append((k, a.shape, b.shape, a_sub, b_sub))

        if bad_value:
            # ---------- new, more-verbose report ----------
            msg = "Value mismatches:\n"
            for k, sA, sB, a_sub, b_sub in bad_value:
                msg += f"  {k}: compared over "
                msg += "full shape " if sA == sB else "overlapping slice "
                msg += f"{sA} vs {sB}\n"

            msg += "these were the mismatches:\n"
            for k, _, _, a_sub, b_sub in bad_value:
                diff = a_sub - b_sub
                msg += f"{k} :\n"
                msg += f"{name_A} had:\n{textwrap.indent(str(a_sub), '  ')}\n"
                msg += f"{name_B} had:\n{textwrap.indent(str(b_sub), '  ')}\n"
                msg += f"difference ({name_A} - {name_B}):\n{textwrap.indent(str(diff), '  ')}\n"

            logger.debug(contents_str)
            logger.error(msg)
            return -1

        logger.debug(f"{logstr} succeeded")
        return 0

    @classmethod
    def _sortkey(cls, x):
        endnum = re.search(r"\d+$", x)
        if endnum:
            return int(endnum.group())
        else:
            return 0  # others wind up in random order

    @classmethod
    def compare_internals(
        cls,
        name_A: str,
        output_A: VARVALS,
        name_B: str,
        output_B: VARVALS,
        error_tolerance: Optional[Union[float, int]] = None,
    ) -> int:
        """
        Compare only the tensors that appear in *both* dictionaries.

        • `compare_outputs` is still called first - so shape-mismatch diagnostics
        stay exactly the same.
        • We then run a second pass that:
            - Ignores rank mismatches and >1-axis shape mismatches.
            - Slices both tensors to the overlapping extent when exactly one axis
            differs.
            - Collects any *value* mismatches and prints a full dump.
            - If no value mismatches are found it logs an INFO message.
        • Return value is -1 if *either* the first or second pass found a
        mismatch, otherwise 0.
        """
        # ------------------------------- establish common keys ------------------
        key_points = sorted(output_A.keys() & output_B.keys(), key=cls._sortkey)

        key_A = {k: output_A[k] for k in key_points}
        key_B = {k: output_B[k] for k in key_points}

        logger.debug("Comparing Internal Values")
        logger.debug("Key Points:\n%s", key_points)
        logger.debug(
            "%s-only vars (NOT compared):\n%s",
            name_A,
            sorted(output_A.keys() - key_points),
        )
        logger.debug(
            "%s-only vars (NOT compared):\n%s",
            name_B,
            sorted(output_B.keys() - key_points),
        )

        # ---------------------- first pass: shape diagnostics -------------------
        shape_err = cls.compare_outputs(
            name_A, key_A, name_B, key_B, error_tolerance, logstr="compare_internals"
        )  # prints shape problems if any

        # ---------------------- second pass: value mismatches -------------------
        mismatches = []  # (key, shape_A, shape_B, slice_A, slice_B, diff)
        for k in key_points:
            a, b = key_A[k], key_B[k]

            # Skip if rank differs or >1 axis differs - we can’t slice sensibly.
            if a.ndim != b.ndim:
                continue
            diff_axes = [
                i for i, (sa, sb) in enumerate(zip(a.shape, b.shape)) if sa != sb
            ]
            if len(diff_axes) > 1:
                continue

            # Build slice tuple
            if len(diff_axes) == 0:
                sl = (Ellipsis,)
            else:
                ax = diff_axes[0]
                overlap = min(a.shape[ax], b.shape[ax])
                slicer = [slice(None)] * a.ndim
                slicer[ax] = slice(0, overlap)
                sl = tuple(slicer)

            a_sub, b_sub = a[sl], b[sl]

            if error_tolerance is None:
                equal = np.all(a_sub == b_sub)
            else:
                equal = np.all(np.abs(a_sub - b_sub) <= error_tolerance)

            if not equal:
                mismatches.append((k, a.shape, b.shape, a_sub, b_sub, a_sub - b_sub))

        # ---------------------- print summary of second pass --------------------
        if mismatches:
            msg = "Internal value mismatches (after slicing to overlapping extents):\n"
            for k, sA, sB, *_ in mismatches:
                msg += f"  {k}: {sA} vs {sB}\n"
            msg += "these were the mismatches:\n"
            for k, _, _, a_sub, b_sub, diff in mismatches:
                msg += f"{k} :\n"
                msg += f"{name_A} had:\n{textwrap.indent(str(a_sub), '  ')}\n"
                msg += f"{name_B} had:\n{textwrap.indent(str(b_sub), '  ')}\n"
                msg += f"difference ({name_A} - {name_B}):\n{textwrap.indent(str(diff), '  ')}\n"

            logger.error(msg)
            return -1  # value error in internals
        else:
            logger.info(
                "Internal comparisons: **no value mismatches** "
                "(shape-only differences ignored)."
            )
            return shape_err  # 0 if shapes OK, −1 if only shape problems

    @classmethod
    def check_mask_complete(cls, mask):
        """for now, we don't handle checking outputs that don't have full masks
        this functionality can be added later and this check removed"""
        for k, v in mask.items():
            if np.sum(v.flatten()) != np.prod(v.shape):
                raise NotImplementedError()

    @classmethod
    def compare_runs(
        cls,
        inputs: VARVALS,
        *runners,
        names: Optional[List[str]] = None,
        compare_internals: bool = False,
        except_on_error: bool = True,
        error_tolerance: Optional[Union[float, int]] = None,
        no_reset: bool = False,
        compare_status: Optional[Dict] = None,
    ):
        """run two FemtoRunners next to each other and compare the outputs

        doesn't compare internal states, which can be hard to generalize, returns them instead

        Args:
            inputs : (dict) : same format to FemtoRunne.run()
            *runners : (variable number of :obj:`FemtoRunner`) : the FemtoRunners to compare
            compare_internals : also check internal variables values' match
        """
        np.set_printoptions(threshold=10000)

        if names is None:
            names = [runner.__class__.__name__ for runner in runners]
        assert len(names) == len(runners)

        outs = []
        internals = []
        out_masks = []
        durs = []

        def run_one(name, runner):
            t0 = time.time()

            try:
                if not no_reset:
                    runner.reset()

                out, internal, out_mask = runner.run(inputs)
                outs.append(out)
                internals.append(internal)
                out_masks.append(out_mask)

                runner.finish()
            except:
                runner.finish()  # we need to try to exit cleanly for some runners, notably FB's SimRunner
                raise

            tdur = time.time() - t0
            durs.append(tdur)

        for name, runner in zip(names, runners):
            run_one(name, runner)

        saw_err = False
        for name, runner, out in zip(names[1:], runners[1:], outs[1:]):
            err = FemtoRunner.compare_outputs(
                names[0], outs[0], name, out, error_tolerance
            )
            saw_err = saw_err or (err != 0)
            if not saw_err:
                logger.info(
                    "Output comparison succeeded! checking internal key points (if supplied)"
                )

            if err:
                # if the output didn't match, run the internal comparison anyway for debug purposes
                logger.info(
                    "Output comparison failed! checking internal key points (if supplied)"
                )
                for name, runner, out in zip(names[1:], runners[1:], internals[1:]):
                    FemtoRunner.compare_internals(
                        names[0], internals[0], name, out, error_tolerance
                    )

        saw_internal_err = False
        if compare_internals:
            # check internal values that name-match
            for name, runner, out in zip(names[1:], runners[1:], internals[1:]):
                err = FemtoRunner.compare_internals(
                    names[0], internals[0], name, out, error_tolerance
                )
                saw_internal_err = saw_internal_err or (err != 0)

        if saw_err:
            status_str = "OUTPUT COMPARISONS FAILED! See log\n"
            final_log = logger.error
        elif not saw_err and saw_internal_err:
            status_str = (
                "Output comparison succeeded, BUT internal points differ! See log\n"
            )
            final_log = logger.warning
        else:
            status_str = "Comparison of these runners SUCCEEDED!:\n"
            final_log = logger.info

        for name, runner, dur in zip(names, runners, durs):
            status_str += textwrap.indent(f"{name} : took {round(dur, 2)} s\n", "  ")
        final_log(status_str)

        if saw_err and except_on_error:
            raise ValueError(status_str)

        # fill pass by ref compare_status dict
        if compare_status is not None:
            compare_status["pass"] = not saw_err
            compare_status["status_str"] = status_str

        np.set_printoptions(threshold=1000)  # the default, put it back

        _rekey = lambda x: {n: vals for n, vals in zip(names, x)}
        # rekey from runner index to supplied name for convenience
        return _rekey(outs), _rekey(internals)


class ComposedRunner(FemtoRunner):
    """create a new FemtoRunner object that strings one or more runners together

    The port maps allow for hooking up output names to input names

    Args:
        list_of_runners : (list of :obj:`FemtoRunner`) :
            list of femtorunners to stack in a sequence
        list_of_port_maps : (list of dicts, or None) :
            list of port maps, or None where a port map is not needed
            must be the same length as list_of_runners
            individual list elements may also be None if no mapping is needed for that layer
            [{output_i_name : input_i+1_name, ...}, ...]
    """

    def __init__(self, list_of_runners, list_of_port_maps=None):
        self.runners = list_of_runners
        self.port_maps = list_of_port_maps

    def reset(self, reset_vals=None):
        for runner in self.runners():
            runner.reset(reset_vals)

    def finish(self):
        for runner in self.runners:
            runner.finish()

    def step(self, input_vals):
        layer_inputs = input_vals
        all_internals = {}
        for i, runner in enumerate(self.runners):
            outputs, internals = runner.step(layer_inputs)

            if self.port_maps is not None and self.port_maps[i] is not None:
                layer_inputs = {}
                port_map = self.port_maps[i]
                for k, v in outputs.items():
                    layer_inputs[port_map[k]] = v
            else:
                layer_inputs = outputs

            for k, v in internals:
                if k in all_internals:
                    raise NotImplementedError(
                        "colliding state names in ComposedRunner, need to deal with this somehow"
                    )
                all_internals[k] = v

        return layer_inputs, all_internals
