import logging
from numbers import Number
from typing import Dict, List, Optional, Tuple, Union

import numpy

from .data_access import TaskWithDataAccess
from .utils import data_utils
from .utils.integrate_utils import is_counter_name

logger = logging.getLogger(__name__)


class BaseIntegrate(
    TaskWithDataAccess,
    input_names=[],
    optional_input_names=[
        "mask",
        "flatfield",
        "darkcurrent",
        "integration_options",
        "fixed_integration_options",
    ],
    register=False,
):

    def _get_ewoks_pyfai_options(self) -> dict:
        # Integration options
        ewoks_pyfai_options = dict()

        integration_options = data_utils.data_from_storage(
            self.inputs.integration_options, remove_numpy=True
        )
        if integration_options:
            ewoks_pyfai_options.update(integration_options)

        fixed_integration_options = data_utils.data_from_storage(
            self.get_input_value("fixed_integration_options", None), remove_numpy=True
        )
        if fixed_integration_options:
            ewoks_pyfai_options.update(fixed_integration_options)

        # Default units
        ewoks_pyfai_options.setdefault("unit", "2th_deg")

        # Correction images
        if not self.missing_inputs.mask and self.inputs.mask is not None:
            ewoks_pyfai_options["mask"] = self.get_image(
                data_utils.data_from_storage(self.inputs.mask)
            )
        if not self.missing_inputs.flatfield and self.inputs.flatfield is not None:
            ewoks_pyfai_options["flatfield"] = self.get_image(
                data_utils.data_from_storage(self.inputs.flatfield)
            )
        if not self.missing_inputs.darkcurrent and self.inputs.darkcurrent is not None:
            ewoks_pyfai_options["darkcurrent"] = self.get_image(
                data_utils.data_from_storage(self.inputs.darkcurrent)
            )

        return ewoks_pyfai_options

    def _pyfai_normalization_factor(
        self,
        monitors: List[Union[numpy.ndarray, Number, str, list, None]],
        references: List[Union[numpy.ndarray, Number, str, list, None]],
        ptdata: Optional[Dict[str, numpy.ndarray]] = None,
    ) -> Tuple[float, float]:
        r"""Returns the pyfai normalization factor based on a monitor and a references.

        The pyfai normalization factor is defined as

        .. code::

            Inorm = I / (normalization_factor1 * normalization_factor2 * ...)

        Monitor normalization is done like this

        .. code::

            Inorm = I * reference1 / monitor1 * reference2 / monitor2 * ...

        which means that the normalization factor is

        .. code::

            normalization_factor = monitor1 / reference1 * monitor2 / reference2 * ...

        Both monitors and references can be defined by:

         * scalar value
         * array or list of numbers
         * counter name
         * data URL
        """
        numerator = 1.0
        for value in monitors:
            if not data_utils.is_data(value):
                value = 1
            elif is_counter_name(value):
                if ptdata is None:
                    raise ValueError("monitor value cannot be a counter name")
                value = ptdata[value]
            else:
                value = self.get_data(value)
            numerator *= value

        if not numpy.isscalar(numerator):
            raise ValueError("monitor values need to be scalars")

        denominator = 1.0
        for value in references:
            if not data_utils.is_data(value):
                value = 1
            elif is_counter_name(value):
                if ptdata is None:
                    raise ValueError("reference value cannot be a counter name")
                value = ptdata[value]
            else:
                value = self.get_data(value)
            denominator *= value

        if not numpy.isscalar(denominator):
            raise ValueError("reference values need to be scalars")

        return numerator, denominator
